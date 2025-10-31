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

    'depends': ['tms','tms_sale'],
    
    'data': [
        "security/ir.model.access.csv",
        'views/res_partner_views.xml',
        'views/sale_order_views.xml',
        'views/tms_order_views.xml',
        'views/tms_stage_views.xml',
        'wizard/sale_order_trip.xml',
    ],
    "maintainers": ["bartacruz"],

}

