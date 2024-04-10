# -*- coding: utf-8 -*-
from datetime import datetime
from dateutil.relativedelta import relativedelta
from openerp import models, fields, api, _
from openerp.exceptions import Warning
import openerp.addons.decimal_precision as dp
import logging
_logger = logging.getLogger(__name__)

class create_vencimientos_cuotas(models.TransientModel):
    """Líneas de presupuesto"""

    _name = 'pa.create_budget_lines'
    _description = u'Crear líneas de presupuesto'

    budget_id_origen = fields.Many2one(
        comodel_name='pa.budget',
        string = u'Presupuesto origen',
        required=True,
        )
    budget_id_destino = fields.Many2one(
        comodel_name='pa.budget',
        string = u'Presupuesto destino',
        required=True,
        )

    def create_lineas_presupuesto(self):
        lineas_origen = self.env['pa.budget.lines'].search([('budget_id','=',self.budget_id_origen.id)])
        if lineas_origen: 
            for linea in lineas_origen:
                self.env['pa.budget.lines'].create({
                    'budget_id': self.budget_id_destino.id,
                    'accounts_ids': [(6,0,linea.accounts_ids.id)],
                    'monto': linea.monto
                })
        else: raise exceptions.Warning(_(u"No hay líneas en presupuesto origen."))
        return True    

