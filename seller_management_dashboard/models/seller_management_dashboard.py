# -*- coding: utf-8 -*-

from dateutil.relativedelta import relativedelta
import datetime
from pytz import utc
from odoo import models, fields, api, _


class Dashboard(models.Model):
    _inherit = 'stock.picking'

    @api.model
    def check_user_group(self):
        uid = request.session.uid
        user = self.env['res.users'].sudo().search([('id', '=', uid)], limit=1)
        if user.has_group('seller_management.group_sellers_management_manager'):
            return True
        else:
            return False

    @api.model
    def get_product_details(self):
        data = {
            'seller':0,
            'seller_product':0,
            'seller_product_draft':0,
            'seller_product_to_approve':0,
            'seller_product_approve':0,
            'seller_product_rejected':0,
        }
        product = self.env['product.template']
        seller = self.env['res.partner']
        data['seller'] = seller.search_count([('seller','=',True)])
        data['seller_product'] = product.search_count([('seller_id', '!=', False)])
        data['seller_product_draft'] = product.sudo().search_count([('seller_id', '!=', False),('state','=','draft')])
        data['seller_product_to_approve'] = product.sudo().search_count([('seller_id', '!=', False),('state','=','to_approve')])
        data['seller_product_approve'] = product.sudo().search_count([('seller_id', '!=', False),('state','=','approve')])
        data['seller_product_rejected'] = product.sudo().search_count([('seller_id', '!=', False),('state','=','reject')])
        return data
    def _action_view_seller_product(self, mode=False):
        domain = [('seller_id','!=',False)]
        if mode == 'seller_product_draft':
            domain += [('state','=','draft')]

        if mode == 'seller_product_to_approve':
            domain += [('state','=','to_approve')]

        if mode == 'seller_product_approve':
            domain += [('state','=','approve')]

        if mode == 'seller_product_rejected':
            domain += [('state','=','reject')]

        if mode == 'seller_product':
            domain = domain

        if mode == 'seller':
            domain = [('seller', '=', True)]
        
            views = [(self.env.ref('sale.view_order_tree').id, 'list'),
                            (self.env.ref('sale.view_order_form').id, 'form')]
        
            return {'name': ('Sellers'),
                    'type': 'ir.actions.act_window',
                    'res_model': 'res.partner',
                    'view_mode': 'tree,form',
                    'views': views,
                    'domain': domain,
                    'target': 'current'
                }
        views = [(self.env.ref('seller_management.view_seller_tree').id, 'list'),
                        (self.env.ref('seller_management.view_seller_form').id, 'form')]
    
        return {'name': ('Seller Products'),
                'type': 'ir.actions.act_window',
                'res_model': 'product.template',
                'view_mode': 'tree,form',
                'views': views,
                'domain': domain,
                'target': 'current'
            }
    @api.model
    def product_action_dashboard_seller_list(self):
        return self._action_view_seller_product(mode='seller')
    @api.model
    def product_action_dashboard_seller_product_list(self):
        return self._action_view_seller_product(mode='seller_product')
    @api.model
    def sale_action_dashboard_seller_product_draft_list(self):
        return self._action_view_seller_product(mode='seller_product_draft')
    @api.model
    def sale_action_dashboard_seller_product_to_approve_list(self):
        return self._action_view_seller_product(mode='seller_product_to_approve')
    @api.model
    def sale_action_dashboard_seller_product_approve_list(self):
        return self._action_view_seller_product(mode='seller_product_approve')
    @api.model
    def sale_action_dashboard_seller_product_rejected_list(self):
        return self._action_view_seller_product(mode='seller_product_rejected')
    
    @api.model
    def get_sale_order_details(self):
        data = {
            'seller_order':0,
            'shopify_order':0,
            'website_order':0,
            'total_sale_order':0,
            'today_sale':0,
            'last_seven_days':0,
        }
        sale = self.env['sale.order']
        data['seller_order'] = sale.search_count([('seller_id','!=',False)])
        data['shopify_order'] = sale.search_count([('shopify_order_id','!=',False)])
        data['website_order'] = sale.search_count([('is_website_order','=',True)])
        data['total_sale_order'] = sale.search_count([])
        data['today_sale'] = sale.search_count([('date_order', '>=', fields.Datetime.to_string(datetime.date.today()))])
        one_week_ago = fields.Datetime.to_string(datetime.date.today() - relativedelta(days=7))
        data['last_seven_days'] = sale.search_count([('date_order', '>=', one_week_ago)])
        return data
    
    @api.model
    def sale_action_dashboard_shopify_order_list(self):
        return self._action_view_sale_order(mode='shopify_order')
    @api.model
    def sale_action_dashboard_seller_order_list(self):
        return self._action_view_sale_order(mode='seller_order')
    @api.model
    def sale_action_dashboard_website_order_list(self):
        return self._action_view_sale_order(mode='website_order')
    @api.model
    def sale_action_dashboard_total_sale_order_list(self):
        return self._action_view_sale_order(mode='total_sale_order')
    @api.model
    def sale_action_dashboard_today_sale_list(self):
        return self._action_view_sale_order(mode='today_sale')
    @api.model
    def sale_action_dashboard_last_seven_days_list(self):
        return self._action_view_sale_order(mode='last_seven_days')
    
    def _action_view_sale_order(self, mode=False):
        domain = [('company_id', '=', self.env.company.id)]
        one_week_ago = fields.Datetime.to_string(datetime.date.today() - relativedelta(days=7))
        if mode == 'shopify_order':
            domain += [('shopify_order_id','!=',False)]

        if mode == 'seller_order':
            domain += [('seller_id','!=',False)]

        if mode == 'website_order':
            domain += [('is_website_order','=',True)]

        if mode == 'total_sale_order':
            domain = domain

        if mode == 'today_sale':
            domain += [('date_order', '>=', fields.Datetime.to_string(datetime.date.today()))]

        if mode == 'last_seven_days':
            domain += [('date_order', '>=', one_week_ago)]
        
        views = [(self.env.ref('sale.view_order_tree').id, 'list'),
                           (self.env.ref('sale.view_order_form').id, 'form')]
      
        return {'name': ('Sale Orders'),
                'type': 'ir.actions.act_window',
                'res_model': 'sale.order',
                'view_mode': 'tree,form',
                'views': views,
                'domain': domain,
                'target': 'current'
            }
    
    
    @api.model
    def retrieve_transfers(self):
        """ This function returns the values to populate the custom dashboard in
            the stock picking views.
        """
        self.check_access_rights('read')

        result = {
            'unfulfiled': 0,
            'new_orders': 0,
            'ready_to_ship': 0,
            'manifest': 0,
            'delivered': 0,
            'all_orders': 0,
            'wp_awb':0,
            'gen_awb':0,
            'wp_pickup':0,
            'gen_pickup':0,
            'wp_manifest':0,
            'gen_manifest':0,
        }
        # easy counts
        pickings = self.env['stock.picking']
        result['unfulfiled'] = pickings.search_count([('shiprocket_order_status_id.status_code', 'not in', ('5','7','9','16','26','33','39','40','41','42'))])
        result['new_orders'] = pickings.search_count([('shiprocket_order_status_id.status_code', '=', '1'),('is_awb_generated','=',False)])
        result['ready_to_ship'] = pickings.search_count([('shiprocket_order_status_id.status_code', '=', '3'),('is_awb_generated','=',True)])
        result['manifest'] = pickings.search_count([('shiprocket_order_status_id.status_code', '=', '3'),('is_pickup_request_done', '=', True),('is_awb_generated','=',True)])
        result['delivered'] = pickings.search_count([('shiprocket_order_status_id.status_code', '=', '7')])
        result['all_orders'] = pickings.search_count([('shiprocket_order_status_id', '!=', False)])
        bulk_process = self.env['shiprocket.bulk.process']
        result['wp_awb'] = bulk_process.search_count([('state','in',('waiting_awb','awb_created_partially'))])
        result['gen_awb'] = bulk_process.search_count([('state','=','awb_created')])
        result['wp_pickup'] = bulk_process.search_count([('state','in',('waiting_create_pickup','pickup_created_partially'))])
        result['gen_pickup'] = bulk_process.search_count([('state','=','pickup_created')])
        result['wp_manifest'] = bulk_process.search_count([('state','in',('waiting_to_manifest','ready_to_manifest'))])
        result['gen_manifest'] = bulk_process.search_count([('state','=','manifest_generated')])
        return result

    @api.model
    def stock_bulk_action_dashboard_wp_awb_list(self):
        return self._action_view_bulk_process(tranfers='wp_awb')
    @api.model
    def stock_bulk_action_dashboard_gen_awb_list(self):
        return self._action_view_bulk_process(tranfers='gen_awb')
    @api.model
    def stock_bulk_action_dashboard_wp_pickup_list(self):
        return self._action_view_bulk_process(tranfers='wp_pickup')
    @api.model
    def stock_bulk_action_dashboard_gen_pickup_list(self):
        return self._action_view_bulk_process(tranfers='gen_pickup')
    @api.model
    def stock_bulk_action_dashboard_wp_manifest_list(self):
        return self._action_view_bulk_process(tranfers='wp_manifest')
    @api.model
    def stock_bulk_action_dashboard_gen_manifest_list(self):
        return self._action_view_bulk_process(tranfers='gen_manifest')
    
    def _action_view_bulk_process(self, tranfers=False):
        domain = [('company_id', '=', self.env.company.id)]
        
        if tranfers == 'wp_awb':
            domain += [('state','in',('waiting_awb','awb_created_partially'))]

        if tranfers == 'gen_awb':
            domain += [('state','=','awb_created')]

        if tranfers == 'wp_pickup':
            domain += [('state','in',('waiting_create_pickup','pickup_created_partially'))]

        if tranfers == 'gen_pickup':
            domain += [('state','=','pickup_created')]

        if tranfers == 'wp_manifest':
            domain += [('state','in',('waiting_to_manifest','ready_to_manifest'))]

        if tranfers == 'gen_manifest':
            domain += [('state','=','manifest_generated')]
        
        action = self.env["ir.actions.actions"]._for_xml_id("delivery_shiprocket.action_shiprocket_bulk_process")
        action['views'] = [(self.env.ref('delivery_shiprocket.view_shiprocket_bulk_process_tree').id, 'tree'),
                           (self.env.ref('delivery_shiprocket.view_shiprocket_bulk_process_form').id, 'form')]
      
        return {'name': 'Bulk Process',
                'type': 'ir.actions.act_window',
                'res_model': 'shiprocket.bulk.process',
                'view_mode': 'tree,form',
                'views': [(self.env.ref('delivery_shiprocket.view_shiprocket_bulk_process_tree').id, 'list'),
                           (self.env.ref('delivery_shiprocket.view_shiprocket_bulk_process_form').id, 'form')],
                'domain': domain,
                'target': 'current'
            }
    
    @api.model
    def stock_action_dashboard_unfulfiled_list(self):
        return self.search([])._action_view_quotes(tranfers='unfulfiled')
    
    @api.model
    def stock_action_dashboard_new_orders_list(self):
        return self.search([])._action_view_quotes(tranfers='new_orders')

    @api.model
    def stock_action_dashboard_ready_to_ship_list(self):
        return self.search([])._action_view_quotes(tranfers='ready_to_ship')

    @api.model
    def stock_action_dashboard_manifest_list(self):
        return self.search([])._action_view_quotes(tranfers='manifest')

    @api.model
    def stock_action_dashboard_delivered_list(self):
        return self.search([])._action_view_quotes(tranfers='delivered')
    
    @api.model
    def stock_action_dashboard_all_orders_list(self):
        return self.search([])._action_view_quotes(tranfers='all_orders')

    def _action_view_quotes(self, tranfers=False):
        domain = [('company_id', '=', self.env.company.id)]
        if tranfers == 'unfulfiled':
            domain += [('shiprocket_order_status_id.status_code', 'not in', ('5','7','9','16','26','33','39','40','41','42'))]

        if tranfers == 'new_orders':
            domain += [('shiprocket_order_status_id.status_code', '=', '1'),('is_awb_generated','=',False)]

        if tranfers == 'ready_to_ship':
            domain += [('shiprocket_order_status_id.status_code', '=', '3'),('is_awb_generated','=',True)]

        if tranfers == 'manifest':
            domain += [('shiprocket_order_status_id.status_code', '=', '3'),('is_pickup_request_done', '=', True),('is_awb_generated','=',True)]

        if tranfers == 'delivered':
            domain += [('shiprocket_order_status_id.status_code', '=', '7')]

        if tranfers == 'all_orders':
            domain += [('shiprocket_order_status_id', '!=',False)]

        action = self.env["ir.actions.actions"]._for_xml_id("stock.action_picking_tree_all")

        action['domain'] = domain
        
        action['views'] = [(self.env.ref('stock.vpicktree').id, 'tree'),
                           (self.env.ref('stock.view_picking_form').id, 'form')]
        return {'name': 'Transfer',
                'type': 'ir.actions.act_window',
                'res_model': 'stock.picking',
                'view_mode': 'tree,form',
                'views': [(self.env.ref('stock.vpicktree').id, 'list'),
                           (self.env.ref('stock.view_picking_form').id, 'form')],
                'domain': domain,
                'target': 'current'
            }