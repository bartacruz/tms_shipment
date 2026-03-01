from odoo import _, api, fields, models
from odoo.tools import frozendict


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    def _compute_totals(self):
        tms_factors = {}
        for line in self.filtered(lambda r: r.product_id.tms_trip):
            tms_factors[line.id] = line.tms_factor
            line.tms_factor = 1
        ret = super()._compute_totals()
        for line in self.filtered(lambda r: r.product_id.tms_trip):
            line.tms_factor =tms_factors[line.id]
        return ret
    
    def _compute_all_tax(self):
        tms_factors = {}
        for line in self.filtered(lambda r: r.product_id.tms_trip):
            tms_factors[line.id] = line.tms_factor
            line.tms_factor = 1
            
        ret = super()._compute_all_tax()
        
        for line in self.filtered(lambda r: r.product_id.tms_trip):
            line.tms_factor =tms_factors[line.id]
        return ret
                
    def _convert_to_tax_base_line_dict(self):
        """ Convert the current record to a dictionary in order to use the generic taxes computation method
        defined on account.tax.
        :return: A python dictionary.
        """
        self.ensure_one()
        tms_factor = self.tms_factor
        if self.product_id.tms_trip:
            self.tms_factor = 1
        ret = super()._convert_to_tax_base_line_dict()
        if self.product_id.tms_trip:
            self.tms_factor = tms_factor
        return ret
        
        # if self.product_id.tms_trip:
        #     is_invoice = self.move_id.is_invoice(include_receipts=True)
        #     sign = -1 if self.move_id.is_inbound(include_receipts=True) else 1

        #     return self.env['account.tax']._convert_to_tax_base_line_dict(
        #         self,
        #         partner=self.partner_id,
        #         currency=self.currency_id,
        #         product=self.product_id,
        #         taxes=self.tax_ids,
        #         price_unit=self.price_unit if is_invoice else self.amount_currency,
        #         quantity=self.quantity if is_invoice else 1.0,
        #         discount=self.discount if is_invoice else 0.0,
        #         account=self.account_id,
        #         analytic_distribution=self.analytic_distribution,
        #         price_subtotal=sign * self.amount_currency,
        #         is_refund=self.is_refund,
        #         rate=(abs(self.amount_currency) / abs(self.balance)) if self.balance else 1.0
        #     )
        # return super()._convert_to_tax_base_line_dict()