from odoo import _, api, fields, models

class ProductTemplate(models.Model):
    _inherit = "product.template"

    seller_id = fields.Many2one("res.partner",'Seller',index=True, copy=False,default=lambda self: self.env.user.partner_id.id if self.env.user.partner_id.seller else False)
    state = fields.Selection([('draft','Draft'),('approve','Approved'),('reject','Rejected')],string='State',default='draft',copy=False)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('seller_id', False):
                seller_obj = self.env['res.partner'].browse(vals['seller_id'])
                if seller_obj.auto_approve_product:
                    vals.update({'state': 'approve'})
        return super(ProductTemplate, self).create(vals_list)

    def button_approve(self):
        return self.write({'state': 'approve'})

    def button_reject(self):
        return self.write({'state': 'reject'})

    def button_draft(self):
        return self.write({'state': 'draft'})
    
class ProdductProduct(models.Model):
    _inherit = "product.product"

    seller_id = fields.Many2one(related="product_tmpl_id.seller_id", readonly=False,store=True, index=True, copy=False,domain="[('seller','=',True),('active','=',True),('parent_id','=',False)]")
    state = fields.Selection(related='product_tmpl_id.state', store=True, readonly=False,copy=False)
