from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        if self.seller_id and self.seller_id.email:
            self.send_mail_on_order_confirm()
        return res

    
    def send_mail_on_order_confirm(self):
        '''Send Mail To Seller On Order Confirmation'''
        template = self.env.ref(
            "seller_send_order_mail.mail_template_seller_sale_confirmation",
            raise_if_not_found=False,
        )
        if template:
            template.send_mail(
                self.id, force_send=True, raise_exception=False
            )
        return True
    