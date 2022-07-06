# -*- coding: utf-8 -*-

{
    'name': 'Product Change Request',
    'version': '14.0',
    'summary': 'Product Change Request For Sellers',
    'description': 'Product Change Request For Sellers',
    'depends': ['product','seller_management'],
    'data': [
            'security/security.xml',
            'security/ir.model.access.csv',
            'views/product_view.xml',
            'wizard/get_cancel_reason_view.xml'
            ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
