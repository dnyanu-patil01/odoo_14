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
    voter_number = fields.Char(string="Voter ID Number")
    existing_voter_id_number = fields.Char(string="Existing Voter ID Number", required=True)
    assembly_constituency = fields.Char(string="Assembly Constituency", required=True)
    locality = fields.Char(string="Locality", required=True)
    post_office = fields.Char(string="Post Office", required=True)
    passport_photo = fields.Image(string="Passport Photo", required=True)
    passport_photo_filename = fields.Char()
    adhar_card = fields.Binary('Adhar Card Front', attachment=True, required=True)
    adhar_card_filename = fields.Char()
    adhar_card_back_side = fields.Binary('Adhar Card Back', attachment=True, required=True)
    adhar_card_back_side_filename = fields.Char()
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
    abhyasi_id = fields.Char(string="Abhyasi ID")
    aadhaar_card_number = fields.Char(string="Aadhar Card Number", required=True)
    pan_card_number = fields.Char(string="Pan card number")
    members_count = fields.Char(string="How many members staying with you?")
    citizenship = fields.Selection([
        ('Indian', 'Indian'),
        ('NRI', 'NRI'),
        ('Overseas', 'Overseas')
    ], required=True)
    passport_number = fields.Char(string="Passport Number")
    vehicle_number = fields.Char(string="Vehicle number")
    vehicle_owner = fields.Char(string="Vehicle owner")
    vehicle_type = fields.Char(string="Vehicle type")
    additional_vehicle_number = fields.Char(string="Additional Vehicle number")
    work_profile = fields.Selection([
        ('Resident', 'Resident'),
        ('Volunteer', 'Volunteer'),
        ('Employee', 'Employee'),
        ('NMR', 'NMR'),
        ('Contractor', 'Contractor')
    ])
    change_voter_id_address = fields.Selection([
        ('Yes', 'Yes'),
        ('No', 'No'),
    ], string="Do you want to change your Voter Id card Address")
    residence_type = fields.Selection([
        ('Rented Place', 'Rented Place'),
        ('Owner', 'Owner'),
    ], string="Room Details")
    family_members_ids = fields.Many2many('res.partner', 'res_partner_family_members_rel', 'family_member_id', 'partner_id', string='Family Members')
    relative_aadhaar_card_number = fields.Char(string="Relative Aadhar Card Number")
    vehicle_details_ids = fields.One2many('vehicle.details', 'partner_id', string='Vehicle Details')
    birth_country_id = fields.Many2one('res.country', string="Birth Country")
    already_have_kanha_voter_id = fields.Selection([
        ('Yes', 'Yes'),
        ('No', 'No'),
    ], string="Already Have Kanha Voter ID")
    kanha_voter_id_number = fields.Char(string="Kanha Voter ID Number", required=True)
    kanha_voter_id_image = fields.Binary('Kanha Voter ID Image', attachment=True, required=True)
    kanha_voter_id_image_filename = fields.Char()
    
    voter_id_file = fields.Binary('Voter ID/EPIC File', attachment=True, required=True)
    voter_id_file_filename = fields.Char()
    declaration_form = fields.Binary('Declaration Form File', attachment=True, required=True)
    declaration_form_filename = fields.Char()

    need_new_kanha_voter_id = fields.Selection([
        ('Yes', 'Yes'),
        ('No', 'No'),
    ], string="Need New Kanha Voter ID")

    # _sql_constraints = [
    #     ('aadhaar_card_number_unique', 'UNIQUE(aadhaar_card_number)', 'An Adhar Card Number must be unique!'),
    # ]
