# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import datetime,timedelta, date

class Project(models.Model):
    _inherit = "project.project"
    priority = fields.Selection(
        [
            ('0', 'Baja'),
            ('1', 'Media'),
            ('2', 'Alta'),
        ], 
        string='Prioridad',
        index=True,
        default='0')
    
    opportunity_id = fields.Many2one('crm.lead', string='Oportunidad')
    products_node_ids = fields.Many2many(readonly=True,related='opportunity_id.products_node_ids', string='Nodos')  
    sale_order_line = fields.One2many(readonly=True,related='sale_order_id.order_line', string='Servicios')
    stage_change_date = fields.Datetime(string="Fecha y hora cambio de etapa")  

    def write(self, values):
        if 'stage_id' in values and values['stage_id']:
            values['stage_change_date'] = datetime.now()
        return super(Project, self).write(values)    