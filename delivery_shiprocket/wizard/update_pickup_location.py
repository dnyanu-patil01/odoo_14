from odoo import api, fields, models, _
from ..models.shiprocket_request import ShipRocket

class UpdatePickupLocation(models.TransientModel):
    _name = "update.pickup.location"
    _description = "Update Pickup Location"

    pickup_location_id = fields.Many2one('shiprocket.pickup.location',required=True)

    def update_pickup_location(self):
        """ Get Order Cancellation Reason"""
        picking_ids = self.env.context.get('picking_ids') or False
        if picking_ids:
            picking_records = self.env['stock.picking'].browse(picking_ids).filtered(lambda l:l.shiprocket_order_status_id.status_code == '1')
            shiprocket = ShipRocket(self.env.company)
            shiprocket._update_pickup_location(picking_records,self.pickup_location_id)
        return True