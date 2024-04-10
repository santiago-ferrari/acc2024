# -*- coding: utf-8 -*-
from openerp import models, fields, api, exceptions, _
from openerp.exceptions import Warning
import openerp.addons.decimal_precision as dp
import logging
import calendar
from datetime import date, datetime, timedelta
import pytz
from dateutil.relativedelta import relativedelta
_logger = logging.getLogger(__name__)

class presupuesto(models.TransientModel):

    _name = 'pa.wizard_report_presupuesto'
    _description = 'Cuentas presupuestarias'
    reporte = fields.Selection(
        [('pe','Presupuesto de erogaciones'),('pi','Presupuesto de recursos'),
        ('epe',u'Ejecución de presupuesto: Erogaciones'),('epi',u'Ejecución de presupuesto: Recursos')],
        required=True,
        string='Reporte',
        )    
  
    budget_id = fields.Many2one(
        comodel_name='pa.budget',
        string = u'Presupuesto',
        required=True,
        )    
    #date_start = fields.Date(string='Fecho inicio')
    date_end = fields.Date(
        string='Fecha hasta',
        default=fields.Date.today()
    )
    #accounts_tags_ingreso_eroga_ids = fields.Many2many(
    #    comodel_name='account.account.tag',
    #    required=True,
    #    string='Ingresos/Erogaciones',
    #    domain="([('name', 'in', ('INGRESOS','EROGACIONES')])"
    #    )
    #accounts_tags_niveles_ids = fields.Many2many(
    #    comodel_name='account.account.tag',
    #    required=True,
    #    string='Niveles',
    #    domain="([('name', 'in', ['Subrubro','Rubro','Inciso Recurso','Anexo Recurso','Item','Sub-Partida','Partida','Item','Part. Pal.','Inciso Erogación','Anexo Erogación' ])])"
    #    )


    def print_report_presupuesto(self, data):
        res = self.read(['reporte', 
                         'budget_id',
                         'date_end',
                         #'accounts_tags_niveles_ids',
                        ])
        res = res and res[0] or {}
        data['form'] = res
        if res.get('id',False):
            data['ids']=[res['id']]      
        _logger.warn("adolfo datas "+str(data))
        
        #return self.env['report'].with_context(landscape=True).get_action(self,'public_administration.presupuesto', data=data)
        return self.env.ref('public_administration.pa_presupuesto').report_action(self, data=data)
      
    

    def download_file_lf(self):
        res=self.env['ir.exports'].export_il(self.date_start,
                                            self.date_end, 
                                            None, 
                                            None)
        return res    
