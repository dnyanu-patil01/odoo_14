# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from datetime import datetime, date, timedelta
from odoo.exceptions import Warning
from itertools import groupby
from operator import itemgetter, mod

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    seller_group_id = fields.Many2one("seller.group")
    picking_id = fields.Many2one('stock.picking','Stock Transfer',readonly=True)
    merge_delivery_count = fields.Integer(string='Delivery Orders', compute='_compute_merged_picking_ids')
    
    def merge_quotations(self,order_ids):
        # To Get All Order Lines Of The Orders
        all_order_lines = self.env['sale.order.line'].search([('seller_group_id','!=',False),('order_id','in',order_ids)],order="seller_group_id")
        #To Get Unqiue Seller Group ID Mapped In The Order Lines
        seller_group_ids = list(set(all_order_lines.mapped('seller_group_id').ids))
        order_line_values = []
        #Dict To Store Sale Order Id and Original Order ID of every sale order line
        for key, values in groupby(all_order_lines, lambda l: (l.seller_group_id)):
            for val in values:
                order_line_values.append({'sale_line_id':val,'order_id':val.order_id.id})
        #Based On Seller Group,Replace Order line vals with single order id and validating it to create grouped Delivery Order
        for seller_group in seller_group_ids:
            seller_group_order_lines = all_order_lines.filtered(lambda line:line.seller_group_id.id == seller_group)
            sale_order_id = seller_group_order_lines.mapped('order_id').ids[0]
            for order in seller_group_order_lines.mapped('order_id'):
                order.order_line.write({'order_id':sale_order_id})
            merged_so = self.browse(sale_order_id)
            merged_so.action_confirm()
        #To Rewrite Original Order ID Back In Sale Order Lines
        for sale_line in order_line_values:
            self.browse(sale_line['order_id']).write({"state":"sale"})
            sale_line['sale_line_id'].write({'order_id':sale_line['order_id']})
        # To Validate Sale Order Without Seller Group or Seller ID
        so_without_grouped_seller = self.env['sale.order.line'].search([('seller_group_id','=',False),('order_id','in',order_ids)]).mapped('order_id')
        for order in so_without_grouped_seller:
            order.action_confirm()
        #To Map Delivery Order In Sale Order
        for order in all_order_lines.mapped('order_id'):
            picking_id = self.env['stock.move'].search([('sale_line_id','in',order.order_line.ids)]).mapped('picking_id')
            if picking_id:
                order.write({'picking_id':picking_id.id})
        return True
                       
    def action_view_merged_delivery(self):
        action = self.env["ir.actions.actions"]._for_xml_id("seller_management.seller_stock_transfer_action")
        if len(self.picking_id.sale_order_ids) > 1:
            action['domain'] = [('id', '=', self.picking_id.id),('seller_group_id.seller_ids','in',self.seller_id.id)]
        elif self.picking_id:
            form_view = [(self.env.ref('seller_management.view_seller_stock_picking_form').id, 'form')]
            if 'views' in action:
                action['views'] = form_view + [(state,view) for state,view in action['views'] if view != 'form']
            else:
                action['views'] = form_view
            action['res_id'] = self.picking_id.id
        # Prepare the context.
        picking_id = self.picking_id.filtered(lambda l: l.picking_type_id.code == 'outgoing')
        if picking_id:
            picking_id = picking_id[0]
        else:
            picking_id = self.picking_id
        action['context'] = dict(self._context, default_seller_id=self.seller_id.id, default_picking_type_id=picking_id.picking_type_id.id, default_origin=self.name, default_group_id=picking_id.group_id.id)
        return action

    @api.depends('picking_id')
    def _compute_merged_picking_ids(self):
        for order in self:
            order.merge_delivery_count = len(order.picking_id.sale_order_ids)

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    seller_group_id = fields.Many2one("seller.group")

    @api.onchange('product_id')
    def product_id_change(self):
        res = super(SaleOrderLine, self).product_id_change()
        if self.product_id.seller_id.seller_group_id:
            self.seller_group_id = self.product_id.seller_id.seller_group_id.id
        else:
            self.seller_group_id = False
        return res

    def _prepare_procurement_group_vals(self):
        if self.product_id.seller_id.seller_group_id:
            name = self.product_id.seller_id.seller_group_id.name
            return {
                'name': name,
                'move_type': self.order_id.picking_policy,
                'seller_group_id': self.product_id.seller_id.seller_group_id.id,
                'partner_id': self.order_id.partner_shipping_id.id,
                'sale_id': self.order_id.id,
            }
        else:
            return {
                'name': self.order_id.name,
                'move_type': self.order_id.picking_policy,
                'sale_id': self.order_id.id,
                'partner_id': self.order_id.partner_shipping_id.id,
            }

    def _prepare_procurement_values(self, group_id=False):
        res = super(SaleOrderLine, self)._prepare_procurement_values(group_id)
        if self.product_id.seller_id.seller_group_id:
            res.update({'seller_group_id':self.product_id.seller_id.seller_group_id.id})
        return res

    def write(self, values):
        lines = self.env['sale.order.line']
        res = super(SaleOrderLine, self).write(values)
        if 'seller_group_id' in values:
            lines = self
        if lines:
            previous_product_uom_qty = {line.id: line.product_uom_qty for line in lines}
            lines._action_launch_stock_rule(previous_product_uom_qty)
        return res


class StockMove(models.Model):
    _inherit = 'stock.move'

    seller_group_id = fields.Many2one("seller.group")

    def _get_new_picking_values(self):
        vals = super(StockMove, self)._get_new_picking_values()
        if self.sale_line_id.seller_group_id:
            vals['seller_group_id'] = self.sale_line_id.seller_group_id.id
        return vals

    def _key_assign_picking(self):
        keys = super(StockMove, self)._key_assign_picking()
        return keys + (self.sale_line_id.seller_group_id,)


    def _search_picking_for_assignation(self):
        self.ensure_one()
        picking = super(StockMove, self)._search_picking_for_assignation()
        if self.sale_line_id and self.sale_line_id.seller_group_id:
            picking = picking.filtered(lambda l: l.seller_id.seller_group_id.id == self.sale_line_id.seller_group_id.id)
            if picking:
                picking = picking[0]
        return picking

class ProcurementGroup(models.Model):
    _inherit = 'procurement.group'

    seller_group_id = fields.Many2one("seller.group")
    seller_id = fields.Many2one("res.partner")

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    seller_group_id = fields.Many2one("seller.group")
    sale_order_ids = fields.One2many("sale.order",'picking_id')
    group_seller_ids = fields.Many2many("res.partner")
    merge_so_count = fields.Integer(string='Orders', compute='_compute_merged_so_ids')

    @api.depends('sale_order_ids')
    def _compute_merged_so_ids(self):
        for pick in self:
            pick.merge_so_count = len(pick.sale_order_ids)

    def _get_new_picking_values(self):
        """We need this method to set Seller in Stock Picking"""
        res = super(StockMove, self)._get_new_picking_values()
        if self.sale_line_id.seller_id.seller_group_id:
            res.update({
                'seller_group_id': self.sale_line_id.seller_id.seller_group_id.id,
                        })
        return res

class StockRule(models.Model):
    _inherit = 'stock.rule'

    def _get_custom_move_fields(self):
        """We need this method to set Seller in Stock Move"""
        fields = super(StockRule, self)._get_custom_move_fields()
        fields += ['seller_group_id']
        return fields

class AccountMove(models.Model):
    _inherit = 'account.move'

    picking_id = fields.Many2one('stock.picking','Delivery Order',readonly=True)