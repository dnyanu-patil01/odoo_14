from odoo import  fields, models, _
from odoo.exceptions import UserError


class UpdateDeliveryCarrier(models.TransientModel):
    _name = "update.delivery.carrier"
    _description = "Update Delivery Carrier"

    carrier_id = fields.Many2one('delivery.carrier',required=True)
    delivery_type = fields.Selection(related='carrier_id.delivery_type',store=True)
    tracking_url = fields.Char('Tracking URL')
    tracking_ref = fields.Char('Tracking Reference')

    def update_delivery_carrier(self):
        picking_ids = self.env.context.get('picking_ids') or False
        if picking_ids:
            picking_records = self.env['stock.picking'].browse(picking_ids)
            valid_records = picking_records.filtered(lambda l:l.shiprocket_order_status_id.status_code in (False,'5') and l.state == 'done')
            vals = {
                'carrier_id':self.carrier_id.id,
            }
            if self.delivery_type == 'self':
                vals.update({
                    'self_tracking_url':self.tracking_url,
                    'carrier_tracking_ref':self.tracking_ref,
                })
            if self.delivery_type != 'self':
                vals.update({
                    'self_tracking_url':False,
                    'carrier_tracking_ref':False,
                })
            if valid_records:
                picking_records.write(vals)
            else:
                raise UserError("You cannot change the delivery carrier for this delivery order")
        return True