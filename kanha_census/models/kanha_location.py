from odoo import fields, models, api,_
from odoo.exceptions import UserError, ValidationError


class KanhaLocation(models.Model):
    _name = "kanha.location"
    _description = "Kanha Location"
    _parent_name = "parent_id"
    _parent_store = True
    _rec_name = 'complete_name'
    _order = 'complete_name'

    name = fields.Char('Name', index=True, required=True)
    complete_name = fields.Char(
        'Complete Name', compute='_compute_complete_name',
        store=True)
    parent_id = fields.Many2one('kanha.location', 'Parent Location', index=True, ondelete='cascade')
    parent_path = fields.Char(index=True)
    child_id = fields.One2many('kanha.location', 'parent_id', 'Child Location')
    active = fields.Boolean('Active', default=True)
    
    @api.depends('name', 'parent_id.complete_name')
    def _compute_complete_name(self):
        for location in self:
            if location.parent_id:
                location.complete_name = '%s / %s' % (location.parent_id.complete_name, location.name)
            else:
                location.complete_name = location.name
                
    @api.constrains('parent_id')
    def _check_location_recursion(self):
        if not self._check_recursion():
            raise ValidationError(_('You cannot create recursive categories.'))
        return True
    
    @api.model
    def name_create(self, name):
        return self.create({'name': name}).name_get()[0]
    
    def unlink(self):
        main_category = self.env.ref('product.product_category_all')
        if main_category in self:
            raise UserError(_("You cannot delete this product category, it is the default generic category."))
        return super().unlink()


class KanhaHouseNumber(models.Model):
    _name = "kanha.house.number"
    _description = "Kanha House Number"
    _order = "name"

    name = fields.Char('Kanha House Number',required=True)
    kanha_location_id = fields.Many2one('kanha.location',required=True)
    active = fields.Boolean('Active', default=True)
    application_count = fields.Integer(compute='_compute_application_count', string='Related Application Count')


    def unlink(self):
        related_records = self.env['res.partner'].search([('kanha_house_number_id','in',self.ids)])
        if related_records:
            raise UserError(_("You cannot delete this house number.It is used in applications."))
        return super().unlink()

    def _compute_application_count(self):
        self.application_count = len(self.env['res.partner'].search([('kanha_house_number_id','=',self.id)]))

    def action_view_application(self):
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id("kanha_census.kanha_partner_action")
        action['domain'] = [
            ('kanha_house_number_id', '=', self.id),
        ]
        return action