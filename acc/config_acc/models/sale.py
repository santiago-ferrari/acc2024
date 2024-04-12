# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


import logging
_logger = logging.getLogger(__name__)
    
   
class Presupuesto(models.Model):
    _inherit = "sale.order"

    dias_prueba = fields.Integer(string=u'Días de prueba')