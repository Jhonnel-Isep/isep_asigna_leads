# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions, _

class LogRegister(models.Model):
    _name = 'logs'
    _description = 'logs de asignacion agentes'
    