{
    "name": """HFN Website Add To Cart""",
    "summary": """Add Products To Cart Without Reloading Page or Redirect to cart page""",
    "category": "Sale",
    "version": "14.0.0",
    "application": False,

    "author": "Heartfulness Team",
    "depends": [
        "website",'website_sale','sale'
    ],
    "data": [
        "views/website_sale_add_to_cart_views.xml",
    ],

    "auto_install": False,
    "installable": True,
}
