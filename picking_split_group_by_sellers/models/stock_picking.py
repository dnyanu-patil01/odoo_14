from odoo import _, api, fields, models
from datetime import date, datetime

class StockPicking(models.Model):
    _inherit = "stock.picking"

    invoice_count = fields.Integer(string='Invoices', compute='_compute_invoice_count')
    
    def _compute_invoice_count(self):
        """This compute function used to count the number of invoice for the picking"""
        for picking_id in self:
            move_ids = self.env['account.move'].search([('picking_id', '=', picking_id.id)])
            if move_ids:
                self.invoice_count = len(move_ids)
            else:
                self.invoice_count = 0
           
    
    def action_view_seller_invoice(self):
        """Action Method To View Invoice From Delivery"""
        invoices = self.env['account.move'].search([('picking_id', '=', self.id)])
        action = self.env["ir.actions.actions"]._for_xml_id("seller_management.action_sellers_invoices")
        if len(invoices) > 1:
            action['domain'] = [('id', 'in', invoices.ids)]
        elif len(invoices) == 1:
            form_view = [(self.env.ref('seller_management.view_seller_invoice_form').id, 'form')]
            if 'views' in action:
                action['views'] = form_view + [(state,view) for state,view in action['views'] if view != 'form']
            else:
                action['views'] = form_view
            action['res_id'] = invoices.id
        else:
            action = {'type': 'ir.actions.act_window_close'}

        context = {
            'default_move_type': 'out_invoice',
        }
        if len(self) == 1:
            context.update({
                'default_seller_id': self.seller_id.id,
                'create':False,
            })
        action['context'] = context
        return action
    
    
    def generate_invoice(self):
        '''To Generate Invoice'''
        order_ids = self.get_related_sale_orders()
        if order_ids:
            for order in self.env['sale.order'].browse(order_ids):
                invoice_ids = order._create_invoices()
                if invoice_ids:
                    for invoice in invoice_ids:
                        invoice.write({'picking_id':self.id})
                        invoice.action_post()
                        self.create_invoice_payment(invoice)
        else:
            message_id = self.env['message.box'].create({'message':"No Sale Order Found To Generate Invoice"})
            return {
                "name": "Information",
                "type": "ir.actions.act_window",
                "view_mode": "form",
                "res_model": "message.box",
                "res_id": message_id.id,
                "target": "new",
            }

    @api.model
    def _default_payment_journal(self):
        '''To Get Payment Journal To Create Payment Record'''
        account_journal_obj = self.env['account.journal']
        company_id = self._context.get('company_id', self.env.company.id)
        domain = [('type', '=', "bank"),
                  ('company_id', '=', company_id)]
        return account_journal_obj.search(domain, limit=1)

    def create_invoice_payment(self, invoices):
        '''To Create Payment Record For The Invoices'''
        account_payment_obj = self.env['account.payment']
        for invoice in invoices:
            if invoice.amount_residual:
                vals = self.prepare_payment_dict(invoice)
                if invoice.amount_residual:
                    payment_id = account_payment_obj.create(vals)
                    #To Make Sure Seller ID Is Not Getting Passed
                    payment_move = self.env['account.move'].search([('payment_id','=',payment_id.id)],limit=1)
                    if payment_move:
                        payment_move.write({'seller_id':False})
                    payment_id.action_post()
                    self.reconcile_payment(payment_id, invoice)
        return True
    
    def reconcile_payment(self, payment_id, invoice):
        """To reconcile payment and invoice"""
        move_line_obj = self.env['account.move.line']
        domain = [('account_internal_type', 'in', ('receivable', 'payable')),
                  ('reconciled', '=', False)]
        line_ids = move_line_obj.search([('move_id', '=', invoice.id)])
        to_reconcile = [line_ids.filtered( \
                lambda line: line.account_internal_type == 'receivable')]

        for payment, lines in zip([payment_id], to_reconcile):
            payment_lines = payment.line_ids.filtered_domain(domain)
            for account in payment_lines.account_id:
                (payment_lines + lines).filtered_domain([('account_id', '=', account.id),
                                                         ('reconciled', '=', False)]).reconcile()

    def _default_payment_method(self):
        '''To Get Payment Method To Pass In Payment Record'''
        payment_method_obj = self.env['account.payment.method']
        domain = [('payment_type', '=', "inbound"),
                  ('code', '=', 'manual')]
        return payment_method_obj.search(domain, limit=1)

    def prepare_payment_dict(self,invoice):
        '''To Prepare Payment Record Dictionary'''
        return {
            'journal_id': self._default_payment_journal().id,
            'ref': invoice.payment_reference,
            'currency_id': invoice.currency_id.id,
            'payment_type': 'inbound',
            'date': invoice.date,
            'partner_id': invoice.partner_id.id,
            'amount': invoice.amount_residual,
            'payment_method_id': self._default_payment_method().id,
            'partner_type': 'customer'}

    def get_related_sale_orders(self):
        '''To Get Related Sale Orders For The Delivery
        Stock Move Line->Move ID-->Sale Line ID-->Order ID'''
        order_ids = []
        if self.env.user.has_group('seller_management.group_sellers_management_manager'):
            order_ids = self.move_line_ids_without_package.mapped('move_id').mapped('sale_line_id').mapped('order_id').ids
        elif self.env.user.has_group('seller_management.group_sellers_management_user'):
            order_ids = self.move_line_ids_without_package.mapped('move_id').mapped('sale_line_id').mapped('order_id').filtered(lambda s:s.seller_id.id == self.env.user.partner_id.id).ids
        else:
            order_ids.append(self.sale_id.id)
        return list(set(order_ids))