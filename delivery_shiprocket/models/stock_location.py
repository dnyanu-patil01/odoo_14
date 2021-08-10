from odoo import fields, models


class StockLocation(models.Model):
    _inherit = "stock.location"

    shiprocket_location_id = fields.Many2one(
        "shiprocket.pickup.location", "Shiprocket Location"
    )
