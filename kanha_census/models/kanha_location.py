from odoo import fields, models


class KanhaLocation(models.Model):
    _name = 'kanha.location'

    name = fields.Char(string='Name')