odoo.define('hfn_magazine_subscription.magazine_subscription', function (require) {
'use strict';

var publicWidget = require('web.public.widget');

publicWidget.registry.MaganizeSubscription = publicWidget.Widget.extend({
    selector: '#website_magazine_subscription_form',
    events: {
        'click #get_details': '_onGetAddress',
        'change input[name="id_number"]': '_onGetAddress',
        'change select[name="country_id"]': '_onCountryChange',
        'change input[id="no_of_subcription_e1"]': '_onSubscription',
        'change input[id="no_of_subcription_e2"]': '_onSubscription',
        'change input[id="no_of_subcription_h1"]': '_onSubscription',
        'change input[id="no_of_subcription_h2"]': '_onSubscription',
        'change input[id="no_of_subcription_ta1"]': '_onSubscription',
        'change input[id="no_of_subcription_ta2"]': '_onSubscription',
        'change input[id="no_of_subcription_te1"]': '_onSubscription',
        'change input[id="no_of_subcription_te2"]': '_onSubscription',
        'change select[name="state_id"]': '_onStateChange',
        'change input[name="deliver_at"]': '_onDeliverAt',
        'click form[action="/subscription/confirm_order"] a.a-submit': '_onOrder',
        'click form[target="_self"] button[type=submit]': '_onOrderPayment',
    },


    init: function (parent, params) {
        this._super.apply(this, arguments);
        $("#id_number").val();
        this._onGetAddress();
        this._onSubscription();
        this._onDeliverAt();
    },

        /**
     * @override
     */
    start: function () {
    var def = this._super.apply(this, arguments);

    this.$state = this.$('select[name="state_id"]');
    this.$stateOptions = this.$state.filter(':enabled').find('option:not(:first)');
    this.$center = this.$('select[name="center_id"]');
    this.$centerOptions = this.$center.filter(':enabled').find('option:not(:first)');
    this._adaptAddressForm();
    this._adaptCenterAddressForm();
    
    return def;
},
_adaptAddressForm: function () {
    var $country = this.$('select[name="country_id"]');
    var countryID = ($country.val() || 0);
    this.$stateOptions.detach();
    var $displayedState = this.$stateOptions.filter('[data-country_id=' + countryID + ']');
    var nb = $displayedState.appendTo(this.$state).show().length;
    this.$state.parent().toggle(nb >= 1);
},
_adaptCenterAddressForm: function () {
    var $state = this.$('select[name="state_id"]');
    var stateID = ($state.val() || 0);
    this.$centerOptions.detach();
    var $displayedCenter = this.$centerOptions.filter('[data-state_id=' + stateID + ']');
    var nb = $displayedCenter.appendTo(this.$center).show().length;
    this.$center.parent().toggle(nb >= 1);
},
_onDeliverAt: function (e) {
    var deliver_at = document.schedule_meeting_form.deliver_at.value;
    
    if (deliver_at=='center'){
        $("#center_id_div").show();
    }
    else{
        $("#center_id_div").hide();
    }
},
_onStateChange: function () {
    this._adaptCenterAddressForm();
},
_onSubscription: function (e) {
    var no_of_subcription_e1 = document.schedule_meeting_form.no_of_subcription_e1.value;
    var no_of_subcription_e2 = document.schedule_meeting_form.no_of_subcription_e2.value;
    var no_of_subcription_h1 = document.schedule_meeting_form.no_of_subcription_h1.value;
    var no_of_subcription_h2 = document.schedule_meeting_form.no_of_subcription_h2.value;
    var no_of_subcription_ta1 = document.schedule_meeting_form.no_of_subcription_ta1.value;
    var no_of_subcription_ta2 = document.schedule_meeting_form.no_of_subcription_ta2.value;
    var no_of_subcription_te1 = document.schedule_meeting_form.no_of_subcription_te1.value;
    var no_of_subcription_te2 = document.schedule_meeting_form.no_of_subcription_te2.value;
    var amount_e = 0;
    var amount_h = 0;
    var amount_ta = 0;
    var amount_te = 0;
    if (no_of_subcription_e1){
        amount_e += 1500 * no_of_subcription_e1
    }
    if (no_of_subcription_e2){
        amount_e += 3000 * no_of_subcription_e2
    }
    if (no_of_subcription_h1){
        amount_h += 1500 * no_of_subcription_h1
    }
    if (no_of_subcription_h2){
        amount_h += 3000 * no_of_subcription_h2
    }
    if (no_of_subcription_te1){
        amount_te += 1500 * no_of_subcription_te1
    }
    if (no_of_subcription_te2){
        amount_te += 3000 * no_of_subcription_te2
    } 
    if (no_of_subcription_ta1){
        amount_ta += 1500 * no_of_subcription_ta1
    }
    if (no_of_subcription_ta2){
        amount_ta += 3000 * no_of_subcription_ta2
    }
    $("#amount_e1").val(amount_e)
    $("#amount_h1").val(amount_h)
    $("#amount_ta1").val(amount_ta)
    $("#amount_te1").val(amount_te)
    $("#amount").val(amount_e+amount_h+amount_ta+amount_te)
    
},

//--------------------------------------------------------------------------
// Handlers
//--------------------------------------------------------------------------

/**
 * @private
 */
_onCountryChange: function () {
    this._adaptAddressForm();
},
    _adaptAddressForm: function () {
        var $country = this.$('select[name="country_id"]');
        var countryID = ($country.val() || 0);
        this.$stateOptions.detach();
        var $displayedState = this.$stateOptions.filter('[data-country_id=' + countryID + ']');
        var nb = $displayedState.appendTo(this.$state).show().length;
        this.$state.parent().toggle(nb >= 1);
    },

    /**
     * @private
     * @param {Event} ev
     */
     _onGetAddress: function (ev) {
        var id_number = $("#id_number").val();
        var self = this;
        if (! id_number){
            return
        }
        $('#s_website_form_result, #o_website_form_result').html('');
        document.getElementById("schedule_meeting_form").reset();
        $("#id_number").val(id_number)
        return this._rpc({
                model: 'magazine.subscription',
                method: 'get_abhiyasi_data',
                args: [id_number],
            }).then(function (data) {
                if (data['id_number']){
                    $("#id_number").val(data['id_number'])
                }
                else{
                    self.do_warn('Error','Details Not Found.Please Verify The Entered ID Number & Try Again Once.')

                }
                if (data['name']){
                    $("#name").val(data['name'])
                }
                if (data['email']){
                    $("#email").val(data['email'])
                }
                if (data['mobile']){
                    $("#mobile").val(data['mobile'])
                }
                if (data['street']){
                    $("#street").val(data['street'])
                }
                if (data['country']){
                    $("#country_id").val(data['country']).change();
                }
                if (data['state']){
                    $("#state_id").val(data['state']).change();
                }
                if (data['city']){
                    $("#city").val(data['city']);
                }
                if (data['zip']){
                    $("#zip").val(data['zip']);
                }
            })
    },
});
});

