# -*- coding: utf-8 -*-
{
    'name': "Comisiones",

    'summary': """
        Modulo para calculo de comisiones """,

    'description': """
        Long description of module's purpose
    """,

    'author': "Mastermind Software Services",
    'website': "https://www.mss.mx",
    'license': 'LGPL-3',

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Sales',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'sale', 'hr'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
