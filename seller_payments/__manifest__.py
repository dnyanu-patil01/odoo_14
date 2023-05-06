{
    'name': "Seller's Monthly Payments For Sellers",
    'category': 'Seller',
    'summary': "Seller's Monthly Payments For Sellers",
    'author': 'Suveetha',
    'version': '14.0',
    'description': """
    Seller's Monthly Payments For Sellers
    """,
    'depends': ['seller_management'],
    'data': [
        "security/ir.model.access.csv",
        "views/seller_payment_view.xml",
        "data/ir_cron_data.xml",
        "data/ir_sequence.xml"
    ],
    'qweb': [],
    'installable': True,
    'auto_install': True,
    'license': 'LGPL-3',
}