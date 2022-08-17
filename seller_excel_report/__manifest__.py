{
    'name': 'Excel Report For Sellers',
    'category': 'Report',
    'summary': 'Excel Report For Sellers',
    'author': 'leelapriskila',
    'version': '14.0',
    'description': """
    Sale Excel Report,Invoice Excel Report
    """,
    'depends': ['sale','seller_management'],
    'data': [
        "security/ir.model.access.csv",
        'wizard/sale_report_wizard_view.xml',
        "wizard/invoice_report_wizard_view.xml",
        "views/report_log_view.xml",
    ],
    'qweb': [],
    'installable': True,
    'auto_install': True,
    'license': 'LGPL-3',
}
