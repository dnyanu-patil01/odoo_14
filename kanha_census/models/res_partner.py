# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from datetime import date, timedelta, datetime
from odoo.exceptions import AccessError
import logging
_logger = logging.getLogger(__name__)
from odoo.osv import expression


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
    birth_town = fields.Char(string='Birth Town', required=True)
    birth_district = fields.Char(string='Birth District')
    birth_country_id = fields.Many2one('res.country', string="Birth Country", default=lambda self: self.env['res.country'].search([('code','=','IN')]))
    birth_state_id = fields.Many2one("res.country.state", string='Birth State')
    relation_other = fields.Char(string="Other Relative")
    relation_type = fields.Selection([
        ('Father', 'Father'),
        ('Mother', 'Mother'),
        ('Husband', 'Husband'),
        ('Wife', 'Wife'),
        ('Other', 'Other'),
        ('Sister', 'Sister'),
        ('Brother', 'Brother')
    ], string='Relation')
    relative_name = fields.Char(string='Name of Relative')
    relative_surname = fields.Char(string='Surname of Relative')
    kanha_location_id = fields.Many2one('kanha.location', string="Kanha Location", required=True)
    house_number = fields.Char(string='House Number')
    kanha_house_number_id = fields.Many2one('kanha.house.number', string='Kanha House Number', required=True)
    resident_of_kanha_from_date = fields.Date(string='Resident of Kanha From Date', required=True)
    existing_voter_id_number = fields.Char(string="Existing Voter ID Number", required=True)
    assembly_constituency = fields.Char(string="Assembly Constituency")
    locality = fields.Char(string="Locality")
    post_office = fields.Char(string="Post Office")
    indian_visa = fields.Image(string="Photo of Indian Visa",attachment=True)
    indian_visa_filename = fields.Char()
    passport_photo = fields.Image(string="Passport Size Photo", required=True)
    passport_photo_filename = fields.Char()
    passport_id_image = fields.Image(string="Passport ID", attachment=True)
    passport_id_image_filename = fields.Char()
    adhar_card = fields.Binary('Aadhar Card Front', attachment=True)
    adhar_card_filename = fields.Char()
    adhar_card_back_side = fields.Binary('Aadhar Card Back', attachment=True)
    adhar_card_back_side_filename = fields.Char()
    age_proof = fields.Binary(string='Age Proof')
    age_proof_filename = fields.Char()
    address_proof = fields.Binary( string='Address Proof')
    address_proof_filename = fields.Char()
    application_type = fields.Selection([
        ('New Application', 'New Application'),
        ('Transfer Application', 'Transfer Application'),
    ])
    abhyasi_id = fields.Char(string="Abhyasi ID")
    aadhaar_card_number = fields.Encrypted(string="Aadhar Card Number", index=True)
    members_count = fields.Char(string="How many members staying with you?")
    citizenship = fields.Selection([
        ('Indian', 'Indian'),
        ('Overseas', 'Overseas')
    ], required=True)
    passport_number = fields.Encrypted(string="Passport Number")
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
    family_members_ids = fields.Many2many('res.partner', 'res_partner_family_members_rel', 'family_member_id', 'partner_id',  string='Family Members', readonly=True ,compute='_compute_family_members')
    relative_aadhaar_card_number = fields.Encrypted(string="Relative Aadhar Card Number")
    is_geoadmin = fields.Boolean(
        string='Is Geo Admin', 
        compute='_compute_is_geoadmin', 
        store=False
    )
    card_print_log_ids = fields.One2many('card.print.log', 'partner_id', string='Card Print Logs')

    @api.depends('user_id')  
    def _compute_is_geoadmin(self):
        group_geo_admin = self.env.ref('kanha_census.group_geoadmin_access')
        for record in self:
            record.is_geoadmin = group_geo_admin in self.env.user.groups_id

    @api.depends('kanha_house_number_id')
    def _compute_family_members(self):
        for record in self:
            family_members = self.search([('kanha_house_number_id', '=', record.kanha_house_number_id.id)]).filtered(lambda member: member.id != record.id)
            record.family_members_ids = [(6, 0, family_members.ids)]

    vehicle_details_ids = fields.One2many('vehicle.details', 'partner_id', string='Vehicle Details')
    already_have_kanha_voter_id = fields.Selection([
        ('Yes', 'Yes'),
        ('No', 'No'),
    ], string="Do you have Voter ID")
    kanha_voter_id_number = fields.Encrypted(string="Existing Voter ID Number")
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
    state = fields.Selection([
        ('saved_not_submitted', 'Saved Not Submitted'),
        ('submitted', 'Submitted'),
        ], string='Status', readonly=True, copy=False, index=True, tracking=3, default='saved_not_submitted')
    application_reference_no = fields.Char(string='If already applied for Kanha voter ID, please provide application reference number')
    passport_front_image = fields.Image(string="Passport Front Image", attachment=True)
    passport_front_image_filename = fields.Char()
    passport_back_image = fields.Image(string="Passport Back Image", attachment=True)
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
    ],default="draft")
    rejection_reason = fields.Text("Reason For Rejection")
    birth_state_textfield = fields.Char(string="Birth State")
    birth_country_name = fields.Char(related="birth_country_id.name", string="Birth Country Name")
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
    ], string='Do you need Voter ID in Kannah')
    is_preceptor = fields.Selection([
        ('Yes', 'Yes'),
        ('No', 'No')],
        string='Are you a preceptor?'
    )
    year_of_birth = fields.Integer(string="Year Of Birth",readonly=True)
    
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
        template = self.env.ref('kanha_census.mail_template_visa_reminder')
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
        template = self.env.ref('kanha_census.mail_template_application_rejection')
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
        if(application_status =="approved"):
            template = self.env.ref('kanha_census.mail_template_application_approved')
        elif(application_status =="to_approve"):
            template = self.env.ref('kanha_census.mail_template_application_submitted')
            if emails:
                email_to = ','.join([emails,email_to])
        elif(application_status =="deleted"):
            template = self.env.ref('kanha_census.mail_template_application_delete')
            if emails:
                email_to = ','.join([emails,email_to])
        ctx = dict(self.env.context)
        ctx['email_to'] = email_to
        ctx['email_from'] = self.env.user.company_id.email
        if template:
            template.with_context(ctx).send_mail(self.id, force_send=True)  

    def send_deleted_application_mail(self):
        template = self.env.ref('kanha_census.mail_template_application_delete')
        ctx = dict(self.env.context)
        emails = self.env["ir.config_parameter"].sudo().get_param("email_recipients")
        resident_email = self.email
        email_to = ','.join([emails,resident_email])
        ctx['email_to'] = email_to
        ctx['email_from'] = self.env.user.company_id.email
        if template:
            template.with_context(ctx).send_mail(self.id, force_send=True) 

    @api.model
    def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):
        user = self.env.user
        if user.allowed_locations_ids and user.has_group('base.group_user'):
            allowed_location_ids = user.allowed_locations_ids.ids
            args += [('kanha_location_id', 'in', allowed_location_ids),('kanha_location_id','!=',False)]
        return super(ResPartner, self)._search(args, offset, limit, order, count, access_rights_uid)
    
    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True):
        user = self.env.user
        if user.allowed_locations_ids and user.has_group('base.group_user'):
            allowed_location_ids = user.allowed_locations_ids.ids
            domain = expression.AND([domain, [('kanha_location_id', 'in', allowed_location_ids)]])
        return super(ResPartner, self).read_group(domain, fields, groupby, offset, limit, orderby, lazy)