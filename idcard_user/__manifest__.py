##############################################################################
# __manifest__.py
##############################################################################
{
    'name': 'ID Card Printer',
    'version': '1.0',
    'category': 'Tools',
    'summary': 'Module for ID Card Printing Team Access',
    'description': """
        This module provides a dedicated view and security setup for the ID card 
        printing team, ensuring access to only the necessary fields.
    """,
    'author': 'Your Name',
    'depends': ['base'],
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'views/res_partner_views.xml',
    ],
    'installable': True,
    'application': False,
}
