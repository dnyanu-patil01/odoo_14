# -*- coding: utf-8 -*-
from odoo import fields, models

class ProductPackaging(models.Model):
    _inherit = "product.packaging"

    package_carrier_type = fields.Selection(
        selection_add=[("shiprocket", "Shiprocket")],
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
        self.write({'state': 'approve'})
        action = self.env["ir.actions.actions"]._for_xml_id("shopify_ept.action_shopify_export_odoo_products_ept")
        action['context'] = dict(self.env.context)
        return action