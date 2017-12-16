# -*- coding: utf-8 -*-
from odoo import http
import re
import logging
from contextlib import closing

from odoo import models, fields, api
from odoo.tools.translate import _
import odoo
from odoo.service import db
from odoo.exceptions import ValidationError
from odoo import SUPERUSER_ID

DBNAME_PATTERN = '^[a-zA-Z0-9][a-zA-Z0-9_.-]+$'
# This is for the time being.Later it should b added in config
SUPERLOGIN = "wahabalimalik@gmail.com"
SUPERPWD = "123456"

class SaasDatabase(models.Model):
    _name = 'saas.database'
    _description = 'Saas Database Management Model'
    
    state = fields.Selection([('init', 'initialize'), ('auth', 'Auth'), ('expire', 'Expire'), ('live', 'Live')], readonly=True, default='init', copy=False, string="Status")
    name = fields.Char('Database Name', required=True)
    business_name = fields.Many2one('res.partner', string = 'Business Name', domain = "[('is_company', '=', True)]")
    country = fields.Many2one('res.country')
    demo = fields.Boolean()
    inrollment_date = fields.Date('Inrollment Date',default=lambda self: fields.Datetime.now())
    expiry_date = fields.Date('Expiry Date')
    users = fields.Many2many('res.partner')
    admin_user = fields.Many2many('res.partner')
    apps = fields.Many2many('ir.module.module')

    @api.multi
    def inits(self):
        # check if valid database name
        if not re.match(DBNAME_PATTERN, self.name):
            raise Exception(_('Invalid database name. Only alphanumerical characters, underscore, hyphen and dot are allowed.'))
        # check if db already exit
        if self.name in http.db_list():
            raise ValidationError(_('The database: %s already exist.' %(self.name)))
        # check if module assign
        if not self.apps:
            raise ValidationError(_('You should have to assign alteast one app to database.'))
        # check if user assign
        if not self.users:
            raise ValidationError(_('You should have to assign alteast one user to database.'))
        # check if admin user assign
        if not self.users:
            raise ValidationError(_('You should have to assign alteast one admin user to database.'))
        # check all users have email assign
        for rec in self.users:
            if not rec.email:
                raise ValidationError(_('User : %s has no email assign.' %(rec.name)))
        # check if multi users assign same email
        users = [(x.email,) for x in self.users]
        dup = [x for x in users if users.count(x) > 1]
        if len(dup) > 1:
            raise ValidationError(_('Emial : %s assign to muliple users please check.' %(dup[0])))
        # check if user already exist on any other database
        for db_name in http.db_list():
            db = odoo.sql_db.db_connect(db_name)
            with closing(db.cursor()) as cr:
                cr.execute('SELECT login FROM res_users ORDER BY login')
                rec = cr.fetchall()
                dup  = list(set(users).intersection(rec))
                if len(dup) > 0:
                    raise ValidationError(_('Emial : %s already exist PLEASE CHANGE' %(dup[0])))
        self.write({'state': 'auth'})

    @api.multi
    def auth(self):
        master_pwd = odoo.tools.config['admin_passwd']
        name,demo,lang,password,login = self.name,self.demo,'en_US',SUPERPWD,SUPERLOGIN
        country_code = self.country.code or False
        try:
            # creating database
            http.dispatch_rpc('db', 'create_database', [master_pwd, name, bool(demo), lang, password, login, country_code])
            # uploading users in database
            self.update_usr()
            # Assign module to database
            self.update_mod()
            self.write({'state': 'live'})
        except Exception, e:
            error = "Database creation error: %s" % str(e) or repr(e)

    @api.multi
    def delete(self):
        master_pwd = odoo.tools.config['admin_passwd']
        name = self.name
        try:
            http.dispatch_rpc('db','drop', [master_pwd, name])
            self.write({'state': 'init'})
        except Exception, e:
            error = "Database deletion error: %s" % str(e) or repr(e)

    @api.multi
    def update_mod(self):
        module_names = [x.name for x in self.apps]
        db = odoo.sql_db.db_connect(self.name)
        with closing(db.cursor()) as cr:
            env = api.Environment(cr, SUPERUSER_ID, {})
            action = env['ir.actions.act_window'].search([('id','=',env.ref('my_control_panel.apps_action').id)])
            action.domain = [('name','in',module_names)]
            cr.commit()

    @api.multi
    def update_usr(self):
        db = odoo.sql_db.db_connect(self.name)
        with closing(db.cursor()) as cr:
            env = api.Environment(cr, SUPERUSER_ID, {})
            Users = env['res.users']
            for rec in self.users:
                Users.create({
                    'name': rec.name,
                    'login': rec.email,
                    'password' : '12345',
                    'lang' : rec.lang,
                    'image': rec.image,
                    })
            self.create_groups(env)
            cr.commit()

    def create_groups(self,env):
        users_record = [rec.id for rec in env['res.users'].search([])]
        group_id = env.ref('my_control_panel.group_saas_manager')
        group = env['res.groups'].search([('id', '=', group_id.id)])
        for rec in users_record:
            group.users = [(4, rec)]

    @api.onchange('business_name')
    def _onchange_users(self):
    	if self.business_name:
            db_name = (str(self.business_name.name).lower()).replace(" ", "_")
            if db_name in http.db_list():
                raise ValidationError(_('The database: %s already exist.' %(db_name)))
            else:
                self.name = db_name
            return {'domain':{
            'users':[('parent_id','like',self.business_name.name)],
            'admin_user':[('parent_id','like',self.business_name.name)]
            }}