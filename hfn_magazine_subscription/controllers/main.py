from re import T
import pytz
from datetime import datetime, timedelta
from odoo import http, SUPERUSER_ID, _

from odoo import http
from odoo.http import request
from odoo.addons.website_form.controllers.main import WebsiteForm
from odoo.exceptions import ValidationError

import json

key_to_be_deleted = [
    'no_of_subcription_e1','no_of_subcription_e2',
    'no_of_subcription_h2','no_of_subcription_h1',
    'no_of_subcription_ta1','no_of_subcription_ta2',
    'no_of_subcription_te1','no_of_subcription_te2',
    'amount_e1','amount_h1','amount_ta1','amount_te1'
]
class WebsiteMagazineSubscription(http.Controller):

    @http.route(['/magazine_subscription'], type='http', auth="user", methods=['GET'], website=True)
    def schedule(self, **kw):
        values = {
            'countries':  request.env['res.country'].sudo().search([]),
            'states':  request.env['res.country.state'].sudo().search([]),
            'centers':request.env['res.center'].search([]),
            }
        return request.render('hfn_magazine_subscription.magazine_subscription', values)
    
class WebsiteMagazineSubscriptionForm(WebsiteForm):

    @http.route('/maganize_subscriptionmagazine.subscription', type='http', auth="public", methods=['POST'], website=True)
    def website_form_maganize_subscription(self, **kwargs):
        model_record = request.env.ref('hfn_magazine_subscription.model_magazine_subscription')
        try:
            self.extract_data(model_record, kwargs)
            if 'id_number' in kwargs and not kwargs['id_number'].isalnum():
                return json.dumps({'error':'ID Number Must Be Combination Of Aplhabets And Numbers'})
            if 'deliver_at' not in kwargs or not kwargs['deliver_at']:
                return json.dumps({'error':['Error','Invalid Value For Deliver At']})
            elif kwargs['deliver_at'] == 'center' and 'center_id' not in kwargs:
                return json.dumps({'error':['Error','Invalid Value For Center']})
            if kwargs['amount'] == '0' or 'amount' not in kwargs:
                return json.dumps({'error':['Error','Invalid Value For Amount']})
            if kwargs['country_id'] and request.env['res.country'].browse(int(kwargs['country_id'])).state_required:
                if 'state_id' not in kwargs or not kwargs['state_id']:
                    return json.dumps({'error':['Error','State Value Is Required For Selected Country']})
            if 'payment_mode' not in kwargs or not kwargs['payment_mode']:
                return json.dumps({'error':['Error','Invalid Payment Mode']})
        except ValidationError as e:
            return json.dumps({'error_fields': e.args[0]})
        subscription_value = self.create_subscription_lines(**kwargs)
        res = {key: value for (key, value) in subscription_value.items() if key not in key_to_be_deleted}
        subscription = request.env['magazine.subscription'].create(res)
        if subscription:
            request.session.update({'last_subscription_id':subscription.id})
            return json.dumps({'id': subscription.id})
    
    def create_subscription_lines(self,**data):
        line_ids = []
        if 'no_of_subcription_e1' in data:
            no_of_sub = int(data['no_of_subcription_e1'])
            line_ids.append((0,0,{'language':'english','subscription_period':'1','no_of_subcription':no_of_sub,'amount':no_of_sub*1500}))
        if 'no_of_subcription_h1' in data:
            no_of_sub = int(data['no_of_subcription_h1'])
            line_ids.append((0,0,{'language':'hindi','subscription_period':'1','no_of_subcription':no_of_sub,'amount':no_of_sub*1500}))
        if 'no_of_subcription_ta1' in data:
            no_of_sub = int(data['no_of_subcription_ta1'])
            line_ids.append((0,0,{'language':'tamil','subscription_period':'1','no_of_subcription':no_of_sub,'amount':no_of_sub*1500}))
        if 'no_of_subcription_te1' in data:
            no_of_sub = int(data['no_of_subcription_te1'])
            line_ids.append((0,0,{'language':'telugu','subscription_period':'1','no_of_subcription':no_of_sub,'amount':no_of_sub*1500}))
        if 'no_of_subcription_e2' in data:
            no_of_sub = int(data['no_of_subcription_e2'])
            line_ids.append((0,0,{'language':'english','subscription_period':'2','no_of_subcription':no_of_sub,'amount':no_of_sub*3000}))
        if 'no_of_subcription_h2' in data:
            no_of_sub = int(data['no_of_subcription_h2'])
            line_ids.append((0,0,{'language':'hindi','subscription_period':'2','no_of_subcription':no_of_sub,'amount':no_of_sub*3000}))
        if 'no_of_subcription_ta2' in data:
            no_of_sub = int(data['no_of_subcription_ta2'])
            line_ids.append((0,0,{'language':'tamil','subscription_period':'2','no_of_subcription':no_of_sub,'amount':no_of_sub*3000}))
        if 'no_of_subcription_te2' in data:
            no_of_sub = int(data['no_of_subcription_te2'])
            line_ids.append((0,0,{'language':'telugu','subscription_period':'2','no_of_subcription':no_of_sub,'amount':no_of_sub*3000}))
        data.update({'subscriprion_line':line_ids,'subscription_added_by':request.env.user.id})
        return data



class WebsiteForm(WebsiteForm):

    def _handle_website_form(self, model_name, **kwargs):
        if model_name == 'magazine.subscription':
            if kwargs['country_id']:
                kwargs.update({'country_id':int(kwargs['country_id'])})
            if kwargs['state_id']:
                kwargs.update({'state_id':int(kwargs['state_id'])})
            if kwargs['center_id']:
                kwargs.update({'center_id':int(kwargs['center_id'])})
            if kwargs['amount']:
                kwargs.update({'amount':float(kwargs['amount'])})
            kwargs.update({'subscription_added_by':request.env.user.id})
        return super(WebsiteForm, self)._handle_website_form(model_name, **kwargs)
