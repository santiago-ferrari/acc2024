# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
import odoo.addons.decimal_precision as dp
from datetime import datetime,timedelta, date
from odoo.exceptions import ValidationError 
 
import logging
_logger = logging.getLogger(__name__)

class account_move_line(models.Model):
    _inherit = 'account.move.line'
    
    def compute_presupuesto(self):
        for line in self:
            budget_line = self.env['pa.budget.lines'].search([('accounts_ids','in',[line.account_id.id]),('budget_id.fiscalyear_id.name','=',str(datetime.now().year))], limit=1)
            line.saldo_current_budget_line = budget_line.saldo
            line.monto_current_budget_line = budget_line.monto    

    saldo_current_budget_line = fields.Float(
        string='Saldo',
        help = u'Saldo presupuesto año en curso',
        readonly=True,
        compute = "compute_presupuesto",
        )
    monto_current_budget_line = fields.Float(
        string ='Presupuestado',
        help = u'Presupuesto año en curso',
        readonly=True,
        compute = "compute_presupuesto",        
        )
        