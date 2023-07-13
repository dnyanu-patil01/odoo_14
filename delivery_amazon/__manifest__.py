{
    "name": """Delivery Amazon""",
    "summary": """Delivery Amazon""",
    "category": "Operations/Inventory/Delivery",
    "version": "14.0",
    "application": False,

    "author": "Heartfulness Team",
    "depends": ['delivery', 'stock'],
    "data": [
            "security/ir.model.access.csv",
            "data/ir_cron.xml",
            "views/res_company_view.xml",
            "views/stock_picking_views.xml",
    ],

    "auto_install": False,
    "installable": True,
}
