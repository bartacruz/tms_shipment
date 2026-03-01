from odoo import _, api, fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"
    
    tms_origin_locality_id = fields.Many2one('afip.locality')
    tms_destination_locality_id = fields.Many2one('afip.locality')
    
    def _prepare_tms_values(self, **kwargs):
        ret = super()._prepare_tms_values(**kwargs)
        ret['origin_locality_id'] = self.tms_origin_locality_id.id or None
        ret['destination_locality_id'] = self.tms_destination_locality_id.id or None
        
        if self.state == "cancel":
            stage = self.env.ref("tms.tms_stage_order_cancelled")
        else:
            stage = self.env.ref("tms.tms_stage_order_draft")
        if self.tms_order_ids.stage_id != stage:
            ret['stage_id']=stage.id
        
        return ret
    
    def _check_required_fields(self):
        print("Ignoring fields check")
    
    @api.depends('order_id.pricelist_id', 'tms_order_ids.distance', 'product_uom_qty','tms_factor')
    def _compute_pricelist_item_id(self):
        super()._compute_pricelist_item_id()
        for line in self:
                if line.order_id.pricelist_id.tms_use_distance and line.tms_order_ids:
                    quantity = line.tms_order_ids[0].distance
                    print("checking pricelist_item of",line,"with",quantity)
                    line.pricelist_item_id = line.order_id.pricelist_id._get_product_rule(
                        line.product_id,
                        quantity=quantity or 1,
                        uom=line.product_uom,
                        date=line._get_order_date(),
                    )
            
    # def _get_pricelist_price(self):
    #     self.ensure_one()
    #     if self.order_id.pricelist_id.tms_use_distance and self.tms_order_ids:
    #         price = self.pricelist_item_id._compute_price(
    #             product=self.product_id.with_context(**self._get_product_price_context()),
    #             quantity=self.tms_order_ids[0].distance or 1,
    #             uom=self.product_uom,
    #             date=self._get_order_date(),
    #             currency=self.currency_id,
    #         )
    #     else:
    #         price = super()._get_pricelist_price()
    #     return price

    @api.depends("product_id", "product_template_id")
    def _compute_sale_order_line_tms(self):
        super()._compute_sale_order_line_tms()
        for line in self:
            if not line.product_id.tms_trip:
                continue
            if line.product_template_id.tms_factor_type == 'distance':
                line.tms_factor_uom = line.product_template_id.tms_factor_distance_uom.name
            elif line.product_template_id.tms_factor_type == 'weight':
                line.tms_factor_uom = line.product_template_id.tms_factor_weight_uom.name
            else:
                line.tms_factor_uom = False
                
    def _convert_to_tax_base_line_dict(self, **kwargs):
        self.ensure_one()
        units_uom = self.env.ref('uom.product_uom_categ_unit')
        if self.tms_order_ids and self.product_id.uom_id.category_id != units_uom:
            # It's a TMS order that uses tms_factor for price determination, but not for subtotal computation
            print("TMS order",self.tms_order_ids," . tweaking subtotal")
            return self.env["account.tax"]._convert_to_tax_base_line_dict(
                self,
                partner=self.order_id.partner_id,
                currency=self.order_id.currency_id,
                product=self.product_id,
                taxes=self.tax_id,
                price_unit=self.price_unit,
                quantity=self.product_uom_qty,
                discount=self.discount,
                price_subtotal=self.price_subtotal,
                **kwargs,
            )
        return super()._convert_to_tax_base_line_dict(**kwargs)                