# -*- coding: utf-8 -*-
import base64
import json
import re
from odoo import http, tools, _, fields
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager, get_records_pager
from odoo.addons.website.controllers.main import Website
import zipfile
import os
from io import BytesIO
import shutil
import tempfile
from datetime import datetime
from odoo.exceptions import MissingError
import ast


class Website(Website):

    @http.route(auth="user")
    def index(self, **kw):
        return super(Website, self).index(**kw)


class CustomerPortal(CustomerPortal):
    
    KANHA_VOTER_ID_FIELDS = ["birth_state_id",
                             "birth_country_id",
                             "birth_district",
                             "birth_town",
                             "change_voter_id_address",
                             "already_have_kanha_voter_id",
                             "kanha_voter_id_number",
                             "kanha_voter_id_image",
                             "kanha_voter_id_image_filename",
                             "kanha_voter_id_back_image",
                             "kanha_voter_id_back_image_filename",
                             "need_new_kanha_voter_id",
                             "application_type",
                             "declaration_form",
                             "declaration_form_filename",
                             "relation_type",
                             "relative_aadhaar_card_number",
                             "relative_name",
                             "relative_surname",
                             "application_reference_no"
                             ]
    EXISTING_VOTER_ID_FIELDS = ["country_id",
                                "state_id",
                                "assembly_constituency",
                                "house_number",
                                "locality",
                                "town",
                                "post_office",
                                "zip"]

    @http.route(['/family', '/family/page/<int:page>'], type='http', auth="user", website=True)
    def partner_list(self, page=1, search='', **kw):
        values = {}
        ResPartner = request.env['res.partner']
        
        domain = ['|',('create_uid','=',request.env.user.id),('email','=',request.env.user.email)]
        
        if request.env.user.has_group('base.group_user'):
            domain = ['|', ('type', '!=', 'private'), ('type', '=', False),('kanha_location_id', 'in', request.env.user.allowed_locations_ids.ids)]
        if request.env.user.has_group('base.group_system'):
            domain = []

        if search:
            subdomains = [('name', 'ilike', search)]
            domain = domain+subdomains

        partner_count = ResPartner.sudo().search_count(domain)
        
        url_args = {}
        if search:
            url_args['search'] = search
        
        pager = portal_pager(
            url="/family",
            url_args=url_args,
            total=partner_count,
            page=page,
            step=self._items_per_page
        )
        
        partners = ResPartner.sudo().search(domain, limit=self._items_per_page, offset=pager['offset'])
        request.session['partner_history'] = partners.ids[:100]
        
        values.update({
            'partners': partners,
            'page_name': 'family',
            'pager': pager,
            'default_url': '/family',
            'search': search
        })
        return request.render("kanha_census.portal_my_family_members", values)

    def kanha_portal_form_validate(self, data, partner_id):
        error = dict()
        error_message = []

        if data.get('email') and not tools.single_email_re.match(data.get('email')):
            error["email"] = _('Invalid Email! Please enter a valid email address.')
            error_message.append(_('Invalid Email! Please enter a valid email address.'))
        
        if data.get('govt_id_proof'):
            govt_id_proof = data.get('govt_id_proof')
            if not govt_id_proof or len(govt_id_proof.strip()) == 0:
                error["govt_id_proof"] = _('Government ID Proof is required!')
                error_message.append(_('Government ID Proof is required!'))
        
        if data.get('pan_card_number'):
            is_valid = self.is_valid_pan_number(data.get('pan_card_number'))
            if not is_valid:
                error["pan_card_number"] = _('Invalid Pan Number!')
                error_message.append(_('Invalid Pan Number!'))
        
        if data.get('aadhaar_card_number'):
            is_valid = self.is_valid_aadhaar_number(data.get('aadhaar_card_number'))
            if not is_valid:
                error["aadhaar_card_number"] = _('Invalid Aadhaar Number!')
                error_message.append(_('Invalid Aadhaar Number!')) 
            
            ResPartner = request.env['res.partner']
            partner = ResPartner.sudo().search([('id', '=', partner_id)])    
            if(not partner):
                is_adhar_no_exsist = ResPartner.sudo().search([('aadhaar_card_number', '=', data.get('aadhaar_card_number'))])
                if(is_adhar_no_exsist): 
                    error["aadhaar_card_number"] = 'error'
                    error_message.append(_('Aadhar Number is already exist!'))    
        
        if data.get('relative_aadhaar_card_number'):
            relative_aadhaar_card_number = data.get('relative_aadhaar_card_number')
            is_valid = self.is_valid_aadhaar_number(relative_aadhaar_card_number)
            if not is_valid:
                error["aadhar_card_number"] = _('Invalid Relative Aadhar Number!')
                error_message.append(_('Invalid Relative Aadhar Number!'))               

        if data.get('mobile'):
            is_valid = self.is_valid_mobile_number(data.get('mobile'))
            if not is_valid:
                error["mobile"] = _('Invalid Mobile Number!')
                error_message.append(_('Invalid Mobile Number!')) 
        
        if data.get('emergency_contact'):
            is_valid = self.is_valid_mobile_number(data.get('emergency_contact'))
            if not is_valid:
                error["emergency_contact"] = _('Invalid Emergency Contact Number!')
                error_message.append(_('Invalid Emergency Contact Number!'))
                
        if data.get('property_owner_phone'):
            is_valid = self.is_valid_mobile_number(data.get('property_owner_phone'))
            if not is_valid:
                error["property_owner_phone"] = _('Invalid Property Owner Phone Number!')
                error_message.append(_('Invalid Property Owner Phone Number!'))
        
        if data.get('year_of_birth'):
            is_valid = self.is_valid_year(data.get('year_of_birth'))
            if not is_valid:
                error["year_of_birth"] = _('You cannot enter a Year in the future for Year of Birth !')
                error_message.append(_('You cannot enter a Year in the future for Year of Birth!'))

        if data.get("resident_of_kanha_from_date"):
            is_valid = self.is_valid_date(data.get('resident_of_kanha_from_date'))
            if not is_valid:
                error["resident_of_kanha_from_date"] = _('You cannot enter a date in the future for Resident of kanha from date!')
                error_message.append(_('You cannot enter a date in the future for Resident of kanha from date!'))      
        
        if data.get("visa_start_date"):
            is_valid = self.is_valid_date(data.get('visa_start_date'))
            if not is_valid:
                error["visa_start_date"] = _('You cannot enter a date in the future for Visa Start date!')
                error_message.append(_('You cannot enter a date in the future for Visa Start date!'))      

        if data.get("visa_end_date"):
            is_valid = self.is_valid_future_date(data.get('visa_end_date'))
            if not is_valid:
                error["visa_end_date"] = _('You cannot enter a date in the future for Visa End date!')
                error_message.append(_('You cannot enter a date in the future for Visa End date!'))      

        if data.get("vehicle_new_lines"):
            try:
                old_vehicles = []
                if data.get("vehicle_details_ids"):
                    vehicle_details_ids = json.loads(data.get("vehicle_details_ids"))
                    old_vehicles = [v for k, v in vehicle_details_ids.items()]
                
                new_vehicles = json.loads(data.get("vehicle_new_lines"))
                error_encountered = False
                
                for vehicle in new_vehicles:
                    fasttag_number = vehicle.get('fasttag_rfid_no')
                    if(fasttag_number):
                        is_valid = self.is_valid_fasttag_rfid(fasttag_number)
                        if not is_valid:
                            error_encountered = True  
                            
                for vehicle in old_vehicles:
                    fasttag_number = vehicle.get('fasttag_rfid_no')
                    if(fasttag_number):
                        is_valid = self.is_valid_fasttag_rfid(fasttag_number)
                        if not is_valid:
                            error_encountered = True
                            
                if error_encountered:
                    error["fasttag_rfid_no"] = _('Please enter a valid 16-digit FastTag RFID starting with 6.')
                    error_message.append(_('Please enter a valid 16-digit FastTag RFID starting with 6.'))   
            except (ValueError, TypeError) as e:
                error["vehicle_new_lines"] = _('Invalid vehicle data format.')
                error_message.append(_('Invalid vehicle data format.'))

        for field in ['adhar_card', 'adhar_card_back_side', 'passport_photo', 'address_proof', 'passport_front_image', 'passport_back_image', 'indian_visa']:
            file_data = data.get(field)
            if file_data and hasattr(file_data, 'filename'):
                file_content = file_data.read()
                file_size_kb = len(file_content) / 1024
                
                if file_size_kb > 500:
                    error[field] = _('File size cannot exceed 500KB')
                    error_message.append(_('File size cannot exceed 500KB for %s') % field)
                
                filename = file_data.filename.lower()
                if not (filename.endswith('.jpg') or filename.endswith('.jpeg')):
                    error[field] = _('Only JPG format is allowed')
                    error_message.append(_('Only JPG format is allowed for %s') % field)
                
                file_data.seek(0)

        family_member_files = ['govt_id_proof', 'passport_photo_file', 'address_proof_file']
        for idx in range(10):
            for file_field in family_member_files:
                field_name = f'family_member_{file_field}_{idx}'
                file_data = data.get(field_name)
                if file_data and hasattr(file_data, 'filename'):
                    file_content = file_data.read()
                    file_size_kb = len(file_content) / 1024
                    
                    if file_size_kb > 500:
                        error[field_name] = _('File size cannot exceed 500KB')
                        error_message.append(_('File size cannot exceed 500KB for family member document'))
                    
                    filename = file_data.filename.lower()
                    if not (filename.endswith('.jpg') or filename.endswith('.jpeg')):
                        error[field_name] = _('Only JPG format is allowed')
                        error_message.append(_('Only JPG format is allowed for family member document'))
                    
                    file_data.seek(0)
        
        return error, error_message

    def is_valid_pan_number(self, pan_number):
        regex = "[A-Z]{5}[0-9]{4}[A-Z]{1}"
        p = re.compile(regex)
        if(re.search(p, pan_number) and len(pan_number) == 10):
            return True
        else:
            return False
        
    def is_valid_aadhaar_number(self, emp_aadhaar):
        regex = ("^[2-9]{1}[0-9]{3}\\" + "s[0-9]{4}\\s[0-9]{4}$")
        p = re.compile(regex)
        if(re.search(p, emp_aadhaar)) and len(emp_aadhaar) == 14:
            return True
        else:
            return False
        
    def is_valid_mobile_number(self, mobile_number):
        pattern = re.compile("(0|91)?[6-9][0-9]{9}")
        if pattern.match(mobile_number) and len(mobile_number) == 10:
            return True
        else:
            return False

    def is_valid_fasttag_rfid(self, fastag_rfid):
        try:
            val = str(fastag_rfid)
        except ValueError:
            return False

        pattern = r'^6\d{15}$'
        if re.match(pattern, val):
            return True
        else:
            return False  
        
    def is_valid_date(self, date_val):
        try:
            date_val = datetime.strptime(date_val, "%Y-%m-%d")
            present = datetime.now()
            if(date_val.date() <= present.date()):
                return True
            else:
                return False
        except ValueError:
            return False
    
    def is_valid_year(self, year_val):
        try:
            year_val = int(year_val)
            current_year = datetime.now().year
            if year_val <= current_year:
                return True
            else:
                return False
        except ValueError:
            return False

    def is_valid_future_date(self, date_val):
        try:
            date_val = datetime.strptime(date_val, "%Y-%m-%d")
            present = datetime.now()
            if(date_val.date() >= present.date()):
                return True
            else:
                return False
        except ValueError:
            return False

    @http.route('/website_form/<int:partner_id>/<string:model_name>', type='http', auth="user", methods=['POST'], website=True, csrf=False)
    def save_portal_form(self, partner_id=None, model_name=None, access_token=None, **post):
        try:
            request.params.pop('csrf_token', None)
            is_submit = post.get("is_submit")
            post.pop("is_submit", None)
            
            ResPartner = request.env['res.partner']
            partner = ResPartner.sudo().search([('id', '=', partner_id)]) if partner_id else False
            
            if post and request.httprequest.method == 'POST':
                error, error_message = self.kanha_portal_form_validate(post, partner_id)
                
                post['state'] = 'saved_not_submitted'
                post['application_status'] = 'draft'
                if(is_submit == 'true'):
                    post['state'] = 'submitted'
                    post['application_status'] = 'to_approve'
                    
                if not error:
                    post_vals = post.copy()
                    for field_name, field_value in post_vals.items():
                        if hasattr(field_value, 'filename'):
                            post.pop(field_name)
                            field_name = field_name.split('[', 1)[0]
                            post[field_name] = field_value
                            
                    values = {}
                    values.update(post)
                    values.update({'is_published': True})

                    field_mapping = {
                        'members_staying': 'members_count',
                        'preceptor': 'is_preceptor',
                        'abhyasi_id': 'abhyasi_id'
                    }

                    for web_field, backend_field in field_mapping.items():
                        if web_field in values:
                            values[backend_field] = values.pop(web_field)

                    if values.get('has_voter_id_in_kanha'):
                        if values['has_voter_id_in_kanha'] == 'Yes':
                            values['has_voter_id_in_kanha'] = True
                        else:
                            values['has_voter_id_in_kanha'] = False
                    
                    if values.get('do_you_need_voter_id_in_kanha'):
                        if values['do_you_need_voter_id_in_kanha'] == 'Yes':
                            values['do_you_need_voter_id_in_kanha'] = True
                        else:
                            values['do_you_need_voter_id_in_kanha'] = False

                    if(values.get('change_voter_id_address') != 'Yes'):
                        self.remove_invisible_fields_value(values, self.EXISTING_VOTER_ID_FIELDS)
                    
                    if(values.get('citizenship') == 'Overseas'):
                        self.remove_invisible_fields_value(values, self.KANHA_VOTER_ID_FIELDS)
                        if values.get('birth_country_name'):
                            values['birth_country_name'] = values.get('birth_country_name')
                    else:
                        self.remove_invisible_fields_value(values)

                    overseas_fields = [
                        'birth_country_name', 'property_owner_name', 'property_owner_email', 
                        'property_owner_phone', 'residence_type', 'passport_number', 
                        'full_name_passport', 'emergency_contact'
                    ]
                    
                    for file_field in ['adhar_card_back_side', 'adhar_card', 'kanha_voter_id_image', 
                                     'kanha_voter_id_back_image', 'age_proof', 'address_proof', 
                                     'passport_photo', 'passport_front_image', 'passport_back_image', 'indian_visa']:
                        if not values.get(f'{file_field}_filename'):
                            values[file_field] = ''
                    
                    for date_field in ["resident_of_kanha_from_date", "visa_start_date", "visa_end_date"]:
                        if values.get(date_field) == '':
                            values[date_field] = False
                    
                    if(values.get("year_of_birth")):
                        try:
                            values['year_of_birth'] = int(values['year_of_birth'])
                        except:
                            values['year_of_birth'] = False
                           
                    many_2_one_fields = ['birth_state_id', 'kanha_location_id', 'country_id', 'state_id',
                                       'kanha_house_number_id', 'work_profile_id','department_id','birth_country_id']
                    for field in set(many_2_one_fields) & set(values.keys()):
                        try:
                            values[field] = int(values[field]) if values[field] else False
                        except:
                            values[field] = False

                    for field in set(['adhar_card', 'adhar_card_back_side', 'passport_photo', 'indian_visa',
                                    'passport_front_image', 'passport_back_image', 'age_proof', 'address_proof',
                                    'declaration_form', 'kanha_voter_id_back_image', 'kanha_voter_id_image']) & set(values.keys()):
                        file = post.get(field)
                        if(file):
                            file_content = file.read()
                            if(file_content):
                                values[field] = base64.encodebytes(file_content)
                            else:
                                values.pop(field, None)

                    vehicle_details_vals = []
                    try:
                        vehicle_new_lines = json.loads(values.get('vehicle_new_lines', '[]'))
                        if(vehicle_new_lines):
                            for vehicle_new_rec in vehicle_new_lines:
                                vehicle_details_vals.append([0, 0, vehicle_new_rec])
                        values.pop('vehicle_new_lines', None)
                        values['vehicle_details_ids'] = vehicle_details_vals
                    except (ValueError, TypeError):
                        values.pop('vehicle_new_lines', None)

                    family_member_vals = []
                    family_member_count = 0
                    
                    while True:
                        name_field = f'family_member_name_{family_member_count}'
                        relation_field = f'family_member_relation_{family_member_count}'
                        blood_group_field = f'family_member_blood_group_{family_member_count}'
                        govt_id_field = f'family_member_govt_id_proof_{family_member_count}'
                        passport_photo_field = f'family_member_passport_photo_file_{family_member_count}'
                        address_proof_field = f'family_member_address_proof_file_{family_member_count}'
                        
                        if name_field not in values and name_field not in post:
                            break
                        
                        member_name = values.get(name_field, '').strip() or post.get(name_field, '').strip()
                        member_relation = values.get(relation_field, '').strip() or post.get(relation_field, '').strip()
                        member_blood_group = values.get(blood_group_field, '').strip() or post.get(blood_group_field, '').strip()
                        
                        if member_name and member_relation:
                            member_vals = {
                                'name': member_name,
                                'relation': member_relation,
                                'blood_group': member_blood_group,
                                'sequence': family_member_count,
                            }
                            
                            for file_field, db_field in [
                                (govt_id_field, 'govt_id_proof'),
                                (passport_photo_field, 'passport_photo'), 
                                (address_proof_field, 'address_proof')
                            ]:
                                file = post.get(file_field)
                                if file and hasattr(file, 'read'):
                                    file_content = file.read()
                                    if file_content:
                                        member_vals[db_field] = base64.encodebytes(file_content)
                                        if hasattr(file, 'filename'):
                                            member_vals[f'{db_field}_filename'] = file.filename
                            
                            family_member_vals.append([0, 0, member_vals])
                        
                        for field in [name_field, relation_field, blood_group_field, govt_id_field, 
                                    passport_photo_field, address_proof_field]:
                            values.pop(field, None)
                        family_member_count += 1

                    if family_member_vals:
                        values['family_member_ids'] = family_member_vals

                    relative_partner = False
                    kanha_house_number_id = post.get('kanha_house_number_id')
                    kanha_location_id = post.get('kanha_location_id')
                    if(kanha_house_number_id):
                        try:
                            relative_partner = ResPartner.sudo().search([
                                ('kanha_house_number_id', '=', int(kanha_house_number_id)),
                                ('kanha_location_id','=', int(kanha_location_id))
                            ])
                        except ValueError:
                            pass

                    if partner:
                        try:
                            vehicle_details_ids = json.loads(post.get('vehicle_details_ids', '{}'))
                            partner_vehicle_ids = partner.vehicle_details_ids.ids
                            if(vehicle_details_ids):
                                partner_vehicle_ids = list(map(str, partner_vehicle_ids))
                                deleted_vehicle_ids = list(set(partner_vehicle_ids).symmetric_difference(set(vehicle_details_ids.keys())))
                                for deleted_id in deleted_vehicle_ids:
                                    vehicle_details_vals.append([2, int(deleted_id)])
                                    if deleted_id in partner_vehicle_ids:
                                        partner_vehicle_ids.remove(deleted_id)
                                for partner_vehicle in partner_vehicle_ids:
                                    vehicle_vals = vehicle_details_ids.get(str(partner_vehicle))
                                    if vehicle_vals:
                                        vehicle_details_vals.append([1, int(partner_vehicle), vehicle_vals])
                            elif(partner_vehicle_ids and not vehicle_details_ids):
                                for partner_vehicle in partner_vehicle_ids:
                                    vehicle_details_vals.append([2, partner_vehicle])
                            
                            values['vehicle_details_ids'] = vehicle_details_vals
                        except (ValueError, TypeError):
                            pass

                        if partner.family_member_ids:
                            values['family_member_ids'] = [(5,)] + family_member_vals

                        if(kanha_house_number_id and int(kanha_house_number_id) != partner.kanha_house_number_id.id):
                            partner.write({'family_members_ids': [(5,)]})
                            if(relative_partner):
                                partner.sudo().write({'family_members_ids': [(6, 0, relative_partner.ids)]})
                                relative_partner.sudo().write({'family_members_ids': [(4, partner.id)]})

                        rfid_card_no = int(values.get("rfid_card_no", 0)) if values.get("rfid_card_no") else 0
                        if(rfid_card_no != partner.rfid_card_no):
                            values['state'] = partner.state
                            values['application_status'] = partner.application_status

                        partner.sudo().write(values)  
                        if(partner.application_status == 'to_approve'):
                            partner.send_application_status_mail(partner.application_status)                               
                    else:
                        partner = ResPartner.sudo().create(values)
                        if(partner.application_status == 'to_approve'):
                            partner.send_application_status_mail(partner.application_status)
                        if(relative_partner):
                            partner.sudo().write({'family_members_ids': [(6, 0, relative_partner.ids)]})
                            relative_partner.sudo().write({'family_members_ids': [(4, partner.id)]})    
                    
                    return request.make_response(
                        json.dumps({'id': partner.id, 'success': True}),
                        headers={'Content-Type': 'application/json'}
                    )

        except Exception as e:
            error = {'general': str(e)}
            error_message = [str(e)]

        return request.make_response(
            json.dumps({
                'id': False,
                'success': False,
                'error': error,
                'error_message': error_message,
                'error_fields': error,
            }),
            headers={'Content-Type': 'application/json'}
        )

    @http.route('/website_form_family/<int:partner_id>/<string:model_name>', type='http', auth="user", website=True)
    def family_portal_form(self, partner_id=None, model_name=None, access_token=None, **post):
        ResPartner = request.env['res.partner']
        partner = ResPartner.sudo().search([('id', '=', partner_id)])
        if partner.email == request.env.user.email or partner.create_uid == request.env.user or request.env.user.has_group('base.group_user'):
            values = self.get_default_values_for_kanha(partner_id)
            values.update({
                'zipcode': post.get('zip'),
                'partner': partner,
            })
            if partner.citizenship == 'Indian':
                response = request.render("kanha_census.kanha_family_portal_form_indian", values)
            elif partner.citizenship == 'Overseas':
                response = request.render("kanha_census.kanha_family_portal_form_overseas", values)
            else:
                response = request.render("kanha_census.selection_form_view", values)
            response.headers['X-Frame-Options'] = 'DENY'
            return response
        else:
            print("You cannot access this record !")
    
    @http.route(['/add_family_members_indian/<int:partner_id>'], type='http', auth="public", website=True)
    def add_family_members_indian(self, redirect=None, partner_id=None, model_name=None, **post):
        values = self.get_default_values_for_kanha()
        current_partner = request.env.user.partner_id
        ResPartner = request.env['res.partner']
        partner = ResPartner.sudo().search([('id', '=', partner_id)])
        values.update({
            'partner': partner,
            'surname': current_partner.surname,
            'kanha_location_id': current_partner.kanha_location_id.id if current_partner.kanha_location_id else None,
            'kanha_house_number_id':  current_partner.kanha_house_number_id.id if current_partner.kanha_house_number_id else None,
        })
        response = request.render("kanha_census.kanha_family_portal_form_indian", values)
        return response
    
    @http.route(['/add_family_members_overseas/<int:partner_id>'], type='http', auth="public", website=True)
    def add_family_members_overseas(self, redirect=None, partner_id=None, model_name=None,**post):
        values = self.get_default_values_for_kanha()
        current_partner = request.env.user.partner_id
        ResPartner = request.env['res.partner']
        partner = ResPartner.sudo().search([('id', '=', partner_id)])
        values.update({
            'partner': partner,
            'surname': current_partner.surname,
            'is_overseas': True,
            'kanha_location_id': current_partner.kanha_location_id.id if current_partner.kanha_location_id else None,
            'kanha_house_number_id':  current_partner.kanha_house_number_id.id if current_partner.kanha_house_number_id else None,
        })
        response = request.render("kanha_census.kanha_family_portal_form_overseas", values)
        return response
    
    @http.route(['/select_citizen'], type='http', auth="public", website=True)
    def select_citizen(self, redirect=None, **post):
        values = self.get_default_values_for_kanha()
        current_partner = request.env.user.partner_id
        values.update({
            'partner': None,
            'surname': current_partner.surname,
            'relative_surname': current_partner.surname,
            'relative_name': current_partner.name,
        })
        response = request.render("kanha_census.selection_form_view", values)
        return response
    
    def get_default_values_for_kanha(self, partner_id=None):
        values = {}
        country = request.env['res.country'].sudo().search([])
        country_india = request.env['res.country'].sudo().browse(104)
        states = request.env['res.country.state'].sudo().search([])
        kanha_location_parent_ids = request.env['kanha.location'].search([]).parent_id.ids
        kanha_locations_nth_child = request.env['kanha.location'].search([('id', 'not in', kanha_location_parent_ids)])
        kanha_house_numbers = request.env['kanha.house.number'].search([])
        work_profiles = request.env['work.profile'].search([])
        work_department = request.env['work.department'].search([])

        values.update({
            'states': states,
            'page_name': 'family',
            'kanha_locations': kanha_locations_nth_child,
            'kanha_house_numbers':kanha_house_numbers,
            'work_profiles': work_profiles,
            'work_department':work_department,
            'birth_countries': country,
            'countries': country_india,
            'error': {},
            'error_message': [],
            })
        return values
    
    @http.route(['/vehicle_details_form'], type='http', auth="user", methods=['POST'], website=True)
    def get_vehicle_details_form(self, **post):
        return request.env['ir.ui.view']._render_template("kanha_census.vehicle_details_model_form", post)

    def remove_invisible_fields_value(self, values, fields=None):
        if(fields):
            many2one_fields = ['country_id', 'birth_country_id', 'state_id', 'birth_state_id', 'work_profile_id','department_id']
            for field in fields:
                if (field in many2one_fields):
                    values[field] = None
                else:
                    values[field] = ''
        else:
            if(values.get('already_have_kanha_voter_id') == 'Yes'):
                values['need_new_kanha_voter_id'] = ''
            if(values.get('already_have_kanha_voter_id') == 'No'):
                values['kanha_voter_id_number'] = ''
                values['kanha_voter_id_image'] = ''
                values['kanha_voter_id_image_filename'] = '' 
                values['kanha_voter_id_back_image'] = ''
                values['kanha_voter_id_back_image_filename'] = ''
            if((values.get('need_new_kanha_voter_id') != 'Yes') and (values.get('change_voter_id_address') != 'Yes')):
                values['application_type'] = ''   
                values['declaration_form'] = ''   
                values['declaration_form_filename'] = ''   
            if(values.get('application_type') == 'Transfer Application'): 
                values['declaration_form'] = ''   
                values['declaration_form_filename'] = '' 

    def zip(self, path, ziph):
        for root, dirs, files in os.walk(path):
            for file in files:
                ziph.write(os.path.join(root, file),
                           os.path.relpath(os.path.join(root, file),
                                           os.path.join(path, '..')))    

    @http.route("/web/attachment/download_zip", type="http", auth="user")
    def download_zip(self, partner_ids=None):
        root_temp_dir_path = os.path.join(tempfile.gettempdir(), 'Documents')
        if os.path.exists(root_temp_dir_path):
            shutil.rmtree(root_temp_dir_path)
        os.makedirs(root_temp_dir_path)
        filestream=BytesIO()
        partner_ids = map(int, partner_ids.split(","))
        res_partners = request.env['res.partner'].browse(partner_ids)
        for res_partner in res_partners:
            request.env.cr.execute("""
                    SELECT id
                      FROM ir_attachment
                     WHERE res_id IN %s AND res_field IN 
                     ('adhar_card', 'adhar_card_back_side', 'age_proof', 'address_proof', 'kanha_voter_id_image','kanha_voter_id_back_image', 'declaration_form', 'passport_photo', 'passport_front_image', 'passport_back_image','indian_visa')
                """, [tuple(res_partner.ids)])
            ir_attachments = request.env.cr.fetchall()
            attachments = request.env["ir.attachment"].search([('id','in', ir_attachments)])
            partner_name = res_partner.name+"-"+str(res_partner.id)
            partner_temp_dir = os.path.join(root_temp_dir_path, partner_name)
            if os.path.exists(partner_temp_dir):
                shutil.rmtree(partner_temp_dir)
            os.makedirs(partner_temp_dir)
            for attachment in attachments:
                attachment = attachment.sudo()
                mimetype = attachment.mimetype.split("/")[-1]
                extension = "."+mimetype
                file = open(os.path.join(partner_temp_dir, attachment.name+extension), 'wb')
                os.stat(attachment._full_path(attachment.store_fname))
                for line in open(attachment._full_path(attachment.store_fname), 'rb').readlines():    
                    file.write(line)
                file.close()    
        
        with zipfile.ZipFile(filestream, mode='w', compression=zipfile.ZIP_DEFLATED) as zipf:
            self.zip(root_temp_dir_path, zipf)
                    
        request.env['residents.documents.downloads.history'].create({
            'downloaded_by':request.env.user.id,
            'downloaded_datetime':fields.Datetime.now(),
            'partner_ids':[(6, 0, res_partners.ids)]
        })
        return  http.send_file(
            filepath_or_fp=filestream,
            mimetype="application/zip",
            as_attachment=True,
            cache_timeout=3,
            filename=_("Documents.zip"),
        )

    @http.route('/delete_family_members', type='http', auth="user", methods=['POST'], website=True, csrf=False)
    def delete_family_members(self, access_token=None, **post):
        request.params.pop('csrf_token', None)
        deleted_partner_ids = post.get('deleted_partner_ids')
        if(deleted_partner_ids):
            try:
                partner_id = int(deleted_partner_ids)
                ResPartner = request.env['res.partner']
                partner = ResPartner.sudo().search([('id', '=', partner_id)])
                user = request.env['res.users'].sudo().search([('partner_id', '=', partner.id)])
                if(partner.application_status in ["draft", "rejected"]) and partner.rfid_card_no <= 0:
                    if user.id == request.env.user.id:
                        return "current_user"
                    else:
                        partner.sudo().unlink()
                        return "deleted"
                else:
                    return "cannot_delete"
            except ValueError:
                return "invalid_id"
        else:
            return "no_records"