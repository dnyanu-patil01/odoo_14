# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    surname = fields.Char(string='Surname')
    gender = fields.Selection([
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other')
    ], required=True)
    date_of_birth = fields.Date(string='Date of birth', required=True)
    town = fields.Char(string='Town/Village Name', required=True)
    district = fields.Char(string='District', required=True)
    birth_town = fields.Char(string='Birth Town/Village Name', required=True)
    birth_district = fields.Char(string='Birth District', required=True)
    birth_state_id = fields.Many2one("res.country.state", string='Birth State', ondelete='restrict')
    relation_type = fields.Selection([
        ('Father', 'Father'),
        ('Mother', 'Mother'),
        ('Husband', 'Husband'),
        ('Wife', 'Wife'),
        ('Other', 'Other')
    ])
    relative_name = fields.Char(string='Relative Name')
    relative_surname = fields.Char(string='Relative Surname')
    kanha_location_id = fields.Many2one('kanha.location', string="Kanha Location", required=True)
    house_number = fields.Char(string='House Number', required=True)
    kanha_house_number = fields.Char(string='Kanha House Number', required=True)
    resident_of_kanha_from_date = fields.Date(string='Resident of Kanha From Date', required=True)
    voter_number = fields.Char(string="Voter Number", required=True)
    assembly_constituency = fields.Char(string="Assembly Constituency", required=True)
    locality = fields.Char(string="Locality", required=True)
    post_office = fields.Char(string="Post Office", required=True)
    passport_photo = fields.Image(string="Passport Photo", required=True)
    passport_photo_filename = fields.Char()
    adhar_card = fields.Binary('Adhar Card', attachment=True, required=True)
    adhar_card_filename = fields.Char()
    age_proof = fields.Binary(string='Age Proof', required=True)
    age_proof_filename = fields.Char()
    address_proof = fields.Binary( string='Address Proof', required=True)
    address_proof_filename = fields.Char()
    age_declaration_form = fields.Binary(string='Age Declaration Form', required=True)
    age_declaration_form_filename = fields.Char()
    application_type = fields.Selection([
        ('New Application', 'New Application'),
        ('Transfer Application', 'Transfer Application'),
    ], required=True)
    abhyasi_id = fields.Char(string="Abhyasi ID", required=True)
    aadhaar_card_number = fields.Char(string="Aadhar Card Number", required=True)
    pan_card_number = fields.Char(string="Pan card number", required=True)
    members_count = fields.Char(string="How many members staying with you?", required=True)
    citizenship = fields.Selection([
        ('Indian', 'Indian'),
        ('NRI', 'NRI'),
        ('Overseas', 'Overseas')
    ], required=True)
    passport_number = fields.Char(string="Passport Number", required=True)
    vehicle_number = fields.Char(string="Vehicle number", required=True)
    vehicle_owner = fields.Char(string="Vehicle owner", required=True)
    vehicle_type = fields.Char(string="Vehicle type", required=True)
    additional_vehicle_number = fields.Char(string="Additional Vehicle number", required=True)
    work_profile = fields.Selection([
        ('Resident', 'Resident'),
        ('Volunteer', 'Volunteer'),
        ('Employee', 'Employee'),
        ('NMR', 'NMR'),
        ('Contractor', 'Contractor')
    ], required=True)
    change_voter_id_address = fields.Selection([
        ('Yes', 'Yes'),
        ('No', 'No'),
    ], string="Do you want to change your Voter Id card Address", required=True)
    room_details = fields.Selection([
        ('Rented', 'Rented'),
        ('Owner', 'Owner'),
    ], string="Do you want to change your Voter Id card Address", required=True)
    family_members_ids = fields.Many2many('res.partner', 'res_partner_family_members_rel', 'family_member_id', 'partner_id', string='Family Members')
    relative_aadhaar_card_number = fields.Char(string="Relative Aadhar Card Number")
