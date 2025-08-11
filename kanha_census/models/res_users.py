from odoo import models, fields

class ResUsers(models.Model):
    _inherit = 'res.users'

    allowed_locations_ids = fields.Many2many('kanha.location', string='Allowed Locations')