# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from zeep import Client
from requests import Session
from requests.auth import HTTPBasicAuth
from zeep.transports import Transport
from odoo.exceptions import ValidationError

import logging

_logger = logging.getLogger(__name__)


import requests

class Partner(models.Model):
    _inherit = "res.partner"
    localidad_id = fields.Many2one('acc.localidad', string='Localidad')
    # product_node_ids = fields.Many2one('product.product','',domain="[('is_node','=',True)]")    
    def getProveedorZeep(self):
        wsdl = "http://datosinteroperables.test.cba.gov.ar/services/Finanzas/DatosProveedorCUB?wsdl"
        session = Session()
        session.auth = HTTPBasicAuth('OSBUSER_AGCONECT', 'OSB_AGCON*?')
        #An additional argument 'transport' is passed with the authentication details
 
        session.proxies = {
                                'https': 'http://proxysrv:8080',
                                }          
        client = Client(wsdl, transport=Transport(session=session)) 
        request_data = {
        'cuit': '20248842270',
        }
        response = client.service.obtenerDatosProveedorCUB(**request_data)
        return {
            'warning': {
            'title': 'Warning!',
            'message': response}
            }       
    def getProveedorRequestButton(self):
    
        url="http://datosinteroperables.test.cba.gov.ar/services/Finanzas/DatosProveedorCUB?wsdl:8080"
        #headers = {'content-type': 'application/soap+xml'}
        headers = {'content-type': 'text/xml'}
        body ="""<soap:Header xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
                    <wsse:Security soap:mustUnderstand="1"
                    xmlns:wsse="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-s
                    ecext-1.0.xsd">
                    <wsse:UsernameToken>
                    <wsse:Username>OSBUSER_AGCONECT</wsse:Username>
                    <wsse:Password
                    Type="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-username-token-pr
                    ofile-1.0#PasswordText">OSB_AGCON*?</wsse:Password>;
                    </wsse:UsernameToken>
                    </wsse:Security>
                    </soap:Header>"""

# <ns:encabezado>
# <!--Optional:-->
# <ns1:usuario>20248842270</ns1:usuario>
# <!--Optional:-->
# <ns1:token>?</ns1:token>
# <!--Optional:-->
# <ns1:sign>?</ns1:sign>
# <!--Optional:-->
# <ns1:aplicacion>Nombre_Aplicacion</ns1:aplicacion> 🡺 Nombre de la
# aplicación que usa
# el servicio
# </ns:encabezado>
        response = requests.post(url,data=body,headers=headers)
        _logger.warning('response webservice '+str(response))
        return {
            'warning': {
            'title': 'Warning!',
            'message': response}
            }
            
        #<button name="getProveedorRequestButton" string="Chequear proveedor" type="object" class="oe_link oe_inline"/>