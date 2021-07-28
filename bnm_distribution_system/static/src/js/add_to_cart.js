odoo.define('bnm_distribution_system.addToCart', function(require) {
    "use strict";
    var VariantMixin = require('sale.VariantMixin');
    var wSaleUtils = require('website_sale.utils');

    require("web.zoomodoo");

    var core = require('web.core');
    var VariantMixin = require('sale.VariantMixin');

    var publicWidget = require('web.public.widget');
    console.log(publicWidget);

    publicWidget.registry.addToCart = publicWidget.registry.WebsiteSale.extend(VariantMixin, {
        selector: '.oe_website_sale, #add_to_cart',
        events: _.extend({}, VariantMixin.events || {}, {

            'click  .a-submit-cart ': 'async _onClickAddAjax',
            'keypress': '_onKeypress',

        }),

        _onKeypress: function(e) {
            if (e.key === 'Enter') {
                e.stopPropagation();
                return false;
            }
        },

        init: function() {

            this._super.apply(this, arguments);
            $("#add_to_cart").unbind("click").bind("click", function(e) {
                e.stopPropagation();
            });
            var self = this;
            $("#add_to_cart").bind("click", function(e) {

                return self._onClickAddAjax(e);
            });

        },

        /**
         * @param {MouseEvent} ev
         */
        _onClickAddAjax: function(ev) {
            var $input = $(ev.currentTarget);
            this.isBuyNow = $(ev.currentTarget).attr('id') === 'buy_now';
            return this._handleAddCart($(ev.currentTarget).closest('form'), $input);

        },

        _handleAddCart: function($form, $input) {
            var self = this;
            this.$form = $form;


            var productSelector = [
                'input[type="hidden"][name="product_id"]',
                'input[type="radio"][name="product_id"]:checked'
            ];

            var productReady = this.selectOrCreateProduct(
                $form,
                parseInt($form.find(productSelector.join(', ')).first().val(), 10),
                $form.find('.product_template_id').val(),
                false
            );

            return productReady.then(function(productId) {
                $form.find(productSelector.join(', ')).val(productId);

                self.rootProduct = {
                    product_id: productId,
                    quantity: parseFloat($form.find('input[name="add_qty"]').val() || 1),
                    product_custom_attribute_values: self.getCustomVariantValues($form.find('.js_product')),
                    variant_values: self.getSelectedVariantValues($form.find('.js_product')),
                    no_variant_attribute_values: self.getNoVariantAttributeValues($form.find('.js_product'))
                };

                return self._onProductReadyCart($input);
            });
        },

        _onProductReadyCart: function($input) {
            return this._submitFormCart($input);
        },

        _submitFormCart: function($input) {

            let params = this.rootProduct;
            params.add_qty = params.quantity;

            params.product_custom_attribute_values = JSON.stringify(params.product_custom_attribute_values);
            params.no_variant_attribute_values = JSON.stringify(params.no_variant_attribute_values);

            if (this.isBuyNow) {
                params.express = true;
            }

            this._rpc({
                    route: "/shop/cart/update_json",
                    params: params,
                })
                .then(function(data) {
                    wSaleUtils.updateCartNavBar(data);
                });
        },


    });

});