# -*- coding: utf-8 -*-
from odoo import models, fields, api, tools

class ShipmentMethodInherit(models.Model):
    _inherit = "delivery.carrier"

    delivery_type = fields.Selection(selection_add=[('amazon_shipment', 'Amazon Delivery')])