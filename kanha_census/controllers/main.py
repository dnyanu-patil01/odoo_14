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


class Website(Website):

    #Requires Login To View Home Page
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
        current_partner = request.env.user.partner_id
        ResPartner = request.env['res.partner']
        # Fetch logged in partner's family members based on Kanha House no.
        # if(current_partner.kanha_house_number_id):
        #     domain = ['|', ('id', '=', current_partner.id), ('kanha_house_number_id', '=', current_partner.kanha_house_number_id.id),('kanha_location_id','=',current_partner.kanha_location_id.id)]
        # else:
        #     domain = [('id', '=', current_partner.id)]
        domain = ['|',('create_uid','=',request.env.user.id),('email','=',request.env.user.email)]
        if search:
            subdomains = [('name', 'ilike', search)]
            domain = domain+subdomains
        
        # For admin user display all partner records
        if request.env.is_admin():
            domain = []

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
            'search': search
        })
        return request.render("kanha_census.portal_my_family_members", values)

    def kanha_portal_form_validate(self, data, partner_id):
        error = dict()
        error_message = []

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
            
            # Checks Aadhar Number is Unique
            ResPartner = request.env['res.partner']
            partner = ResPartner.sudo().search([('id', '=', partner_id)])    
            if(not partner):
                is_adhar_no_exsist = ResPartner.sudo().search([('aadhaar_card_number', '=', data.get('aadhaar_card_number'))])
                if(is_adhar_no_exsist): 
                    error["aadhaar_card_number"] = 'error'
                    error_message.append(_('Aadhar Number is already exist!'))    
        
        # Relative Aadhar card validation
        if data.get('relative_aadhaar_card_number'):
            relative_aadhaar_card_number = data.get('relative_aadhaar_card_number')
            is_valid = self.is_valid_aadhaar_number(relative_aadhaar_card_number)
            if not is_valid:
                error["aadhar_card_number"] = _('Invalid Relative Aadhar Number!')
                error_message.append(_('Invalid Relative Aadhar Number!'))               

        # Mobile number validation
        if data.get('mobile'):
            is_valid = self.is_valid_mobile_number(data.get('mobile'))
            if not is_valid:
                error["mobile"] = _('Invalid Mobile Number!')
                error_message.append(_('Invalid Mobile Number!')) 
                
        # Date of Birth validation
        if data.get('date_of_birth'):
            is_valid = self.is_valid_date(data.get('date_of_birth'))
            if not is_valid:
                error["date_of_birth"] = _('You cannot enter a date in the future for Date of Birth !')
                error_message.append(_('You cannot enter a date in the future for Date of Birth!'))             
        
        # Resident of kanha from date validation
        if data.get("resident_of_kanha_from_date"):
            is_valid = self.is_valid_date(data.get('resident_of_kanha_from_date'))
            if not is_valid:
                error["resident_of_kanha_from_date"] = _('You cannot enter a date in the future for Resident of kanha from date!')
                error_message.append(_('You cannot enter a date in the future for Resident of kanha from date!'))      
        
        # Resident of kanha from date validation
        if data.get("visa_start_date"):
            is_valid = self.is_valid_date(data.get('visa_start_date'))
            if not is_valid:
                error["visa_start_date"] = _('You cannot enter a date in the future for Visa Start date!')
                error_message.append(_('You cannot enter a date in the future for Visa Start date!'))      

        # Resident of kanha from date validation
        if data.get("visa_end_date"):
            is_valid = self.is_valid_future_date(data.get('visa_end_date'))
            if not is_valid:
                error["visa_end_date"] = _('You cannot enter a date in the future for Resident of kanha from date!')
                error_message.append(_('You cannot enter a date in the future for Resident of kanha from date!'))      

        return error, error_message

    def is_valid_pan_number(self, pan_number):
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
        
    def is_valid_aadhaar_number(self, emp_aadhaar):
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
        
    def is_valid_mobile_number(self, mobile_number):
        # Valid Mobile Number
        #    1.Begins with 0 or 91
        #    2.Then contains 7 or 8 or 9.
        #    3.Then contains 9 digits
        # pattern = re.compile("(0|91)?[6-9][0-9]{9}")
        pattern = re.compile("(0/91)?[7-9][0-9]{9}")
        if pattern.match(mobile_number) and len(mobile_number) == 10:
            return True
        else:
            return False
        
    def is_valid_date(self, date_val):
        # Validate date value should not be more than today's date
                        
        date_val = datetime.strptime(date_val, "%Y-%m-%d")
        present = datetime.now()
        if(date_val.date() <= present.date()):
            return True
        else:
            return False

    def is_valid_future_date(self, date_val):
        # Validate date value should not be more than today's date
                        
        date_val = datetime.strptime(date_val, "%Y-%m-%d")
        present = datetime.now()
        if(date_val.date() >= present.date()):
            return True
        else:
            return False

    @http.route('/website_form/<int:partner_id>/<string:model_name>', type='http', auth="user", methods=['POST'], website=True)
    def save_portal_form(self, partner_id=None, model_name=None, access_token=None, **post):
        request.params.pop('csrf_token', None)
        is_submit = post.get("is_submit")
        post.pop("is_submit")
        ResPartner = request.env['res.partner']
        partner = ResPartner.sudo().search([('id', '=', partner_id)])
        if post and request.httprequest.method == 'POST':
            error = dict()
            post['state'] = 'saved_not_submitted'
            # Validates the form only when Submit the form. When Saves ignores the form validation
            error, error_message = self.kanha_portal_form_validate(post, partner_id)
            aadhaar_card_number = post.get('aadhaar_card_number')
            citizenship = post.get('citizenship')
            passport_number = post.get('passport_number')
            if citizenship == "Indian" and not aadhaar_card_number:
                error = "aadhaar_card_number"
                error_message = 'Aadhaar Card Number is Mandatory to Save/Submit Record'
            if citizenship == "Overseas" and not passport_number:
                error = "passport_number"
                error_message = 'Passport Number is Mandatory to Save/Submit Record'
            # if not post.get('aadhaar_card_number'):
            #     error = "aadhaar_card_number"
            #     error_message = 'Aadhaar Card Number is Mandatory to Save/Submit Record'
            if(is_submit == 'true'):
                post['state'] = 'submitted'
                post['application_status'] = 'to_approve'
            if not error and is_submit == 'false':
                # Prepares File fields
                post_vals = post.copy()
                for field_name, field_value in post_vals.items():
                    # If the value of the field if a file
                    if hasattr(field_value, 'filename'):
                        # Undo file upload field name indexing
                        post.pop(field_name)
                        field_name = field_name.split('[', 1)[0]
                        post[field_name] = field_value
                values = {}
                values.update(post)
                values.update({'is_published': True})
                values.update({'application_status': 'draft'})
                # Removes Invisible fields value
                if(values.get('change_voter_id_address') != 'Yes'):
                    # self.remove_existing_voter_id_details(values)
                    self.remove_invisible_fields_value(values, self.EXISTING_VOTER_ID_FIELDS)
                if(values.get('citizenship') == 'Overseas'):
                    # self.remove_kanha_voter_id_details(values)
                    self.remove_invisible_fields_value(values, self.KANHA_VOTER_ID_FIELDS)
                else:
                    self.remove_invisible_fields_value(values)
                
                # Removes attachment when delete it
                if(not values.get('adhar_card_back_side_filename')):
                    values['adhar_card_back_side'] = ''
                if(not values.get('adhar_card_filename')):
                    values['adhar_card'] = ''
                if(not values.get('kanha_voter_id_image_filename')):
                    values['kanha_voter_id_image'] = ''
                if(not values.get('kanha_voter_id_back_image_filename')):
                    values['kanha_voter_id_back_image'] = ''
                if(not values.get('age_proof_filename')):
                    values['age_proof'] = ''
                if(not values.get('address_proof_filename')):
                    values['address_proof'] = '' 
                if(not values.get('passport_photo_filename')):
                    values['passport_photo'] = ''
                if(not values.get('passport_front_image_filename')):
                    values['passport_front_image'] = ''
                if(not values.get('passport_back_image_filename')):
                    values['passport_back_image'] = ''
                if(not values.get('indian_visa_filename')):
                    values['indian_visa'] = ''
                
                # Set False if the value for the date field is not given
                if(values.get("date_of_birth") == ''):
                    values['date_of_birth'] = False
                if(values.get("resident_of_kanha_from_date") == ''):
                    values['resident_of_kanha_from_date'] = False
                if(values.get("visa_start_date") == ''):
                    values['visa_start_date'] = False
                if(values.get("visa_end_date") == ''):
                    values['visa_end_date'] = False
                       
                # Prepare Many2One values
                many_2_one_fields = ['birth_state_id', 'kanha_location_id', 'country_id', 'state_id','kanha_house_number_id']
                # if(post.get('change_voter_id_address') == 'Yes'):
                #     many_2_one_fields.append('state_id')
                for field in set(many_2_one_fields) & set(values.keys()):
                    try:
                        values[field] = int(values[field])
                    except:
                        values[field] = False
                # Insert File input value
                for field in set(['adhar_card',
                                  'adhar_card_back_side',
                                  'passport_photo',
                                  'indian_visa',
                                  'passport_front_image',
                                  'passport_back_image',
                                  'age_proof',
                                  'address_proof',
                                  'declaration_form',
                                  'kanha_voter_id_back_image',
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
                # new records
                vehicle_new_lines = json.loads(values.get('vehicle_new_lines'))
                if(vehicle_new_lines):
                    for vehicle_new_rec in vehicle_new_lines:
                        vehicle_details_vals.append([0, 0, vehicle_new_rec])
                values.pop('vehicle_new_lines')
                values['vehicle_details_ids'] = vehicle_details_vals

                # Links family members based on Kanha house no.
                relative_partner = False
                kanha_house_number_id = post.get('kanha_house_number_id')
                kanha_location_id = post.get('kanha_location_id')
                if(kanha_house_number_id):
                    relative_partner = ResPartner.sudo().search([('kanha_house_number_id', '=', kanha_house_number_id),('kanha_location_id','=',kanha_location_id)])

                # If partner exist, updates the records else create a new partner record
                if partner:
                    # Updates vehicle info
                    vehicle_details_ids = json.loads(post.get('vehicle_details_ids'))
                    partner_vehicle_ids = partner.vehicle_details_ids.ids
                    if(vehicle_details_ids):
                        partner_vehicle_ids = list(map(str, partner_vehicle_ids))
                        # Deletes record
                        deleted_vehicle_ids = list(set(partner_vehicle_ids).symmetric_difference(set(vehicle_details_ids.keys())))
                        for deleted_id in deleted_vehicle_ids:
                            vehicle_details_vals.append([2, int(deleted_id)])
                            partner_vehicle_ids.remove(deleted_id)
                        # Updates record
                        for partner_vehicle in partner_vehicle_ids:
                            vehicle_vals = vehicle_details_ids.get(str(partner_vehicle))
                            vehicle_details_vals.append([1, partner_vehicle, vehicle_vals])
                    # Delete all records when 
                    elif(partner_vehicle_ids and not vehicle_details_ids):
                        for partner_vehicle in partner_vehicle_ids:
                            vehicle_details_vals.append([2, partner_vehicle])
                    
                    values['vehicle_details_ids'] = vehicle_details_vals
                    # Links family members
                    if(kanha_house_number_id != partner.kanha_house_number_id.id):
                        partner.write({'family_members_ids': [(5,)]})
                        partner_list_to_unlink = ResPartner.sudo().search([('family_members_ids', '=', partner.id)])
                        for partner_list in partner_list_to_unlink:
                            partner_list.write({'family_members_ids': [(3, partner.id)]})
                        # Links family members
                        if(relative_partner):
                            partner.sudo().write({'family_members_ids': [(6, 0, relative_partner.ids)]})
                            relative_partner.sudo().write({'family_members_ids': [(4, partner.id)]})
                    # updates partner
                    partner.sudo().write(values)
                else:
                    # creates new partner record
                    partner = ResPartner.sudo().create(values)
                    # Links family members
                    if(relative_partner):
                        partner.sudo().write({'family_members_ids': [(6, 0, relative_partner.ids)]})
                        relative_partner.sudo().write({'family_members_ids': [(4, partner.id)]})    
                return json.dumps({'id': partner.id})
            if is_submit == 'true':
                if partner:
                    partner.sudo().write({'application_status':'to_approve','state':'submitted'})
                    return json.dumps({'id': partner.id})
        return json.dumps({
            'id': False,
            'error': error,
            'error_message': error_message,
            'error_fields': error,
            })

    @http.route('/website_form_family/<int:partner_id>/<string:model_name>', type='http', auth="user", website=True)
    def family_portal_form(self, partner_id=None, model_name=None, access_token=None, **post):
        ResPartner = request.env['res.partner']
        partner = ResPartner.sudo().search([('id', '=', partner_id)])
        if partner == request.env.user.partner_id or partner.create_uid == request.env.user.id:
            values = self.get_default_values_for_kanha(partner_id)
            is_kanha_voter_info_required = True
            if partner.citizenship == 'Overseas':
                is_kanha_voter_info_required = False
            values.update({
                'zipcode': post.get('zip'),
                'partner': partner,
                'is_kanha_voter_info_required': is_kanha_voter_info_required
            })
            if partner.citizenship == 'Indian':
                response = request.render("kanha_census.kanha_family_portal_form_indian", values)
            else:
                response = request.render("kanha_census.kanha_family_portal_form_overseas", values)
            response.headers['X-Frame-Options'] = 'DENY'
            return response
        else:
            print("You cannot access this record !")
    
    @http.route(['/add_family_members_indian'], type='http', auth="public", website=True)
    def add_family_members_indian(self, redirect=None, **post):
        values = self.get_default_values_for_kanha()
        current_partner = request.env.user.partner_id
        values.update({
            'partner': None,
            'surname': current_partner.surname,
            'kanha_location_id': current_partner.kanha_location_id.id if current_partner.kanha_location_id else None,
            'kanha_house_number_id':  current_partner.kanha_house_number_id.id if current_partner.kanha_house_number_id else None,
        })
        response = request.render("kanha_census.kanha_family_portal_form_indian", values)
        return response
    
    @http.route(['/add_family_members_overseas'], type='http', auth="public", website=True)
    def add_family_members_overseas(self, redirect=None, **post):
        values = self.get_default_values_for_kanha()
        current_partner = request.env.user.partner_id
        values.update({
            'partner': None,
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
        # Fetch the record who doesnt have any child records
        kanha_location_parent_ids = request.env['kanha.location'].search([]).parent_id.ids
        kanha_locations_nth_child = request.env['kanha.location'].search([('id', 'not in', kanha_location_parent_ids)])
        #Fetch the record of kanha house number
        kanha_house_numbers = request.env['kanha.house.number'].search([])
        values.update({
            'states': states,
            'page_name': 'family',
            'kanha_locations': kanha_locations_nth_child,
            'kanha_house_numbers':kanha_house_numbers,
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
            many2one_fields = ['country_id', 'birth_country_id', 'state_id', 'birth_state_id']
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
        """Zip the directory"""
        # ziph is a zipfile handle
        for root, dirs, files in os.walk(path):
            for file in files:
                ziph.write(os.path.join(root, file),
                           os.path.relpath(os.path.join(root, file),
                                           os.path.join(path, '..')))    


    @http.route("/web/attachment/download_zip", type="http", auth="user")
    def download_zip(self, partner_ids=None):
        #create complete filepath of temp directory in the name of Documents
        root_temp_dir_path = os.path.join(tempfile.gettempdir(), 'Documents')
        # Delete if this Temp folder already exists
        if os.path.exists(root_temp_dir_path):
            shutil.rmtree(root_temp_dir_path)
        # Creates temp dir
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
            # Create temp dir in the name of partner inside a root dir
            partner_temp_dir = os.path.join(root_temp_dir_path, partner_name)
            # Delete if the Temp folder already exists
            if os.path.exists(partner_temp_dir):
                shutil.rmtree(partner_temp_dir)
            os.makedirs(partner_temp_dir)
            for attachment in attachments:
                mimetype = attachment.mimetype.split("/")[-1]
                extension = "."+mimetype
                file = open(os.path.join(partner_temp_dir, attachment.name+extension), 'wb')
                os.stat(attachment._full_path(attachment.store_fname))
                for line in open(attachment._full_path(attachment.store_fname), 'rb').readlines():    
                    file.write(line)
                file.close()    
        # Create a ZipFile Object        
        with zipfile.ZipFile(filestream, mode='w', compression=zipfile.ZIP_DEFLATED) as zipf:
            self.zip(root_temp_dir_path, zipf)
                    
        # Creates a Downloads History
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
