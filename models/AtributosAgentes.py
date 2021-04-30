# -*- coding: utf-8 -*-

from odoo import models, fields


class AtribAgentes(models.Model):
    _name = 'atributos.agentes'
    _description = 'Formulario agentes'

    agente_name = fields.Many2one("res.users", string="Agentes")
    vacaciones_inicio = fields.Date(string="Vacaciones inicio", required=False)
    vacaciones_fin = fields.Date(string="Vacaciones fin", required=False)
    horario_laboral = fields.Selection(string="Horario Laboral", selection=[("9-17", "9-17"), ("7-15", "7-15")], required=True, default="9-17")
    area_curso = fields.Many2one("op.area.course", string="Area del Curso", required=False)
    max_leads = fields.Integer(string="Leads Maximos", default="100", required=False)
