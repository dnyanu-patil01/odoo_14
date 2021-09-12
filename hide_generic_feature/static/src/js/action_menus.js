odoo.define('hide_generic_feature.ActionMenus', function (require) {
"use strict";

    const session = require('web.session');
    const { patch } = require('web.utils');
    const components = {
        ActionMenus: require('web.ActionMenus')
    };
    patch(components.ActionMenus, 'hide_generic_feature.ActionMenus', {
        async willStart() {
            this.ShowAction = await session.user_has_group('hide_generic_feature.show_actions_button')
            this.ShowPrint = await session.user_has_group('hide_generic_feature.show_print_button')
            this.actionItems = await this._setActionItems(this.props);
            this.printItems = await this._setPrintItems(this.props);
        },
        async willUpdateProps(nextProps) {
            this.ShowAction = await session.user_has_group('hide_generic_feature.show_actions_button')
            this.ShowPrint = await session.user_has_group('hide_generic_feature.show_print_button')
            this.actionItems = await this._setActionItems(nextProps);
            this.printItems = await this._setPrintItems(nextProps);
        }
    });
});