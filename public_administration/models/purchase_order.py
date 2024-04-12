# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
import odoo.addons.decimal_precision as dp
from datetime import datetime,timedelta, date
from odoo.exceptions import ValidationError 
 
import logging
_logger = logging.getLogger(__name__)

class purhase_order(models.Model):
    _inherit = 'purchase.order'

    def button_confirm(self):
        for order in self:
            if order.state not in ['draft', 'sent']:
                continue
            order.order_line._validate_analytic_distribution()
            order._add_supplier_to_product()
            # Deal with double validation process
            if order._approval_allowed():
                order.button_approve()
            else:
                order.write({'state': 'to approve'})
            if order.partner_id not in order.message_partner_ids:
                order.message_subscribe([order.partner_id.id])
        return True