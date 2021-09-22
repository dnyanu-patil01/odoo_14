from odoo import _, api, fields, models

class AccountMove(models.Model):
    _inherit = "account.move"

    seller_id = fields.Many2one("res.partner",'Seller',index=True, copy=False)

    def get_sale_order_data(self):
        for rec in self:
            orders = self.env['sale.order'].search([(
                'name', '=', rec.invoice_origin)], limit=1)
        return orders

    def print_invoice(self):
        return self.env.ref('account.account_invoices').report_action(self)