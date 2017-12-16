# -*- coding: utf-8 -*-
{
    'name': "My Control Panel",
    'category': 'SaaS',

    'description': """
This is a Control Panel for Client :
====================================================

Where they can view:
----------------------
    - i-Authentic modules
    - ii-Can See there balance
    - iii-Can contact to hosting service
    - iv-Get mails form hosting service
    - etc
    """,

    'depends': ['web'],
    'auto_install': True,

    'data': [
        'security/saas_security.xml',
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/dashboard_templates.xml',
    ],
    'qweb': ['static/src/xml/dashboard.xml'],
}