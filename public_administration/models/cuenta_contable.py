# -*- coding: utf-8 -*-

from openerp import models, fields, api, _
import openerp.addons.decimal_precision as dp
from datetime import datetime,timedelta, date
from odoo.exceptions import ValidationError

from ast import literal_eval

import logging
_logger = logging.getLogger(__name__)

class AccountAccount(models.Model):
    
    _inherit = 'account.account'
    recurso_erogacion = fields.Selection([('erogacion','Erogación'),('recurso','Recurso')],
        string = u'Recurso/Erogación',
        #default = 'erogacion'
    )
    # _sql_constraints = [
            # #('code_company_uniq', 'CHECK(1=1)', 'Existe !'),
            # ('code_company_uniq', 'unique (code,recurso_erogacion,company_id)', u'El código debe ser único por tipo recurso o erogacion !')
    # ]
