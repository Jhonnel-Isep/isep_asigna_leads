# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions, _

class AtribAgentes(models.Model):
    _name = 'atrb_agentes'
    _description = 'Formulario agentes'

    agente = fields.Char(
        string='' # agentes
    )
    vacaciones_inicio = fields.Date(
        string='Vacaciones inicio'
    )
    Vacaciones_fin = fields.Date(
        string='Vacaciones fin'
    )
   
    horario_laboral = fields.Selection([
        ('9-17'),
        ('7-15')
    ], '')

    area_curso = fields.Selection([
        ('psicologia'),
        ('otra')
    ], '')


    max_leads = fields.Integer(
        string="Leads Maximos",
        default="100",  
        required=False
        )
    
# Extender los atributos de los roles? o agregar el segmento de roles en este modelo?