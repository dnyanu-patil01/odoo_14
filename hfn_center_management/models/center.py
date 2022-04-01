from odoo import fields, models, api
from odoo.exceptions import UserError, ValidationError


class Center(models.Model):
    _name = "res.center"
    _description = "Ashram Center"
    _inherit = ['mail.thread']
    _order = 'name asc'
    

    name = fields.Char('Name', index=True, required=True)
    active = fields.Boolean('Active', default=True)
    state_id = fields.Many2one('res.country.state','State',required=True)
    assigned_user_ids = fields.Many2many("res.users",string="Responsible Users")

    _sql_constraints = [
        ('name_state_uniq', 'unique (name,state_id)', 'The Name of the Center must be unique per State !')
    ]


class CountryState(models.Model):
    _inherit = 'res.country.state'

    center_ids = fields.One2many('res.center', 'state_id', string='Center')

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    center_id = fields.Many2one('res.center', string='Center',index=True, copy=False)

    def _prepare_invoice(self):
        """This method used set center info in customer invoice.
        """
        invoice_val = super(SaleOrder, self)._prepare_invoice()
        if self.center_id:
            invoice_val.update({'center_id': self.center_id.id})
        return invoice_val

class AccountMove(models.Model):
    _inherit = "account.move"

    center_id = fields.Many2one('res.center', string='Center',index=True, copy=False)

class StockMove(models.Model):
    _inherit = "stock.move"

    center_id = fields.Many2one('res.center', string='Center',index=True, copy=False)

    def _get_new_picking_values(self):
        """We need this method to set Center in Stock Picking"""
        res = super(StockMove, self)._get_new_picking_values()
        order_id = self.sale_line_id.order_id
        if order_id.center_id:
            res.update({'center_id': order_id.center_id.id})
        return res

class StockRule(models.Model):
    _inherit = 'stock.rule'

    def _get_custom_move_fields(self):
        """We need this method to set Center in Stock Move"""
        fields = super(StockRule, self)._get_custom_move_fields()
        fields += ['center_id']
        return fields

class StockPicking(models.Model):
    _inherit = "stock.picking"

    center_id = fields.Many2one('res.center', string='Center',index=True, copy=False)

class AccountMove(models.Model):
    _inherit = "account.move"

    center_id = fields.Many2one('res.center', string='Center',index=True, copy=False)

class ResPartner(models.Model):
    _inherit = 'res.partner'

    center_id = fields.Many2one('res.center', string='Center',index=True, copy=False)

class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    #To Pass Center To Stock Move
    def _prepare_procurement_values(self, group_id=False):
        res = super(SaleOrderLine, self)._prepare_procurement_values(group_id)
        if self.order_id.center_id:
            res.update({'center_id':self.order_id.center_id.id})
        return res