# -*- coding: utf-8 -*-
import logging
_logger = logging.getLogger(__name__)
from odoo import models, fields, api, _ 
from odoo.exceptions import UserError
from datetime import date, timedelta

class MotivosNoFactibilidades(models.Model):
    _name = 'acc.motivo.no.factibilidad'
    _description = 'Motivo de no factibilidad'
    name = fields.Char(string=u'Nombre')
    
class Lead(models.Model):
    _inherit = "crm.lead"

    partner_industry_id = fields.Many2one(readonly=True, related="partner_id.industry_id",string='Industria')
    partner_localidad_id = fields.Many2one(readonly=True,related='partner_id.localidad_id')
    products_node_ids = fields.Many2many('product.product',domain="[('is_node','=',True)]",string='Nodos')
    cumple_requisitos_legales = fields.Boolean('Cumple requisitos legales')
    project_id = fields.Many2one('project.project', string='Proyecto')
    project_stage_id = fields.Many2one(readonly=True,related='project_id.stage_id')
    node_zone_localidad_id = fields.Many2one(readonly=True,related='products_node_ids.zone_localidad_id')
    node_nodo_arsat = fields.Many2one(readonly=True,related='products_node_ids.nodo_arsat')
    motivo_no_factibilidad_id = fields.Many2one('acc.motivo.no.factibilidad',string='Motivo de no factibilidad')
    
    estado_contrato = fields.Selection([
                    ('doc_pendiente','1-Doc Pendiente'),
                    ('a_validar_GCA','2-A validar por GCA'),
                    ('doc_ok','3-Doc Ok'),
                    ('firmado','4-Firmado'),
                    ('firmado_acc','5-Firmado ACC'),
                    ('piloto','6-Piloto'),
                    ], 
                    string='Estado del contrato',
                    index=True,
        )
    tipo_factibilidad = fields.Selection([
                    ('interna','Interna'),
                    ('externa','Externa'),
                    ], 
                    string='Tipo factibilidad',
                    required=True,
        )
    ticket_jira = fields.Char('Ticket Jira')
    
    presentada_gca = fields.Boolean(u'Presentada a Gerencia Comercial?')
    
    def create(self, vals):
        reg = super(Lead, self).create(vals)
        # if reg.project_id:
            # project = self.env['project.project'].browse([re.project_id.id])
            # if project: project.write({'opportunity_id': reg.id})
        return reg            
        
    @api.depends('stage_id','tipo_factibilidad')
    def _onsave_stage_id(self):
        #Al pasar una oportunidad a estado no factible que se le asigne una actividad al ingeniero comercial de reingenieria
        stage_factibilizar=self.env.ref('config_acc.stage_factibilizar')
        _logger.warning('self.stage_id ' +str(self.stage_id.name))
        if self.stage_id.id == stage_factibilizar.id:
            today = date.today()
            dias_despues =0
            if self.tipo_factibilidad == 'interna': dias_despues = today + timedelta(days=5)
            if self.tipo_factibilidad == 'externa': dias_despues = today + timedelta(days=10)
            for user in self.env['res.users'].search([]):
                if user.has_group ('config_acc.acc_group_ingeniero_comercial'):
                    self.env['mail.activity'].create({'user_id': user.id,
                                                    'res_model_id': 'crm.lead',
                                                    'date_deadline':dias_despues})     
    
    def write(self, values):
    
        if 'project_id' in values and values['project_id']:
            project = self.env['project.project'].browse([values['project_id']])
            if project: project.write({'opportunity_id': self.id})

        #Al pasar una oportunidad a estado no factible que se le asigne una actividad al ingeniero comercial de reingenieria
        stage_factibilizar=self.env.ref('config_acc.stage_factibilizar')
        stage_no_factible=self.env.ref('config_acc.stage_no_factible')
        # _logger.warning('values ' +str(values))
        if 'stage_id' in values and int(values['stage_id']) == stage_no_factible.id:
            for user in self.env['res.users'].search([]):
                if user.has_group ('config_acc.acc_group_ingeniero_comercial'):
                    tipo_actividad=None
                    tipo_actividad=  self.env.ref('mail.mail_activity_data_todo')
                    if tipo_actividad: tipo_actividad=tipo_actividad.id
                    dias_despues =fields.Date.today()
                    self.env['mail.activity'].create({'user_id': user.id,
                                                    'res_model_id': self.env.ref('crm.model_crm_lead').id,
                                                    'res_id':self.id,
                                                    'date_deadline':dias_despues,
                                                    'summary':u'Oportunidad a no factible',
                                                    'activity_type_id':tipo_actividad,
                                                    })          
        if 'stage_id' in values and int(values['stage_id']) == stage_factibilizar.id:
            today = date.today()
            dias_despues =fields.Date.today()
            tipo_factibilidad= self._origin.tipo_factibilidad
            if 'tipo_factibilidad' in values: tipo_factibilidad = values['tipo_factibilidad']
            
            if tipo_factibilidad == 'interna': dias_despues = fields.Date.today() + timedelta(days=5)
            if tipo_factibilidad == 'externa': dias_despues = fields.Date.today() + timedelta(days=10)
            # _logger.warning('dias_despues ' +str(dias_despues))            
            for user in self.env['res.users'].search([]):
                if user.has_group ('config_acc.acc_group_ingeniero_comercial'):
                    tipo_actividad=None
                    tipo_actividad=  self.env.ref('mail.mail_activity_data_todo')
                    if tipo_actividad: tipo_actividad=tipo_actividad.id
                    
                    self.env['mail.activity'].create({'user_id': user.id,
                                                    'res_model_id': self.env.ref('crm.model_crm_lead').id,
                                                    'res_id':self.id,
                                                    'date_deadline':dias_despues,
                                                    'summary':u'Presentación de pedido de factibilidad',
                                                    'activity_type_id':tipo_actividad,
                                                    })  
                                                    
        return super(Lead, self).write(values) 
        
    @api.onchange('stage_id')
    def _onchange_stage_id(self):
        stage_factibilizar=self.env.ref('config_acc.stage_factibilizar')
        stage_negociacion=self.env.ref('config_acc.stage_negociacion')
        stage_provision=self.env.ref('config_acc.stage_provision')
        for record in self:
        
            if not self.env.user.has_group ('config_acc.acc_group_crm_a_factibilizar') and record.stage_id.id == stage_factibilizar.id:
                raise UserError(_('Usted no posee permisos para pasar A factibilizar esta oportunidad'))

            if not self.env.user.has_group ('config_acc.acc_group_crm_a_negociacion') and record.stage_id.id == stage_negociacion.id:
                raise UserError(_('Usted no posee permisos para pasar A Negociación esta oportunidad'))

            if not self.env.user.has_group ('config_acc.acc_group_crm_a_provision') and record.stage_id.id == stage_provision.id:
                raise UserError(_('Usted no posee permisos para pasar A Provisión esta oportunidad'))
            
            if not self.presentada_gca and record.stage_id.id == stage_negociacion.id:
                raise UserError(_('Antes de continuar, la oportunidad debe estar presentada a la Gerencia Comercial'))

    @api.onchange('estado_contrato')
    def _onchange_estado_contrato(self):
        for record in self:
            if not self.env.user.has_group ('config_acc.acc_group_estado_contrato_doc_pendiente_validarCGA') and record.estado_contrato == 'a_validar_GCA' and record._origin.estado_contrato=='doc_pendiente':
                raise UserError(_('Usted no posee permisos para pasar el estado del contrato desde 1-Doc Pendiente a 2-A validar por GCA'))                 
            
            if not self.env.user.has_group ('config_acc.acc_group_crm_estado_contrato_a_firmado_acc') and record.estado_contrato == 'firmado_acc':
                raise UserError(_('Usted no posee permisos para pasar el estado del contrato a 5-Firmado ACC'))
            
            if record._origin.estado_contrato not in ('doc_pendiente', None, False) and not self.env.user.has_group ('config_acc.acc_group_responsable_legales') and record.estado_contrato != 'a_validar_GCA' and record.estado_contrato != 'doc_pendiente':
                raise UserError(_('Usted no posee permisos para pasar el estado del contrato. Sólo usuarios con permiso Responsable Legales pueden cambiarlo'))          
