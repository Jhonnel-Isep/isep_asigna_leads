# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions, _

class LogRegister(models.Model):
    _name = 'logs'
    _description = 'logs de asignacion agentes'
    
    # opcion A
    # nombre del agente
    # pais del agente
    # Criterio de seleccion
    
    # opcion B
    # fecha / agente / pais agente / filtro vaciones 
    # horario de trabajo / atendido previamente / area agente / mismo pais
    # max leads 