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
                             "voter_id_number_optional_id",
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

        family_member_count = 0
        while True:
            mobile_field = f'family_member_mobile_{family_member_count}'
            emergency_contact_field = f'family_member_emergency_contact_{family_member_count}'
            
            if mobile_field not in data and emergency_contact_field not in data:
                break
                
            if data.get(mobile_field):
                is_valid = self.is_valid_mobile_number(data.get(mobile_field))
                if not is_valid:
                    error[mobile_field] = _('Invalid Family Member Mobile Number!')
                    error_message.append(_('Invalid Family Member Mobile Number!'))
                    
            if data.get(emergency_contact_field):
                is_valid = self.is_valid_mobile_number(data.get(emergency_contact_field))
                if not is_valid:
                    error[emergency_contact_field] = _('Invalid Family Member Emergency Contact!')
                    error_message.append(_('Invalid Family Member Emergency Contact!'))
            
            family_member_count += 1
        
        if data.get('year_of_birth'):
            is_valid = self.is_valid_year(data.get('year_of_birth'))
            if not is_valid:
                error["year_of_birth"] = _('You cannot enter a Year in the future for Year of Birth!')
                error_message.append(_('You cannot enter a Year in the future for Year of Birth!'))

        if data.get('members_count'):
            try:
                members_count = int(data.get('members_count'))
                if members_count < 1 or members_count > 8:
                    error["members_count"] = _('Members count must be between 1 and 8!')
                    error_message.append(_('Members count must be between 1 and 8!'))
            except ValueError:
                error["members_count"] = _('Invalid members count!')
                error_message.append(_('Invalid members count!'))

        for field in ['any_gov_id_proof', 'passport_front_image', 'passport_back_image', 'indian_visa', 'passport_photo', 'address_proof', 'age_proof']:
            file_data = data.get(field)
            if file_data and hasattr(file_data, 'filename'):
                try:
                    if hasattr(file_data, 'stream'):
                        file_content = file_data.stream.read()
                        file_data.stream.seek(0)
                    elif hasattr(file_data, 'read'):
                        current_pos = file_data.tell() if hasattr(file_data, 'tell') else 0
                        file_data.seek(0)
                        file_content = file_data.read()
                        file_data.seek(current_pos)
                    else:
                        continue
                        
                    file_size_kb = len(file_content) / 1024
                    
                    if file_size_kb > 500:
                        error[field] = _('File size cannot exceed 500KB')
                        error_message.append(_('File size cannot exceed 500KB for %s') % field)
                    
                    filename = file_data.filename.lower()
                    if field == 'any_gov_id_proof':
                        if not (filename.endswith('.jpg') or filename.endswith('.jpeg') or filename.endswith('.pdf')):
                            error[field] = _('Only JPG and PDF formats are allowed')
                            error_message.append(_('Only JPG and PDF formats are allowed for %s') % field)
                    else:
                        if not (filename.endswith('.jpg') or filename.endswith('.jpeg')):
                            error[field] = _('Only JPG format is allowed')
                            error_message.append(_('Only JPG format is allowed for %s') % field)
                except Exception:
                    continue

        family_member_files = ['passport_photo']
        for idx in range(10):
            for file_field in family_member_files:
                field_name = f'family_member_{file_field}_{idx}'
                file_data = data.get(field_name)
                if file_data and hasattr(file_data, 'filename'):
                    try:
                        if hasattr(file_data, 'stream'):
                            file_content = file_data.stream.read()
                            file_data.stream.seek(0)
                        elif hasattr(file_data, 'read'):
                            current_pos = file_data.tell() if hasattr(file_data, 'tell') else 0
                            file_data.seek(0)
                            file_content = file_data.read()
                            file_data.seek(current_pos)
                        else:
                            continue
                            
                        file_size_kb = len(file_content) / 1024
                        
                        if file_size_kb > 500:
                            error[field_name] = _('File size cannot exceed 500KB')
                            error_message.append(_('File size cannot exceed 500KB for family member document'))
                        
                        filename = file_data.filename.lower()
                        if not (filename.endswith('.jpg') or filename.endswith('.jpeg')):
                            error[field_name] = _('Only JPG format is allowed')
                            error_message.append(_('Only JPG format is allowed for family member document'))
                    except Exception:
                        continue
        
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

    def _process_file_upload(self, file_data):
        if not file_data or not hasattr(file_data, 'filename'):
            return None
            
        try:
            if hasattr(file_data, 'stream'):
                file_data.stream.seek(0)
                file_content = file_data.stream.read()
            elif hasattr(file_data, 'read'):
                current_pos = file_data.tell() if hasattr(file_data, 'tell') else 0
                file_data.seek(0)
                file_content = file_data.read()
                file_data.seek(current_pos)
            else:
                return None
                
            if file_content:
                if isinstance(file_content, str):
                    file_content = file_content.encode('utf-8')
                return base64.b64encode(file_content).decode('utf-8')
            return None
        except Exception:
            return None

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
                    
                    values = {}
                    values.update(post_vals)
                    values.update({'is_published': True})

                    if values.get('citizenship') == 'Overseas':
                        overseas_fields = [
                            'birth_country_name', 'property_owner_name', 'property_owner_email', 
                            'property_owner_phone', 'residence_type', 'passport_number', 
                            'full_name_passport', 'emergency_contact'
                        ]
                        
                        if values.get('residence_type') != 'Rented Place':
                            for field in ['property_owner_name', 'property_owner_email', 'property_owner_phone']:
                                values[field] = ''

                    family_member_vals = []
                members_count = 0

                try:
                    members_count_val = values.get('members_count', '1')
                    if members_count_val and re.match(r'^[1-8]$', str(members_count_val).strip()):
                        members_count = int(members_count_val)
                    else:
                        members_count = 1
                except:
                    members_count = 1

            for i in range(members_count):
                name_field = f'family_member_name_{i}'
                relation_field = f'family_member_relation_{i}'
                blood_group_field = f'family_member_blood_group_{i}'
                mobile_field = f'family_member_mobile_{i}'
                emergency_contact_field = f'family_member_emergency_contact_{i}'
                passport_photo_field = f'family_member_passport_photo_{i}'
                
                member_name = values.get(name_field, '').strip() or post.get(name_field, '').strip()
                member_relation = values.get(relation_field, '').strip() or post.get(relation_field, '').strip()
                
                if member_name and member_relation:
                    member_vals = {
                        'name': member_name,
                        'relation': member_relation,
                        'blood_group': values.get(blood_group_field, '').strip() or post.get(blood_group_field, '').strip(),
                        'mobile': values.get(mobile_field, '').strip() or post.get(mobile_field, '').strip(),
                        'emergency_contact': values.get(emergency_contact_field, '').strip() or post.get(emergency_contact_field, '').strip(),
                        'sequence': i + 1,
                    }
                    
                    if member_relation.lower() == 'head' or i == 0:
                        main_mobile = values.get('mobile', '').strip()
                        if main_mobile and not member_vals['mobile']:
                            member_vals['mobile'] = main_mobile
                    
                    file_data = post.get(passport_photo_field)
                    processed_file = self._process_file_upload(file_data)
                    if processed_file:
                        member_vals['passport_photo'] = processed_file
                        if hasattr(file_data, 'filename'):
                            member_vals['passport_photo_filename'] = file_data.filename
                        else:
                            member_vals['passport_photo_filename'] = f'passport_photo_{i}.jpg'
                    
                    family_member_vals.append([0, 0, member_vals])
                
                for field in [name_field, relation_field, blood_group_field, mobile_field, 
                            emergency_contact_field, passport_photo_field]:
                    values.pop(field, None)
                    post.pop(field, None)
                if family_member_vals:
                    values['family_member_ids'] = family_member_vals

                    for field in ['any_gov_id_proof', 'passport_front_image', 'passport_back_image', 'passport_photo', 'indian_visa', 'address_proof', 'age_proof']:
                        file_data = post.get(field)
                        processed_file = self._process_file_upload(file_data)
                        if processed_file:
                            values[field] = processed_file
                            if hasattr(file_data, 'filename'):
                                values[f'{field}_filename'] = file_data.filename
                        else:
                            values.pop(field, None)

                    if values.get("year_of_birth"):
                        try:
                            values['year_of_birth'] = int(values['year_of_birth'])
                        except:
                            values['year_of_birth'] = False

                    many_2_one_fields = ['kanha_location_id', 'kanha_house_number_id', 'work_profile_id','department_id']
                    for field in set(many_2_one_fields) & set(values.keys()):
                        try:
                            values[field] = int(values[field]) if values[field] else False
                        except:
                            values[field] = False

                    vehicle_details_vals = []
                    try:
                        vehicle_new_lines = json.loads(values.get('vehicle_new_lines', '[]'))
                        if vehicle_new_lines:
                            for vehicle_new_rec in vehicle_new_lines:
                                vehicle_details_vals.append([0, 0, vehicle_new_rec])
                        values.pop('vehicle_new_lines', None)
                        values['vehicle_details_ids'] = vehicle_details_vals
                    except (ValueError, TypeError):
                        values.pop('vehicle_new_lines', None)

                    if partner:
                        try:
                            vehicle_details_ids = json.loads(post.get('vehicle_details_ids', '{}'))
                            partner_vehicle_ids = partner.vehicle_details_ids.ids
                            if vehicle_details_ids:
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
                            elif partner_vehicle_ids and not vehicle_details_ids:
                                for partner_vehicle in partner_vehicle_ids:
                                    vehicle_details_vals.append([2, partner_vehicle])
                            
                            values['vehicle_details_ids'] = vehicle_details_vals
                        except (ValueError, TypeError):
                            pass

                        if partner.family_member_ids:
                            values['family_member_ids'] = [(5,)] + family_member_vals

                        partner.sudo().write(values)
                        if partner.application_status == 'to_approve':
                            partner.send_application_status_mail(partner.application_status)
                    else:
                        partner = ResPartner.sudo().create(values)
                        if partner.application_status == 'to_approve':
                            partner.send_application_status_mail(partner.application_status)
                    
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
            return request.render('kanha_census.access_denied', {})
    
    @http.route(['/add_family_members_indian/<int:partner_id>'], type='http', auth="user", website=True)
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
    
    @http.route(['/add_family_members_overseas/<int:partner_id>'], type='http', auth="user", website=True)
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
    
    @http.route(['/select_citizen'], type='http', auth="user", website=True)
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
                values['voter_id_number_optional_id'] = ''
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
                    ('any_gov_id_proof', 'adhar_card', 'adhar_card_back_side', 'age_proof', 'address_proof', 'kanha_voter_id_image','kanha_voter_id_back_image', 'declaration_form', 'passport_photo', 'passport_front_image', 'passport_back_image','indian_visa')
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