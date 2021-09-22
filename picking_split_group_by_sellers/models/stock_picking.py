from odoo import _, api, fields, models
from datetime import date, datetime

class StockPicking(models.Model):
    _inherit = "stock.picking"

    def _action_done(self):
        res = super()._action_done()
        invoice_ids = self.get_related_invoices()
        if invoice_ids:
            inv_obj = self.env['account.move'].browse(list(set(invoice_ids)))
            inv_obj.write({'invoice_date':datetime.now().date()})
        return res

    def generate_invoice_report(self):
        invoice_ids = self.get_related_invoices()
        if invoice_ids:
            inv_obj = self.env['account.move'].browse(list(set(invoice_ids)))
            return self.env.ref('account.account_invoices_without_payment').report_action(inv_obj)
        else:
            message_id = self.env['message.box'].create({'message':"No Invoice Details To Print Report"})
            return {
                "name": "Information",
                "type": "ir.actions.act_window",
                "view_mode": "form",
                "res_model": "message.box",
                "res_id": message_id.id,
                "target": "new",
            }

    def  get_related_invoices(self):
        invoice_ids = []
        if self.env.user.has_group('seller_management.group_sellers_management_manager'):
            if self.sale_order_ids:
                for sale in self.sale_order_ids:
                    if sale.invoice_ids:
                        invoice_ids.extend(sale.invoice_ids.ids)
            elif self.sale_id.invoice_ids:
                invoice_ids.extend(self.sale_id.invoice_ids.ids)
        elif self.env.user.has_group('seller_management.group_sellers_management_user'):
            sale_orders = self.sale_order_ids.filtered(lambda s:s.seller_id.id == self.env.user.partner_id.id)
            if sale_orders:    
                for sale in sale_orders:
                    if sale.invoice_ids:
                        invoice_ids.extend(sale.invoice_ids.ids)
            elif self.sale_id.invoice_ids:
                invoice_ids.extend(self.sale_id.invoice_ids.filtered(lambda s:s.seller_id.id == self.env.user.partner_id.id).ids)
        return invoice_ids