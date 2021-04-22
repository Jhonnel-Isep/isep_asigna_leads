# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions, _

class AtribAgentes(models.Model):
    _name = ''
    _description = 'Formulario agentes'

    name = fields.Char(
        string=''
    )
    vacaciones_inicio = fields.Date(
        string='Vacaciones inicio'
    )
    Vacaciones_fin = fields.Date(
        string='Vacaciones fin'
    )
    zona_horaria = max_leads = fields.Integer(
        string="Leads Maximos",
        required=False
        )
   Horario_laboral = fields.Selection([
        ('9-17'),
        ('7-15')
    ], '')

    max_leads = fields.Integer(
        string="Leads Maximos",
        default="100",  
        required=False
        )
    
    def logs(self):
    
    logs =