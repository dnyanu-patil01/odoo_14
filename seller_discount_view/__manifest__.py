{
    # App information
    'name': 'Added Discount Fields In Seller Views',
    'version': '14.0',
    'category': 'Sales',
    'summary': 'Added Discount Fields In Seller Views',
    'license': 'OPL-1',

    # Author
    'author': 'Leelapriskila',

    # Dependencies
    'depends': ['seller_management','sale_fixed_discount','account_invoice_fixed_discount'],

    # Views
    'data': [
        "view/seller_view.xml",
        "reports/report_sale_order.xml",
    ],
}
