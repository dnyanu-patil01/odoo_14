from odoo import _, api, fields, models

class StockWarehouse(models.Model):
    _inherit = "stock.warehouse"

    seller_id = fields.Many2one("res.partner",index=True, copy=False,domain="[('seller','=',True),('active','=',True),('parent_id','=',False)]")
