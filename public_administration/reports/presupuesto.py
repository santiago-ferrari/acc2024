# -*- coding: utf-8 -*-
import locale
import openerp
from itertools import groupby
import operator
import base64
from openerp.exceptions import except_orm, Warning
from openerp import models, fields, api, _
try:
    import xlwt
except ImportError:
    xlwt = None
import re
from io import StringIO
import time
import datetime

import logging
_logger = logging.getLogger(__name__)

class report_presupuesto(models.AbstractModel):

    _name = 'report.public_administration.presupuesto'   
 
    def get_presupuesto_recursos(self, form):
        _logger.warn("adolfo form get_presupuesto_recursos "+str(form))
        data = []

        ids_cuentas = []
        tags_ids = []
        result = {}
        
        tags = self.env['account.account.tag'].search([('name','ilike','Recurso')])
        for tag in tags: tags_ids.append(tag.id)
        
        cuentas_recursos = self.env['account.account'].search([('recurso_erogacion','=','recurso'),])
        if len(cuentas_recursos) == 0: raise Warning(_("No hay cuentas de recursos para mostrar. Asigne etiquetas de recursos a una cuenta al menos."))
        for cuenta in cuentas_recursos: ids_cuentas.append(cuenta.id)

        lineas_presupuesto = self.env['pa.budget.lines'].search([('budget_id','=',form['budget_id'][0]),('account_id', 'in', ids_cuentas)],order="account_id")
        if len(lineas_presupuesto) == 0: raise Warning(_(u"No hay líneas de presupuesto. Establezca al menos una línea para el presupuesto elegido."))
        
        tag_names= [{'name':'Subrubro Recurso','code':'subrubro'},{'name':'Rubro Recurso','code':'rubro'},{'name':'Item Recurso','code':'item'},{'name':'Inciso Recurso','code':'inciso'},{'name':'Anexo Recurso','code':'anexo'}]
        for dict_tag in tag_names:
            ids_cuentas = []
            tag = self.env['account.account.tag'].search([('name','=',dict_tag['name'])])
            cuentas = self.env['account.account'].search([('tag_ids','in',tag.id)])
            for cuenta in cuentas:
                _logger.warn(str(dict_tag['name'])+' - cuenta '+str(cuenta.name))
                ids_cuentas.append(cuenta.id)
            lineas_presupuesto = self.env['pa.budget.lines'].search([('budget_id','=',form['budget_id'][0]),('account_id', 'in', ids_cuentas)], order="account_id")
            
            for lp in lineas_presupuesto:
                result['vista'] = lp.account_vista_presupuesto
                result['codigo'] = ""
                result['descripcion'] = ""
                result['subrubro'] = ""
                result['rubro'] = ""
                result['item'] = ""
                result['inciso'] = ""
                result['anexo'] = ""

                result['codigo'] = lp.account_id.code
                result['descripcion'] = lp.account_id.name

                result[dict_tag['code']] = "$ {:,.2f}".format(lp.monto)

                _logger.warn('result '+str(result))
                data.append(result)
                result = {}

        if data:
            _logger.warn("data recursos cantidad "+str(len(data)))
            data = sorted(data, key = lambda i: i['codigo'],reverse=False) 
            _logger.warn("data recursos "+str(data))
            return data
        else:
            return {}
          
          
    def get_presupuesto_erogaciones(self, form):
        _logger.warn("adolfo form get_presupuesto_erogaciones "+str(form))
        data = []

        ids_cuentas = []
        tags_ids = []
        result = {}
        
        tags = self.env['account.account.tag'].search([('name','ilike','Recurso')])
        for tag in tags: tags_ids.append(tag.id)
        
        cuentas_erogacion = self.env['account.account'].search([('recurso_erogacion','=','erogacion'),])
        _logger.warn("data len(cuentas_erogacion) "+str(len(cuentas_erogacion)))        
        if len(cuentas_erogacion) == 0: raise Warning(_(u"No hay cuentas de erogación para mostrar. Asigne las etiquetas de recursos a una cuenta al menos."))
        for cuenta in cuentas_erogacion: ids_cuentas.append(cuenta.id)

        lineas_presupuesto = self.env['pa.budget.lines'].search([('budget_id','=',form['budget_id'][0]),('account_id', 'in', ids_cuentas)],order="account_id")
        if len(lineas_presupuesto) == 0: raise Warning(_(u"No hay líneas de presupuesto. Establezca al menos una línea para el presupuesto elegido."))
        
        tag_names= [{'name':'Sub-Partida Erogación','code':'sub_partida'},{'name':'Partida Erogación','code':'partida'},{'name':'Sub Item Erogación','code':'sub_item'},{'name':'Item Erogación','code':'item'},{'name':'Part. Pal. Erogación','code':'part_pal'},{'name':'Inciso Erogación','code':'inciso'}, {'name':'Anexo Erogación','code':'anexo'}]
        for dict_tag in tag_names:
            ids_cuentas = []
            tag = self.env['account.account.tag'].search([('name','=',dict_tag['name'])])
            cuentas = self.env['account.account'].search([('tag_ids','in',tag.id)])
            for cuenta in cuentas:
                _logger.warn(str(dict_tag['name'])+' - cuenta '+str(cuenta.name))
                ids_cuentas.append(cuenta.id)
            lineas_presupuesto = self.env['pa.budget.lines'].search([('budget_id','=',form['budget_id'][0]),('account_id', 'in', ids_cuentas)], order="account_id")
            
            for lp in lineas_presupuesto:
                result['vista'] = lp.account_vista_presupuesto
                result['codigo'] = ""
                result['descripcion'] = ""
                result['sub_partida'] = ""
                result['partida'] = ""
                result['sub_item'] = ""
                result['item'] = ""
                result['part_pal'] = ""
                result['inciso'] = ""
                result['anexo'] = ""
                result['codigo'] = lp.account_id.code
                result['descripcion'] = lp.account_id.name
                result['categoria_empleado'] = ""
                result['cargo_empleado'] = ""
                result['importe_mensual_empleado']= ""
                result['importe_anual_empleado']= ""
                
                result[dict_tag['code']] = "$ {:,.2f}".format(lp.monto)
                
                _logger.warn('result '+str(result))
                data.append(result)
                result = {}

        if data:
            _logger.warn("data erogacion cantidad "+str(len(data)))
            data = sorted(data, key = lambda i: i['codigo'],reverse=False) 
            _logger.warn("data erogacion "+str(data))
            return data
        else:
            return {}   
       
 
    def get_ejecucion_recursos(self, form):
        _logger.warn("adolfo form "+str(form))
        data = []
        result = {}
        ids_cuentas = []        
        
        fecha_fin = fields.Date.today()
        mes_actual = str(fields.Date.today())[5:7]
        if form['date_end']: fecha_fin = form['date_end']
          
        tags_ids = []
        
        tags = self.env['account.account.tag'].search([('name','ilike','Recurso')])
        for tag in tags: tags_ids.append(tag.id)
        cuentas_recursos = self.env['account.account'].search([('tag_ids','in',tags_ids)])

        if len(cuentas_recursos) == 0: raise Warning(_("No hay cuentas de recursos para mostrar. Asigne la etiqueta RECURSO a una cuenta al menos."))
        
        for cuenta in cuentas_recursos: ids_cuentas.append(cuenta.id)
        lineas_presupuesto = self.env['pa.budget.lines'].search([('budget_id','=',form['budget_id'][0]),('account_id', 'in', ids_cuentas)],order='account_id')
        if len(lineas_presupuesto) == 0: raise Warning(_(u"No hay líneas de presupuesto. Establezca al menos una línea para el presupuesto elegido."))
        
        for lp in lineas_presupuesto:
            result['vista'] = lp.account_vista_presupuesto
            result['codigo'] = ""
            result['descripcion'] = ""
            result['calculo_recursos'] = ""
            #result['recaudado_mes'] = ""
            result['recaudado_acumulado']= ""
            result['diferencia_acumulada_menos']= ""
            result['diferencia_acumulada_mas']= ""
            result['porcentaje_recaudacion']= ""
        
            result['codigo'] = lp.account_id.code
            result['descripcion'] = lp.account_id.name
            
            result['calculo_recursos'] = "$ {:,.2f}".format(lp.monto)
            #recaudado mes
            #credit = lp.account_id.with_context(date_from = str(lp.budget_id.fiscalyear_id.name)+'-'+mes_actual+'-01',date_to = fecha_fin).compute_values()['credit']
            #credit = lp.account_id.compute_values_with_period(str(lp.budget_id.fiscalyear_id.name)+'-'+mes_actual+'-01',fecha_fin)['credit']
            #result['recaudado_mes'] = "$ {:,.2f}".format(credit)
            
            #recaudado desde el 1 de enero anio en curso hasta fecha fin
            credit = lp.account_id.compute_values_with_period(str(lp.budget_id.fiscalyear_id.name)+'-01-01',fecha_fin)['credit']
            result['recaudado_acumulado'] = "$ {:,.2f}".format(credit)

            result['diferencia_acumulada_menos'] = "$ {:,.2f}".format(float(lp.monto) - float(credit))
            if float(credit) > float(lp.monto): 
                result['diferencia_acumulada_mas'] = "$ {:,.2f}".format(float(credit) - float(lp.monto))
            if float(lp.monto)>0: 
                result['porcentaje_recaudacion'] = "$ {:,.2f}".format(float(credit)/float(lp.monto)*100)
            else:
                result['porcentaje_recaudacion'] = "$ {:,.2f}".format(0)

            data.append(result)
            result = {}
        if data:
            return data
        else:
            return {}

    def get_ejecucion_erogaciones(self, form):
        #locale.setlocale(locale.LC_ALL, 'es_AR')
        _logger.warn("adolfo form "+str(form))
        data = []
        result = {}
        ids_cuentas = []
        
        fecha_fin = fields.Date.today()
        mes_actual = str(fields.Date.today())[5:7]
        if form['date_end']: fecha_fin = form['date_end']
          
        tags_ids = []
        
        tags = self.env['account.account.tag'].search([('name','ilike','Erogación')])
        for tag in tags: tags_ids.append(tag.id)
        cuentas_erogaciones = self.env['account.account'].search([('tag_ids','in',tags_ids)])
        if len(cuentas_erogaciones) == 0: raise Warning(_("No hay cuentas de erogación para mostrar. Asigne la etiqueta EROGACION a una cuenta al menos."))
        for cuenta in cuentas_erogaciones: ids_cuentas.append(cuenta.id)
        lineas_presupuesto = self.env['pa.budget.lines'].search([('budget_id','=',form['budget_id'][0]),('account_id', 'in', ids_cuentas)], order="account_id")
        if len(lineas_presupuesto) == 0: raise Warning(_(u"No hay líneas de presupuesto. Establezca al menos una línea para el presupuesto elegido."))               
        
        for lp in lineas_presupuesto:
            result['vista'] = lp.account_vista_presupuesto
            result['codigo'] = ""
            result['descripcion'] = ""
            result['presupuesto_autorizado'] = "$ {:,.2f}".format(lp.monto)
            #result['imputado_mes'] = ""
            
            #imputado desde el 1 de enero del anio en curso hasta fecha fin
            debit = lp.account_id.compute_values_with_period(str(lp.budget_id.fiscalyear_id.name)+'-01-01', fecha_fin)['debit']
            #result['imputado_mes'] = "$ {:,.2f}".format(debit)
            
            result['imputado_acumulado']= "$ {:,.2f}".format(debit)#round(lp.ejecutado,2)
            result['disponible']= "$ {:,.2f}".format(lp.saldo)
            result['porcentaje_imputado']= ""
            #result['pagado_mes'] = ""
            #result['pagado_acumulado']= ""
            #result['saldo_a_pagar']= ""
            #result['porcentaje_pagado']= ""
        
            result['codigo'] = lp.account_id.code
            result['descripcion'] = lp.account_id.name

            
            
            if float(lp.monto)>0: result['porcentaje_imputado'] = "{:,.2f}".format(float(debit)/float(lp.monto)*100)
            else: result['porcentaje_imputado'] = 0
            
            #result['pagado_mes'] = self.get_ejecucion_childs(domain_account_move_line)
            #domain_account_move_line = [('account_id','in',ids_cuentas_hijas), ('date','>=',str(lp.budget_id.fiscalyear_id.name)+'-01-01'),('date','<=',fecha_fin)]
            #result['pagado_acumulado'] = self.get_ejecucion_childs(domain_account_move_line)
            #result['saldo_a_pagar'] = float(result['presupuesto_autorizado']) - float(result['imputado_acumulado'])
            #result['porcentaje_pagado'] = ((float(result['imputado_acumulado']*float(result['presupuesto_autorizado'])/100),2))

            data.append(result)
            result = {}
        if data:
            return data
        else:
            return {}

    @api.model
    def get_report_values(self, docids, data=None):
        if not data.get('form') or not self.env.context.get('active_model') or not self.env.context.get('active_id'):
            raise UserError(_("Form content is missing, this report cannot be printed."))

        self.model = self.env.context.get('active_model')
        docs = self.env[self.model].browse(self.env.context.get('active_id'))      
        
        presupuesto_erogaciones = None
        presupuesto_recursos = None
        ejecucion_erogaciones = None
        ejecucion_recursos = None
        titulo = None
        if data['form']['reporte'] == 'pi':  
            presupuesto_recursos = self.get_presupuesto_recursos(data['form'])
            titulo = u'Cálculo de Recursos Año '
        if data['form']['reporte'] == 'pe':
            presupuesto_erogaciones = self.get_presupuesto_erogaciones(data['form'])
            titulo = u'Presupuesto de Erogaciones Año '
        if data['form']['reporte'] == 'epi':  
            ejecucion_recursos = self.get_ejecucion_recursos(data['form'])
            titulo = u'Ejecución de presupuesto (Recursos) Año '
        if data['form']['reporte'] == 'epe':  
            ejecucion_erogaciones = self.get_ejecucion_erogaciones(data['form'])
            titulo = u'Ejecución de presupuesto (Erogaciones) Año '
            
        titulo += data['form']['budget_id'][1]+ ' al '+data['form']['date_end']
        #_logger.warn("paso adolfo data " +str(data['form']))
        docargs = {
            'titulo': titulo,
            'presupuesto_recursos': presupuesto_recursos,
            'presupuesto_erogaciones':presupuesto_erogaciones,
            'ejecucion_erogaciones':ejecucion_erogaciones,
            'ejecucion_recursos': ejecucion_recursos,
            'doc_ids': self.ids,
            'doc_model': self.model,
            'data': data,
            'docs': docs,
        }
        return docargs
        #return self.env['report'].render('public_administration.presupuesto', docargs)


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: