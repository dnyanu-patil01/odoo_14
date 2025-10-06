{
    'name': 'Custom Sales Module',
    'version': '14.0.1.0.0',
    'category': 'Sales',
    'summary': 'Custom Sales Order and Line Views for Glass Business',
    'description': '''
        Enhanced sales order and order line views with:
        - Custom fields for glass business
        - Dimension calculations
        - Job work management
        - GST treatment options
    ''',
    'author': 'Your Company',
    'website': 'https://www.yourcompany.com',
    'depends': [
        'base',
        'sale', 
        'sale_management',
        'stock', 
        'account',
        'uom'
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/sales_order_views.xml',
        'reports/proforma_invoice_report.xml',
    ],
    'demo': [],
    'qweb': [],
    'installable': True,
    'auto_install': False,
    'application': False,
    'license': 'LGPL-3',
}