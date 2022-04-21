{
    # App information
    'name': 'Added Wizard To Update Product Price',
    'version': '14.0',
    'category': 'Sales',
    'summary': 'Added Wizard To Update Product Price',
    'license': 'OPL-1',

    # Author
    'author': 'Leelapriskila',

    # Dependencies
    'depends': ['seller_management','shopify_ept'],

    # Views
    'data': [
        'security/ir.model.access.csv',
        'view/product_template_view.xml',
        'wizard/set_price_wizard.xml',
    ],
}
