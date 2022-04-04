# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Material to Material Transfers',
    'version': '1.0',
    'summary': 'Allows Material to Material Transfers',
    'depends': ['stock'],
    'data': [
        'security/ir.model.access.csv',
        'views/m2m_transfers_view.xml',
        'data/data.xml',
    ],
    'auto_install': False,
    'installable': True,
}
