# -*- coding: utf-8 -*-
#########################################################################
#                                                                       #
#   roopeshsivam@gmail.com                                              #
#   GNU LESSER GENERAL PUBLIC LICENSE (LGPL v3)                         #
#                                                                       #
#########################################################################
{
    "name": "Aftership Connector",
    "description": """Aftership Connector""",
    "category": "Delivery",
    "version": "15.0.1.0.0",
    'author': 'Roopesh Sivam',
    "depends": ['delivery', 'sale'],
    'license': 'LGPL-3',
    "data": [
        'security/aftership_connector_security.xml',
        'security/ir.model.access.csv',
        'views/aftership.xml',

    ],
    # 'uninstall_hook': 'uninstall_hook',
}
