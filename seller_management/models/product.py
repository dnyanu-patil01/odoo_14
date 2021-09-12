from odoo import _, api, fields, models

class ProductTemplate(models.Model):
    _inherit = "product.template"

    @api.model   
    def _get_seller_domain(self):
        domain=[]
        if self.env.user.has_group('seller_management.group_sellers_management_manager'):
            domain= [('seller','=',True)]
        elif self.env.user.has_group('seller_management.group_sellers_management_user'):
            domain.append(('id','=',self.env.user.partner_id.id))
        return domain

    seller_id = fields.Many2one("res.partner",'Seller',domain=lambda self:self._get_seller_domain(), index=True, copy=False)
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
        self.write({'state': 'approve'})
        return {}

    def button_reject(self):
        self.write({'state': 'reject'})
        return {}

    def button_draft(self):
        self.write({'state': 'draft'})
        return {}
    
    def _get_filtered_seller_product_record(self):
        action = self.env["ir.actions.actions"]._for_xml_id("seller_management.seller_product_view_action")
        if self.env.user.has_group('seller_management.group_sellers_management_manager'):
            action['domain'] = [('seller_id','!=',False)]
        elif self.env.user.has_group('seller_management.group_sellers_management_user'):
            action['domain'] = [
                ('seller_id', '=', self.env.user.partner_id.id),
                ('seller_id','!=',False)
            ]
        else:
            action['domain'] = [('seller_id','!=',False)]
        action['context'] = {'default_seller_id':self.env.user.partner_id.id}
        return action
    
class ProdductProduct(models.Model):
    _inherit = "product.product"
    @api.model   
    def _get_seller_domain(self):
        domain = [('seller','=',True)]
        if self.env.user.has_group('seller_management.group_sellers_management_user'):
            domain.append(('id','=',self.env.user.partner_id.id))
        return domain

    seller_id = fields.Many2one(related="product_tmpl_id.seller_id",domain=lambda self:self._get_seller_domain(), readonly=False,store=True, index=True, copy=False)
    state = fields.Selection(related='product_tmpl_id.state', store=True, readonly=False,copy=False)
