from odoo import _, api, fields, models

class StockPicking(models.Model):
    _inherit = "stock.picking"

    seller_id = fields.Many2one("res.partner",string="Seller")
