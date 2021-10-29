# -*- coding: utf-8 -*-
import base64
import re
from odoo import http, tools, _
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager, get_records_pager


class CustomerPortal(CustomerPortal):

    MANDATORY_PARTNER_FIELDS = ["name",
                                "email",
                                "mobile",
                                "gender",
                                "date_of_birth",
                                "application_type",
                                "aadhaar_card_number",
                                "citizenship",
                                "country_id",
                                "birth_state_id",
                                "birth_district",
                                "birth_town",
                                "resident_of_kanha_from_date",
                                "kanha_location_id",
                                "kanha_house_number",
                                "adhar_card_filename",
                                "adhar_card_back_side_filename",
                                "passport_photo_filename",
                                "age_proof_filename",
                                "address_proof_filename",
                                "age_declaration_form_filename",
                                ]
    OPTIONAL_PARTNER_FIELDS = ["surname",
                               "relation_type",
                               "relative_name",
                               "relative_surname",
                               "relative_aadhaar_card_number",
                               "room_type",
                               "abhyasi_id",
                               "members_count",
                               "passport_number",
                               "vehicle_number",
                               "vehicle_owner",
                               "vehicle_type",
                               "additional_vehicle_number",
                               "work_profile",
                               "change_voter_id_address",
                               "room_details",
                               "adhar_card",
                               "passport_photo",
                               "age_proof",
                               "address_proof",
                               "age_declaration_form",
                               "pan_card_number",
                               "adhar_card_back_side",
                               "voter_number"
                               ]
    VOTER_INFO_FIELDS = ["existing_voter_id_number",
                         "state_id",
                         "assembly_constituency",
                         "house_number",
                         "locality",
                         "town",
                         "post_office",
                         "zip",
                         "district",
                         ]

    @http.route(['/family', '/family/page/<int:page>'], type='http', auth="user", website=True)
    def partner_list(self, page=1,  **kw):
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
            url="/family",
            total=partner_count,
            page=page,
            step=self._items_per_page
        )
        # search the count to display, according to the pager data
        partners = ResPartner.sudo().search(domain, limit=self._items_per_page, offset=pager['offset'])
        request.session['partner_history'] = partners.ids[:100]

        values.update({
            'partners': partners,
            'page_name': 'family',
            'pager': pager,
            'default_url': '/family',
        })
        return request.render("kanha_census.kanha_portal_list", values)

    def kanha_portal_form_validate(self, data, partner_id):
        error = dict()
        error_message = []
        missing_fields = dict()
        form_fields = {"name": "Name",
                       "email":"Email",
                       "mobile":"Mobile",
                       "gender":"Gender",
                       "date_of_birth": "Date of Birth",
                       "application_type": "Application Type",
                       "aadhaar_card_number":"Adhar Card Number",
                       "citizenship": "Citizenship",
                       "birth_state_id": "Birth State",
                       "birth_district":"Birth District",
                       "birth_town": "Birth Town",
                       "relative_aadhaar_card_number": "Relative Aadhaar Card Number",
                       "resident_of_kanha_from_date": "Resident of Kanha From Date",
                       "kanha_location_id": "Kanha Location",
                       "kanha_house_number":"Kanha House Number",
                       "adhar_card_filename": 'Adhar Card File Front',
                       "passport_photo_filename": "Passport Photo File",
                       "adhar_card_back_side_filename": "Adhar Card File Back",
                       "age_proof_filename": "Age Proof File",
                       "address_proof_filename": "Address Proof File",
                       "age_declaration_form_filename": "Age Declaration Form",
                       "existing_voter_id_number": "Existing Voter Number",
                       "state_id": "State",
                       "assembly_constituency": "Assembly Constituency",
                       "house_number": "House Number",
                       "locality": "Locality",
                       "town": "Town",
                       "post_office": "Post Office",
                       "zip": "Pin Code",
                       "district": "District",
        }
        # Validation
        for field_name in self.MANDATORY_PARTNER_FIELDS:
            if not data.get(field_name):
                error[field_name] = 'missing'
                missing_fields[field_name] = form_fields.get(field_name)
        if(data.get('application_type') == 'Transfer Application'):
            for field_name in self.VOTER_INFO_FIELDS:
                if not data.get(field_name):
                    error[field_name] = 'missing'
                    missing_fields[field_name] = form_fields.get(field_name)
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
                error_message.append(_('Given Relative Aadhar Number does not exist!'))              
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
        if(missing_fields):
            error_message.append("Please fill these required field(s): '%s'" % ','.join(missing_fields.values()))
        
        unknown = [k for k in data if k not in self.MANDATORY_PARTNER_FIELDS + self.OPTIONAL_PARTNER_FIELDS + self.VOTER_INFO_FIELDS]
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

    @http.route(['/family', '/family/<int:partner_id>'], type='http', auth="public", website=True)
    def save_portal_form(self, partner_id=None, redirect=None, access_token=None, **post):
        values = self._prepare_portal_layout_values()
        ResPartner = request.env['res.partner']
        partner = ResPartner.sudo().search([('id', '=', partner_id)])
        values.update({
            'error': {},
            'error_message': [],
        })
        # Fetch the state of India
        country = request.env['res.country'].sudo().search([('code', '=', 'IN')])
        states = request.env['res.country.state'].sudo().search([('country_id', '=', country.id)])
        # Fetch the record who doesnt have any child records
        kanha_location_parent_ids = request.env['kanha.location'].sudo().search([]).parent_id.ids
        kanha_locations_nth_child = request.env['kanha.location'].sudo().search([('id', 'not in', kanha_location_parent_ids)])
        form_values = {}
        form_values.update({
            'states': states,
            'redirect': redirect,
            'page_name': 'family',
            'kanha_locations': kanha_locations_nth_child,
            'zipcode': post.get('zip'),
            'country_id': country
        })
        if post and request.httprequest.method == 'POST':
            error, error_message = self.kanha_portal_form_validate(post, partner_id)
            values.update({'error': error, 'error_message': error_message})
            values.update(post)
            if not error:
                values = {key: post[key] for key in self.MANDATORY_PARTNER_FIELDS}
                values.update({key: post[key] for key in self.OPTIONAL_PARTNER_FIELDS if key in post})
                values.update({'is_published': True})
                many_2_one_fields = ['birth_state_id', 'kanha_location_id', 'country_id']
                if(post.get('application_type') == 'Transfer Application'):
                    values.update({key: post[key] for key in self.VOTER_INFO_FIELDS if key in post})
                    many_2_one_fields.append('state_id')
                for field in set(many_2_one_fields) & set(values.keys()):
                    try:
                        values[field] = int(values[field])
                    except:
                        values[field] = False
                for field in set(['adhar_card', 'adhar_card_back_side', 'passport_photo', 'age_proof', 'address_proof', 'age_declaration_form']) & set(values.keys()):
                        file = post.get(field)
                        file_content = file.read()
                        # Restricts empty file upload when update the records
                        if(file_content):
                            values[field] = base64.encodebytes(file_content)
                        else:
                            values.pop(field)
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
                    partner = partner_created
                if redirect:
                    return request.redirect(redirect)
                form_values.update({
                    'error': {},
                    'error_message': [],
                    'partner': partner,
                })
                values.update(form_values)
                values.update({'success_message': 'Your information has been submitted successfully!'})
                response = request.render("kanha_census.kanha_portal_form", values)
                return response
        form_values.update({'partner': partner})
        values.update(form_values)
        response = request.render("kanha_census.kanha_portal_form", values)
        response.headers['X-Frame-Options'] = 'DENY'
        return response
    
    @http.route(['/add_partner'], type='http', auth="public", website=True)
    def add_family_members(self, redirect=None, **post):
        values = self._prepare_portal_layout_values()
        # Fetch the state of India
        country = request.env['res.country'].sudo().search([('code', '=', 'IN')])
        states = request.env['res.country.state'].sudo().search([('country_id', '=', country.id)])
        # Fetch the record who doesnt have any child records
        kanha_location_parents_ids = request.env['kanha.location'].sudo().search([]).parent_id.ids
        kanha_locations_nth_child = request.env['kanha.location'].sudo().search([('id', 'not in', kanha_location_parents_ids)])
        current_partner = request.env.user.partner_id

        values.update({
            'partner': None,
            'states': states,
            'redirect': redirect,
            'page_name': 'family',
            'kanha_locations': kanha_locations_nth_child,
            'surname': current_partner.surname,
            'relative_surname': current_partner.surname,
            'relative_name': current_partner.name,
            'country_id': country,
            'error': {},
            'error_message': []

        })
        response = request.render("kanha_census.kanha_portal_form", values)
        return response
