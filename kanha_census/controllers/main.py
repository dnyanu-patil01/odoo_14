# -*- coding: utf-8 -*-
import base64
import json

import re
from odoo import http, tools, _
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager, get_records_pager


class CustomerPortal(CustomerPortal):

   
    missing_fields = dict()
    form_fields = {
        "adhar_card_filename": 'Adhar Card File Front',
        "adhar_card_back_side_filename": "Adhar Card File Back",
        "passport_photo_filename": "Passport Photo",
        "age_proof_filename": "Age Proof",
        "address_proof_filename": "Kanha Address Proof",
        }
    
    
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
        return request.render("kanha_census.portal_my_family_members", values)

    def kanha_portal_form_validate(self, data, partner_id):
        error = dict()
        error_message = []
        self.missing_fields = dict()
        for field_name, field_value in data.items():
            # If the value of the field if a file
            if hasattr(field_value, 'filename'):
                # Undo file upload field name indexing
                data.pop(field_name)
                field_name = field_name.split('[', 1)[0]
                data[field_name] = field_value

        # email validation
        if data.get('email') and not tools.single_email_re.match(data.get('email')):
            error["email"] = _('Invalid Email! Please enter a valid email address.')
            error_message.append(_('Invalid Email! Please enter a valid email address.'))
        # Pan card validation
        if data.get('pan_card_number'):
            is_valid = self.is_valid_pan_number(data.get('pan_card_number'))
            if not is_valid:
                error["pan_card_number"] = _('Invalid Pan Number!')
                error_message.append(_('Invalid Pan Number!'))
        # Aadhar card validation
        if data.get('aadhaar_card_number'):
            is_valid = self.is_valid_aadhaar_number(data.get('aadhaar_card_number'))
            if not is_valid:
                error["aadhaar_card_number"] = _('Invalid Aadhaar Number!')
                error_message.append(_('Invalid Aadhaar Number!')) 
        # Relative Aadhar card validation
        if data.get('relative_aadhaar_card_number'):
            relative_aadhaar_card_number = data.get('relative_aadhaar_card_number')
            is_valid = self.is_valid_aadhaar_number(relative_aadhaar_card_number)
            if not is_valid:
                error["aadhar_card_number"] = _('Invalid Aadhar Number!')
                error_message.append(_('Invalid Aadhar Number!'))               
            # Adhar card exsist
            ResPartner = request.env['res.partner']
            is_adhar_exsist = ResPartner.search([('aadhaar_card_number', '=', relative_aadhaar_card_number)])
            if(not is_adhar_exsist): 
                error["relative_aadhaar_card_number"] = _('Given Relative Aadhar Number does not exist!')
                error_message.append(_('Given Relative Aadhar Number does not exist!'))              
        
        # Mobile number validation
        if data.get('mobile'):
            is_valid = self.is_valid_mobile_number(data.get('mobile'))
            if not is_valid:
                error["mobile"] = _('Invalid Mobile Number!')
                error_message.append(_('Invalid Mobile Number!')) 
        # error message for empty required fields
        if(self.missing_fields):
            error_message.append(" Please fill these required field(s): '%s'" % ','.join(self.missing_fields.values()))
                # Undo file upload field name indexing
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

    @http.route('/website_form/<int:partner_id>/<string:model_name>', type='http', auth="public",methods=['POST'], website=True)
    def save_portal_form(self, partner_id=None, model_name=None, access_token=None, **post):
        request.params.pop('csrf_token', None)
        # values = self._prepare_portal_layout_values()
        values = {}
        values.update({
            'error': {},
            'error_message': [],
        })
        country = request.env['res.country'].sudo().search([])
        states = request.env['res.country.state'].sudo().search([])
        # Fetch the record who doesnt have any child records
        kanha_location_parent_ids = request.env['kanha.location'].sudo().search([]).parent_id.ids
        kanha_locations_nth_child = request.env['kanha.location'].sudo().search([('id', 'not in', kanha_location_parent_ids)])
        form_values = {}
        form_values.update({
            'states': states,
            'page_name': 'family',
            'kanha_locations': kanha_locations_nth_child,
            'zipcode': post.get('zip'),
            'birth_countries': country,
            'countries': country
        })
        ResPartner = request.env['res.partner']
        partner = ResPartner.sudo().search([('id', '=', partner_id)])
        if post and request.httprequest.method == 'POST':
            error, error_message = self.kanha_portal_form_validate(post, partner_id)
            values.update({'error': error, 'error_message': error_message})
            values.update(post)
            # Checks Aadhar Number is already exist for new record
            if(not partner):
                ResPartner = request.env['res.partner']
                is_adhar_no_exsist = ResPartner.search([('aadhaar_card_number', '=', post.get('aadhaar_card_number'))])
                if(is_adhar_no_exsist): 
                    error["aadhaar_card_number"] = 'error'
                    error_message.append(_('Aadhar Number is already exist!'))
            if not error:
                values = {}
                values.update(post)
                values.update({'is_published': True})
                many_2_one_fields = ['birth_state_id', 'kanha_location_id', 'country_id']
                if(post.get('change_voter_id_address') == 'Yes'):
                    # values.update({key: post[key] for key in self.VOTER_INFO_FIELDS if key in post})
                    many_2_one_fields.append('state_id')
                for field in set(many_2_one_fields) & set(values.keys()):
                    try:
                        values[field] = int(values[field])
                    except:
                        values[field] = False
                # Insert File input value
                for field in set(['adhar_card',
                                  'adhar_card_back_side',
                                  'passport_photo',
                                  'age_proof',
                                  'address_proof',
                                  'voter_id_file',
                                  'declaration_form',
                                  'kanha_voter_id_image']) & set(values.keys()):
                        file = post.get(field)
                        if(file):
                            file_content = file.read()
                            # Restricts empty file upload when update the records
                            if(file_content):
                                values[field] = base64.encodebytes(file_content)
                            else:
                                values.pop(field)
                # Prepare Vehicle Details 
                vehicle_details_vals = []
                if(values['vehicle_new_lines']):
                        vehicle_new_lines = json.loads(values['vehicle_new_lines'])
                        for vehicle_new_rec in vehicle_new_lines:
                            vehicle_details_vals.append([0, 0, vehicle_new_rec])
                        values.pop('vehicle_new_lines')
                else:
                    values.pop('vehicle_new_lines')
                
                if partner:
                    vehicle_details_ids = json.loads(post.get('vehicle_details_ids'))
                    if(vehicle_details_ids):
                        partner_vehicle_ids = partner.vehicle_details_ids.ids
                        partner_vehicle_ids = list(map(str, partner_vehicle_ids))
                        deleted_vehicle_ids = list(set(partner_vehicle_ids).symmetric_difference(set(vehicle_details_ids.keys())))
                        for deleted_id in deleted_vehicle_ids:
                            vehicle_details_vals.append([2, int(deleted_id)])
                            partner_vehicle_ids.remove(deleted_id)
                        for partner_vehicle in partner_vehicle_ids:
                            vehicle_vals = vehicle_details_ids.get(str(partner_vehicle))
                            vehicle_details_vals.append([1, partner_vehicle, vehicle_vals])
                    values['vehicle_details_ids'] = vehicle_details_vals
                    if not (values.get('application_type')):
                        values['application_type'] = ''
                    partner.sudo().write(values)
                else:
                    values['vehicle_details_ids'] = vehicle_details_vals
                    partner_created = ResPartner.sudo().create(values)
                    if(post.get('relative_aadhaar_card_number')):
                        relative_aadhaar_card_number = post.get('relative_aadhaar_card_number')
                        relative_partner = ResPartner.search([('aadhaar_card_number', '=', relative_aadhaar_card_number)])
                        if(relative_partner):
                            partner_created.sudo().write({'family_members_ids': [(4, relative_partner.id)]})
                            relative_partner.sudo().write({'family_members_ids': [(4, partner_created.id)]})
                    partner = partner_created
                values = {}
                values.update({'id': partner.id})   
                return json.dumps(values)
        return json.dumps({
            'id': False,
            'error': error,
            'error_message': error_message,
            'error_fields': error,
            })

    @http.route('/website_form_family/<int:partner_id>/<string:model_name>', type='http', auth="public", website=True)
    def family_portal_form(self, partner_id=None, model_name=None, access_token=None, **post):
        values = self._prepare_portal_layout_values()
        ResPartner = request.env['res.partner']
        partner = ResPartner.sudo().search([('id', '=', partner_id)])
        country = request.env['res.country'].sudo().search([])
        states = request.env['res.country.state'].sudo().search([])
        # Fetch the record who doesnt have any child records
        kanha_location_parent_ids = request.env['kanha.location'].sudo().search([]).parent_id.ids
        kanha_locations_nth_child = request.env['kanha.location'].sudo().search([('id', 'not in', kanha_location_parent_ids)])
        is_relation_required = False
        current_partner = request.env.user.partner_id
        if current_partner.id != partner_id:
            is_relation_required = True
        is_kanha_voter_info_required = True
        if partner.citizenship == 'Overseas':
            is_kanha_voter_info_required = False
        values.update({
            'states': states,
            'page_name': 'family',
            'kanha_locations': kanha_locations_nth_child,
            'zipcode': post.get('zip'),
            'birth_countries': country,
            'countries': country,
            'partner': partner,
            'error': {},
            'error_message': [],
            'is_relation_required': is_relation_required,
            'is_kanha_voter_info_required': is_kanha_voter_info_required
        })
        response = request.render("kanha_census.kanha_family_portal_form", values)
        response.headers['X-Frame-Options'] = 'DENY'
        return response
    
    @http.route(['/add_family_members'], type='http', auth="public", website=True)
    def add_family_members(self, redirect=None, **post):
        values = self._prepare_portal_layout_values()
        countries = request.env['res.country'].sudo().search([])
        states = request.env['res.country.state'].sudo().search([])
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
            'countries': countries,
            'birth_countries': countries,
            'error': {},
            'error_message': [],
            # 'is_relation_required': True
        })
        response = request.render("kanha_census.kanha_family_portal_form", values)
        return response

    @http.route(['/vehicle_details_form'], type='http', auth="public", methods=['POST'], website=True)
    def get_vehicle_details_form(self, **post):
        post.update({'error': {}, 'error_message': []})
        return request.env['ir.ui.view']._render_template("kanha_census.vehicle_details_model_form", post)
