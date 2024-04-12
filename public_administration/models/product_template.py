# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
 
import logging
_logger = logging.getLogger(__name__)

class ProductTemplate(models.Model):
    _inherit = 'product.template'
    
    pa_budget_accounts_ids = fields.Many2many(
        comodel_name='pa.budget.account',
        string='Cuentas presupuestarias', 
        )