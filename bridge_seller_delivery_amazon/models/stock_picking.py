# -*- coding: utf-8 -*-
from odoo import models, fields, api, tools
from odoo.exceptions import UserError, AccessError, ValidationError

class StockPicking(models.Model):
    _inherit = "stock.picking"
    _order = "id desc"

    def button_validate(self):
        if not self.seller_id:
            raise ValidationError('Please provide the seller.')
        if self.seller_id.use_amzn_shipment == True and self.package_ids and len(self.package_ids) == 1:
            shipping_weight = 0
            for move in self.move_line_ids:
                if move.product_id.weight > move.product_id.volumetric_weight:
                    shipping_weight += move.product_id.weight * move.qty_done
                else:
                    shipping_weight += move.product_id.volumetric_weight * move.qty_done
            self.shipping_weight = shipping_weight
            if shipping_weight <= 2:
                delivery_type = self.env['delivery.carrier'].search([('delivery_type', '=', 'amazon_shipment')], limit=1)
                self.carrier_id = delivery_type.id
                # To Get the Rates of Amazon delivery
                self.amzn_get_rates()
        return super().button_validate()
