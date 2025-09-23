from odoo import fields, models, api, _
from datetime import date, timedelta, datetime
from odoo.exceptions import AccessError, ValidationError
import logging
_logger = logging.getLogger(__name__)
from odoo.osv import expression
import re
import base64
from werkzeug.datastructures import FileStorage


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
    ], string='Blood Group', required=True)
    mobile = fields.Char(string='Mobile Number', required=True)
    emergency_contact = fields.Char(string='Emergency Contact', required=True)
    sequence = fields.Integer(string='Sequence', default=1)
    govt_id_proof = fields.Binary('Government ID Proof', attachment=True)
    govt_id_proof_filename = fields.Char()
    passport_photo = fields.Binary('Passport Size Photo', attachment=True, required=True)
    passport_photo_filename = fields.Char()
    address_proof = fields.Binary('Kanha Address Proof', attachment=True)
    address_proof_filename = fields.Char()

    @api.constrains('mobile')
    def _check_mobile_number(self):
        for record in self:
            if record.mobile and not re.match(r'^[6789]\d{9}$', record.mobile):
                raise ValidationError(_("Mobile number must be a valid 10-digit Indian number starting with 6, 7, 8, or 9."))

    @api.constrains('emergency_contact')
    def _check_emergency_contact(self):
        for record in self:
            if record.emergency_contact and not re.match(r'^[6789]\d{9}$', record.emergency_contact):
                raise ValidationError(_("Emergency contact must be a valid 10-digit Indian number starting with 6, 7, 8, or 9."))
