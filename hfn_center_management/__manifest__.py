# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Community Buying',
    'version': '1.0',
    'summary': 'Community Buying',
    'description': """
       Added Center In Sale Order.
    """,
    'depends': ['sales_team','sale','account','stock'],
    'author': 'leelapriskila',
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'views/center_view.xml',
        'views/res_partner_view.xml',

    ],
    'auto_install': False,
    'installable': True,
}
