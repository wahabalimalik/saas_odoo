# -*- coding: utf-8 -*-
{
    'name': "SaaS Control Panel",

    'summary': """
        Manage users and there databases.
    """,

    'description': """
This is a powerfull module on which you can create other databases:
==================================================================

It supports:
------------

    - i-Databases for companies and there users.
    - ii-Allocate number of modules for this company.So they can only use and install these modules.
    - iii-Allocate space to the company so they can not exceed there limits.
    - iv-Freeze activities on there database if company exceed subscription date.
    - v-Send warnings and notifications to company to recall them about database remaining space and last subscription date.
    """,

    'author': "Wahab Ali Malik",
    'website': "http://www.glarcom.com",

    'category': 'SaaS',
    'version': '0.1',
    'depends': ['base'],
    'data': [
        'views/menuitems.xml',
        'views/database.xml',
        'views/client.xml'
    ],
    'css': ['static/src/css/saas_control_panel.css'],
    'installable': True,
    'application': True,
    'auto_install': False,
}