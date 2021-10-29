# -*- coding: utf-8 -*-
{
    'name': "Market Place Dashboard",
    'version': '14.0.1.0.3',
    'summary': """Market Place - Overview Dashboard""",
    'description': """Market Place - Overview Dashboard""",
    'category': 'Dashboard',
    'author': 'leelapriskila',
    'depends': ['base','seller_management','delivery_shiprocket','bridge_shopify_shiprocket'],
    'data': [
        'views/dashboard_views.xml',
    ],
    'qweb': ["static/src/xml/seller_management_dashboard.xml"],
    'images': ["static/description/icon.png"],
    'license': "AGPL-3",
    'installable': True,
    'application': True,
}
