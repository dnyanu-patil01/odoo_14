from odoo import _, api, fields, models

class StockPicking(models.Model):
    _inherit = "stock.picking"

    seller_id = fields.Many2one("res.partner",string="Seller",copy=False,domain="[('seller','=',True),('active','=',True),('parent_id','=',False)]")
    mobile = fields.Char(related="partner_id.mobile",readonly=True) 
    phone = fields.Char(related="partner_id.phone",readonly=True)
    active = fields.Boolean('Active',default=True, help="If unchecked, it will allow you to hide the delivery order without removing it.")


    @api.model
    def create(self, vals):
        #To Pass Seller ID While Creating Backorders
        if 'backorder_id' in vals and vals['backorder_id'] != False:
            orgin = self.browse(int(vals['backorder_id']))
            if orgin.seller_id:
                vals.update({'seller_id':orgin.seller_id.id})
        return super(StockPicking ,self).create(vals)

    def action_cancel(self):
        """To Trigger Mail To Fulfillment Team On The Cancellation Of SO"""
        template = self.env.ref('seller_management.mail_template_seller_do_cancellation')
        if template:
            mail_id = template.send_mail(self.id)
            Mail = self.env['mail.mail'].sudo().browse(mail_id)
        Mail.send()
        return super().action_cancel()