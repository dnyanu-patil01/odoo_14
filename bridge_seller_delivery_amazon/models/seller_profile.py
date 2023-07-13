# -*- coding: utf-8 -*-
from odoo import models, fields, api, tools

class SellerProfileInherit(models.Model):
    _inherit = "res.partner"

    use_amzn_shipment = fields.Boolean('Use Amazon Shipment?')
