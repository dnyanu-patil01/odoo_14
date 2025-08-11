from odoo import fields, models, api
from odoo.exceptions import ValidationError


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
    fasttag_rfid_no = fields.Char("FastTag RFID Number")
    
    # @api.constrains('fasttag_rfid_no')
    # def _check_fasttag_rfid_no(self):
    #     for record in self:
    #         try:
    #             val = int(record.fasttag_rfid_no)
    #         except ValueError:
    #             raise ValidationError("Please add only numeric digits in Fasttag RFID number!")