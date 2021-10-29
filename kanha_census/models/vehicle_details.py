from odoo import fields, models, api


class Vote(models.Model):
    _name = 'vehicle.details'
    _description = 'Vehicle Details'

    partner_id = fields.Many2one('res.partner', string='Family', ondelete='cascade', required=True)
    vehicle_number = fields.Char(string="Vehicle number")
    vehicle_owner = fields.Char(string="Vehicle owner")
    vehicle_type = fields.Char(string="Vehicle type")
    additional_vehicle_number = fields.Char(string="Additional Vehicle number")