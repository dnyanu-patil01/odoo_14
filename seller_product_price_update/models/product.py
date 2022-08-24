# -*- coding: utf-8 -*-
from odoo import fields, models
from odoo.exceptions import UserError


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    def action_update_price(self):
        default_product_id = self.env.context.get('default_product_id', len(self.product_variant_ids) == 1 and self.product_variant_id.id)
        action = self.env["ir.actions.actions"]._for_xml_id("seller_product_price_update.action_change_product_price")
        action['context'] = dict(
            self.env.context,
            default_product_id=default_product_id,
            default_product_tmpl_id=self.id
        )
        return action