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
    "icon": "/inmo_odoo/static/description/icon.png",
    "category": "Bienes raíces",
    "version": "0.1",
    "depends": ["base", "calendar"],
    "data": [
        "data/event_type_visita_inmobiliaria.xml",
        "views/inmueble_wizard_views.xml",
        "views/visita_inmueble_views.xml",
        "views/inmueble_views.xml",
        "views/inmueble_image_views.xml",
        "security/ir.model.access.csv",
    ],
    "license": "LGPL-3",
    "demo": [
        "demo/demo.xml",
    ],
    "installable": True,
    "application": True,
}
