{
    'name': 'Multi Seller Marketplace',
    'version': '14.0',
    'description': 'Multi Seller Marketplace',
    'summary': 'Multi Seller Marketplace To Store Maintain Sellers and Their Products,Orders.',
    'author': 'leelapriskila',
    'license': 'LGPL-3',
    'category': 'sale',
    'depends': [
        'base','sale','stock','account','product_volume_weight','delivery'
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/seller_view.xml',
        'views/product_view.xml',
        'views/sale_order_view.xml',
        'views/account_move_view.xml',
        'views/stock_location_view.xml',
        'views/stock_move_line_view.xml',
        'views/stock_move_view.xml',
        'views/stock_picking_view.xml',
        'views/seller_inventory_view.xml',
        'views/product_packaging.xml',
        'report/sale_report_view.xml',
        'report/sale_report.xml',
        'report/invoice_report.xml',
        'wizard/get_cancel_reason_view.xml',
    ],
    'demo': [
        ''
    ],
    'auto_install': True,
    'application': True,
}