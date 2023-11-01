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
            self.shipping_weight = self.package_ids.shipping_weight
            if self.package_ids.shipping_weight <= 2:
                delivery_type = self.env['delivery.carrier'].search([('delivery_type', '=', 'amazon_shipment')], limit=1)
                self.carrier_id = delivery_type.id
                # To Get the Rates of Amazon delivery
                self.amzn_get_rates()
        return super(StockPicking, self).button_validate()
