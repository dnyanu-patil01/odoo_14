{
    "name": """Heartyculture Website Sale Extended""",
    "summary": """Heartyculture Website Sale Extended""",
    "category": "Sale",
    "version": "14.0.0",
    "application": False,

    "author": "Heartfulness Team",
    "depends": [
        "website",'website_sale','sale'
    ],
    "data": [
        # "data/mail_data.xml",
        "security/ir.model.access.csv",
        "views/config_view.xml",
        "views/template.xml",
        "views/sale_order_view.xml",
        "views/website_sale_skip_payment.xml",
        "views/website_sale_add_to_cart_views.xml",
        "views/sale_portal_template.xml",
    ],

    "auto_install": False,
    "installable": True,
}
