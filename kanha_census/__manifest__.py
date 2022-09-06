# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Kanha Census',
    'version': '1.0',
    'summary': 'Allows Portal user to add and update the Family members details',
    'description': """
       It Allows Portal user to add and update the Family members details.
    """,
    'depends': ['website', 'website_form','fields_encrypted'],
    'data': [
        'security/ir.model.access.csv',
        'data/website_data.xml',
        'data/kanha_data.xml',
        'data/mail_data.xml',
        'views/portal_templates.xml',
        'views/assets.xml',
        'views/kanha_location_view.xml',
        'views/res_partner_view.xml',
        'views/residents_documents_downloads_history.xml',
        'wizard/residents_document_download.xml',
    ],
    'auto_install': False,
    'installable': True,
}
