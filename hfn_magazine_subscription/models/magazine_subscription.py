# -*- coding: utf-8 -*-
from unittest import result
import requests
import json

from datetime import datetime, timedelta

from odoo import api, models,fields

from odoo.exceptions import AccessError

import base64

API_BASE_URL = "https://profile.srcm.net"

class MagazineSubscription(models.Model):
    _name = 'magazine.subscription'
    _description = 'Magazine Subscription'
    _inherit = 'mail.thread'
    _order = 'id desc'

    name = fields.Char()
    id_number = fields.Char(required=True)
    email = fields.Char()
    # address fields
    street = fields.Char()
    street2 = fields.Char()
    zip = fields.Char(change_default=True)
    city = fields.Char()
    state_id = fields.Many2one("res.country.state", string='State', ondelete='restrict', domain="[('country_id', '=?', country_id)]")
    country_id = fields.Many2one('res.country', string='Country', ondelete='restrict')
    mobile = fields.Char()
    amount = fields.Monetary()
    currency_id = fields.Many2one('res.currency', string="Currency",readonly=True, index=True, default=lambda self: self.env.company)
    company_id = fields.Many2one('res.company', string='Company',readonly=True, index=True, default=lambda self: self.env.company)
    payment_mode = fields.Selection([
        ('cash', 'Cash'),
        ('card','Card'),
        ('upi','UPI'),
        ('cheque','Cheque')
    ], string='Payment Mode')
    subscription_added_by = fields.Many2one('res.users')
    deliver_at = fields.Selection([
        ('home','Deliver to address given'),
        ('center','Pickup at your nearest Meditation Center')
    ],string="Subscription")
    center_id = fields.Many2one('res.center', string='Center',index=True, copy=False)
    
    subscriprion_line = fields.One2many('magazine.subscription.line', 'subscription_id', string='field_name')


    @api.model
    def get_abhiyasi_data(self, id_number):
        if not self.env.company.api_token:
            raise AccessError(('Authentication Token Not Found! Please Contact IT Team And Try Again'))
        if self.env.company.api_token and id_number:
            url="https://profile.srcm.net/api/v2/abhyasis/?ref=%s"%(id_number)
            headers = {
            "Authorization": self.env.company.api_token,
            }
            response_dict={}
            try:
                response = requests.get(url, headers=headers)
                if response.status_code == 200:
                    response_dict = response.json()
            except requests.exceptions.HTTPError as errh:
                raise AccessError(('An Http Error occurred: %s'%(errh)))
            except requests.exceptions.ConnectionError as errc:
                raise AccessError(('No Internet! Please Check Your Internet And Try Again'))
            except requests.exceptions.Timeout as errt:
                raise AccessError(("A Timeout Error occurred: %s"%(repr(errt))))
            except requests.exceptions.RequestException as err:
                raise AccessError(("An Unknown Error occurred: %s"%(repr(err))))
            if 'results' in  response_dict and response_dict['results'] != []:
                data = response_dict['results'][0]
                street = ""
                if 'street2' in data and data['street2']:
                    street+=data['street2']
                if 'street3' in data and data['street3']:
                    street+=' , '+data['street3']
                if 'street4' in data and data['street4']:
                    street+=' , '+data['street4']
                
                abhyasi_data_dict = {
                    'name' : data['name'] if 'name' in data else False,
                    'email' : data['email'] if 'email' in data else False,
                    'id_number' : data['ref'] if 'ref' in data else False,
                    'city' : data['city'] if 'city' in data else False,
                    'street': data['street'],
                    'street2' : street,
                    'zip' : data['postal_code'] if 'postal_code' in data else False,
                    'mobile' : data['mobile'] if 'mobile' in data else False,
                }
                abhyasi_data_dict.update(self.get_country_state(data))
                return abhyasi_data_dict
            else:
                return {}

    @api.model
    def get_country_state(self, data):
        vals={
            'country':False,
            'state':False
        }
        if 'country' in data and data['country']:
            country = self.env['res.country'].search([('name','=',data['country']['name'])],limit=1)
            if country:
                vals.update({'country':country.id})
        if 'state' in data and data['state']:
            state = self.env['res.country.state'].search([('name','=',data['state']['name'])],limit=1)
            if state:
                vals.update({'state':state.id})
        return vals
    
    def print_subscription(self):
        return self.env.ref('hfn_magazine_subscription.action_report_magazine_subscription').report_action(self)
    
    def action_receipt_to_customer(self):
        if not self:
            return False
        if not self.email:
            return False

        message = ("<p>Dear %s,<br/>Your Maganize Subscription Added Successfully</p>") % (self.name)
        mail_values = {
            'subject': ('Heartfulness Magazine Subscription - Regards'),
            'body_html': message,
            'email_from': self.env.company.email or self.env.user.email_formatted,
            'email_to': self.email,
        }

        report = self.env.ref('hfn_magazine_subscription.action_report_magazine_subscription')._render_qweb_pdf(self.ids[0])
        filename = self.name +'Magazine Subscription' + '.pdf'
        attachment = self.env['ir.attachment'].sudo().create({
                'name': filename,
                'type': 'binary',
                'datas': base64.b64encode(report[0]),
                'res_model': 'magazine.subscription',
                'res_id': self.ids[0],
                'mimetype': 'application/x-pdf'
            })
        mail_values.update({'attachment_ids': [(4, attachment.id)]})
        mail = self.env['mail.mail'].sudo().create(mail_values)
        mail.send()
        return True

class SubscriptionLine(models.Model):
    _name = 'magazine.subscription.line'
    _description = 'Magazine Subscription Line'
    _order = 'id desc'

    subscription_id = fields.Many2one('magazine.subscription',ondelete='cascade')
    subscription_period = fields.Selection([
        ('1','One Year'),
        ('2','Two Year')
    ],string="Subscription")
    no_of_subcription = fields.Integer('Subscription Count')
    language = fields.Selection([
        ('english', 'English'),
        ('hindi','Hindi'),
        ('tamil','Tamil'),
        ('telugu','Telugu')
    ], string='Language')
    amount = fields.Float()