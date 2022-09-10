# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models
from datetime import date, timedelta


class ResPartner(models.Model):
    _inherit = 'res.partner'

    surname = fields.Char(string='Surname')
    gender = fields.Selection([
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other')
    ], required=True)
    date_of_birth = fields.Date(string='Date of birth', required=True)
    town = fields.Char(string='Town/Village Name')
    district = fields.Char(string='District')
    birth_town = fields.Char(string='Birth Town', required=True)
    birth_district = fields.Char(string='Birth District', required=True)
    birth_country_id = fields.Many2one('res.country', string="Birth Country", default=lambda self: self.env['res.country'].search([('code','=','IN')]))
    birth_state_id = fields.Many2one("res.country.state", string='Birth State')
    relation_other = fields.Char(string="Other Relative")
    relation_type = fields.Selection([
        ('Father', 'Father'),
        ('Mother', 'Mother'),
        ('Husband', 'Husband'),
        ('Wife', 'Wife'),
        ('Other', 'Other'),
    ], string='Relation')
    relative_name = fields.Char(string='Name of Relative')
    relative_surname = fields.Char(string='Surname of Relative')
    kanha_location_id = fields.Many2one('kanha.location', string="Kanha Location", required=True)
    house_number = fields.Char(string='House Number')
    kanha_house_number = fields.Char(string='Kanha House Number', required=True)
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
    adhar_card = fields.Binary('Aadhar Card Front', attachment=True, required=True)
    adhar_card_filename = fields.Char()
    adhar_card_back_side = fields.Binary('Aadhar Card Back', attachment=True, required=True)
    adhar_card_back_side_filename = fields.Char()
    age_proof = fields.Binary(string='Age Proof', required=True)
    age_proof_filename = fields.Char()
    address_proof = fields.Binary( string='Address Proof', required=True)
    address_proof_filename = fields.Char()
    application_type = fields.Selection([
        ('New Application', 'New Application'),
        ('Transfer Application', 'Transfer Application'),
    ])
    abhyasi_id = fields.Char(string="Abhyasi ID")
    aadhaar_card_number = fields.Encrypted(string="Aadhar Card Number", required=True, index=True)
    pan_card_number = fields.Encrypted(string="Pan card number")
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
    change_voter_id_address = fields.Selection([
        ('Yes', 'Yes'),
        ('No', 'No'),
    ], string="Do you want to change your Voter Id card Address to Kanha")
    residence_type = fields.Selection([
        ('Rented Place', 'Rented Place'),
        ('Owner', 'Owner'),
    ], string="Residence Type")
    family_members_ids = fields.Many2many('res.partner', 'res_partner_family_members_rel', 'family_member_id', 'partner_id', string='Family Members', readonly=True)
    relative_aadhaar_card_number = fields.Encrypted(string="Relative Aadhar Card Number")
    vehicle_details_ids = fields.One2many('vehicle.details', 'partner_id', string='Vehicle Details')
    already_have_kanha_voter_id = fields.Selection([
        ('Yes', 'Yes'),
        ('No', 'No'),
    ], string="Do you have Voter ID")
    kanha_voter_id_number = fields.Encrypted(string="Existing Voter ID Number")
    kanha_voter_id_image = fields.Binary('Voter ID Front Image', attachment=True, required=True)
    kanha_voter_id_image_filename = fields.Char()
    kanha_voter_id_back_image = fields.Binary('Voter ID Back Image', attachment=True, required=True)
    kanha_voter_id_back_image_filename = fields.Char()
    declaration_form = fields.Binary('Declaration Form File', attachment=True, required=True)
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
    visa_start_date = fields.Date(string='Visa Start Date', required=True)
    visa_end_date = fields.Date(string='Visa End Date', required=True)
    visa_type = fields.Selection([
        ('Employment', 'Employment'),
        ('Tourist', 'Tourist'),
        ('Transit', 'Transit'),
        ('Business', 'Business'),
        ('Medical', 'Medical'),
    ])


    def mail_reminder(self):
        """
        Cron to send email regarding the Visa expiry
        """
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
