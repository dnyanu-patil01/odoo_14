{
    'name': "Delivery Shiprocket Dashboard",

    'summary': """
            Delivery Shiprocket Dashboard.""",

    'description': """ Delivery Shiprocket Dashboard View """,

    'author': "leelapriskila",
    'license': 'AGPL-3',
    'category': 'Delivery',
    'version': '14.0.1.0.1',
    'auto_install': False,
    "depends": ['delivery_shiprocket'],
    "data": [
        'views/picking_dashboard_assets.xml',
        'views/stock_picking_view.xml',
    ],
    'qweb': [
        'static/src/xml/picking_dashboard.xml',
    ],
}
