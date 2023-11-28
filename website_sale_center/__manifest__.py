{
    'name': 'eCommerce Sale Center',
    'category': 'Website/Website',
    'summary': 'Add Center to online sales',
    'author': 'leelapriskila',
    'version': '14.0',
    'description': """
Add a to check selection of center to your eCommerce store.
    """,
    'depends': ['website_sale', 'hfn_center_management','website_sale_checkout_skip_payment'],
    'data': [
        'views/website_sale_center_templates.xml',
    ],
    'qweb': [],
    'installable': True,
    'auto_install': True,
    'license': 'LGPL-3',
}
