from odoo import api, models, fields,_


class ResPartner(models.Model):
    _inherit = "res.partner"

    is_auto_generate_product_internal_reference = fields.Boolean("Auto Generate Product Sequence")
    next_sequence = fields.Integer('Next Sequence',readonly=True,copy=False,default=1)


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    default_code = fields.Char(
        'Internal Reference', compute='_compute_default_code',inverse='_set_default_code', store=True,copy=False) 
    article_code = fields.Char(readonly=True)
    product_sequence = fields.Integer('Product Sequence',readonly=True)
    is_auto_generate_product_internal_reference = fields.Boolean(related="seller_id.is_auto_generate_product_internal_reference",store=True)

    _sql_constraints = [
        ('default_code_uniq', 'unique(default_code)', 'Internal Reference must be Unique !'),
    ]


    @api.depends('product_variant_ids', 'product_variant_ids.default_code','seller_id')
    def _compute_default_code(self):
        res = super(ProductTemplate,self)._compute_default_code()
        if self.seller_id and self.seller_id.is_auto_generate_product_internal_reference: 
            unique_variants = self.filtered(lambda template: len(template.product_variant_ids) == 1)
            for template in unique_variants:
                template.default_code = self.article_code
            for template in (self - unique_variants):
                template.default_code = self.article_code
        return res
    
    def get_product_sequence(self,seller_id):
        last_product_sequence = self.search([('seller_id','=',seller_id)]).mapped('product_sequence')
        last_product_sequence += self.search([('seller_id','=',seller_id),('active','=',False)]).mapped('product_sequence')
        return max(last_product_sequence) + 1  if last_product_sequence else 1

    def _update_default_code(self, vals,article_code):
        if any(key in ('seller_id','article_code','attribute_line_ids') for key in vals):
            self.mapped('product_variant_ids').write({
                'default_code': article_code})

    @api.model
    def create(self, vals):
        if 'seller_id' in vals:
            seller = self.env['res.partner'].browse(vals['seller_id'])
            if seller.is_auto_generate_product_internal_reference: 
                sequence = self.get_product_sequence(vals['seller_id'])
                vals['product_sequence'] = sequence
                vals['article_code'] = str(seller.seller_code)+str(sequence).zfill(5)            
        return super(ProductTemplate, self).create(vals)

    def write(self, vals):
        if 'seller_id' in vals:
            seller = self.env['res.partner'].browse(vals['seller_id'])
            if self.seller_id.id != vals['seller_id'] and seller.is_auto_generate_product_internal_reference:
                sequence = self.get_product_sequence(vals['seller_id'])
                vals['product_sequence'] = sequence
                article_code = str(seller.seller_code)+str(sequence).zfill(5)
                vals['article_code'] = article_code
                if 'default_code' in vals and vals['default_code'] == False:
                    vals['default_code'] = vals['article_code']
                self._update_default_code(vals,article_code)
            elif not seller.is_auto_generate_product_internal_reference:
                if 'default_code' in vals:
                    vals['default_code'] = vals['default_code']
                else:
                    vals['default_code'] = False
            else:
                vals['default_code'] = self.default_code
        return super(ProductTemplate, self).write(vals)
    
    @api.onchange('seller_id')
    def _onchange_seller_id(self):
        self.default_code = False

       
class ProductProduct(models.Model):

    _inherit = 'product.product'

    is_auto_generate_product_internal_reference = fields.Boolean(related="seller_id.is_auto_generate_product_internal_reference",store=True)

    @api.model
    def create(self, vals):
        product = super(ProductProduct, self).create(vals)
        if product.seller_id.is_auto_generate_product_internal_reference:
            product.default_code = product.product_tmpl_id.default_code
        return product
