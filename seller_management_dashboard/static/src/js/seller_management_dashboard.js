odoo.define('hrms_dashboard.DashboardRewrite', function (require) {
"use strict";

var AbstractAction = require('web.AbstractAction');
var core = require('web.core');
var rpc = require('web.rpc');
var session = require('web.session');
var web_client = require('web.web_client');
var _t = core._t;
var QWeb = core.qweb;



var SellerManagementDashboard = AbstractAction.extend({

    template: 'SellerManagementDashboardMain',
    cssLibs: [
        '/seller_management_dashboard/static/src/css/lib/nv.d3.css'
    ],
    jsLibs: [
        '/seller_management_dashboard/static/src/js/lib/d3.min.js'
    ],
    events: {
        'click .o_dashboard_action': '_onDashboardActionClicked',
    },
    custom_events: {
        dashboard_open_action: '_onDashboardOpenAction',
    },

    init: function(parent, context) {

        this._super(parent, context);
        this.date_range = 'week';  // possible values : 'week', 'month', year'
        this.date_from = moment().subtract(1, 'week');
        this.date_to = moment();
        this.dashboards_templates = ['StockPickingDashboard'];
        this.login = [];
        this.unfulfiled = [];
        this.new_orders = [];
        this.ready_to_ship = [];
        this.manifest = [];
        this.delivered = [];
        this.all_orders = [];
        this.wp_awb = [];
        this.gen_awb = [];
        this.wp_pickup = [];
        this.gen_pickup = [];
        this.wp_manifest = [];
        this.gen_manifest = [];
        this.seller_order = [];
        this.shopify_order = [];
        this.website_order = [];
        this.total_sale_order = [];
        this.today_sale = [];
        this.last_seven_days = [];
        this.seller = [];
        this.seller_product = [];
        this.seller_product_draft = [];
        this.seller_product_to_approve = [];
        this.seller_product_approve = [];
        this.seller_product_rejected  = [];
    },

    willStart: function(){
        var self = this;
        this.login = {};
        return this._super()
        .then(function() {
            var def0 =  self._rpc({
                    model: 'stock.picking',
                    method: 'check_user_group'
            }).then(function(result) {
                if (result == true){
                    self.is_manager = true;
                }
                else{
                    self.is_manager = false;
                }
            });
            var dashboard_def = self._rpc({
                model: "stock.picking",
                method: "retrieve_transfers",
            })
            .then(function (res) {
              self.unfulfiled = res['unfulfiled'];
              self.new_orders = res['new_orders'];
              self.ready_to_ship = res['ready_to_ship'];
              self.manifest = res['manifest'];
              self.delivered = res['delivered'];
              self.all_orders = res['all_orders'];
              self.wp_awb = res['wp_awb'];
              self.gen_awb = res['gen_awb'];
              self.wp_pickup = res['wp_pickup'];
              self.gen_pickup = res['gen_pickup'];
              self.wp_manifest = res['wp_manifest'];
              self.gen_manifest = res['gen_manifest'];
            });

            var dashboard_sale_order_def = self._rpc({
                model: "stock.picking",
                method: "get_sale_order_details",
            })
            .then(function (res) {
              self.seller_order = res['seller_order'];
              self.shopify_order = res['shopify_order'];
              self.website_order = res['website_order'];
              self.total_sale_order = res['total_sale_order'];
              self.today_sale = res['today_sale'];
              self.last_seven_days = res['last_seven_days'];
            });
            var dashboard_product_def = self._rpc({
                model: "stock.picking",
                method: "get_product_details",
            })
            .then(function (res) {
              self.seller = res['seller'];
              self.seller_product = res['seller_product'];
              self.seller_product_draft = res['seller_product_draft'];
              self.seller_product_to_approve = res['seller_product_to_approve'];
              self.seller_product_approve = res['seller_product_approve'];
              self.seller_product_rejected = res['seller_product_rejected'];
            });
            
        return $.when(def0,dashboard_def,dashboard_sale_order_def,dashboard_product_def);
        });
    },


    start: function() {
            console.log("START FUNCTION")
            var self = this;
            this.set("title", 'Dashboard');
            return this._super().then(function() {
                self.update_cp();
                self.render_dashboards();
                // self.render_graphs();
                self.$el.parent().addClass('oe_background_grey');
            });
        },

    fetch_data: function() {
        var self = this;
        var def0 =  self._rpc({
                model: 'stock.picking',
                method: 'check_user_group'
        }).then(function(result) {
            if (result == true){
                self.is_manager = true;
            }
            else{
                self.is_manager = false;
            }
        });
        var dashboard_def = self._rpc({
            model: "stock.picking",
            method: "retrieve_transfers",
        })
        .then(function (res) {
          self.unfulfiled = res['unfulfiled'];
          self.new_orders = res['new_orders'];
          self.ready_to_ship = res['ready_to_ship'];
          self.manifest = res['manifest'];
          self.delivered = res['delivered'];
          self.all_orders = res['all_orders'];
          self.wp_awb = res['wp_awb'];
          self.gen_awb = res['gen_awb'];
          self.wp_pickup = res['wp_pickup'];
          self.gen_pickup = res['gen_pickup'];
          self.wp_manifest = res['wp_manifest'];
          self.gen_manifest = res['gen_manifest'];
  
        });
        var dashboard_sale_order_def = self._rpc({
            model: "stock.picking",
            method: "get_sale_order_details",
        })
        .then(function (res) {
          self.seller_order = res['seller_order'];
          self.shopify_order = res['shopify_order'];
          self.website_order = res['website_order'];
          self.total_sale_order = res['total_sale_order'];
          self.today_sale = res['today_sale'];
          self.last_seven_days = res['last_seven_days'];
        });
        var dashboard_product_def = self._rpc({
            model: "stock.picking",
            method: "get_product_details",
        })
        .then(function (res) {
          self.seller = res['seller'];
          self.seller_product = res['seller_product'];
          self.seller_product_draft = res['seller_product_draft'];
          self.seller_product_to_approve = res['seller_product_to_approve'];
          self.seller_product_approve = res['seller_product_approve'];
          self.seller_product_rejected = res['seller_product_rejected'];
        });

        return $.when(def0,dashboard_def,dashboard_sale_order_def,dashboard_product_def);
    },


    render_dashboards: function() {
        var self = this;
        if (this.login){
            var templates = []
            if( self.is_manager == true){templates = ['StockPickingDashboard'];}
            else{ templates = ['StockPickingDashboard'];}
            _.each(templates, function(template) {
                self.$('.o_hr_dashboard').append(QWeb.render(template, {widget: self}));
            });
        }
        else{
                self.$('.o_hr_dashboard').append(QWeb.render('EmployeeWarning', {widget: self}));
            }
    },

    _onDashboardActionClicked: function (e) {
        e.preventDefault();
        var self = this;
        var $action = $(e.currentTarget);
        var action_name = $action.attr('name')+"_list";
        if (_.contains(['stock_action_dashboard_unfulfiled_list', 
                        'stock_action_dashboard_new_orders_list',
                        'stock_action_dashboard_ready_to_ship_list',
                        'stock_action_dashboard_manifest_list',
                        'stock_action_dashboard_delivered_list', 
                        'stock_action_dashboard_all_orders_list',
                        'stock_bulk_action_dashboard_wp_awb_list',
                        'stock_bulk_action_dashboard_gen_awb_list',
                        'stock_bulk_action_dashboard_wp_pickup_list',
                        'stock_bulk_action_dashboard_gen_pickup_list',
                        'stock_bulk_action_dashboard_wp_manifest_list',
                        'stock_bulk_action_dashboard_gen_manifest_list',
                        'sale_action_dashboard_shopify_order_list',
                        'sale_action_dashboard_seller_order_list',
                        'sale_action_dashboard_website_order_list',
                        'sale_action_dashboard_total_sale_order_list',
                        'sale_action_dashboard_today_sale_list',
                        'sale_action_dashboard_last_seven_days_list',
                        'product_action_dashboard_seller_list',
                        'product_action_dashboard_seller_product_list',
                        'sale_action_dashboard_seller_product_draft_list',
                        'sale_action_dashboard_seller_product_to_approve_list',
                        'sale_action_dashboard_seller_product_approve_list',
                        'sale_action_dashboard_seller_product_rejected_list',
                    ], action_name)) {
            return this._rpc({model: 'stock.picking', method: action_name})
                .then(function (data) {
                    if (data) {
                    return self.do_action(data);
                    }
                });
        }
        return this.do_action(action_name);
    },
 
   });

    core.action_registry.add('seller_management_dashboard', SellerManagementDashboard);

return SellerManagementDashboard;

});