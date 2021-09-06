{
    # App information
    'name': 'Bridge Between Shopify And Shiprocket',
    'version': '14.0',
    'category': 'Sales',
    'summary': 'Bridge Between Shopify And Shiprocket',
    'license': 'OPL-1',

    # Author
    'author': 'Leelapriskila',

    # Dependencies
    'depends': ['delivery_shiprocket','shopify_ept','product_volume_weight'],

    # Views
    'data': [
        'view/delivery_carrier_view.xml',
        'view/product_packaging.xml',
    ],
}
