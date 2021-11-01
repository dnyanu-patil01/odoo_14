from odoo import fields, models

class ShiprocketPickupLocation(models.Model):
    _inherit = "shiprocket.pickup.location"

    seller_id = fields.Many2one("res.partner",domain=[('seller','=',True),('parent_id','=',False)])

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    self_tracking_url = fields.Char("Tracking Link",copy=False)

class ProviderShiprocket(models.Model):
    _inherit = "delivery.carrier"

    delivery_type = fields.Selection(selection_add=[('self', 'Self Fulfilment')])

    def self_get_tracking_link(self, picking):
        return picking.self_tracking_url