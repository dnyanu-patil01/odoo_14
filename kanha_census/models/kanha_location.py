from odoo import fields, models, api
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