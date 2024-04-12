# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import fields, models, api, _
from odoo.exceptions import UserError
from zeep import transports

import logging

_logger = logging.getLogger(__name__)

class ARTransport(transports.Transport):


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.session.mount('https://', L10nArHTTPAdapter()) # block DH ciphers for AFIP servers
        #10.250.5.8
        #proxysrv.gobiernocba.gov.ar
        #proxydesa.gobiernocba.gob.ar
        #                        'http': 'http://proxydesa:8080',
        self.session.proxies = {
                                'https': 'http://proxysrv:8080',
                                }  
        #transport=Transport(session=session)