# -*- coding: utf-8 -*-

{
    'name': "Seller Minimum Stock Alert",
    'author': 'leelapriskila',
    'category': 'Inventory',
    'version': '1.0',
    'depends': ['base', 'seller_management','sale_management', 'stock'],
    'data': [
             "data/cron.xml",
             ],
    'license': 'LGPL-3',
    'installable': True,
    'application': True,
    'auto_install': False,
}
