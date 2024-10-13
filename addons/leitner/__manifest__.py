{
    "name": "Leitner method for Odoo",
    "summary": "Leitner method for Odoo",
    "description": """
Long description of module's purpose
    """,
    "author": "Victor Laskurain",
    "website": "github.com/victorlaskurain",
    "license": "AGPL-3",
    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    "category": "Uncategorized",
    "version": "18.0.0.0.1",
    # any module necessary for this one to work correctly
    "depends": ["web", "mail"],
    # always loaded
    "data": [
        "security/leitner_security.xml",
        "security/ir.model.access.csv",
        "views/box_set_views.xml",
        "views/card_views.xml",
        "views/deck_views.xml",
        "views/menu_views.xml",
        "views/templates.xml",
    ],
    "application": True,
    # only loaded in demonstration mode
    "demo": [
        "demo/demo.xml",
    ],
}
