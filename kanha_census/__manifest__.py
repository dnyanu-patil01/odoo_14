# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Kanha Census',
    'version': '1.0',
    'summary': 'Access the Portal form of the user',
    'depends': ['website'],
    'data': [
        'security/ir.model.access.csv',
        'data/website_data.xml',
        'views/portal_templates.xml',
        'views/assets.xml',
        'views/kanha_location_view.xml',
        'views/res_partner_view.xml',
    ],
    'auto_install': False,
}
