from odoo import _, api, fields, models

class ProductPackaging(models.Model):
    _inherit = 'product.packaging'

    seller_id = fields.Many2one("res.partner",'Seller',index=True, copy=False,default=lambda self: self.env.user.partner_id.id if self.env.user.partner_id.seller else False,domain="[('seller','=',True),('active','=',True),('parent_id','=',False)]")