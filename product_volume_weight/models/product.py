from odoo import api, fields, models


class Product(models.Model):
    _inherit = "product.product"

    @api.onchange(
        "product_length", "product_height", "product_width"
    )
    def onchange_calculate_volume(self):
        self.volumetric_weight = self.env["product.template"]._calc_volume(
            self.product_length,
            self.product_height,
            self.product_width,
        )

    product_length = fields.Float("Length")
    product_height = fields.Float("Height")
    product_width = fields.Float("Breadth")
    volumetric_weight = fields.Float("Volumetric Weight",digits=(8, 3))



class ProductTemplate(models.Model):
    _inherit = "product.template"

    @api.model
    def _calc_volume(self, product_length, product_height, product_width):
        volume = 0
        if product_length and product_height and product_width:
            volume = (product_length * product_height * product_width)/5000
        return volume

    @api.onchange(
        "product_length", "product_height", "product_width"
    )
    def onchange_calculate_volume(self):
        self.volumetric_weight = self._calc_volume(
            self.product_length,
            self.product_height,
            self.product_width,
        )

    product_length = fields.Float(
        related="product_variant_ids.product_length", readonly=False
    )
    product_height = fields.Float(
        related="product_variant_ids.product_height", readonly=False
    )
    product_width = fields.Float(
        related="product_variant_ids.product_width", readonly=False
    )
    volumetric_weight = fields.Float(
        related="product_variant_ids.volumetric_weight", readonly=False,digits=(8, 3)
    )