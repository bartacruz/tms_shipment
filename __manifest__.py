# -*- coding: utf-8 -*-
{
    'name': "TMS - Shipment",

    'summary': "Truck shipment support for TMS",

    'description': """
Truck shipment support for TMS
    """,

    'author': "Julio Santa Cruz",
    'website': "https://www.bartatech.com",
    'category': 'TMS',
    "version": "17.0.1.0.4",
    "license": "AGPL-3",

    'depends': ['tms','tms_sale','l10n_ar_afip_cpe'],
    "assets": {
        "web.assets_backend": [
            "tms_shipment/static/src/js/driver_list.js",
            "tms_shipment/static/src/js/driver_list.scss",
            "tms_shipment/static/src/js/driver_list.xml",
            "tms_shipment/static/src/js/kanban_controller.js",
            "tms_shipment/static/src/js/kanban_controller.scss",
            "tms_shipment/static/src/js/kanban_controller.xml",
            "tms_shipment/static/src/js/tms_kanban.js",
            "tms_shipment/static/src/views/fields/many2many_trip_field.js",
            "tms_shipment/static/src/views/fields/many2many_trip_field.scss",
            "tms_shipment/static/src/views/fields/many2many_trip_field.xml",
            
        ],
    },
    'data': [
        "security/ir.model.access.csv",
        'views/fleet_vehicle.xml',
        'views/res_partner_views.xml',
        'views/sale_order_views.xml',
        'views/tms_driver_location_views.xml',
        'views/tms_driver_views.xml',
        'views/tms_order_views.xml',
        'views/tms_stage_views.xml',
        'wizard/sale_order_trip.xml',
    ],
    "maintainers": ["bartacruz"],

}

