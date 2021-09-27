# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Hide Generic Features',
    'version': '14.0',
    'category': 'Tools',
    'description': """
Based On The Specific Group
=================================================================
1.Hide Print & Actions Options
2.Hide Menu Userwise
""",
    'depends': [
        'web','base',
    ],
    'author': 'leelapriskila',
    'data': [
        'security/security.xml',
        'views/template.xml',
        'views/res_users.xml',
    ],
    'qweb': [
            'static/src/xml/hide_feature.xml',
        ],
    'demo': []
}
