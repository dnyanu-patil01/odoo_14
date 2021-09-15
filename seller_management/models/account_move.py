from odoo import _, api, fields, models

class AccountMove(models.Model):
    _inherit = "account.move"

    seller_id = fields.Many2one("res.partner",'Seller',index=True, copy=False)
