# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from email.message import EmailMessage
from email.utils import make_msgid
import base64
import datetime
import email
import email.policy
import idna
import logging
import re
import smtplib
import ssl
import sys
import threading

from socket import gaierror, timeout
from OpenSSL import crypto as SSLCrypto
from OpenSSL.crypto import Error as SSLCryptoError, FILETYPE_PEM
from OpenSSL.SSL import Error as SSLError
from urllib3.contrib.pyopenssl import PyOpenSSLContext

from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError
from odoo.tools import ustr, pycompat, formataddr, email_normalize, encapsulate_email, email_domain_extract, email_domain_normalize


_logger = logging.getLogger(__name__)
_test_logger = logging.getLogger('odoo.tests')



import socks

#sobreescribo \usr\lib\python3\dist-packages\odoo\addons\base\models

class IrMailServer(models.Model):
    """Represents an SMTP server, able to send outgoing emails, with SSL and TLS capabilities."""
    _inherit = "ir.mail_server"


    def connect(self, host=None, port=None, user=None, password=None, encryption=None,
                smtp_from=None, ssl_certificate=None, ssl_private_key=None, smtp_debug=False, mail_server_id=None,
                allow_archived=False):
        """Returns a new SMTP connection to the given SMTP server.
           When running in test mode, this method does nothing and returns `None`.

           :param host: host or IP of SMTP server to connect to, if mail_server_id not passed
           :param int port: SMTP port to connect to
           :param user: optional username to authenticate with
           :param password: optional password to authenticate with
           :param string encryption: optional, ``'ssl'`` | ``'starttls'``
           :param smtp_from: FROM SMTP envelop, used to find the best mail server
           :param ssl_certificate: filename of the SSL certificate used for authentication
               Used when no mail server is given and overwrite  the odoo-bin argument "smtp_ssl_certificate"
           :param ssl_private_key: filename of the SSL private key used for authentication
               Used when no mail server is given and overwrite  the odoo-bin argument "smtp_ssl_private_key"
           :param bool smtp_debug: toggle debugging of SMTP sessions (all i/o
                              will be output in logs)
           :param mail_server_id: ID of specific mail server to use (overrides other parameters)
           :param bool allow_archived: by default (False), an exception is raised when calling this method on an
           archived record (using mail_server_id param). It can be set to True for testing so that the exception is no
           longer raised.
        """
        _logger.warning('paso smtplib 0')        
        # Do not actually connect while running in test mode
        if self._is_test_mode():
            return

        mail_server = smtp_encryption = None
        if mail_server_id:
            mail_server = self.sudo().browse(mail_server_id)
            if not allow_archived and not mail_server.active:
                raise UserError(_('The server "%s" cannot be used because it is archived.', mail_server.display_name))
        elif not host:
            mail_server, smtp_from = self.sudo()._find_mail_server(smtp_from)

        if not mail_server:
            mail_server = self.env['ir.mail_server']
        ssl_context = None

        if mail_server:
            smtp_server = mail_server.smtp_host
            smtp_port = mail_server.smtp_port
            if mail_server.smtp_authentication == "certificate":
                smtp_user = None
                smtp_password = None
            else:
                smtp_user = mail_server.smtp_user
                smtp_password = mail_server.smtp_pass
            smtp_encryption = mail_server.smtp_encryption
            smtp_debug = smtp_debug or mail_server.smtp_debug
            from_filter = mail_server.from_filter
            if (mail_server.smtp_authentication == "certificate"
               and mail_server.smtp_ssl_certificate
               and mail_server.smtp_ssl_private_key):
                try:
                    ssl_context = PyOpenSSLContext(ssl.PROTOCOL_TLS)
                    smtp_ssl_certificate = base64.b64decode(mail_server.smtp_ssl_certificate)
                    certificate = SSLCrypto.load_certificate(FILETYPE_PEM, smtp_ssl_certificate)
                    smtp_ssl_private_key = base64.b64decode(mail_server.smtp_ssl_private_key)
                    private_key = SSLCrypto.load_privatekey(FILETYPE_PEM, smtp_ssl_private_key)
                    ssl_context._ctx.use_certificate(certificate)
                    ssl_context._ctx.use_privatekey(private_key)
                    # Check that the private key match the certificate
                    ssl_context._ctx.check_privatekey()
                except SSLCryptoError as e:
                    raise UserError(_('The private key or the certificate is not a valid file. \n%s', str(e)))
                except SSLError as e:
                    raise UserError(_('Could not load your certificate / private key. \n%s', str(e)))

        else:
            # we were passed individual smtp parameters or nothing and there is no default server
            smtp_server = host or tools.config.get('smtp_server')
            smtp_port = tools.config.get('smtp_port', 25) if port is None else port
            smtp_user = user or tools.config.get('smtp_user')
            smtp_password = password or tools.config.get('smtp_password')
            from_filter = self.env['ir.config_parameter'].sudo().get_param(
                'mail.default.from_filter', tools.config.get('from_filter'))
            smtp_encryption = encryption
            if smtp_encryption is None and tools.config.get('smtp_ssl'):
                smtp_encryption = 'starttls' # smtp_ssl => STARTTLS as of v7
            smtp_ssl_certificate_filename = ssl_certificate or tools.config.get('smtp_ssl_certificate_filename')
            smtp_ssl_private_key_filename = ssl_private_key or tools.config.get('smtp_ssl_private_key_filename')

            if smtp_ssl_certificate_filename and smtp_ssl_private_key_filename:
                try:
                    ssl_context = PyOpenSSLContext(ssl.PROTOCOL_TLS)
                    ssl_context.load_cert_chain(smtp_ssl_certificate_filename, keyfile=smtp_ssl_private_key_filename)
                    # Check that the private key match the certificate
                    ssl_context._ctx.check_privatekey()
                except SSLCryptoError as e:
                    raise UserError(_('The private key or the certificate is not a valid file. \n%s', str(e)))
                except SSLError as e:
                    raise UserError(_('Could not load your certificate / private key. \n%s', str(e)))

        if not smtp_server:
            raise UserError(
                (_("Missing SMTP Server") + "\n" +
                 _("Please define at least one SMTP server, "
                   "or provide the SMTP parameters explicitly.")))

        if smtp_encryption == 'ssl':
            if 'SMTP_SSL' not in smtplib.__all__:
                raise UserError(
                    _("Your Odoo Server does not support SMTP-over-SSL. "
                      "You could use STARTTLS instead. "
                       "If SSL is needed, an upgrade to Python 2.6 on the server-side "
                       "should do the trick."))
            connection = smtplib.SMTP_SSL(smtp_server, smtp_port, timeout=SMTP_TIMEOUT)
        else:
            #'proxy_port' should be an integer
            #'PROXY_TYPE_SOCKS4' can be replaced to HTTP or PROXY_TYPE_SOCKS5
            #socks.setdefaultproxy(socks.PROXY_TYPE_HTTP , '10.250.5.8', 8080)
            _logger.warning('paso smtplib')
            #socks.wrapmodule(smtplib)        
            connection = smtplib.SMTP(smtp_server, smtp_port, timeout=SMTP_TIMEOUT)
            
            

        connection.set_debuglevel(smtp_debug)
        if smtp_encryption == 'starttls':
            # starttls() will perform ehlo() if needed first
            # and will discard the previous list of services
            # after successfully performing STARTTLS command,
            # (as per RFC 3207) so for example any AUTH
            # capability that appears only on encrypted channels
            # will be correctly detected for next step
            connection.starttls(context=ssl_context)

        if smtp_user:
            # Attempt authentication - will raise if AUTH service not supported
            local, at, domain = smtp_user.rpartition('@')
            if at:
                smtp_user = local + at + idna.encode(domain).decode('ascii')
            mail_server._smtp_login(connection, smtp_user, smtp_password or '')

        # Some methods of SMTP don't check whether EHLO/HELO was sent.
        # Anyway, as it may have been sent by login(), all subsequent usages should consider this command as sent.
        connection.ehlo_or_helo_if_needed()

        # Store the "from_filter" of the mail server / odoo-bin argument to  know if we
        # need to change the FROM headers or not when we will prepare the mail message
        connection.from_filter = from_filter
        connection.smtp_from = smtp_from

        return connection

