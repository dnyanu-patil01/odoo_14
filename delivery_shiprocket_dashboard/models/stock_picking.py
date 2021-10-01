from dateutil.relativedelta import relativedelta
import datetime

from odoo import api, fields, models


class StockPickingDashboard(models.Model):
    _inherit = "stock.picking"

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
        }
        # easy counts
        pickings = self.env['stock.picking']
        result['unfulfiled'] = pickings.search_count([('shiprocket_order_status_id.status_code', 'not in', ('5','7','9','16','26','33','39','40','41','42'))])
        result['new_orders'] = pickings.search_count([('shiprocket_order_status_id.status_code', '=', '1'),('is_awb_generated','=',False)])
        result['ready_to_ship'] = pickings.search_count([('shiprocket_order_status_id.status_code', '=', '3'),('is_awb_generated','=',True)])
        result['manifest'] = pickings.search_count([('shiprocket_order_status_id.status_code', '=', '3'),('is_pickup_request_done', '=', True),('is_awb_generated','=',True)])
        result['delivered'] = pickings.search_count([('shiprocket_order_status_id.status_code', '=', '7')])
        result['all_orders'] = pickings.search_count([('shiprocket_order_status_id', '!=', False)])
        # bulk_process = self.env['shiprocket.bulk.process']
        # result['wp_awb'] = bulk_process.search_count([('state','in',('waiting_awb','awb_created_partially'))])
        # result['gen_awb'] = bulk_process.search_count([('state','=','awb_created')])
        # result['wp_pickup'] = bulk_process.search_count([('state','in',('waiting_create_pickup','pickup_created_partially'))])
        # result['gen_pickup'] = bulk_process.search_count([('state','=','pickup_created')])
        # result['wp_manifest'] = bulk_process.search_count([('state','in',('waiting_to_manifest','ready_to_manifest'))])
        # result['gen_manifest'] = bulk_process.search_count([('state','=','manifest_generated')])
        return result

    # @api.model
    # def stock_bulk_action_dashboard_wp_awb_list(self):
    #     return self.search([])._action_view_bulk_process(tranfers='wp_awb')
    # @api.model
    # def stock_bulk_action_dashboard_gen_awb_list(self):
    #     return self.search([])._action_view_bulk_process(tranfers='gen_awb')
    # @api.model
    # def stock_bulk_action_dashboard_wp_pickup_list(self):
    #     return self.search([])._action_view_bulk_process(tranfers='wp_pickup')
    # @api.model
    # def stock_bulk_action_dashboard_gen_pickup_list(self):
    #     return self.search([])._action_view_bulk_process(tranfers='gen_pickup')
    # @api.model
    # def stock_bulk_action_dashboard_wp_manifest_list(self):
    #     return self.search([])._action_view_bulk_process(tranfers='wp_manifest')
    # @api.model
    # def stock_bulk_action_dashboard_gen_manifest_list(self):
    #     return self.search([])._action_view_bulk_process(tranfers='gen_manifest')
    
    # def _action_view_bulk_process(self, tranfers=False):
    #     domain = [('company_id', '=', self.env.company.id)]
        
    #     if tranfers == 'wp_awb':
    #         domain += [('state','in',('waiting_awb','awb_created_partially'))]

    #     if tranfers == 'gen_awb':
    #         domain += [('state','=','awb_created')]

    #     if tranfers == 'wp_pickup':
    #         domain += [('state','in',('waiting_create_pickup','pickup_created_partially'))]

    #     if tranfers == 'gen_pickup':
    #         domain += [('state','=','pickup_created')]

    #     if tranfers == 'wp_manifest':
    #         domain += [('state','in',('waiting_to_manifest','ready_to_manifest'))]

    #     if tranfers == 'gen_manifest':
    #         domain += [('state','=','manifest_generated')]
        
    #     action = self.env["ir.actions.actions"]._for_xml_id("delivery_shiprocket.action_shiprocket_bulk_process")
    #     action['views'] = [(self.env.ref('delivery_shiprocket.view_shiprocket_bulk_process_tree').id, 'tree'),
    #                        (self.env.ref('delivery_shiprocket.view_shiprocket_bulk_process_form').id, 'form')]
      
    #     return action
    
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
        return action
