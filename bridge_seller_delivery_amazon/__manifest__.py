{
    # App information
    'name': 'Bridge Between Amazon Delivery And Seller',
    'version': '14.0',
    'category': 'Sales',
    'summary': 'Bridge Between Amazon Delivery And Seller',
    'license': 'OPL-1',

    # Author
    'author': 'Heartfulness Team',

    # Dependencies
    'depends': ['delivery_amazon', 'seller_management'],

    # Views
    'data': [
        # 'views/delivery_order_seller_view.xml',
        'views/seller_view_inherit.xml',
    ],
}
