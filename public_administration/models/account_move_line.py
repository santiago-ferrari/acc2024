# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
import odoo.addons.decimal_precision as dp
from datetime import datetime,timedelta, date
from odoo.exceptions import ValidationError 
 
import logging
_logger = logging.getLogger(__name__)

class account_move_line(models.Model):
    _inherit = 'account.move.line'
    
    # def compute_presupuesto(self):
        # for line in self:
            # budget_line = self.env['pa.budget.lines'].search([('account_id','=',line.pa_budget_account_id.id),('budget_id.fiscalyear_id.name','=',str(datetime.now().year))], limit=1)
            # line.saldo_current_budget_line = budget_line.saldo
            # line.monto_current_budget_line = budget_line.monto  

    #@api.model
    @api.onchange('product_id')
    def _get_budget_lines(self):
        for line in self:
            domain =[]
            if line.move_type in('out_invoice','out_refund','out_receipt'):#cliente
                domain = [('budget_id.fiscalyear_id.name','=',str(datetime.now().year)),('recurso_erogacion','=','recurso'),('account_id','in',[p.id for p in line.product_id.pa_budget_accounts_ids])]
            if line.move_type in('in_invoice','in_refund','in_receipt'):#proveedor
                domain = [('budget_id.fiscalyear_id.name','=',str(datetime.now().year)),('recurso_erogacion','=','erogacion'),('account_id','in',[p.id for p in line.product_id.pa_budget_accounts_ids])]
            _logger.warning('domain '+str(domain))
            return {'domain': {'budget_line_id': domain}}
                    

    saldo_current_budget_line = fields.Float(
        related='budget_line_id.saldo'
        )
    monto_current_budget_line = fields.Float(
        related='budget_line_id.monto'
        )
    facturado_recurso_current_budget_line = fields.Float(
        related='budget_line_id.facturado_recurso'
        ) 
    facturado_erogacion_current_budget_line = fields.Float(
        related='budget_line_id.facturado_erogacion'
        )     
    #pa_budget_account_id = fields.Many2one('pa.budget.account',string='Cuenta presupuestaria',domain="[('id','in',(product_id.pa_budget_accounts_ids))]")
    #pa_budget_account_id = fields.Many2one('pa.budget.account',string='Cuenta presupuestaria')    

    #budget_line_id = fields.Many2one(comodel_name='pa.budget.lines',string='Partida',domain=_get_budget_lines)  
    budget_line_id = fields.Many2one(comodel_name='pa.budget.lines',string='Partida')      