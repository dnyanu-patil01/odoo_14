from odoo import fields, models, api, _
from datetime import date, timedelta, datetime
from odoo.exceptions import AccessError, ValidationError
import logging
_logger = logging.getLogger(__name__)
from odoo.osv import expression
import re


class FamilyMember(models.Model):
    _name = 'family.member'
    _description = 'Family Member Details'

    partner_id = fields.Many2one('res.partner', string='Partner', required=True, ondelete='cascade')
    name = fields.Char(string='Name', required=True)
    relation = fields.Selection([
        ('Head', 'Head of Family'),
        ('Father', 'Father'),
        ('Mother', 'Mother'),
        ('Husband', 'Husband'),
        ('Wife', 'Wife'),
        ('Son', 'Son'),
        ('Daughter', 'Daughter'),
        ('Brother', 'Brother'),
        ('Sister', 'Sister'),
        ('Grandfather', 'Grandfather'),
        ('Grandmother', 'Grandmother'),
        ('Father-in-law', 'Father-in-law'),
        ('Mother-in-law', 'Mother-in-law'),
        ('Brother-in-law', 'Brother-in-law'),
        ('Sister-in-law', 'Sister-in-law'),
        ('Son-in-law', 'Son-in-law'),
        ('Daughter-in-law', 'Daughter-in-law'),
        ('Spouse', 'Spouse'),
        ('Other', 'Other'),
    ], string='Relation', required=True)
    blood_group = fields.Selection([
        ('A+', 'A+'),
        ('A-', 'A-'),
        ('B+', 'B+'),
        ('B-', 'B-'),
        ('O+', 'O+'),
        ('O-', 'O-'),
        ('AB-', 'AB-'),
        ('AB+', 'AB+')
    ], string='Blood Group')
    sequence = fields.Integer(string='Sequence', default=1)
    govt_id_proof = fields.Binary('Government ID Proof', attachment=True)
    govt_id_proof_filename = fields.Char()
    passport_photo = fields.Binary('Passport Size Photo', attachment=True)
    passport_photo_filename = fields.Char()
    address_proof = fields.Binary('Kanha Address Proof', attachment=True)
    address_proof_filename = fields.Char()


class CardPrintLog(models.Model):
    _name = 'card.print.log'
    _description = 'Card Print Log'
    _order = 'print_date desc'

    partner_id = fields.Many2one('res.partner', string='Partner', required=True, ondelete='cascade')
    user_id = fields.Many2one('res.users', string='Printed By', required=True, default=lambda self: self.env.user)
    user_name = fields.Char(string='User Name', related='user_id.name', store=True)
    print_date = fields.Datetime(string='Print Date', default=fields.Datetime.now, required=True)
    print_time = fields.Char(string='Print Time', compute='_compute_print_time', store=True)

    @api.depends('print_date')
    def _compute_print_time(self):
        for record in self:
            if record.print_date:
                record.print_time = record.print_date.strftime('%H:%M:%S')


class BulkCardPrintWizard(models.TransientModel):
    _name = 'bulk.card.print.wizard'
    _description = 'Bulk Card Print Confirmation Wizard'

    partner_ids = fields.Many2many('res.partner', string='Partners')
    message = fields.Text(string='Confirmation Message', readonly=True)
    approved_count = fields.Integer(string='Approved Count')
    total_count = fields.Integer(string='Total Count')

    def action_confirm_print(self):
        if self.partner_ids:
            approved_records = self.partner_ids.filtered(lambda r: r.application_status == 'Approved but Card Not Printed')
            
            for record in approved_records:
                self.env['card.print.log'].create({
                    'partner_id': record.id,
                    'user_id': self.env.user.id,
                })
            
            approved_records.write({'application_status': 'Card Printed'})
            
            message = f"Successfully printed {len(approved_records)} card(s)."
            if len(approved_records) < len(self.partner_ids):
                skipped = len(self.partner_ids) - len(approved_records)
                message += f" {skipped} record(s) were skipped as they were not in 'Approved but Card Not Printed' status."
            
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Bulk Print Cards',
                    'message': message,
                    'type': 'success',
                    'sticky': False,
                }
            }
        return {'type': 'ir.actions.act_window_close'}

    def action_cancel(self):
        return {'type': 'ir.actions.act_window_close'}


class ResPartner(models.Model):
    _inherit = 'res.partner'
    
    surname = fields.Char(string='Surname')
    gender = fields.Selection([
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other')
    ], required=True)
    date_of_birth = fields.Date(string='Date of birth', required=False)
    town = fields.Char(string='Town/Village Name')
    district = fields.Char(string='District')
    birth_town = fields.Char(string='Birth Town')
    birth_district = fields.Char(string='Birth District')
    birth_country_id = fields.Many2one('res.country', string="Birth Country", default=lambda self: self.env['res.country'].search([('code','=','IN')], limit=1))
    birth_state_id = fields.Many2one("res.country.state", string='Birth State')
    relation_other = fields.Char(string="Other Relative")
    relation_type = fields.Selection([
        ('Father', 'Father'),
        ('Mother', 'Mother'),
        ('Husband', 'Husband'),
        ('Wife', 'Wife'),
        ('Son', 'Son'),
        ('Daughter', 'Daughter'),
        ('Brother', 'Brother'),
        ('Sister', 'Sister'),
        ('Grandfather', 'Grandfather'),
        ('Grandmother', 'Grandmother'),
        ('Father-in-law', 'Father-in-law'),
        ('Mother-in-law', 'Mother-in-law'),
        ('Brother-in-law', 'Brother-in-law'),
        ('Sister-in-law', 'Sister-in-law'),
        ('Son-in-law', 'Son-in-law'),
        ('Daughter-in-law', 'Daughter-in-law'),
        ('Spouse', 'Spouse'),
        ('Other', 'Other'),
    ], string="Relation")
    relative_name = fields.Char(string='Name of Relative')
    relative_surname = fields.Char(string='Surname of Relative')
    kanha_location_id = fields.Many2one('kanha.location', string="Kanha Location")
    house_number = fields.Char(string='House Number')
    kanha_house_number_id = fields.Many2one('kanha.house.number', string='Kanha House Number')
    resident_of_kanha_from_date = fields.Date(string='Resident of Kanha From Date')
    existing_voter_id_number = fields.Char(string="Existing Voter ID Number")
    assembly_constituency = fields.Char(string="Assembly Constituency")
    locality = fields.Char(string="Locality")
    post_office = fields.Char(string="Post Office")
    indian_visa = fields.Binary(string="Photo of Indian Visa", attachment=True)
    indian_visa_filename = fields.Char()
    passport_photo = fields.Binary(string="Passport Size Photo", attachment=True)
    passport_photo_filename = fields.Char()
    passport_id_image = fields.Binary(string="Passport ID", attachment=True)
    passport_id_image_filename = fields.Char()
    adhar_card = fields.Binary('Aadhar Card Front', attachment=True)
    adhar_card_filename = fields.Char()
    aadhaar_card_number = fields.Char(string="Aadhaar Card Number")
    adhar_card_back_side = fields.Binary('Aadhar Card Back', attachment=True)
    adhar_card_back_side_filename = fields.Char()
    age_proof = fields.Binary(string='Age Proof', attachment=True)
    age_proof_filename = fields.Char()
    address_proof = fields.Binary(string='Address Proof', attachment=True)
    address_proof_filename = fields.Char()
    govt_id_proof = fields.Binary('Government ID Proof', attachment=True)
    govt_id_proof_filename = fields.Char()
    application_type = fields.Selection([
        ('New Application', 'New Application'),
        ('Transfer Application', 'Transfer Application'),
    ])
    abhyasi_id = fields.Char(string="Abhyasi ID")
    members_count = fields.Char(string="How many members staying with you?")
    citizenship = fields.Selection([
        ('Indian', 'Indian'),
        ('Overseas', 'Overseas')
    ], required=True, default='Overseas')
    passport_number = fields.Char(string="Passport Number")
    work_profile = fields.Selection([
        ('Resident', 'Resident'),
        ('Volunteer', 'Volunteer'),
        ('Employee', 'Employee'),
        ('NMR', 'NMR'),
        ('Contractor', 'Contractor'),
        ('Other','Other')
    ])
    work_profile_id = fields.Many2one('work.profile', string="Resident Type")
    employee_id = fields.Char(string='ID Number')
    department_id = fields.Many2one('work.department',string='Department')
    rfid_card_no = fields.Integer("RFID Card No")
    change_voter_id_address = fields.Selection([
        ('Yes', 'Yes'),
        ('No', 'No'),
    ], string="Do you want to change your Voter Id card Address to Kanha")
    residence_type = fields.Selection([
        ('Rented Place', 'Rented Place'),
        ('Owner', 'Owner'),
        ('General Accommodation', 'General Accommodation'),        
    ], string="Residence Type")
    property_owner_name = fields.Char(string="Property Owner Name")
    property_owner_email = fields.Char(string="Owner's Email ID")
    property_owner_phone = fields.Char(string="Owner's Phone Number")
    family_members_ids = fields.Many2many('res.partner', 'res_partner_family_members_rel', 'family_member_id', 'partner_id',  string='Family Members', readonly=True, compute='_compute_family_members')
    relative_aadhaar_card_number = fields.Char(string="Relative Aadhar Card Number")
    is_geoadmin = fields.Boolean(string='Is Geo Admin', compute='_compute_is_geoadmin', store=False)
    card_print_log_ids = fields.One2many('card.print.log', 'partner_id', string='Card Print Logs')
    family_member_ids = fields.One2many('family.member', 'partner_id', string='Family Members Details')
    birth_country_name = fields.Char(related="birth_country_id.name", string="Birth Country Name", store=True)
    full_name_passport = fields.Char(string='Full Name (as per Passport)')
    srcm_id = fields.Char(string='SRCM ID')
    preceptor_incharge_name = fields.Char(string='Preceptor Name / In-charge Name')
    vehicle_details_ids = fields.One2many('vehicle.details', 'partner_id', string='Vehicle Details')
    already_have_kanha_voter_id = fields.Selection([
        ('Yes', 'Yes'),
        ('No', 'No'),
    ], string="Do you have Voter ID")
    has_voter_id_in_kanha = fields.Selection([
        ('Yes', 'Yes'),
        ('No', 'No'),
    ], string="Do you have a Voter ID in Kanha?", related='already_have_kanha_voter_id', store=False)
    has_voter_id_preserved = fields.Selection([
        ('Yes', 'Yes'),
        ('No', 'No'),
    ], string="Voter ID Preserved")
    voter_id_number_preserved = fields.Selection([
        ('Yes', 'Yes'),
        ('No', 'No'),
    ], string="Voter ID Number Preserved")
    kanha_voter_id_number = fields.Char(string="Existing Voter ID Number")
    kanha_voter_id_image = fields.Binary('Voter ID Front Image', attachment=True)
    kanha_voter_id_image_filename = fields.Char()
    kanha_voter_id_back_image = fields.Binary('Voter ID Back Image', attachment=True)
    kanha_voter_id_back_image_filename = fields.Char()
    declaration_form = fields.Binary('Declaration Form File', attachment=True, required=False)
    declaration_form_filename = fields.Char()
    need_new_kanha_voter_id = fields.Selection([
        ('Yes', 'Yes'),
        ('No', 'No'),
    ], string="Need New Voter ID")
    wants_to_apply_voter_id = fields.Selection([
        ('Yes', 'Yes'),
        ('No', 'No'),
    ], string="Do you want to apply for Voter ID?")
    state = fields.Selection([
        ('saved_not_submitted', 'Saved Not Submitted'),
        ('submitted', 'Submitted'),
    ], string='Status', readonly=True, copy=False, index=True, tracking=3, default='saved_not_submitted')
    application_reference_no = fields.Char(string='If already applied for Kanha voter ID, please provide application reference number')
    passport_front_image = fields.Binary(string="Passport Front Image", attachment=True)
    passport_front_image_filename = fields.Char()
    passport_back_image = fields.Binary(string="Passport Back Image", attachment=True)
    passport_back_image_filename = fields.Char()
    residents_documents_downloads_history_id = fields.Many2one('residents.documents.downloads.history','Residents Documents Downloads History') 
    visa_start_date = fields.Date(string='Visa Start Date')
    visa_end_date = fields.Date(string='Visa End Date')
    visa_type = fields.Selection([
        ('Employment', 'Employment'),
        ('Tourist', 'Tourist'),
        ('Transit', 'Transit'),
        ('Business', 'Business'),
        ('Medical', 'Medical'),
    ])
    application_status = fields.Selection([
        ('draft', 'Draft'),
        ('to_approve', 'Waiting For Approval'),
        ('Approved but Card Not Printed', 'Approved but Card Not Printed'),
        ('Card Printed', 'Card Printed'),
        ('rejected', 'Rejected'),
        ('approved_for_edit', 'Approved for Edit'),
    ], default="draft")
    rejection_reason = fields.Text("Reason For Rejection")
    birth_state_textfield = fields.Char(string="Birth State")
    blood_group = fields.Selection([
        ('A+', 'A+'),
        ('A-', 'A-'),
        ('B+', 'B+'),
        ('B-', 'B-'),
        ('O+', 'O+'),
        ('O-', 'O-'),
        ('AB-', 'AB-'),
        ('AB+', 'AB+')
    ], string='Blood Group')
    emergency_contact = fields.Char(string='Emergency Contact No.')
    do_you_need_voter_id_in_kanha = fields.Selection([
        ('No', 'No'),
        ('Yes', 'Yes') 
    ], string='Do you need a Voter ID in Kanha?')
    is_preceptor = fields.Selection([
        ('Yes', 'Yes'),
        ('No', 'No')],
        string='Are you a preceptor?'
    )
    year_of_birth = fields.Integer(string="Year Of Birth", compute='_compute_year_of_birth', store=True)
    family_details = fields.Text(string='Family Details', compute='_compute_family_details', store=False)
    
    @api.depends('family_member_ids')
    def _compute_family_details(self):
        for record in self:
            if record.family_member_ids:
                details = []
                for member in record.family_member_ids:
                    member_info = f"{member.name} ({member.relation})"
                    if member.blood_group:
                        member_info += f" - {member.blood_group}"
                    details.append(member_info)
                record.family_details = "\n".join(details)
            else:
                record.family_details = ""
    
    @api.constrains('members_count')
    def _check_members_count(self):
        for record in self:
            if record.members_count:
                cleaned_value = record.members_count.strip()
                if not re.match(r'^[1-8]$', cleaned_value):
                    raise ValidationError(_("Members count must be a single digit between 1 and 8 only."))

    @api.onchange('members_count')
    def _onchange_members_count(self):
        if self.members_count:
            self.members_count = self.members_count.strip()
            if not re.match(r'^[1-8]$', self.members_count):
                return {
                    'warning': {
                        'title': _('Invalid Input'),
                        'message': _('Please enter only a single digit between 1 and 8.')
                    }
                }

    @api.depends('user_id')  
    def _compute_is_geoadmin(self):
        group_geo_admin = self.env.ref('kanha_census.group_geoadmin_access', raise_if_not_found=False)
        for record in self:
            if group_geo_admin:
                record.is_geoadmin = group_geo_admin in self.env.user.groups_id
            else:
                record.is_geoadmin = False

    @api.depends('kanha_house_number_id')
    def _compute_family_members(self):
        for record in self:
            if record.kanha_house_number_id:
                family_members = self.search([('kanha_house_number_id', '=', record.kanha_house_number_id.id)]).filtered(lambda member: member.id != record.id)
                record.family_members_ids = [(6, 0, family_members.ids)]
            else:
                record.family_members_ids = [(6, 0, [])]

    @api.depends('date_of_birth')
    def _compute_year_of_birth(self):
        for record in self:
            if record.date_of_birth:
                record.year_of_birth = record.date_of_birth.year
            else:
                record.year_of_birth = False

    def _normalize_relation_value(self, relation_value):
        return relation_value

    def process_family_members_data(self, vals):
        if not vals:
            return []
        
        members_count = vals.get('members_count', '1')
        if members_count and re.match(r'^[1-8]$', str(members_count).strip()):
            members_count = int(members_count)
        else:
            members_count = 1
            
        family_data = []
        
        for i in range(members_count):
            name_key = f'family_member_name_{i}'
            relation_key = f'family_member_relation_{i}'
            blood_group_key = f'family_member_blood_group_{i}'
            govt_id_key = f'family_member_govt_id_{i}'
            passport_photo_key = f'family_member_passport_photo_{i}'
            address_proof_key = f'family_member_address_proof_{i}'
            
            if name_key in vals and vals[name_key]:
                relation_value = vals.get(relation_key, '')
                normalized_relation = self._normalize_relation_value(relation_value)
                
                member_data = {
                    'name': vals[name_key],
                    'relation': normalized_relation,
                    'blood_group': vals.get(blood_group_key, ''),
                    'sequence': i + 1
                }
                
                if govt_id_key in vals and vals[govt_id_key]:
                    member_data['govt_id_proof'] = vals[govt_id_key]
                    
                if passport_photo_key in vals and vals[passport_photo_key]:
                    member_data['passport_photo'] = vals[passport_photo_key]
                    
                if address_proof_key in vals and vals[address_proof_key]:
                    member_data['address_proof'] = vals[address_proof_key]
                
                family_data.append(member_data)
            
            for key in [name_key, relation_key, blood_group_key, govt_id_key, passport_photo_key, address_proof_key]:
                if key in vals:
                    del vals[key]
        
        return family_data

    @api.model_create_multi
    def create(self, vals_list):
        family_data_list = []
        
        for vals in vals_list:
            family_data = self.process_family_members_data(vals)
            family_data_list.append(family_data)
        
        records = super(ResPartner, self).create(vals_list)
        
        for i, record in enumerate(records):
            family_data = family_data_list[i]
            if family_data:
                for member_data in family_data:
                    member_data['partner_id'] = record.id
                    self.env['family.member'].create(member_data)
            else:
                record._create_default_family_member()
        
        return records

    def _create_default_family_member(self):
        for record in self:
            existing_head = self.env['family.member'].search([
                ('partner_id', '=', record.id),
                ('relation', '=', 'Head')
            ], limit=1)
            
            if not existing_head:
                self.env['family.member'].create({
                    'partner_id': record.id,
                    'name': record.name or '',
                    'relation': 'Head',
                    'blood_group': record.blood_group or False,
                    'sequence': 1,
                })

    def write(self, vals):
        family_data = self.process_family_members_data(vals)
        result = super(ResPartner, self).write(vals)
        
        if family_data:
            for record in self:
                record.family_member_ids.unlink()
                for member_data in family_data:
                    member_data['partner_id'] = record.id
                    self.env['family.member'].create(member_data)
        elif 'name' in vals or 'blood_group' in vals:
            for record in self:
                head_member = self.env['family.member'].search([
                    ('partner_id', '=', record.id),
                    ('relation', '=', 'Head')
                ], limit=1)
                
                if head_member:
                    update_vals = {}
                    if 'name' in vals:
                        update_vals['name'] = vals['name']
                    if 'blood_group' in vals:
                        update_vals['blood_group'] = vals['blood_group']
                    
                    if update_vals:
                        head_member.write(update_vals)
        
        return result

    def button_print_card(self):
        self.env['card.print.log'].create({
            'partner_id': self.id,
            'user_id': self.env.user.id,
        })
        self.write({'application_status': 'Card Printed'})
        return self.env.ref('kanha_census.action_kanha_census_id_card_report').report_action(self)
    
    def action_bulk_print_cards(self):
        approved_records = self.filtered(lambda r: r.application_status == 'Approved but Card Not Printed')
        
        for record in approved_records:
            self.env['card.print.log'].create({
                'partner_id': record.id,
                'user_id': self.env.user.id,
            })
        
        approved_records.write({'application_status': 'Card Printed'})
        
        if approved_records:
            message = f"Successfully printed {len(approved_records)} card(s)."
            if len(approved_records) < len(self):
                skipped = len(self) - len(approved_records)
                message += f" {skipped} record(s) were skipped as they were not in 'Approved but Card Not Printed' status."
        else:
            message = "No cards were printed. Selected records are not in 'Approved but Card Not Printed' status."
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Bulk Print Cards',
                'message': message,
                'type': 'success' if approved_records else 'warning',
                'sticky': False,
            }
        }
    
    def button_approval_for_edit(self):
        self.write({'application_status': 'approved_for_edit'})
        return True
    
    def mail_reminder(self):
        template = self.env.ref('kanha_census.mail_template_visa_reminder', raise_if_not_found=False)
        if not template:
            return
            
        today = date.today()
        weekday = today.weekday()
        week_start_date = today - timedelta(days=weekday)
        week_end_date = today + timedelta(days=(6 - weekday))
        ResPartner = self.env['res.partner']
        partners = ResPartner.sudo().search([('visa_end_date', '>=', week_start_date), ('visa_end_date', '<=', week_end_date)])
        all_partner_data = []
        for partner in partners:
            partner_data={}
            partner_data['name'] =  partner.name
            partner_data['visa_end_date'] = partner.visa_end_date
            all_partner_data.append(partner_data)
        ctx = dict(self.env.context)
        ctx['data'] = [{"all_partner_data": all_partner_data}]
        ctx['subject'] = "Remainder about Visa expiry"
        ctx['email_to'] = self.env["ir.config_parameter"].sudo().get_param("email_recipients")
        ctx['email_from'] = self.env.user.company_id.email
        if template:
            template.with_context(ctx).send_mail(self.id, force_send=True)

    def button_reject(self):
        ctx = {"application_ids": self.ids}
        return {
            "name": ("Reject Product Details Updates"),
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "res_model": "application.reject.reason",
            "target": "new",
            "context": ctx,
        }
    
    def button_approve(self):
        self.send_application_status_mail("approved")
        return self.write({'application_status':'Approved but Card Not Printed'})
    
    def send_rejection_reason_in_mail(self):
        template = self.env.ref('kanha_census.mail_template_application_rejection', raise_if_not_found=False)
        if not template:
            return
            
        ctx = dict(self.env.context)
        ctx['reason'] = self.rejection_reason
        ctx['subject'] = self.name +" Application Rejected - Regards"
        ctx['email_to'] = self.email
        ctx['email_from'] = self.env.user.company_id.email
        if template:
            template.with_context(ctx).send_mail(self.id, force_send=True)

    def unlink(self):
        for partner in self:
            if(partner.application_status in ["draft","rejected"]):
                user = self.env['res.users'].search([('partner_id', '=', partner.id)])
                if user:                
                    if user.id == self.env.user.id:
                        raise AccessError(_("Please contact Administrator to delete this record."))
                    else:
                        user.unlink()                      
            else:
                raise AccessError(_("You can delete only records in draft and rejected state."))            
        for partner in self:
            partner.send_application_status_mail("deleted")
        return super(ResPartner, self).unlink()

    def send_application_status_mail(self, application_status):
        email_to = self.email
        emails = self.env["ir.config_parameter"].sudo().get_param("email_recipients")
        
        template = None
        if(application_status =="approved"):
            template = self.env.ref('kanha_census.mail_template_application_approved', raise_if_not_found=False)
        elif(application_status =="to_approve"):
            template = self.env.ref('kanha_census.mail_template_application_submitted', raise_if_not_found=False)
            if emails:
                email_to = ','.join([emails,email_to])
        elif(application_status =="deleted"):
            template = self.env.ref('kanha_census.mail_template_application_delete', raise_if_not_found=False)
            if emails:
                email_to = ','.join([emails,email_to])
                
        if template:
            ctx = dict(self.env.context)
            ctx['email_to'] = email_to
            ctx['email_from'] = self.env.user.company_id.email
            template.with_context(ctx).send_mail(self.id, force_send=True)  

    def send_deleted_application_mail(self):
        template = self.env.ref('kanha_census.mail_template_application_delete', raise_if_not_found=False)
        if not template:
            return
            
        ctx = dict(self.env.context)
        emails = self.env["ir.config_parameter"].sudo().get_param("email_recipients")
        if emails and self.email:
            email_to = ','.join([emails, self.email])
        else:
            email_to = emails or self.email
        ctx['email_to'] = email_to
        ctx['email_from'] = self.env.user.company_id.email
        if template:
            template.with_context(ctx).send_mail(self.id, force_send=True)

    @api.model
    def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):
        user = self.env.user
        if hasattr(user, 'allowed_locations_ids') and user.allowed_locations_ids and user.has_group('base.group_user'):
            allowed_location_ids = user.allowed_locations_ids.ids
            args += [('kanha_location_id', 'in', allowed_location_ids),('kanha_location_id','!=',False)]
        return super(ResPartner, self)._search(args, offset, limit, order, count, access_rights_uid)
    
    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True):
        user = self.env.user
        if hasattr(user, 'allowed_locations_ids') and user.allowed_locations_ids and user.has_group('base.group_user'):
            allowed_location_ids = user.allowed_locations_ids.ids
            domain = expression.AND([domain, [('kanha_location_id', 'in', allowed_location_ids)]])
        return super(ResPartner, self).read_group(domain, fields, groupby, offset, limit, orderby, lazy)