from odoo import  models,api,fields
from datetime import date,datetime
from datetime import timedelta
class ResPartner(models.Model):
    _inherit = "res.partner"
    
    is_send_order_mail = fields.Boolean('Send Daily Orders Mail')

class SaleOrder(models.Model):
    _inherit = "sale.order"
    
    @api.model
    def cron_send_seller_order_report(self):
        today = date.today()
        yesterday = today - timedelta(days = 1)
        start_date = yesterday.strftime('%Y-%m-%d 00:00:00')
        end_date = yesterday.strftime('%Y-%m-%d 23:59:59')
        print(start_date)
        print(end_date)
        ctx = dict(self.env.context)
        ctx.update({
            'subject': 'Sales Order On '+yesterday.strftime('%d-%b-%Y')+' - Regards',
            'email_from': self.env.company.email or self.env.user.email_formatted,
            'order_date':yesterday.strftime('%d-%b-%Y'),
        })
        for seller in self.env['res.partner'].search([('is_send_order_mail','=',True),('seller','=',True),('active','=',True),('parent_id','=',False)]):
            orders = self.env['sale.order'].search([('date_order','>=',start_date),('date_order','<=',end_date),('seller_id','=',seller.id)])
            if orders:
                ctx.update({
                    'email_to': seller.email,
                    'order_count':len(orders.ids),
                    })
                template = self.env.ref('seller_send_order_mail.mail_template_seller_sale_order')
                if template:
                    mail_id = template.with_context(ctx).send_mail(self.id)
                    Mail = self.env['mail.mail'].browse(mail_id)
                Mail.send()
        return True