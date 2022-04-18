# -*- coding: utf-8 -*-

{
    'name': 'Magazine Subscription from Portal',
    'version': '14.0.0',
    'author': 'Leelapriskila',
    'depends': ['website_form','hfn_center_management'],
    'summary': "Magazine Subscription from Portal",
    'category': 'website',
    'data': [
        'security/ir.model.access.csv',
        'data/website_calendar_data.xml',
        'data/ir_cron.xml',
        'data/website_data.xml',
        'views/templates.xml',
        'views/res_company_views.xml',
        'views/magazine_subscription.xml',
        'views/report_magazine_subscription.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
