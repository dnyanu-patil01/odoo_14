# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from datetime import datetime, date, timedelta
from odoo.exceptions import Warning
from itertools import groupby
from operator import itemgetter

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    seller_group_id = fields.Many2one("seller.group")
    picking_id = fields.Many2one('stock.picking','Stock Transfer',readonly=True)

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

class StockPicking(models.Model):
    _inherit = 'procurement.group'

    seller_group_id = fields.Many2one("seller.group")
    seller_id = fields.Many2one("res.partner")

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    seller_group_id = fields.Many2one("seller.group")
    sale_order_ids = fields.One2many("sale.order",'picking_id')

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