# -*- coding: utf-8 -*-
from odoo import fields, models, api
from .shiprocket_request import ShipRocket
from odoo.exceptions import UserError
import requests
import base64


class StockPicking(models.Model):
    _inherit = "stock.picking"
    _order = "id desc"

    def _get_default_channel_id(self):
        custom_channel =  self.env['shiprocket.channel'].search(
            [('base_channel_code', '=', 'CS')],limit=1)
        if custom_channel:
            return custom_channel.id
        else:
            return False
    
    def _get_default_pickup_location_id(self):
        pickup_location =  self.env['shiprocket.pickup.location'].search(
            [('pickup_location', '=', 'Kanha')],limit=1)
        if pickup_location:
            return pickup_location.id
        else:
            return False

    # Fields To Store The Response After Create Order Request
    shiprocket_order_id = fields.Char(readonly=True, string="Order ID", copy=False)
    shiprocket_shipping_id = fields.Char(
        readonly=True, string="Shipping ID", copy=False
    )
    # Some Additional Fields To Pass In Create Order Request
    shipping_charges = fields.Float(copy=False)
    giftwrap_charges = fields.Float(copy=False)
    transaction_charges = fields.Float(copy=False)
    payment_method = fields.Selection(
        [("Prepaid", "Prepaid"), ("COD", "COD")], default="Prepaid"
    )
    order_type = fields.Selection(
        [("ESSENTIALS", "Essentials"), ("NON ESSENTIALS", "Non Essentials")],
        default="NON ESSENTIALS"
    )
    comment = fields.Char(copy=False)
    # To Store The Error Response Message
    response_comment = fields.Char(readonly=True, copy=False, tracking=True)
    # To Auto Fetch From Seller
    pickup_location = fields.Many2one("shiprocket.pickup.location", copy=False,default=_get_default_pickup_location_id)
    channel_id = fields.Many2one("shiprocket.channel", copy=False,default=_get_default_channel_id)
    # Serviceablity Related Fields
    shiprocket_serviceability_matrix = fields.One2many(
        "shiprocket.serviceability.matrix", "picking_id", copy=False
    )
    recommended_courier_company_id = fields.Many2one(
        "shiprocket.courier", "By Setting", copy=False, tracking=True
    )
    shiprocket_recommended_courier_id = fields.Many2one(
        "shiprocket.courier", "By Shiprocket", copy=False, tracking=True
    )
    courier_id = fields.Many2one("shiprocket.courier", copy=False)
    courier_rate = fields.Float("Courier Rate", copy=False)
    shiprocket_awb_code = fields.Char(copy=False)
    # Url to download manifest
    manifest_url = fields.Char(copy=False)
    label_url = fields.Char(copy=False)
    # To Show Shiprocket Order Status
    shiprocket_order_status_id = fields.Many2one(
        "shiprocket.order.status", string="Order Status", copy=False, tracking=True
    )
    pickup_request_note = fields.Text("Pickup Request Note", copy=False)
    is_awb_generated = fields.Boolean(copy=False, readonly=True)
    is_manifest_generated = fields.Boolean(copy=False, readonly=True)
    is_pickup_request_done = fields.Boolean(copy=False, readonly=True)
    rto_courier_rate = fields.Float(copy=False, readonly=True)
    is_order_rto = fields.Boolean(copy=False, readonly=True)
    bulk_order_id = fields.Many2one("shiprocket.bulk.process",copy=False, readonly=True)
    cancel_reason = fields.Text("Reason",copy=False, readonly=True)

    def _send_confirmation_email(self):
        super(StockPicking, self)._send_confirmation_email()
        for pick in self:
            if pick.carrier_id and pick.is_return_picking:
                if (
                    pick.picking_type_code == "incoming"
                    and pick.carrier_id.delivery_type == "shiprocket"
                ):
                    pick.carrier_id.shiprocket_return_order_creation(pick)

    def shiprocket_check_serviceability(self):
        """check the available courier services and generate courier serviceability matrix"""
        vals = {
            "pickup_postcode": int(self.pickup_location.pin_code),
            "delivery_postcode": int(self.partner_id.zip),
            "order_id": int(self.shiprocket_order_id),
        }
        shiprocket = ShipRocket(self.env.company)
        # API Call To Get Cost Matrix
        response_data = shiprocket._get_courier_serviceability(vals, self)
        if response_data:
            self.shiprocket_serviceability_matrix.unlink()
            self.write(response_data)
        return True

    def shiprocket_create_awb(self):
        """To generate awb for the current order"""
        courier = False
        if self.courier_id:
            courier = self.courier_id
        elif self.recommended_courier_company_id:
            courier = self.recommended_courier_company_id
        elif self.shiprocket_recommended_courier_id:
            courier = self.shiprocket_recommended_courier_id
        if not courier:
            raise UserError("Please Set Courier To Create AWB")
        courier_id = self.shiprocket_serviceability_matrix.filtered(
            lambda line: line.courier_company_id.id == courier.id
        )
        vals = {
            "courier_id": int(courier.code),
            "shipment_id": int(self.shiprocket_shipping_id),
        }
        shiprocket = ShipRocket(self.env.company)
        # API Call To Create AWB
        response_data = shiprocket._create_awb(vals, self)
        if response_data:
            response_data.update(
                {
                    "courier_id": courier_id.courier_company_id.id,
                    "courier_rate": courier_id.rate,
                }
            )
            self.write(response_data)
        else:
            self.write(
                {
                    "courier_id": courier_id.courier_company_id.id,
                    "courier_rate": courier_id.rate,
                }
            )
        return True

    def shiprocket_generate_pickup_request(self):
        """Request For Shipment Pickup Creation"""
        shiprocket = ShipRocket(self.env.company)
        # API Call To Create Pickup Request
        shipping_id = int(self.shiprocket_shipping_id)
        response_data = shiprocket._generate_pickup_request([shipping_id])
        self.get_shiprocket_status()
        if 'pickup_request_note' in response_data:
            response_data.update({'is_pickup_request_done':True})
        self.write(response_data)
        return response_data

    def shiprocket_generate_manifest_request(self):
        """Generate Manifest"""
        shiprocket = ShipRocket(self.env.company)
        # API Call To Create Pickup
        shipping_id = int(self.shiprocket_shipping_id)
        response_data = shiprocket._generate_manifest_request([shipping_id])
        self.get_shiprocket_status()
        if response_data:
            self.write(response_data)
        return response_data

    def shiprocket_reassign_courier(self):
        self.shiprocket_check_serviceability()
        courier_id = self.shiprocket_serviceability_matrix.filtered(
            lambda line: line.courier_company_id.id
            == self.recommended_courier_company_id.id
        )
        set_courier_id = self.env["set.courier"].create(
            {
                "selected_courier_id": courier_id.id,
                "picking_id": self.id,
            }
        )
        ctx = {"reassign": True}
        return {
            "name": ("Re-assign Courier And Generate AWB"),
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "res_model": "set.courier",
            "res_id": set_courier_id.id,
            "target": "new",
            "context": ctx,
        }

    def shiprocket_generate_label_request(self):
        """To Generate Label URL"""
        shiprocket = ShipRocket(self.env.company)
        # API Call To Generate Label
        shipping_id = int(self.shiprocket_shipping_id)
        response_data = shiprocket._generate_label_request([shipping_id])
        if response_data:
            self.write(response_data)
        if 'label_url' in response_data:
            self.generate_attachment_pdf(response_data['label_url'],'Label')
        return True

    def shiprocket_print_manifest_request(self):
        """print manifest request"""
        shiprocket = ShipRocket(self.env.company)
        # API Call To Generate Label
        order_id = int(self.shiprocket_order_id)
        response_data = shiprocket._print_manifest_request([order_id])
        self.get_shiprocket_status()
        if response_data:
            self.write(response_data)
        if 'manifest_url' in response_data:
            self.generate_attachment_pdf(response_data['manifest_url'],'Manifest')
        return

    def shiprocket_cancel_shipment(self):
        """To Cancel Order In Shiprocket"""
        for transfer in self:
            if not transfer.shiprocket_order_id:
                transfer.write({"response_comment":"Shiprocket Order ID Required To Cancel Order"})
                return 
            shiprocket = ShipRocket(self.env.company)
            # API Call To Generate Label
            order_id = int(transfer.shiprocket_order_id)
            response_data = shiprocket._cancel_order_request([order_id])
            #Creating Return DO for order status before manifest
            if response_data in (200,204) and transfer.shiprocket_order_status_id.status_code in ('1','2','3','4','12','13','14'):
                transfer.create_return_picking()
                response_data = "Order Cancellation In Shiprocket And Return Order Also Created."
            transfer.get_shiprocket_status()
            transfer.write({'response_comment':str(response_data)})
        return True

    def get_shiprocket_status(self):
        '''To Get Shiprocket Order Status'''
        if not self.shiprocket_order_id:
            raise UserError("Shiprocket Order ID Is Needed To Get Status")
        shiprocket = ShipRocket(self.env.company)
        response_data = shiprocket._get_order_status(self)
        if "response_comment" in response_data:
            self.write(response_data)
            return False
        if response_data:
            vals = {
                "shiprocket_order_status_id": self.env["shiprocket.order.status"]
                .search(
                    [("status_code", "=", response_data["order_status_code"])],
                    limit=1,
                )
                .id,
            }
            # To check for RTO Status and To Update RTO Rate
            if response_data["order_status_code"] in ["15", "17"]:
                vals.update(
                    {"rto_courier_rate": self.courier_rate, "is_order_rto": True}
                )
            #Auto Generation Of Return Of The Delivery Order
            if response_data['order_status_code'] == '16':
                self.create_return_picking()
            if response_data['order_status_code'] == "4":
                vals.update(
                    {"is_pickup_request_done": True}
                )
            self.write(vals)
        return True

    def create_return_picking(self):
        '''
        Create Return Picking For RTO Delivered Order
        '''
        return_pick_wiz = self.env['stock.return.picking'].with_context(
        active_model='stock.picking', active_id=self.id,shiprocket=False).create({})
        return_pick_wiz._onchange_picking_id()
        return_picking_id, dummy = return_pick_wiz.with_context(active_id=self.id)._create_returns()
        return_picking = self.env['stock.picking'].browse(return_picking_id)
        return_picking.action_confirm()
        for rec in return_picking.move_lines:
            rec.quantity_done = rec.product_uom_qty
        return_picking.button_validate()

    def get_courier_id(self, code, name):
        """To Get Courier ID from courier code"""
        courier = self.env["shiprocket.courier"]
        courier_id = courier.search([("code", "=", code)], limit=1)
        if not courier_id:
            courier_id = courier.create(
                {
                    "name": name,
                    "code": code,
                }
            )
        return courier_id.id

    def set_courier_id(self):
        """To Set Courier Based On Courier Serviceablilty Matrix"""
        courier_id = self.shiprocket_serviceability_matrix.filtered(
            lambda line: line.courier_company_id.id
            == self.recommended_courier_company_id.id
        )
        set_courier_id = self.env["set.courier"].create(
            {
                "selected_courier_id": courier_id.id,
                "picking_id": self.id,
            }
        )
        return {
            "name": ("Set Courier To Generate AWB"),
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "res_model": "set.courier",
            "res_id": set_courier_id.id,
            "target": "new",
        }

    @api.model
    def action_update_order_status(self):
        ''''Cron To Auto Update Order Status'''
        pickings = self.search(
            [
                ("state", "=", "done"),
                ("carrier_id.delivery_type", "=", "shiprocket"),
                ("shiprocket_order_id", "!=", False),
                ("shiprocket_order_status_id.is_call_status_cron","=",True)
            ]
        )
        for picking in pickings:
            picking.get_shiprocket_status()
            if not picking.shiprocket_order_status_id.is_call_status_cron:
                picking.shiprocket_serviceability_matrix.unlink()
        return True
    
    def generate_attachment_pdf(self,urls,type):
        response = requests.get(urls,stream=True)
        Attachment = self.env['ir.attachment']
        attachment_name = "%s-%s"%(type,self.name)
        prev_attachment = Attachment.search(
            [
                ('res_model','=','stock.picking'),
                ('res_id','=',self.id),
                ('name','=',attachment_name)
            ]
        )
        if prev_attachment:
            prev_attachment.unlink()
        attachment_id = Attachment.create({
        'name': attachment_name,
        'type': 'binary',
        'datas': base64.b64encode(response.content),
        'res_model': 'stock.picking',
        'res_id': self.id,
        })
        return True
    
    def bulk_awb_creation_request(self,bulk_process):
        """Call To Bulk AWB Creation Process"""
        shiprocket = ShipRocket(self.env.company)
        shiprocket.bulk_awb_creation_request(self,bulk_process)
        return True

    def action_get_cancel_reason(self):
        picking_ids = self.env.context.get('active_ids') or False
        if not picking_ids:
            ctx={'picking_ids':self.ids}
        else:
            ctx = {"picking_ids": picking_ids}
        return {
            "name": ("Cancel Order In Shiprocket"),
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "res_model": "order.cancel.reason",
            "target": "new",
            "context":ctx,
        }

    def update_shiprocket_details_in_transfer(self):
        picking_ids = self.env.context.get('active_ids') or False
        if picking_ids:
            for picking in self.browse(picking_ids):
                picking.with_delay().get_order_details()
            message_id = self.env['message.box'].create({'message':"Shiprocket Order Details Will Be Updated Few Minutes In Odoo."})
            return {
                "name": "Information",
                "type": "ir.actions.act_window",
                "view_mode": "form",
                "res_model": "message.box",
                "res_id": message_id.id,
                "target": "new",
            }
        
    
    def get_order_details(self):
        shiprocket = ShipRocket(self.env.company)
        shiprocket._get_order_details(self)
        return True
    
    def action_update_pickup_location(self):
        '''popup wizard to choose new pickup location and update the same in shiprocket'''
        picking_ids = self.env.context.get('active_ids') or False
        if not picking_ids:
            ctx={'picking_ids':self.ids}
        else:
            ctx = {"picking_ids": picking_ids}
        return {
            "name": ("Update Pickup Location In Shiprocket"),
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "res_model": "update.pickup.location",
            "target": "new",
            "context":ctx,
        }