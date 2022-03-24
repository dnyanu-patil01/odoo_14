from odoo import _, api, fields, models
from datetime import date, datetime

class StockPicking(models.Model):
    _inherit = "stock.picking"    

    def _action_done(self):
        res = super(StockPicking, self)._action_done()
        for pick in self:
            if pick.sale_id and pick.sale_id.name == pick.origin:
                wiz_id = self.env['sale.advance.payment.inv'].create({'advance_payment_method':'delivered'})
                wiz_id.with_context(active_ids = pick.sale_id.id).create_invoices()
                pick.sale_id.invoice_ids.filtered(lambda line: line.state == 'draft').action_post()
        return res