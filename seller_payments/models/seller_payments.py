from odoo import _, api, fields, models
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

class SellerPayments(models.Model):
    _name = "seller.payments"
    _description = 'Seller Payments'
    _order = 'id DESC'

    name = fields.Char(size=120)
    seller_id = fields.Many2one('res.partner',string="Seller", required=True)
    from_date = fields.Datetime('From Date',required=True)
    to_date = fields.Datetime('To Date',required=True)
    total_sales_amount = fields.Float('Total Sales Amount',required=True)
    total_untaxed_sales_amount = fields.Float('Total Untaxed Amount',required=True)
    commission = fields.Float('Commission')
    commissions_gst = fields.Float('Commission GST')
    tds = fields.Float('TDS')
    tcs = fields.Float('TCS')
    net_payable_amount = fields.Float('Net Payable AMount')
    utr_number = fields.Char('UTR Number')
    payment_date = fields.Date('Payment Date')
    sales_order_ids = fields.One2many('sale.order', 'seller_payments_id', string="Sales Order")

    def seller_payments_creation(self):
        sellers = self.env['res.partner'].search([('seller', '=', True)])
        today = datetime.now().date() - relativedelta(months=+1)
        first_day = today.replace(day=1)
        prev_month_end_date = first_day - timedelta(days=1)
        prev_month_st_date = prev_month_end_date.replace(day=1)
        for rec in sellers:
            sale_orders = self.env['sale.order'].search([('seller_id', '=', rec.id),('date_order','>=',prev_month_st_date),('date_order','<=',prev_month_end_date)])
            print(sale_orders,prev_month_st_date,prev_month_end_date)
            sales_total_amount = sum(sale_orders.mapped("amount_total"))
            untaxed_total_amount = sum(sale_orders.mapped("amount_untaxed"))
            if sales_total_amount > 0.0:
                payment = self.create({'from_date': prev_month_st_date,
                                       'to_date': prev_month_end_date,
                                       'seller_id': rec.id,
                                       'total_sales_amount': sales_total_amount,
                                       'total_untaxed_sales_amount': untaxed_total_amount,
                                       })

                sale_orders.write({'seller_payments_id': payment.id})

    @api.model
    def create(self, vals):
        """
        This method used to create a sequence for monthly seller payments data.
        """
        seq = self.env["ir.sequence"].next_by_code("seller.payments") or "/"
        vals.update({"name": seq or ""})
        return super(SellerPayments, self).create(vals)
