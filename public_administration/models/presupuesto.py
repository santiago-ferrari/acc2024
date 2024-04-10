# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
import odoo.addons.decimal_precision as dp

import logging
_logger = logging.getLogger(__name__)
    
   
class Presupuesto(models.Model):

    _name = "pa.budget"
    _description = u"Presupuesto"
    _order = 'fiscalyear_id DESC'
    _rec_name = 'fiscalyear_id'
    
    fiscalyear_id = fields.Many2one(
        comodel_name='date.range',
        domain="[('type_name', '=', u'Año')]",        
        string = u'Año',
        required=True,
    )
        
    document_id = fields.Many2one(
        comodel_name='pa.budget.document',
        string = u'Documento relacionado',
        required=True,
    )
    
class LineasPresupuesto(models.Model):

    _name = "pa.budget.lines"
    _description = u"Líneas de presupuesto"
    _order = 'budget_id, name DESC'
    
    def compute_comprado(self):
        for line in self: 
            pol = self.env['purchase.order.line'].read_group(
            [
            ('state','in',['purchase','done']),
            ('budget_line_id','=',line.id),
            ('date_approve','>=',line.budget_id.fiscalyear_id.date_start),
            ('date_approve','<=',line.budget_id.fiscalyear_id.date_end)],
            ['price_total','price_total:sum'],['price_total']) 
            _logger.warning('pol adolfo '+str(pol)) 
            if len(pol)>0:
                for dict_pol in pol:
                    line.comprado += float(dict_pol['price_total'])            
                
            else: line.comprado =0
            
    def compute_comprado_facturado(self):
        for line in self: 
            pol = self.env['purchase.order.line'].read_group(
            [('invoice_lines.parent_state','=','posted'),
            ('state','in',['purchase','done']),
            ('budget_line_id','=',line.id),
            ('date_approve','>=',line.budget_id.fiscalyear_id.date_start),
            ('date_approve','<=',line.budget_id.fiscalyear_id.date_end)],
            ['price_total','price_total:sum'],['price_total']) 
            logger.warning('pol adolfo '+str(pol))
            comprado_y_facturado =0
            if len(pol)>0: 
                for dict_pol in pol:
                    comprado_y_facturado += dict_pol['price_total']
            return comprado_y_facturado
            
    def compute_balance(self):
    
        for line in self:
            balance = 0.0
            credit = 0.0
            debit = 0.0        
            for aml in self.env['account.move.line'].search([('account_id','in',line.accounts_ids.ids),('date','>=',line.budget_id.fiscalyear_id.date_start),('date','<=',line.budget_id.fiscalyear_id.date_end)]):
                _logger.warning('aml adolfo '+str(aml.debit))                
                #si tiene impuestos, si es factura
                if aml.price_total >0: credit += aml.price_total
                #si es asiento pero no factura
                if aml.price_total == 0: credit += aml.credit                
                
                if aml.price_total > 0: debit += aml.price_total
                if aml.price_total == 0: debit += aml.debit            

                # credit += aml.credit
                # debit += aml.debit
                    
            if line.recurso_erogacion == 'recurso': 
                line.ejecutado = credit
            if line.recurso_erogacion == 'erogacion': 
                line.ejecutado = debit
                
            line.saldo = line.monto-line.ejecutado-line.comprado
            
    budget_id = fields.Many2one(
        comodel_name='pa.budget',
        string = u'Presupuesto',
        required=True,
        )
        
    modificacion_presupuesto = fields.Boolean(
        string=u"Modificación del presupuesto",
        help=u"Indica si la línea corresponde a un presupuesto que se carga por primera vez en el año, o durante el transcurso del año (modificación del presupuesto).",
        default=True,
        required=True,
        readonly=True
        )
    name = fields.Char('Partida', 
        required=True
        )   
    accounts_ids = fields.Many2many(
        comodel_name='account.account',
        #inverse='budget_line_id'
        string='Cuenta', 
        domain="[('deprecated', '=', False)]",
        required=True,
        )        
    recurso_erogacion = fields.Selection([('erogacion','Erogación'),('recurso','Recurso')],
        string = u'Recurso/Erogación',
        default = 'erogacion',
        required=True
    )
 
    monto = fields.Float(
        string='Presupuestado', 
        required=True,
        )
    comprado = fields.Float(
        'Comprado',
        compute = "compute_comprado",
        )         
    ejecutado = fields.Float(
        'Ejecutado',
        compute = "compute_balance",
        )    
    saldo = fields.Float(
        'Saldo',
        compute = "compute_balance",
        store=True
        )

    _sql_constraints = [('budget_line_uniq','UNIQUE (budget_id,accounts_ids)',u'La cuenta debe ser única por presupuesto')
                       ,('monto_mayor_cero','CHECK (monto >= 0)','El monto debe ser mayor o igual a cero'),]
    
    
    # def name_get(self):
        # result = []
        # for record in self:
            # result.append((record.id, record.budget_id.fiscalyear_id.name +' - '+ record.accounts_ids.name))
        # return result
      
    @api.model
    def create(self, values):
        line =  super(LineasPresupuesto, self).create(values)
        proceso_id = self.env['ir.sequence'].next_by_code('log.lineas.presupuesto')
        self.env['pa.budget.lines.history'].create({'proceso_id':proceso_id,'budget_id':line.budget_id.id, 'budget_line':line.name,'accounts_ids':line.accounts_ids,'monto':line.monto, 'accion':'nueva'})
        return line
    
    def write(self, values):
        proceso_id = self.env['ir.sequence'].next_by_code('log.lineas.presupuesto')
        if 'monto' in values and values['monto']: 
            self.env['pa.budget.lines.history'].create({'proceso_id':proceso_id,'budget_id':self.budget_id.id, 'accounts_ids':self.accounts_ids,'monto': values['monto'], 'accion':'modificacion'})            
            #el compute balance se hace al ultimo, una vez que se modifican las cuentas
            self.compute_balance()
        if 'accounts_ids' in values and values['accounts_ids']: 
            self.env['pa.budget.lines.history'].create({'proceso_id':proceso_id,'budget_id':self.budget_id.id, 'budget_line':self.name, 'accounts_ids':values['accounts_ids'],'monto': self.monto, 'accion':'modificacion'})
        if 'budget_id' in values and values['budget_id']: 
            self.env['pa.budget.lines.history'].create({'proceso_id':proceso_id,'budget_id':values['budget_id'], 'budget_line':self.name, 'accounts_ids':self.accounts_ids,'monto': self.monto, 'accion':'modificacion'})
        return super(LineasPresupuesto, self).write(values)

    def unlink(self):
        proceso_id = self.env['ir.sequence'].next_by_code('log.lineas.presupuesto')
        for record in self:
            record.env['pa.budget.lines.history'].create({'proceso_id':proceso_id,'budget_id':record.budget_id.id,'budget_line':record.name,'accounts_ids':record.accounts_ids,'monto': record.monto, 'accion':'eliminacion'})
        return super(LineasPresupuesto, self).unlink()                
    
class HistorialLineasPresupuesto(models.Model):

    _name = 'pa.budget.lines.history'
    _order = 'id DESC'
    
    proceso_id = fields.Char('Proceso')
    
    budget_id = fields.Many2one(
        comodel_name='pa.budget',
        string = u'Presupuesto',
        readonly=True,
        #ondelete='set null'        
        )
    # budget_line_id = fields.Many2one(
        # comodel_name='pa.budget.lines', 
        # string='Partida', 
        # readonly=True,
        # #ondelete='set null'
        # )        
    budget_line = fields.Char('Partida'
        )    
    accounts_ids = fields.Many2many(
        comodel_name='account.account',
        string='Cuenta', 
        readonly=True,
        #ondelete='set null'
        )  
    monto = fields.Float(
        'Presupuestado',
        readonly=True, 
        )

    accion = fields.Selection(
        [('nueva','Nueva línea'),('modificacion',u'Modificación'),('eliminacion','Eliminación')],
        required=True,
        default='modificacion',
        string="Acción",
        readonly=True
        )
      
class Documentos(models.Model):

    _name = "pa.budget.document"
    _description = u"Ordenanzas, resoluciones y decretos"
    _rec_name = 'numero'
    
    documento_tipo = fields.Selection(
        [('ordenanza','Ordenanza'),('decreto','Decreto'),('resolucion',u'Resolución')],
        required=True,
        default='resolucion',
        string='Tipo',
        )
    
    fiscalyear_id = fields.Many2one(
        comodel_name='date.range',
        domain="[('type_name', '=', u'Año')]",        
        string = u'Año',
        required=True,
        )
    numero= fields.Char(u'Número',
        required=True,
    )
    documento = fields.Text('Texto del documento')
    attachment_ids = fields.Many2many('ir.attachment', string='Archivos adjuntos')
    
    
    def name_get(self):
        result = []
        for record in self: result.append((record.id, str(record.fiscalyear_id.name)+'/' +str(record.numero) or ""))
        return result 
      
class Compensaciones(models.Model):

    _name = "pa.budget.compensacion"
    _description = u"Erogación: Compensación de cuentas"
    _order = 'document_id DESC'

    budget_id = fields.Many2one(
        comodel_name='pa.budget',
        string = u'Presupuesto',
        required=True,
        )

    document_id = fields.Many2one(
        comodel_name='pa.budget.document',
        string = u'Documento relacionado',
        required=True,
        )
    budget_line_id_origen = fields.Many2one(
        comodel_name='pa.budget.lines', 
        string='Partida origen', 
        required=True,
        )
    monto_budget_line_origen = fields.Float(
        'Presupuestado origen',
        readonly=True, 
        ) 
    saldo_budget_line_origen = fields.Float(
        'Balance origen',
        digits=dp.get_precision('Account'),
        required=True,
        ) 
    budget_line_id_destino = fields.Many2one(
        comodel_name='pa.budget.lines', 
        string='Partida destino', 
        required=True,
        )
    monto_budget_line_destino = fields.Float(
        'Presupuestado destino',
        readonly=True, 
        )
    saldo_budget_line_destino = fields.Float(
        'Balance destino',
        digits=dp.get_precision('Account'),
        required=True,
        )
    monto = fields.Float(
        'Monto transferido', 
        help='Monto transferido desde la cuenta origen a la destino', 
        required=True, 
        digits=0
        )

