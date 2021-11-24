from odoo import _, api, fields, models
from odoo.exceptions import UserError
from ..models.shiprocket_request import ShipRocket


class WizBarcodesRead(models.TransientModel):
    _name = "wiz.barcodes.read"
    _inherit = ["barcodes.barcode_events_mixin"]
    _description = "Wizard to read barcode"
    # To prevent remove the record wizard until 3 days old
    _transient_max_hours = 72

    _barcode_scanned = fields.Char("Barcode Scanned")
    stock_picking_ids = fields.One2many(
        "wiz.stock.picking.lines", "wizard_id", string="Pickings", compute=""
    )
    bulk_process_id = fields.Many2one("shiprocket.bulk.process", readonly=True)

    def on_barcode_scanned(self, barcode):
        if barcode:
            line = self.env["wiz.stock.picking.lines"].search(
                [
                    ("bulk_process_id", "=", self.bulk_process_id.id),
                    ("shiprocket_awb_code", "=", barcode),
                    ("picking_id.is_manifest_generated", "=", False),
                ]
            )
            message = None
            if line:
                self.stock_picking_ids = [[4, line.id]]
            else:
                message = "Invalid AWB Code"
        if message:
            formatted_msg = "<b>%s</b>"%(message)
            message_id = self.env['message.box'].create({'message':formatted_msg})
            return {
                "name": "Error",
                "type": "ir.actions.act_window",
                "view_mode": "form",
                "res_model": "message.box",
                "res_id": message_id.id,
                "target": "new",
            }

    def generate_manifest_bulk(self):
        self.with_delay().generate_bulk_manifest()
    
    def generate_bulk_manifest(self):
        shiprocket = ShipRocket(self.env.company)
        picking_ids = self.stock_picking_ids.mapped('picking_id').filtered(lambda m:m.is_manifest_generated == False).ids
        response_details = ''
        for ids in self.bulk_process_id.split_request_ids(picking_ids):
            splited_picking_ids = self.env['stock.picking'].browse(ids)
            shipment_ids = list(
            map(int, splited_picking_ids.mapped("shiprocket_shipping_id")))
            response_data = shiprocket._generate_manifest_request(shipment_ids)
            if 'manifest_url' in response_data:
                splited_picking_ids.write({'is_manifest_generated':True})
            else:
                for picking in splited_picking_ids:
                    if not picking.is_manifest_generated:
                        res = picking.shiprocket_generate_manifest_request()
                        if 'manifest_url' not in res:
                            response_details+=str(res)
        self.bulk_process_id.write({"response_comment": str(response_details)})
        self.bulk_process_id.with_delay().send_mail_on_queue_completion()
        self.bulk_process_id.with_delay(priority=30).create_log_lines()
        return True


class PortalWizard(models.TransientModel):
    """
    A model to configure users in the portal wizard.
    """

    _name = "wiz.stock.picking.lines"
    _description = "Portal User Config"
    # To prevent remove the record wizard until 3 days old
    _transient_max_hours = 72

    wizard_id = fields.Many2one("wiz.barcodes.read", string="Wizard")
    picking_id = fields.Many2one(
        "stock.picking", string="Delivery Order", ondelete="cascade"
    )
    bulk_process_id = fields.Many2one("shiprocket.bulk.process", readonly=True)
    shiprocket_order_id = fields.Char(
        related="picking_id.shiprocket_order_id", string="Shiprocket Order ID"
    )
    shiprocket_awb_code = fields.Char(string="AWB Code")
    courier_id = fields.Many2one("shiprocket.courier", related="picking_id.courier_id")
    shiprocket_order_status_id = fields.Many2one(
        "shiprocket.order.status",
        related="picking_id.shiprocket_order_status_id",
    )