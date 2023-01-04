# -*- coding: utf-8 -*-

{
    'name': "Seller GST Mapping",
    'author': 'leelapriskila',
    'category': 'Product',
    'version': '1.0',
    'depends': ['seller_management','seller_product_management'],
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml'
    ],
    'license': 'LGPL-3',
    'installable': True,
    'application': True,
    'auto_install': False,
}
