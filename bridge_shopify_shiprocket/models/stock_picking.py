from odoo import fields, models

class ShiprocketPickupLocation(models.Model):
    _inherit = "shiprocket.pickup.location"

    seller_id = fields.Many2one("res.partner",domain=[('seller','=',True),('parent_id','=',False)])
