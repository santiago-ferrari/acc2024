# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class ZonaLocalidad(models.Model):
    _name = 'acc.zona.localidad'
    _description='Zona de la localidad'   
    name = fields.Char(string=u'Zona de la localidad')
 
class Localidad(models.Model):
    _name = 'acc.localidad'
    _description='Localidad de los nodos'
    
    name = fields.Char(string=u'Nombre')
    nombre_abreviado = fields.Char(string=u'Nombre abreviado')
    departamento = fields.Char(string=u'Departamento')
    link_indec = fields.Char(string=u'Link INDEC')


class NodoState(models.Model):
    _name = 'acc.node.state'
    _description='Estado de los nodos'
    
    name = fields.Char(string=u'Estado del nodo')

class Produt(models.Model):
    _inherit = "product.template"
    _description ='Nodos'
    

    is_node = fields.Boolean(string=u'Es un nodo?')
    localidad_id = fields.Many2one('acc.localidad', string='Localidad')
    partner_maintenance_id =fields.Many2one('res.partner', string='Mantiene')
    nodo_arsat =fields.Many2one('acc.localidad', string='Nodo ARSAT')
    node_state_id=fields.Many2one('acc.node.state', string='Estado del nodo')
    zone_localidad_id =fields.Many2one('acc.zona.localidad', string='Zona de la localidad')    
