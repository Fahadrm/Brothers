# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.osv import expression
from odoo.exceptions import UserError


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    product_mrp = fields.Many2one('stock.mrp.product.report',string='MRP',store=True)
    qty_available = fields.Float(string='On Hand',store=True)




    @api.onchange('product_id')
    def product_id_change(self):
        res = super(SaleOrderLine, self).product_id_change()
        if self.product_id:

            if len(self.product_id.product_mrp_ids) >= 1:
                # for mrp in self.product_id.product_mrp_ids:
                recs_sorted = self.product_id.product_mrp_ids.sorted(key=lambda r: r.name)
                mrp_value = recs_sorted[0].id if recs_sorted else 0
                self.product_mrp = mrp_value
                # self.qty_available =self.product_mrp.qty
        return res



    @api.depends('order_id.pricelist_id')
    @api.depends_context('fsm_sale_id','product_mrp','show_mrp')
    @api.onchange('product_id','product_mrp','order_line')
    def _get_lot_mrps(self):
        mrp_float =[]
        for product in self:
            if product.product_mrp:
                product.qty_available=product.product_mrp.qty
            lot_mrp = product.product_id.product_mrp_ids
            if lot_mrp:
                for rec in lot_mrp:
                    mrp_float.append(rec.id)

        res = {}
        res['domain'] = {'product_mrp': [('id', 'in', mrp_float)]}
        return res


    @api.onchange('product_mrp','product_uom_qty','product_uom')
    def product_mrp_change(self):
        if not self.product_id:
            return
        if not self.product_mrp:
            self.product_id_change()
            # return
        # self._get_lot_mrps()
        # if self.order_id.pricelist_id and self.order_id.partner_id and self.order_id.pricelist_id.is_mrp == True:
        product_context = dict(self.env.context, partner_id=self.order_id.partner_id.id, date=self.order_id.date_order,uom=self.product_uom.id)
        price, rule_id = self.order_id.pricelist_id.with_context(product_context).get_product_price_rule(
            self.product_id, self.product_uom_qty or 1.0, self.order_id.partner_id)
        pricelist_rule = self.env['product.pricelist.item'].browse(rule_id)
        if self.order_id.pricelist_id and self.order_id.partner_id and self.order_id.pricelist_id.item_ids.filtered(lambda l: l.is_mrp == True):
            if pricelist_rule:
                for item in pricelist_rule:
                    if item.is_mrp == True:
                        product = self.product_id.with_context(
                            lang=self.order_id.partner_id.lang,
                            partner=self.order_id.partner_id,
                            quantity=self.product_uom_qty,
                            date=self.order_id.date_order,
                            pricelist=self.order_id.pricelist_id.id,
                            uom=self.product_uom.id,
                            fiscal_position=self.env.context.get('fiscal_position'),
                            product_mrp=self.product_mrp.id
                        )
                        # self.order_id.pricelist_id.item_ids._compute_price(self.product_mrp.mrp,self.product_uom, product)
                        self.price_unit = self.env['account.tax']._fix_tax_included_price_company(self._get_display_price(product),
                                                                                                  product.taxes_id, self.tax_id,
                                                                                                  self.company_id)

class ProductProduct(models.Model):
    _inherit = "product.product"

    def price_compute(self, price_type, uom=False, currency=False, company=None):
        # mrp wise price compute
        if self._context.get('product_mrp'):
            move_line_id = self.env['stock.mrp.product.report'].browse(self._context['product_mrp'])
            # product_mrp = self._context.get('product_mrp')
            if not uom and self._context.get('uom'):
                uom = self.env['uom.uom'].browse(self._context['uom'])
            if not currency and self._context.get('currency'):
                currency = self.env['res.currency'].browse(self._context['currency'])

            products = self
            if price_type == 'standard_price':
                # standard_price field can only be seen by users in base.group_user
                # Thus, in order to compute the sale price from the cost for users not in this group
                # We fetch the standard price as the superuser
                products = self.with_company(company or self.env.company).sudo()

            prices = dict.fromkeys(self.ids, 0.0)
            for product in products:
                prices[product.id] = move_line_id.name or 0.0
                if price_type == 'list_price':
                    prices[product.id] += product.price_extra
                    # we need to add the price from the attributes that do not generate variants
                    # (see field product.attribute create_variant)
                    if self._context.get('no_variant_attributes_price_extra'):
                        # we have a list of price_extra that comes from the attribute values, we need to sum all that
                        prices[product.id] += sum(self._context.get('no_variant_attributes_price_extra'))

                if uom:
                    prices[product.id] = product.uom_id._compute_price(prices[product.id], uom)

                # Convert from current user company currency to asked one
                # This is right cause a field cannot be in more than one currency
                if currency:
                    prices[product.id] = product.currency_id._convert(
                        prices[product.id], currency, product.company_id, fields.Date.today())

            return prices
        else:
            return super(ProductProduct, self).price_compute(price_type, uom=uom, currency=currency, company=company)

