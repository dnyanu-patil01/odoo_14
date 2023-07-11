from odoo import fields, models


class VehicleDetails(models.Model):
    _name = 'vehicle.details'
    _description = 'Vehicle Details'

    partner_id = fields.Many2one('res.partner', string='Family', ondelete='cascade', required=True)
    vehicle_number = fields.Char(string="Vehicle number")
    vehicle_owner = fields.Char(string="Vehicle owner")
    vehicle_type = fields.Selection([
        ('Two Wheeler', 'Two Wheeler'),
        ('Four Wheeler', 'Four Wheeler'),
    ])
    fasttag_rfid_no = fields.Integer("FastTag RFID Number")

