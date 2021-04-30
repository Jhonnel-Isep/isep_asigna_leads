# -*- coding: utf-8 -*-

from odoo import models, fields

class AutoLeadLogRegister(models.Model):
    _name = 'lead.logs'
    _description = 'logs de asignacion agentes'
    
   
    agente_lead = fields.Many2one("res.users", string="Agentes")
    pais_lead = fields.Many2one("res.country", string="Pais")
    filtro_vacaciones = fields.Boolean(default=False, required=False)
    filtro_feriado = fields.Boolean(default=False, required=False)
    filtro_pais = fields.Boolean(default=False, required=False)
    filtro_horario = fields.Boolean(default=False, required=False)
    filtro_atendido_previamente = fields.Boolean(default=False, required=False)
    filtro_area_curso = fields.Boolean(default=False, required=False)
    filtro_max_lead = fields.Boolean(default=False, required=False)
    
    # fecha / agente / pais agente / filtro vaciones 
    # horario de trabajo / atendido previamente / area curso / mismo pais
    # max leads 