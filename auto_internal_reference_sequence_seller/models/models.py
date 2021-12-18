from odoo import api, models, fields,_


class ResPartner(models.Model):
    _inherit = "res.partner"

    is_auto_generate_product_internal_reference = fields.Boolean("Auto Generate Product Sequence")
    seller_product_sequence_id = fields.Many2one('ir.sequence', string='Product Sequence',
        help="This sequence is automatically created by Odoo but you can change it "
        "to customize the reference numbers of your orders.", copy=False)

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    is_auto_generate_product_internal_reference = fields.Boolean(related="seller_id.is_auto_generate_product_internal_reference",store=True)
   
class ProductProduct(models.Model):

    _inherit = 'product.product'

    is_auto_generate_product_internal_reference = fields.Boolean(related="seller_id.is_auto_generate_product_internal_reference",store=True)
    default_code = fields.Char(
        required=True,
        default="/",
        tracking=True,
        help="Set to '/' and save if you want a new internal reference "
        "to be proposed.",
    )

    @api.model
    def create(self, vals):
        if "default_code" not in vals or vals["default_code"] == "/":
            seller_id = vals.get("seller_id", False)
            template_id = vals.get("product_tmpl_id", False)
            seller_obj = self.env["res.partner"]
            if seller_id:
                # Created as a product.product
                seller = seller_obj.browse(seller_id)
            elif template_id:
                # Created from a product.template
                template = self.env["product.template"].browse(template_id)
                seller = template.seller_id
            if seller and seller.is_auto_generate_product_internal_reference and seller.seller_product_sequence_id:
                vals["default_code"] = seller.seller_product_sequence_id._next()
        return super().create(vals)

    def write(self, vals):
        """To assign a new internal reference, just write '/' on the field.
        Note this is up to the user, if the product category is changed,
        she/he will need to write '/' on the internal reference to force the
        re-assignment."""
        if vals.get("default_code", "") == "/" or 'seller_id' in vals:
            seller_obj = self.env["res.partner"]
            for product in self:
                if product.seller_id:
                    if product.seller_id.id != vals.get('seller_id'):
                        seller_id = vals.get("seller_id", product.seller_id.id)
                        seller = seller_obj.browse(seller_id)
                        if seller and seller.is_auto_generate_product_internal_reference and seller.seller_product_sequence_id:
                            ref = seller.seller_product_sequence_id._next()
                            vals["default_code"] = ref
                            if len(product.product_tmpl_id.product_variant_ids) == 1:
                                product.product_tmpl_id.write({"default_code": ref})
                elif not product.seller_id and vals.get('seller_id') and vals.get("default_code", "") != "/":
                    pass
                super(ProductProduct, product).write(vals)
            return True
        return super().write(vals)
