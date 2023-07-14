# -*- coding: utf-8 -*-
from odoo import models, fields, api, tools
from odoo.exceptions import UserError, AccessError, ValidationError

class StockPicking(models.Model):
    _inherit = "stock.picking"
    _order = "id desc"

    def compute_package_weight(self):
        if self.seller_id.use_amzn_shipment == True:
            shipping_weight = 0
            for move in self.move_line_ids:
                if move.product_id.weight > move.product_id.volumetric_weight:
                    shipping_weight += move.product_id.weight * move.qty_done
                else:
                    shipping_weight += move.product_id.volumetric_weight * move.qty_done
            self.pack_shipping_weight = shipping_weight

    def button_validate(self):
        if not self.service_id:
            raise ValidationError('Please select the service before validating')
        if self.seller_id.use_amzn_shipment == True and self.package_ids and len(self.package_ids) == 1:
            shipping_weight = 0
            for move in self.move_line_ids:
                if move.product_id.weight > move.product_id.volumetric_weight:
                    shipping_weight += move.product_id.weight * move.qty_done
                else:
                    shipping_weight += move.product_id.volumetric_weight * move.qty_done
            if shipping_weight > self.shipping_weight:
                self.pack_shipping_weight = shipping_weight
            if shipping_weight <= 2:
                delivery_type = self.env['delivery.carrier'].search([('delivery_type', '=', 'amazon_shipment')], limit=1)
                self.carrier_id = delivery_type.id
        return super().button_validate()
