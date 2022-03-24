# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import http, _
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.addons.portal.controllers.portal import CustomerPortal

from odoo.http import request

class CustomerPortal(CustomerPortal):
    MANDATORY_BILLING_FIELDS = ["name", "phone", "email", "street", "city", "country_id","state_id","center_id"]
    OPTIONAL_BILLING_FIELDS = ["zipcode", "vat", "company_name"]
    
    def _prepare_portal_layout_values(self):
        values =  super(CustomerPortal, self)._prepare_portal_layout_values()
        centers = request.env['res.center'].search([])
        values.update({'centers':centers})
        return values

class WebsiteSaleCenter(WebsiteSale):

    #Requires Login To View Shop Page
    @http.route(auth="user")
    def shop(self, page=0, category=None, search='', ppg=False, **post):
        return super(WebsiteSaleCenter, self).shop(page=page, category=category, search=search, ppg=ppg, **post)
    
    @http.route(auth="user")
    def cart(self, access_token=None, revive='', **post):
        return super(WebsiteSaleCenter, self).cart(access_token=access_token, revive=revive, **post)

    def checkout_values(self, **kw):
        values =  super(WebsiteSaleCenter, self).checkout_values(**kw)
        centers = request.env['res.center'].search([])
        values.update({'centers':centers})
        return values

    def _get_shop_payment_values(self, order, **kwargs):
        values =  super(WebsiteSaleCenter, self)._get_shop_payment_values(order,**kwargs)
        centers = request.env['res.center'].search([])
        values.update({'centers':centers})
        return values
    
    @http.route(['/shop/payment'], type='http', auth="public", website=True)
    def payment(self, **post):
        order = request.website.sale_get_order()
        center_id = order.partner_shipping_id.center_id or order.partner_id.center_id or False
        if order and center_id:
            order.write({'center_id':center_id.id})
        return super(WebsiteSaleCenter, self).payment(**post)

    def _get_mandatory_fields_billing(self, country_id=False):
        req = self._get_mandatory_billing_fields()
        req += ['center_id']
        print(req)
        return req

    def _get_mandatory_fields_shipping(self, country_id=False):
        req = self._get_mandatory_shipping_fields()
        req += ['center_id']
        print(req)
        return req

    @http.route(['/shop/state_infos/'], type='json', auth="public", methods=['POST'], website=True)
    def state_infos(self, mode,**kw):
        return dict(
            centers=[(st.id, st.name) for st in request.env['res.center'].search([('state_id','=',int(kw.get('state_id')))])],
        )

    def values_postprocess(self, order, mode, values, errors, error_msg):
        new_values = {}
        new_values, errors, error_msg = super().values_postprocess(order, mode, values, errors, error_msg)
        
        if 'center_id' in values:
            new_values.update({'center_id':values.get('center_id')})
        return new_values, errors, error_msg