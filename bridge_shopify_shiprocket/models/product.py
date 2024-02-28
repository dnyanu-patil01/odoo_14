# -*- coding: utf-8 -*-
from odoo import fields, models

class ProductPackaging(models.Model):
    _inherit = "product.packaging"

    package_carrier_type = fields.Selection(
        selection_add=[("shiprocket", "Shiprocket"),("self", "Self Fulfilment")],
        ondelete={'shiprocket': 'set default'}
    )
    delivery_package_id = fields.Many2one(
        'product.packaging', 'Package Type', index=True)

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def _pre_put_in_pack_hook(self, move_line_ids):
        res = super(StockPicking, self)._pre_put_in_pack_hook(move_line_ids)
        packaging = False
        delivery_package = False
        if len(move_line_ids) == 1:
            packaging = self.env["product.packaging"].search(
                [
                    ("product_id", "=", move_line_ids.product_id.id),
                    ("qty", "=", move_line_ids.qty_done),
                    ("delivery_package_id",'!=',False)
                ],
                limit=1,
            )
        if res and packaging:
            delivery_package = self._put_in_pack(move_line_ids)
            if delivery_package:
                shipping_weight = 0
                for move in move_line_ids:
                    if move.product_id.weight > move.product_id.volumetric_weight:
                        shipping_weight+= move.product_id.weight * move.qty_done
                    else:
                        shipping_weight += move.product_id.volumetric_weight * move.qty_done
                delivery_package.write({'packaging_id':packaging.delivery_package_id.id,'shipping_weight':shipping_weight})
                return res
            else:
                return self._set_delivery_packaging()
        else:
            return self._set_delivery_packaging()

class ProductTemplate(models.Model):
    _inherit = "product.template"

    def button_approve(self):
        shopify_instance_id = self.env['shopify.instance.ept'].search([],limit=1)
        shopify_export = self.env['shopify.prepare.product.for.export.ept'].create({
            'export_method':'direct',
            'shopify_instance_id':shopify_instance_id.id
        })
        
        active_template_ids = self._context.get("active_ids", []) or [self.id]
        shopify_export.with_context({'active_ids':active_template_ids}).prepare_product_for_export()
        shopify_product_template_ids = self.env['shopify.product.template.ept'].search([('product_tmpl_id','in',active_template_ids)])
        import_product_obj = self.env['shopify.process.import.export'].create({
            'shopify_is_update_basic_detail':True,
            'shopify_is_set_price':True,
            'shopify_is_set_image':True,
            'shopify_is_publish':'publish_product_web',
        })
        for product in shopify_product_template_ids:
            """To check product is already created in shopify 
            if yes,then we are updating the details alone 
            else we are pushing product to shopify"""
            if product.exported_in_shopify:
                import_product_obj.with_context({'active_ids':product.ids}).manual_update_product_to_shopify()
            else:
                import_product_obj.with_context({'active_ids':product.ids}).manual_export_product_to_shopify()
        return super(ProductTemplate,self).button_approve()