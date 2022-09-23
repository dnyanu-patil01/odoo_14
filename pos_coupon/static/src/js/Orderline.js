odoo.define('pos_coupon.Orderline', function (require) {
    'use strict';

    const Orderline = require('point_of_sale.Orderline');
    const Registries = require('point_of_sale.Registries');

    const PosCouponOrderline = (Orderline) =>
        class extends Orderline {
            /**
             * @override
             */
            get addedClasses() {
                const res = super.addedClasses;
                Object.assign(res, {
                    'program-reward': this.props.line.is_program_reward,
                });
                return res;
            }
        };

    Registries.Component.extend(Orderline, PosCouponOrderline);

    return Orderline;
});
