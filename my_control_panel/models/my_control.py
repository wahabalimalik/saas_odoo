# -*- coding: utf-8 -*-

from odoo import models, fields, api

class MyPanel(models.Model):
    _name = 'my.control'

    name = fields.Char()
    value = fields.Integer()
    value2 = fields.Float()
    description = fields.Text()