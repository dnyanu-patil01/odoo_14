odoo.define('website_sale_center.center', function (require) {
'use strict';

var core = require('web.core');
var publicWidget = require('web.public.widget');

var _t = core._t;
var concurrency = require('web.concurrency');
var dp = new concurrency.DropPrevious();
var publicWidget = require('web.public.widget');
var VariantMixin = require('sale.VariantMixin');

publicWidget.registry.portalCenterDetails = publicWidget.Widget.extend({
    selector: '.o_portal_details',
    events: {
        'change select[name="state_id"]': '_onStateChange',
    },

    /**
     * @override
     */
    start: function () {
        var def = this._super.apply(this, arguments);

        this.$center = this.$('select[name="center_id"]');
        this.$centerOptions = this.$center.filter(':enabled').find('option:not(:first)');
        this._adaptCenterAddressForm();

        return def;
    },

    //--------------------------------------------------------------------------
    // Private
    //--------------------------------------------------------------------------

    /**
     * @private
     */
     _adaptCenterAddressForm: function () {
        var $state = this.$('select[name="state_id"]');
        var stateID = ($state.val() || 0);
        this.$centerOptions.detach();
        var $displayedCenter = this.$centerOptions.filter('[data-state_id=' + stateID + ']');
        var nb = $displayedCenter.appendTo(this.$center).show().length;
        this.$center.parent().toggle(nb >= 1);
    },

    //--------------------------------------------------------------------------
    // Handlers
    //--------------------------------------------------------------------------

    /**
     * @private
     */
     _onStateChange: function () {
        this._adaptCenterAddressForm();
    },
});
publicWidget.registry.WebsiteSaleConfirmOrder = publicWidget.Widget.extend(VariantMixin, {
    selector: '.oe_website_sale',
    // read_events: ,
    events: _.extend({}, VariantMixin.events || {}, {
        'change select[name="state_id"]': '_onChangeState',
    }),
    init: function () {
        this._super.apply(this, arguments);
        this._changeState = _.debounce(this._changeState.bind(this), 500);
    },
    start() {
        const def = this._super(...arguments);
        this.$('select[name="state_id"]').change();
        return def;
    },
    _onChangeState: function (ev) {
        if (!this.$('.checkout_autoformat').length) {
            return;
        }
        this._changeState();
    },

    _changeState: function () {
        if (!$("select[name='state_id']").val()) {
            return;
        }
        this._rpc({
            route: "/shop/state_infos/",
            params: {
                'state_id':$("select[name='state_id']").val(),
                'mode': $("#country_id").attr('mode'),
            },
        }).then(function (data) {
            // populate centers and display
            var selectCenters = $("select[name='center_id']");
            // dont reload centers at first loading (done in qweb)
            if (selectCenters.data('init')===0 || selectCenters.find('option').length===1) {
                if (data.centers.length || data.center_required) {
                    selectCenters.html('');
                    _.each(data.centers, function (x) {
                        var opt = $('<option>').text(x[1])
                            .attr('value', x[0])
                            selectCenters.append(opt);
                    });
                    selectCenters.parent('div').show();
                } else {
                    selectCenters.val('').parent('div').hide();
                }
                selectCenters.data('init', 0);
            } else {
                selectCenters.data('init', 0);
            }
        });
    },
});
});
