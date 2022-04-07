from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError


class M2MTransfers(models.Model):
    _name = 'm2m.transfers'
    _description = 'Material To Material Transfers'

    name = fields.Char(
        'Reference', default=lambda self: self.env['ir.sequence'].next_by_code('m2m.transfers') or _('New'),
        required=True)
    current_product_id = fields.Many2one('product.product', string='Current Product', required=True)
    quantity = fields.Float(string='Quantity', required=True)
    current_location_id = fields.Many2one('stock.location', 'Current Location', domain=[('usage', '=', 'internal')], required=True)
    new_product_id = fields.Many2one('product.product', string='New Product', required=True)
    new_location_id = fields.Many2one('stock.location', 'New Location', domain=[('usage', '=', 'internal')], required=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Confirmed'),
        ('cancel', 'Cancelled'),
    ], string='Status', default='draft')
    
    @api.constrains('quantity')
    def _check_quantity(self):
        if any([m.quantity <= 0 for m in self]):
            raise ValidationError(_('Quantity should be more than 0.'))
    
    def _prepare_move_values(self,val):
        """
        This function prepares move values.
        """
        return {
            'name': val['name'],
            'location_id': val['location_id'],
            'location_dest_id': val['location_dest_id'],
            'product_id': val['product_id'],
            'product_uom': val['product_uom'],
            'product_uom_qty': self.quantity,
            'state':'done',
            'move_line_ids': [(0, 0, {'product_id': val['product_id'],
                                           'product_uom_id': val['product_uom'], 
                                           'qty_done': self.quantity,
                                            'location_id': val['location_id'],
                                            'location_dest_id': val['location_dest_id'],
                                            })],
        }
    
    def button_confirm(self):
        """ Creates stock move entry """
        virtual_grown_plants_location = self.env.ref('material_to_material_transfer.virtual_grown_plants_location', raise_if_not_found=False).id
        values = [{'name': self.name, 'product_id': self.current_product_id.id, 'location_id': self.current_location_id.id, 'location_dest_id': virtual_grown_plants_location, 'product_uom':self.current_product_id.uom_id.id},
                  {'name': self.name, 'product_id': self.new_product_id.id, 'location_id': virtual_grown_plants_location, 'location_dest_id': self.new_location_id.id,'product_uom':self.new_product_id.uom_id.id}]
        for val in values:
            stock_move = self.env['stock.move'].create(self._prepare_move_values(val))
            stock_move._action_confirm()
            stock_move._action_assign()
            stock_move._action_done()
        self.write({'state': 'confirm'})

    @api.onchange('current_product_id')
    def _onchange_current_product_id(self):
        """ Lists selected product's location. """

        if self.current_product_id:
            self.current_location_id = False
            self.new_product_id = False
            product_location_ids = self.env['stock.quant'].search([('product_id', '=', self.current_product_id.id)]).location_id.ids
            return {'domain': {'current_location_id': [('id', 'in', product_location_ids), ('usage', '=', 'internal')]}}
    
    def action_cancel(self):
        self.write({'state': 'cancel'})
        
    def unlink(self):
        if any(record.state not in ('draft', 'cancel') for record in self):
            raise UserError(_('You can only delete draft records.'))
        return super(M2MTransfers, self).unlink()
    
    def button_draft(self):
        self.write({'state': 'draft'})
        return {}
