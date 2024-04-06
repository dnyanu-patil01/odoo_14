# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.
from odoo import models, fields


class StockPicking(models.Model):
    _inherit = "stock.picking"

    updated_in_shopify = fields.Boolean(default=False)
    is_shopify_delivery_order = fields.Boolean("Shopify Delivery Order", default=False)
    shopify_instance_id = fields.Many2one("shopify.instance.ept", "Instance")
    shopify_order_number = fields.Char(related="sale_id.shopify_order_number", string="Shopify Order Number", store=True)
