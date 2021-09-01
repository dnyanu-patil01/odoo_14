# -*- coding: utf-8 -*-
import base64
from odoo import fields, models, api
from .shiprocket_request import ShipRocket
from odoo.exceptions import UserError
from odoo.tools import pdf
import requests

class ShiprocketBulkProcess(models.Model):
    _name = "shiprocket.bulk.process"
    _description = "Shiprocket Bulk Processing"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    def _get_default_channel_id(self):
        custom_channel =  self.env['shiprocket.channel'].search(
            [('base_channel_code', '=', 'CS')],limit=1)
        if custom_channel:
            return custom_channel.id
        else:
            return False

    name = fields.Char("Name", required=True, tracking=True)
    pickup_location_id = fields.Many2one(
        "shiprocket.pickup.location", "Shiprocket Pickup Location", tracking=True,required=True
    )
    stock_picking_ids = fields.Many2many("stock.picking", string="Delivery Orders",domain="[('pickup_location','=',pickup_location_id),('picking_type_code', '=', 'outgoing'),('delivery_type','=','shiprocket'),('state','=','done'),('shiprocket_shipping_id','!=',False),('shiprocket_awb_code','=',False)]")
    channel_id = fields.Many2one("shiprocket.channel", "Channel", tracking=True,default=_get_default_channel_id)
    shiprocket_courier_priority = fields.Selection(
        [
            ("rate", "Best Rated"),
            ("price", "Cheapest"),
            ("fast", "Fasted"),
            ("custom", "Custom"),
            ("recommend", "Recommended By Shiprocket"),
        ],
        default="price",
        string="Courier Priority",
        tracking=True,
        ondelete="set null"
    )
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("waiting_awb", "Waiting To Generate AWB"),
            ("awb_created", "AWB Generated"),
            ("awb_created_partially","AWB Generated Partially"),
            ("waiting_create_pickup","Waiting To Create Pickup Request"),
            ("pickup_created", "Pickup Created"),
            ("pickup_created_partially", "Pickup Created Partially"),
            ("waiting_to_manifest", "Waiting To Generate Manifest"),
            ("ready_to_manifest", "Ready To Generate Manifest"),
            ("manifest_generated", "Manifest Generated"),
            ("close", "Closed"),
            ("done", "Completed"),
        ],
        default="draft",
        tracking=True,
        ondelete="set null",
        required=False
    )
    # manifest_url = fields.Char(readonly=True)
    # label_url = fields.Char(readonly=True)
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        default=lambda self: self.env["res.company"]._company_default_get(),
    )
    user_id = fields.Many2one(
        "res.users", string="Responsible", default=lambda self: self.env.uid
    )
    response_comment = fields.Char(readonly=True)

    @api.constrains('stock_picking_ids')
    def _constrains_check_stock_picking_ids(self):
        for record in self:
            if not record.stock_picking_ids:
                raise UserError(('Please Select Atleast One Picking Line To Proceed'))

    def shiprocket_create_awb(self):
        '''
        Draft ---> Waiting To Generate AWB
        It will schedule queue job to generate AWB and Labels.
        '''
        self.write({"state": "waiting_awb"})
        self.stock_picking_ids.write({'bulk_order_id':self.id})
        self.with_delay().generate_awb_bulk()
        
    
    def generate_awb_bulk(self):
        '''
        Job Queue Function Executed Asyn
        '''
        shiprocket = ShipRocket(self.env.company)
        for picking in self.stock_picking_ids.filtered(lambda r: r.is_awb_generated == False):
            picking.shiprocket_check_serviceability()
            if self.set_courier_id(picking):
                picking.with_delay().shiprocket_create_awb()
                picking.get_shiprocket_status()
                if 'shiprocket_awb_code' in picking:
                    picking.write({"is_awb_generated":True})
        self.send_mail_on_queue_completion()
        return True

    def shiprocket_get_ready_to_manifest(self):
        self.write({"state": "waiting_to_manifest"})
        self.with_delay().prepare_to_generate_manifest()

    def prepare_to_generate_manifest(self):
        shiprocket = ShipRocket(self.env.company)
        self.env["wiz.stock.picking.lines"].search(
            [("bulk_process_id", "=", self.id)]
        ).unlink()
        wizard_picking_lines = []
        for picking in self.stock_picking_ids:
            picking.get_shiprocket_status()
            wizard_picking_lines.append({
                    "picking_id": picking.id,
                    "bulk_process_id": self.id,
                    "shiprocket_awb_code": picking.shiprocket_awb_code,
                }
            )
        self.env["wiz.stock.picking.lines"].create(wizard_picking_lines)
        self.send_mail_on_queue_completion()
        return True

    def set_courier_id(self, picking):
        serviceability_matrix = self.env["shiprocket.serviceability.matrix"]
        if self.shiprocket_courier_priority == "rate":
            courier_id = serviceability_matrix.search(
                [("picking_id", "=", picking.id)], order="rating desc", limit=1
            )
        if self.shiprocket_courier_priority == "price":
            courier_id = serviceability_matrix.search(
                [("picking_id", "=", picking.id)], order="rate", limit=1
            )
        if self.shiprocket_courier_priority == "fast":
            courier_id = serviceability_matrix.search(
                [("picking_id", "=", picking.id)], order="etd_hours", limit=1
            )
        if self.shiprocket_courier_priority == "custom":
            courier_id = serviceability_matrix.filtered(
                lambda line: line.courier_company_id.id
                == picking.recommended_courier_company_id.id
            )
        if self.shiprocket_courier_priority == "recommend":
            courier_id = serviceability_matrix.filtered(
                lambda line: line.courier_company_id.id
                == picking.shiprocket_recommended_courier_id.id
            )
        if courier_id:
            set_courier_id = self.env["set.courier"].create(
                {
                    "selected_courier_id": courier_id.id,
                    "picking_id": picking.id,
                }
            )
            set_courier_id.set_courier_in_picking()
            return True
        return False

    
    def generate_pickup_request_bulk(self):
        '''Create Queue Job To Generate Pickup Request In Shiprocket'''
        self.write({'state':'waiting_create_pickup'})
        self.with_delay().generate_pickup_request()

    def generate_pickup_request(self):
        shiprocket = ShipRocket(self.env.company)
        picking_ids = self.stock_picking_ids.filtered(lambda m:m.is_pickup_request_done == False).ids
        response_details = ''
        for ids in self.split_request_ids(picking_ids):
            splited_picking_ids = self.env['stock.picking'].browse(ids)
            shipment_ids = list(
            map(int, splited_picking_ids.mapped("shiprocket_shipping_id")))
            response_data = shiprocket._generate_pickup_request(shipment_ids)
            if 'pickup_request_note' in response_data:
                splited_picking_ids.write({'is_pickup_request_done':True})
            else:
                for picking in splited_picking_ids:
                    if not picking.is_pickup_request_done:
                        res = picking.shiprocket_generate_pickup_request()
                        if 'pickup_request_note' not in res:
                            response_details+=str(res)
        self.write({"response_comment": str(response_details)})
        self.send_mail_on_queue_completion()
        return True

    def print_manifest_bulk(self):
        order_ids = list(
            map(
                int,
                self.stock_picking_ids.filtered(
                    lambda s: s.is_manifest_generated != False
                ).mapped("shiprocket_order_id"),
            )
        )
        shiprocket = ShipRocket(self.env.company)
        manifest_url_list = []
        response_content = ""
        shiprocket = ShipRocket(self.env.company)
        for ids in self.split_request_ids(order_ids):
            response_data = shiprocket._print_manifest_request(ids)
            if 'manifest_url' in response_data:
                manifest_url_list.append(response_data.get('manifest_url'))
            else:
                response_content += response_data['response_comment']
        if manifest_url_list != []:
            self.generate_attachment_pdf(manifest_url_list,'Manifest')
        if response_content:
            self.write({"response_comment":response_content})

    def print_labels_bulk(self):
        shipment_ids = list(
            map(
                int,
                self.stock_picking_ids.filtered(
                    lambda s: s.shiprocket_awb_code != False
                ).mapped("shiprocket_shipping_id"),
            )
        )
        label_url_list = []
        response_content = ""
        shiprocket = ShipRocket(self.env.company)
        for ids in self.split_request_ids(shipment_ids):
            response_data = shiprocket._generate_label_request(ids)
            if 'label_url' in response_data:
                label_url_list.append(response_data.get('label_url'))
            else:
                response_content += response_data['response_comment']
        if label_url_list != []:
            self.generate_attachment_pdf(label_url_list,'Labels')
        response_data = shiprocket._generate_label_request(shipment_ids)
        if response_content:
            self.write({"response_comment":response_content})

    def shiprocket_open_wizard(self):
        wiz_barcodes_read_id = self.env["wiz.barcodes.read"].create(
            {"bulk_process_id": self.id}
        )
        return {
            "name": ("Scan Label Barcode"),
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "res_model": "wiz.barcodes.read",
            "res_id": wiz_barcodes_read_id.id,
            "target": "new",
        }

    def split_request_ids(self,ids):
        '''split request ids based on api limit in ir.config_parameter
        '''
        Parameters = self.env["ir.config_parameter"].sudo()
        n = int(Parameters.get_param("no_of_request_per_api_call"))
        if not n:
            return []
        return [ids[i * n:(i + 1) * n] for i in range((len(ids) + n - 1) // n )] 
    
    def generate_attachment_pdf(self,attachment_urls,type):
        pdf_content = []
        for url in attachment_urls:
            response = requests.get(url,stream=True)
            pdf_content.append(response.content)
        content = pdf.merge_pdf(pdf_content)
        Attachment = self.env['ir.attachment']
        attachment_name = "%s-%s"%(type,self.name)
        prev_attachment = Attachment.search([('res_model','=','shiprocket.bulk.process'),('res_id','=',self.id),('name','=',attachment_name)])
        if prev_attachment:
            prev_attachment.unlink()
        attachment_id = Attachment.create({
        'name': attachment_name,
        'type': 'binary',
        'datas': base64.b64encode(content),
        'res_model': 'shiprocket.bulk.process',
        'res_id': self.id,
        })
        return True
    
    def email_message_content(self):
        new_state = self.set_state()
        if self.state in ('awb_created_partially','awb_created'):
            fill_content = (self.name,'Waiting To Generate AWB',new_state)
        if self.state in ('pickup_created_partially','pickup_created'):
            fill_content = (self.name,'Waiting To Create Pickup Request',new_state)
        if self.state in ('ready_to_manifest','waiting_to_manifest','manifest_generated'):
            fill_content = (self.name,'Waiting To Generate Manifest',new_state)
        if not new_state:
            message = """"
            The Bulk Process : %s No Process Happens in the process please kindly process it one more time.
            State Changed : No Change
            """ %(self.name)
        message = """
            The Bulk Process : %s
            
            State Changed : 
            %s -----> %s
        """ % (fill_content)
        return message
    
    def send_mail_on_queue_completion(self):
        
        Parameters = self.env["ir.config_parameter"].sudo()
        email_to = Parameters.get_param("shiprocket_bulk_process_recipients")
        ctx = {
            "email_to": email_to,
            "message": self.email_message_content(),
        }
        template = self.env.ref(
            "delivery_shiprocket.shiprocket_bulk_process_mail_template",
            raise_if_not_found=False,
        )
        if template:
            template.with_context(ctx).send_mail(
                self.id, force_send=True, raise_exception=False
            )
        return True
    
    def set_state(self):
        if self.state in ('waiting_awb','awb_created_partially'):
            if any(x.is_awb_generated == False for x in self.stock_picking_ids):
                self.write({'state':'awb_created_partially'})
                return 'AWB Generated Partially'
            else:
                self.write({'state':'awb_created'})
                return 'AWB Generated'
        if self.state in ('waiting_create_pickup','pickup_created_partially'):
            if any(x.is_pickup_request_done == False for x in self.stock_picking_ids):
                self.write({'state':'pickup_created_partially'})
                return 'Pickup Request Generated Partially'
            else:
                self.write({'state':'pickup_created'})
                return 'Pickup Request Generated'
        if self.state == 'waiting_to_manifest':
            self.write({"state": "ready_to_manifest"})
            return 'Ready To Generate Manifest'
        if self.state == 'ready_to_manifest':
            if any(x.is_manifest_generated == False for x in self.stock_picking_ids):
                self.write({'state':'ready_to_manifest'})
                return 'Ready To Manifest'
            else:
                self.write({'state':'manifest_generated'})
                return 'Manifest Generated'
        return True        

        
