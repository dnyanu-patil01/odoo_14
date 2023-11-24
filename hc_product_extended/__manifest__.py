{
    'name': 'Product Extended',
    'category': 'Product',
    'summary': 'Product Related Customization',
    'author': 'leelapriskila',
    'version': '14.0',
    'description': """

 Product Related Customization.
Add mandatory fields for product creation/edit page in HC

    1.POS Product Category
    2.HSN Code
    3.Customer Taxes
    4.Operating Unit
    """,
    'depends': ['product','account','l10n_in','point_of_sale','product_operating_unit'],
    'data': [
        'views/view.xml',
    ],
    'qweb': [],
    'installable': True,
    'auto_install': True,
    'license': 'LGPL-3',
}
