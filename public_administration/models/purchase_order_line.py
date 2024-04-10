# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
import odoo.addons.decimal_precision as dp
from datetime import datetime,timedelta, date
from odoo.exceptions import ValidationError 
 
import logging
_logger = logging.getLogger(__name__)

class purhase_order_line(models.Model):
    _inherit = 'purchase.order.line'

    saldo_current_budget_line = fields.Float(
        related='budget_line_id.saldo'
        )
    monto_current_budget_line = fields.Float(
        related='budget_line_id.monto'
        )
    comprado_current_budget_line = fields.Float(
        related='budget_line_id.comprado'
        )        
    budget_line_id = fields.Many2one(
        comodel_name='pa.budget.lines', 
        string='Partida', 
        #required=True,
        )