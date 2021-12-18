# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Kanha Census',
    'version': '1.0',
    'summary': 'Allows Portal user to add and update the Partner details',
    'description': """
       It Allows Portal user to add and update the Partner details.
    """,
    'depends': ['website', 'website_form','fields_encrypted'],
    'data': [
        'security/ir.model.access.csv',
        'data/website_data.xml',
        'data/kanha_data.xml',
        'views/portal_templates.xml',
        'views/assets.xml',
        'views/kanha_location_view.xml',
        'views/res_partner_view.xml',

    ],
    'auto_install': False,
    'installable': True,
}
