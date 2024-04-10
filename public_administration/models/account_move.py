from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

 
import logging
_logger = logging.getLogger(__name__)

class account_move(models.Model):
    _inherit = 'account.move'
    
    # @api.constrains('invoice_origin')
    # def verificar_total_commpra(self):
    def _post(self, soft=True):
        for record in self:

            purchases = self.env['purchase.order'].search([('name','=',record.invoice_origin)])
            # _logger.warning('purchase adolfo '+str(purchase))
            # _logger.warning('purchase.amount_untaxed adolfo '+str(purchase.amount_untaxed))               
            # _logger.warning('record.amount_untaxed adolfo '+str(record.amount_untaxed))            
            if len(purchases)>0:
                for purchase in purchases:
                    all_invoices_amount_untaxed=0
                    invoice_names=''
                    for invoice in purchase.invoice_ids:
                        all_invoices_amount_untaxed += invoice.amount_untaxed
                        invoice_names += invoice.name+' - '
                    if purchase.amount_untaxed < all_invoices_amount_untaxed:
                    # _logger.warning('purchase.amount_untaxed adolfo '+str(purchase.amount_untaxed))               
                    # _logger.warning('record.amount_untaxed adolfo '+str(record.amount_untaxed))
                        if len(purchase.invoice_ids)>1:
                            raise ValidationError(_('La suma de los montos totales sin impuestos de este comprobante y de '+invoice_names+' puede ser mayor al monto total sin impuestos de la orden de compras '+str(purchase.name)))
                        if len(purchase.invoice_ids)==1:
                            raise ValidationError(_('El monto total sin impuestos de este comprobante no puede ser mayor al monto total sin impuestos de la orden de compras '+str(purchase.name)))
        return super(account_move, self)._post(soft=True)