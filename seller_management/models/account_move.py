from odoo import _, api, fields, models

class AccountMove(models.Model):
    _inherit = "account.move"

    seller_id = fields.Many2one("res.partner",'Seller',index=True, copy=False,domain="[('seller','=',True),('active','=',True),('parent_id','=',False)]")

    def get_sale_order_data(self):
        for rec in self:
            orders = self.env['sale.order'].search([(
                'name', '=', rec.invoice_origin)], limit=1)
        return orders

    def print_invoice(self):
        return self.env.ref('account.account_invoices').report_action(self)
    
    #override _get_last_sequence_domain to fix sequence without seller
    def _get_last_sequence_domain(self, relaxed=False):
        where_string, param = super(AccountMove, self)._get_last_sequence_domain(relaxed)
        if self.seller_id and self.move_type in ('out_invoice','out_refund'):
            where_string += "AND seller_id = %(seller_id)s"
            param.update({'seller_id':self.seller_id.id})
        #To Make Sure Seller ID Is Not Getting Passed
        elif self.move_type == 'entry':
            self.write({'seller_id':False})
        else:
            where_string += "AND seller_id is null"
        return where_string, param