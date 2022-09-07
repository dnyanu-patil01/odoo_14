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


class ProductPricelist(models.Model):
    _inherit = 'product.pricelist.item'

    def create(self,values):
        product = super(ProductPricelist,self).create(values)
        if self.env.context.get('update_shopify_price'):
            product.push_price_change_to_shopify()
        return product

    def write(self,values):
        product = super(ProductPricelist,self).write(values)
        if self.env.context.get('update_shopify_price'):
            self.push_price_change_to_shopify()
        return product
        
    def push_price_change_to_shopify(self):
        shopify_product_tmpl_id = self.env['shopify.product.template.ept'].search([('product_tmpl_id','=',self.product_tmpl_id.id)])
        if shopify_product_tmpl_id:
            import_product_obj = self.env['shopify.process.import.export'].create({
            'shopify_is_update_basic_detail':False,
            'shopify_is_set_price':True,
            'shopify_is_set_image':False,
            'shopify_is_publish':'publish_product_web',
            })
            import_product_obj.with_context({'active_ids':shopify_product_tmpl_id.id}).sudo().manual_update_product_to_shopify() 
        return True   