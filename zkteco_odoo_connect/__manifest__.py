# -*- coding: utf-8 -*-
{
    'name': 'Odoo Zkteco Attendance Integration',
    'version': "15.0.0.1",
    'description': 'API Integration for Attendance Machine',
    'author': "Roopesh Sivam",
    'depends': ['hr_attendance', 'hr'],
    'data': [
        'security/zkteco_odoo_connect_security.xml',
        'security/ir.model.access.csv',

        'views/machine.xml'
       
    ],
    'installable': True,
    'application': True,
    # 'post_init_hook': 'post_init_hook',
}
