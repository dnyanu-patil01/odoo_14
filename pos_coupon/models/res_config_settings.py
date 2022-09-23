# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    module_pos_coupon = fields.Boolean("Coupon and Promotion Programs", help="Allow the use of coupon and promotion programs in PoS.")