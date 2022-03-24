# -*- coding: utf-8 -*-
from odoo import http
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.addons.portal.controllers.portal import CustomerPortal

from odoo.http import request

class CustomerPortal(CustomerPortal):

    def _prepare_portal_layout_values(self):
        values =  super(CustomerPortal, self)._prepare_portal_layout_values()
        centers = request.env['res.center'].search([])
        values.update({'centers':centers})
        return values

class WebsiteSale(WebsiteSale):

    def checkout_values(self, **kw):
        values =  super(WebsiteSale, self).checkout_values(**kw)
        centers = request.env['res.center'].search([])
        values.update({'centers':centers})
        return values

    def _get_shop_payment_values(self, order, **kwargs):
        values =  super(WebsiteSale, self)._get_shop_payment_values(order,**kwargs)
        centers = request.env['res.center'].search([])
        values.update({'centers':centers})
        return values