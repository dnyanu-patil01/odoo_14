odoo.define('bnm_distribution_system.website_additional_fields', function(require) {
    "use strict";
    require('website_sale.website_sale');
    var publicWidget = require('web.public.widget');
    var VariantMixin = require('sale.VariantMixin');
    $(document).ready(function() {
        'use strict';
        $('.modal_add_payment_details').on('hidden.bs.modal', function() {
            $(this).find('form').trigger('reset');
        })
        $('#payment_date').datepicker({
            dateFormat: "dd-mm-yy",
            todayHighlight: true,
            autoclose: true,
            autoSize: true,
            container: '#box2',
            orientation: 'top right',
            maxDate: new Date($.now()),
        });
        $("#payment_date").on('keydown paste focus', function(e) {
            if (e.keyCode != 9) // ignore tab
                e.preventDefault();
        });
        $('#additional_info .customer_name,.customer_contact_no,.customer_email').blur(function() {
            $('#additional_info').find('div.alert.alert-danger').remove();
            $('#o_confirm_order_button').prop('disabled', false);
        });
    });
    publicWidget.registry.WebsiteSaleConfirmOrder = publicWidget.Widget.extend(VariantMixin, {
        selector: '.oe_website_sale',
        // read_events: ,
        events: _.extend({}, VariantMixin.events || {}, {
            'click #o_confirm_order_button': '_onConfirmSubmit',
        }),
        _onConfirmSubmit: function(ev) {
            ev.preventDefault();
            var $aSubmit = $(ev.currentTarget);
            $aSubmit.prop('disabled', true);
            this._rpc({
                route: '/shop/additional_customer_details',
                params: {
                    'customer_name': $('#customer_name').val(),
                    'customer_contact_no': $('#customer_contact_no').val(),
                    'customer_email': $('#customer_email').val(),
                }
            }).then(function(result) {
                if (result.errors) {
                    $('#additional_info .alert').remove();
                    $('#additional_info div:first').prepend("<div class='alert alert-danger'>" + result.errors + "</div>")
                    ev.stopPropagation();
                } else {
                    $aSubmit.closest('form').submit();
                }
            });
            setTimeout(function() {}, 2000);

        },
    });
});