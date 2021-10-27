odoo.define('delivery_shiprocket_dashboard.picking_dashboard', function (require) {
"use strict";

var core = require('web.core');
var ListController = require('web.ListController');
var ListModel = require('web.ListModel');
var ListRenderer = require('web.ListRenderer');
var ListView = require('web.ListView');
var SampleServer = require('web.SampleServer');
var view_registry = require('web.view_registry');

var QWeb = core.qweb;

// Add mock of method 'retrieve_quotes' in SampleServer, so that we can have
// the sample data in empty Sale kanban and list view
let dashboardValues;
SampleServer.mockRegistry.add('stock.picking/retrieve_transfers', () => {
    return Object.assign({}, dashboardValues);
});


//--------------------------------------------------------------------------
// List View
//--------------------------------------------------------------------------

var StockPickingListDashboardRenderer = ListRenderer.extend({
    events:_.extend({}, ListRenderer.prototype.events, {
        'click .o_dashboard_action': '_onDashboardActionClicked',
    }),
    /**
     * @override
     * @private
     * @returns {Promise}
     */
    _renderView: function () {
        var self = this;
        return this._super.apply(this, arguments).then(function () {
            var values = self.state.dashboardValues;
            var stock_picking_dashboard = QWeb.render('stock_picking_dashboard.StockPickingDashboard', {
                values: values,
            });
            self.$el.prepend(stock_picking_dashboard);
        });
    },

    /**
     * @private
     * @param {MouseEvent}
     */
    _onDashboardActionClicked: function (e) {
        e.preventDefault();
        var $action = $(e.currentTarget);
        this.trigger_up('dashboard_open_action', {
            action_name: $action.attr('name')+"_list",
            action_context: $action.attr('context'),
        });
    },
});

var StockPickingListDashboardModel = ListModel.extend({
    /**
     * @override
     */
    init: function () {
        this.dashboardValues = {};
        this._super.apply(this, arguments);
    },

    /**
     * @override
     */
    __get: function (localID) {
        var result = this._super.apply(this, arguments);
        if (_.isObject(result)) {
            result.dashboardValues = this.dashboardValues[localID];
        }
        return result;
    },
    /**
     * @override
     * @returns {Promise}
     */
    __load: function () {
        return this._loadDashboard(this._super.apply(this, arguments));
    },
    /**
     * @override
     * @returns {Promise}
     */
    __reload: function () {
        return this._loadDashboard(this._super.apply(this, arguments));
    },

    /**
     * @private
     * @param {Promise} super_def a promise that resolves with a dataPoint id
     * @returns {Promise -> string} resolves to the dataPoint id
     */
    _loadDashboard: function (super_def) {
        var self = this;
        var dashboard_def = this._rpc({
            model: 'stock.picking',
            method: 'retrieve_transfers',
        });
        return Promise.all([super_def, dashboard_def]).then(function(results) {
            var id = results[0];
            dashboardValues = results[1];
            self.dashboardValues[id] = dashboardValues;
            return id;
        });
    },
});

var StockPickingListDashboardController = ListController.extend({
    custom_events: _.extend({}, ListController.prototype.custom_events, {
        dashboard_open_action: '_onDashboardOpenAction',
    }),

    /**
     * @private
     * @param {OdooEvent} e
     */
    _onDashboardOpenAction: function (e) {
        var self = this;
        var action_name = e.data.action_name;
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
                    ], action_name)) {
            return this._rpc({model: this.modelName, method: action_name})
                .then(function (data) {
                    if (data) {
                    return self.do_action(data);
                    }
                });
        }
        return this.do_action(action_name);
    },
});

var StockPickingListDashboardView = ListView.extend({
    config: _.extend({}, ListView.prototype.config, {
        Model: StockPickingListDashboardModel,
        Renderer: StockPickingListDashboardRenderer,
        Controller: StockPickingListDashboardController,
    }),
});

view_registry.add('stock_list_dashboard', StockPickingListDashboardView);

return {
    StockPickingListDashboardModel: StockPickingListDashboardModel,
    StockPickingListDashboardRenderer: StockPickingListDashboardRenderer,
    StockPickingListDashboardController: StockPickingListDashboardController,
};

});