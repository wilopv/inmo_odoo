{  # noqa: B018
    "name": "Inmuebles",
    "summary": "Gestión básica de inmuebles",
    "description": """
        Módulo para la gestión básica de inmuebles en Odoo.
        Permite registrar, modificar y eliminar inmuebles,
        así como gestionar sus características y estados,
        agilizando la obtención de la información pública del
        del registro catastral.
    """,
    "author": "wilopv",
    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    "category": "Bienes raíces",
    "version": "0.1",
    # any module necessary for this one to work correctly
    "depends": ["base", "calendar"],
    # always loaded
    "data": [
        "data/event_type_visita_inmobiliaria.xml",
        "views/inmueble_wizard_views.xml",
        "views/visita_inmueble_views.xml",
        "views/inmueble_views.xml",
        "views/inmueble_image_views.xml",
        "security/ir.model.access.csv",
    ],
    "license": "LGPL-3",
    # only loaded in demonstration mode
    "demo": [
        "demo/demo.xml",
    ],
    "installable": True,
    "application": True,
}
