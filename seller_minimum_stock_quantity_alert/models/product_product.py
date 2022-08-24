# -*- coding: utf-8 -*-

from odoo import models, _
from datetime import date


class ProductProduct(models.Model):
    _inherit = "product.product"

    def cron_send_minimum_stock_alert(self):
        sellers = self.env['res.partner'].search([('seller','=',True)])
        for seller in sellers:
            products = self.env['product.product'].search([('seller_id','=',seller.id)])
            low_stock_products = products.filtered(lambda p: p.type != 'service' and p.virtual_available <= 5)
            dynamic_row = ""
            mail_dict = {}
            if low_stock_products:
                for product in low_stock_products:
                    dynamic_row += "<tr><td>{0}</td><td>{1}</td><td>{2}</td></tr>".format(product.default_code,
                                                                                        str(product.display_name),
                                                                                    str(product.virtual_available))
                mail_dict = {
                            "subject": seller.display_name +' Minimum Stock Alert On '+ date.today().strftime("%d-%b-%Y"),
                            "email_from": self.env.user.company_id.email,
                            "email_to": seller.email,
                            "body_html": "<p>Hello! " + seller.name + "</p><br/> Available quantity is less than 5.Please kindly update your stock quantity<p>\
                    <br/><br/><table class='table table-sm o_main_table'><thead><tr>\
                    <td>Internal Reference</td><td>Product Name</td><td>Available Quantity</td></tr>\
                    </thead> "+dynamic_row + "<tbody></tbody></table>"
                    "<br></br><p> Thanks You, <br/> HFN Life</p>"
                            }
            if mail_dict:
                mail_create = self.env['mail.mail'].create(mail_dict)
                mail_create.send()
