# © 2016 ADHOC SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, api, fields, _
from odoo.exceptions import ValidationError


class AccountPaymentGroup(models.Model):
    _inherit = "account.payment.group"

    # def post(self):
        # """ Post payment group. Sobrescribo para poner en matched_move_line_ids la cuenta presupuestaria"""
        # return_value = super(AccountPaymentGroup, self)).post()
        # for move_line in matched_move_line_ids:
            # if move_line.
            # move_line.write({'':})

        # return True

 