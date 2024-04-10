# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
import odoo.addons.decimal_precision as dp

import logging
_logger = logging.getLogger(__name__)

class Compensaciones(models.TransientModel):
    _name = "pa.budget.compensacion.wizard"
    _description = u"Erogación: Crear compensación de cuentas"
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
        domain="[('recurso_erogacion', '=', 'erogacion'),('saldo', '>', '0'),('budget_id', '=', budget_id)]",
        )
    monto_budget_line_origen = fields.Float(
        'Presupuestado origen',
        related='budget_line_id_origen.monto',
        readonly=True, 
        ) 
    saldo_budget_line_origen = fields.Float(
        'Saldo origen',
        related='budget_line_id_origen.saldo',
        digits=dp.get_precision('Account'),
        readonly=True, 
        ) 
    budget_line_id_destino = fields.Many2one(
        comodel_name='pa.budget.lines', 
        string='Partida destino', 
        required=True,
        domain="[('recurso_erogacion', '=', 'erogacion'),('saldo', '<', '0'),('budget_id', '=', budget_id)]",
        )
    monto_budget_line_destino = fields.Float(
        'Presupuestado destino',
        related='budget_line_id_destino.monto',
        readonly=True, 
        )
    saldo_budget_line_destino = fields.Float(
        'Saldo destino',
        related='budget_line_id_destino.saldo',
        digits=dp.get_precision('Account'),
        readonly=True, 
        )
    monto = fields.Float(
        'Monto a transferir', 
        help='Monto a transferir desde la cuenta origen a la destino', 
        required=True, 
        digits=dp.get_precision('Account'),
        )

    @api.constrains('monto')
    def _check_monto(self):
        for r in self:
            if r.monto > r.saldo_budget_line_origen: raise models.ValidationError('No hay salddo suficiente en la cuenta origen para transferir ' + str(r.saldo))
            if r.monto <= 0.0: raise models.ValidationError('El monto a transferir no puede ser menor o igual a cero.')
            if r.budget_line_id_origen.id == r.budget_line_id_destino.id : raise models.ValidationError('La cuenta origen y destino no puede ser la misma.')
  

    def create_compensacion_presupuesto(self):
        
        compensacion = self.env['pa.budget.compensacion'].create({
                                                        'budget_id':self.budget_id.id,
                                                        'document_id':self.document_id.id,
                                                        'budget_line_id_origen': self.budget_line_id_origen.id,
                                                        'monto_budget_line_origen': self.monto_budget_line_origen,
                                                        'saldo_budget_line_origen': self.saldo_budget_line_origen,
                                                        'budget_line_id_destino': self.budget_line_id_destino.id,
                                                        'monto_budget_line_destino': self.monto_budget_line_destino,
                                                        'saldo_budget_line_destino': self.saldo_budget_line_destino,
                                                        'monto': self.monto,
                                                        })                
        #_logger.warn("compensacion " +str(compensacion))                                                        
        #decremento la cuenta origen
        self.budget_line_id_origen.write({'monto': self.monto_budget_line_origen - self.monto})
        #incremento la cuenta destino
        self.budget_line_id_destino.write({'monto': self.monto_budget_line_destino + self.monto})
        return