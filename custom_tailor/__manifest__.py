{
    'name': 'Sainaath Tailoring Management',
    'version': '1.0',
    'summary': 'Manage tailoring measurements, billing, labour commissions, SMS alerts, and delivery tracking.',
    'author': 'Your Name',
    'category': 'Services',
    'depends': ['base', 'sale_management', 'stock', 'account', 'hr'],
    'data': [
        'security/ir.model.access.csv',
        'views/tailor_order_views.xml',
        'data/scheduled_sms_job.xml',
        'reports/measurement_reports.xml',
        'reports/bill_reports.xml',
        'reports/bulk_reports.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}