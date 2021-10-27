# -*- coding: utf-8 -*-
import base64
import re
from odoo import http, tools, _
from odoo.http import request
from odoo.exceptions import AccessError, MissingError
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager, get_records_pager


class CustomerPortal(CustomerPortal):

    MANDATORY_PARTNER_FIELDS = ["name",
                                "email",
                                "gender",
                                "mobile",
                                "date_of_birth",
                                "resident_of_kanha_from_date",
                                "kanha_location_id",
                                "application_type",
                                "pan_card_number",
                                "aadhaar_card_number",
                                # "relative_aadhaar_card_number"
                                ]
    OPTIONAL_PARTNER_FIELDS = ["company_name",
                               "surname",
                               "relation_type",
                               "relative_name",
                               "relative_surname",
                               "relative_aadhaar_card_number",
                               "room_type",
                               "abhyasi_id",
                               "members_count",
                               "citizenship",
                               "passport_number",
                               "vehicle_number",
                               "vehicle_owner",
                               "vehicle_type",
                               "additional_vehicle_number",
                               "work_profile",
                               "change_voter_id_address",
                               "room_details"
                               ]
    VOTER_INFO_FIELDS = ["house_number",
                         "locality",
                         "town",
                         "voter_number",
                         "assembly_constituency",
                         "post_office",
                         "district",
                         "state_id",
                         "zipcode",
                         ]
    
    DOCUMENT_INFO_FIELDS = ["adhar_card",
                           "age_proof",
                           "address_proof",
                           "age_declaration_form",
                           "passport_photo",
                           ]


    def _partner_get_page_view_values(self, partner, access_token, **kwargs):
        values = {
            'page_name': 'partner',
            'partner': partner,
        }
        return self._get_page_view_values(partner, access_token, values, 'partners_history', False, **kwargs)

    
    @http.route(['/partners', '/partners/page/<int:page>'], type='http', auth="user", website=True)
    def portal_partners(self, page=1,  **kw):
        # values = self._prepare_portal_layout_values()
        values = {}
        current_partner = request.env.user.partner_id
        ResPartner = request.env['res.partner']
        if current_partner.aadhaar_card_number:
            domain = ['|',('id', '=', current_partner.id),('relative_aadhaar_card_number', '=', current_partner.aadhaar_card_number)]
        else:
            domain = [('id', '=', current_partner.id)]
        # count for pager
        partner_count = ResPartner.sudo().search_count(domain)
        # make pager
        pager = portal_pager(
            url="/partners",
            total=partner_count,
            page=page,
            step=self._items_per_page
        )
        # if request.env.user.has_group('base.group_portal'):
        # search the count to display, according to the pager data
        partners = ResPartner.sudo().search(domain, limit=self._items_per_page, offset=pager['offset'])
        request.session['partners_history'] = partners.ids[:100]

        values.update({
            'partners': partners,
            'page_name': 'partner',
            'pager': pager,
            'default_url': '/partners',
        })
        return request.render("kanha_census.portal_partners", values)
    
    @http.route(['/partner_old/<int:partner_id>'], type='http', auth="public", website=True)
    def portal_partner(self, partner_id=None, access_token=None, **kw):
        try:
            partner_sudo = self._document_check_access('res.partner', partner_id, access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')

        values = self._partner_get_page_view_values(partner_sudo, access_token, **kw)
        return request.render("kanha_census.portal_partner", values)

    def partner_form_validate(self, data, partner_id):
        error = dict()
        error_message = []
        # Validation
        for field_name in self.MANDATORY_PARTNER_FIELDS:
            if not data.get(field_name):
                error[field_name] = 'missing'
        if(data.get('application_type') == 'Transfer Application'):
            for field_name in self.VOTER_INFO_FIELDS:
                if not data.get(field_name):
                    error[field_name] = 'missing'
        if(not partner_id):
            for field_name in self.DOCUMENT_INFO_FIELDS:
                if not data.get(field_name):
                    error[field_name] = 'missing'
        # email validation
        if data.get('email') and not tools.single_email_re.match(data.get('email')):
            error["email"] = 'error'
            error_message.append(_('Invalid Email! Please enter a valid email address.'))
        # Pan card validation
        if data.get('pan_card_number'):
            is_valid = self.is_valid_pan_number(data.get('pan_card_number'))
            if not is_valid:
                error["pan_card_number"] = 'error'
                error_message.append(_('Invalid Pan Number!'))
        # Aadhar card validation
        if data.get('aadhar_card_number'):
            is_valid = self.is_valid_aadhaar_number(data.get('aadhar_card_number'))
            if not is_valid:
                error["aadhar_card_number"] = 'error'
                error_message.append(_('Invalid Aadhar Number!')) 
                
        # Relative Aadhar card validation
        if data.get('relative_aadhaar_card_number'):
            relative_aadhaar_card_number = data.get('relative_aadhaar_card_number')
            is_valid = self.is_valid_aadhaar_number(relative_aadhaar_card_number)
            if not is_valid:
                error["aadhar_card_number"] = 'error'
                error_message.append(_('Invalid Aadhar Number!'))               
            # Adhar card exsist
            ResPartner = request.env['res.partner']
            is_adhar_exsist = ResPartner.search([('aadhaar_card_number', '=', relative_aadhaar_card_number)])
            if(not is_adhar_exsist): 
                error["relative_aadhaar_card_number"] = 'error'
                error_message.append(_('Relative Aadhar Number does not exist!'))              
        if ((data.get('relation_type')) and (not data.get('relative_aadhaar_card_number'))):
            error["relative_aadhaar_card_number"] = 'error'
            error_message.append(_('Relative Aadhar Number is Mandatory!'))
        
        # Mobile number validation
        if data.get('mobile'):
            is_valid = self.is_valid_mobile_number(data.get('mobile'))
            if not is_valid:
                error["mobile"] = 'error'
                error_message.append(_('Invalid Mobile Number!')) 
        # error message for empty required fields
        if [err for err in error.values() if err == 'missing']:
            error_message.append(_('Some required fields are empty.'))

        unknown = [k for k in data if k not in self.MANDATORY_PARTNER_FIELDS + self.OPTIONAL_PARTNER_FIELDS + self.VOTER_INFO_FIELDS + self.DOCUMENT_INFO_FIELDS]
        if unknown:
            error['common'] = 'Unknown field'
            error_message.append("Unknown field '%s'" % ','.join(unknown))

        return error, error_message

    def is_valid_pan_number(self,pan_number):
        # Valid Pan Card Conditions:
        #     1.It should be ten characters long.
        #     2.The first five characters should be any upper case alphabets.
        #     3.The next four-characters should be any number from 0 to 9.
        #     4.The last(tenth) character should be any upper case alphabet.
        #     5.It should not contain any white spaces.
        regex = "[A-Z]{5}[0-9]{4}[A-Z]{1}"
        p = re.compile(regex)
        if(re.search(p, pan_number) and len(pan_number) == 10):
            return True
        else:
            return False
            # raise Warning("Invalid Pan Number!")
        
    def is_valid_aadhaar_number(self,emp_aadhaar):
        # Valid Aadhar number conditions:
        #     1.It should have 12 digits.
        #     2.It should not start with 0 and 1.
        #     3.It should not contain any alphabet and special characters.
        #     4.It should have white space after every 4 digits.
        regex = ("^[2-9]{1}[0-9]{3}\\" + "s[0-9]{4}\\s[0-9]{4}$")
        p = re.compile(regex)
        if(re.search(p, emp_aadhaar)) and len(emp_aadhaar) == 14:
            return True
        else:
            return False
            # raise Warning("Invalid Aadhar Number!")
        
    def is_valid_mobile_number(self,mobile_number):
        #Valid Mobile Number
        #    1.Begins with 0 or 91
        #    2.Then contains 7 or 8 or 9.
        #    3.Then contains 9 digits
        pattern = re.compile("(0/91)?[6-9][0-9]{9}")
        if pattern.match(mobile_number):
            return True
        else:
            return False
            # raise Warning("Invalid Mobile Number!")

    @http.route(['/partner/portal/form', '/partner/<int:partner_id>'], type='http', auth="public", website=True)
    def update_partner(self, partner_id=None, redirect=None, access_token=None, **post):
        values = self._prepare_portal_layout_values()
        ResPartner = request.env['res.partner']
        partner = ResPartner.sudo().search([('id', '=', partner_id)])
        values.update({
            'error': {},
            'error_message': [],
        })
        if post and request.httprequest.method == 'POST':
            error, error_message = self.partner_form_validate(post, partner_id)
            values.update({'error': error, 'error_message': error_message})
            values.update(post)
            if not error:
                values = {key: post[key] for key in self.MANDATORY_PARTNER_FIELDS}
                values.update({key: post[key] for key in self.OPTIONAL_PARTNER_FIELDS if key in post})
                for field in set(['state_id']) & set(values.keys()):
                    try:
                        values[field] = int(values[field])
                    except:
                        values[field] = False
                for field in set(['passport_photo', 'adhar_card', 'age_proof', 'address_proof', 'age_declaration_form']) & set(values.keys()):
                        file = post.get(field)
                        # values[field] = self.insert_attachment(file)
                        values[field] = base64.encodebytes(file.read())
                values.update({'zip': values.pop('zipcode', '')})
                
                if partner:
                    partner.sudo().write(values)
                else:
                    partner_created = ResPartner.sudo().create(values)
                    if(post.get('relative_aadhaar_card_number')):
                        relative_aadhaar_card_number = post.get('relative_aadhaar_card_number')
                        relative_partner = ResPartner.search([('aadhaar_card_number', '=', relative_aadhaar_card_number)])
                        if(relative_partner):
                            partner_created.sudo().write({'family_members_ids': [(4, relative_partner.id)]})
                            relative_partner.sudo().write({'family_members_ids': [(4, partner_created.id)]})

                if redirect:
                    return request.redirect(redirect)
                return request.redirect('/partners')

        states = request.env['res.country.state'].sudo().search([])
        kanha_locations = request.env['kanha.location'].sudo().search([])
        values.update({
            'partner': partner,
            'states': states,
            'has_check_vat': hasattr(request.env['res.partner'], 'check_vat'),
            'redirect': redirect,
            'page_name': 'my_details',
            'kanha_locations': kanha_locations
        })
        response = request.render("kanha_census.portal_user_details", values)
        response.headers['X-Frame-Options'] = 'DENY'
        return response
    
    @http.route(['/add_partner'], type='http', auth="public", website=True)
    def add_partner_form(self, redirect=None, **post):
        values = self._prepare_portal_layout_values()
        values.update({
            'error': {},
            'error_message': [],
        })
        states = request.env['res.country.state'].sudo().search([])
        kanha_locations = request.env['kanha.location'].sudo().search([])
        values.update({
            'partner': 0,
            'states': states,
            'redirect': redirect,
            'page_name': 'my_details',
            'kanha_locations': kanha_locations
        })
        response = request.render("kanha_census.portal_user_details", values)
        return response
    
    # def insert_attachment(self, file):
    #     Attachments = request.env['ir.attachment']
    #     partner_id = request.env.user.partner_id.id
    #     attachment = Attachments.create({
    #         'name':file.name,
    #         'res_model': 'res.partner',
    #         'res_id': partner_id,
    #         'datas': base64.encodebytes(file.read())
    #     })
    #     return attachment.id