from odoo import api, fields, models, _
from odoo.exceptions import UserError

class SetPrice(models.TransientModel):
    _name = "change.product.price"
    _description = "Set Price"

    pricelist_id = fields.Many2one(
        "product.pricelist", "Select Pricelist"
    )
    product_id = fields.Many2one('product.product', 'Product', required=True)
    product_tmpl_id = fields.Many2one('product.template', 'Template', required=True)
    product_variant_count = fields.Integer('Variant Count',
        related='product_tmpl_id.product_variant_count', readonly=False)
    new_price = fields.Float(
        'New Price', default=1,
        digits='Product Unit of Measure', required=True,
        help='This Price of the product.')
    
    new_compare_at_price = fields.Float(
        'New Compare at Price', default=0,
        digits='Product Unit of Measure', required=True)

    @api.onchange('product_id')
    def _onchange_product_id(self):
        self.new_price = self.product_id.lst_price

    @api.constrains('new_price')
    def check_new_price(self):
        if any(wizard.new_price <= 0 for wizard in self):
            raise UserError(_('Price cannot be negative or zero.'))

    def change_product_price(self):
        """ Changes the Product Price by creating/editing corresponding pricelist.
        """
        if self.product_variant_count == 1:
            self.product_tmpl_id.write({'list_price':self.new_price})
            self.product_id.write({'compare_at_price':self.new_compare_at_price})
        else:
            self.product_id.write({'compare_at_price':self.new_compare_at_price})
        
        pricelist = self.env["product.pricelist.item"].search(
                        [
                            ("product_tmpl_id", "=", self.product_tmpl_id.id),
                            ("product_id", "=", self.product_id.id),
                        ]
                    )
        if pricelist:
            pricelist.with_context({'update_shopify_price':True}).write({"fixed_price": self.new_price})
        else:
            pricelist = self.env["product.pricelist"].search([], limit=1)
            if pricelist:
                self.env["product.pricelist.item"].with_context({'update_shopify_price':True}).create(
                    {
                        "pricelist_id": pricelist.id,
                        "product_id": self.product_id.id,
                        "product_tmpl_id": self.product_tmpl_id.id,
                        "fixed_price": self.new_price,
                        "compute_price": "fixed",
                    }
                    )
        return True