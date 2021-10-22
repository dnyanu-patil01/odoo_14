# # -*- coding: utf-8 -*-

from odoo import models, fields, api, _

# class sale_order(models.Model):

#     _inherit = "sale.order"
#     _description = 'Sale Order'

#     customer_name = fields.Char("Customer Name")
#     customer_contact_no = fields.Char("Contact Number")
#     customer_email = fields.Char("Contact Email")
#     payment_mode_id = fields.Many2one("customer.payment.mode","Mode Of Payment")
#     payment_date = fields.Date('Payment Date')
#     payment_reference = fields.Char('Payment Reference')
#     payment_amount = fields.Float('Paid Amount')
#     state = fields.Selection([
#         ('draft', 'Quotation'),
#         ('sent', 'Quotation Sent'),
#         ('payment_confirmation', 'Waiting For Payment Confirmation'),
#         ('sale', 'Sales Order'),
#         ('done', 'Locked'),
#         ('cancel', 'Cancelled'),
#         ], string='Status', readonly=True, copy=False, index=True, tracking=3, default='draft')
#     is_website_order = fields.Boolean(default=False,string="Is Website Order")
    
class CustomerPaymentMode(models.Model):
    _name = "customer.payment.mode"
    _description = "CustomerPaymentMode"

    name = fields.Char("Name")
    active = fields.Boolean("Active",default=True)