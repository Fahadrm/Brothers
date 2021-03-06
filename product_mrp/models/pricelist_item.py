# -*- coding: utf-8 -*-

from odoo import models, fields, api, tools
from odoo.exceptions import RedirectWarning, UserError, ValidationError


class Pricelistitem(models.Model):
    _inherit = "product.pricelist.item"

    is_mrp = fields.Boolean(string='Based On MRP', default=False)

class Pricelist(models.Model):
    _inherit = "product.pricelist"

    is_mrp = fields.Boolean(string='Based On MRP', default=False)

class ProductionLot(models.Model):
    _inherit = 'stock.production.lot'

    product_mrp = fields.Many2one('stock.mrp.product.report', string='MRP', store=True)
    customer_locations = fields.Many2one('location.code', 'Locations', ondelete='set null')



class StockQuant(models.Model):
    _inherit = 'stock.quant'

    product_mrp = fields.Many2one('stock.mrp.product.report', string='MRP', store=True,related='lot_id.product_mrp',readonly=False)
    customer_locations = fields.Many2one('location.code', 'Locations', ondelete='set null',store=True,related='lot_id.customer_locations',readonly=False)


    @api.model
    def _get_inventory_fields_write(self):
        """ Returns a list of fields user can edit when he want to edit a quant in `inventory_mode`.
        """
        res = super()._get_inventory_fields_write()
        res.append('product_mrp')
        res.append('customer_locations')
        # res += ['product_mrp', 'customer_locations']
        return res

    def _gather(self, product_id, location_id, lot_id=None, package_id=None, owner_id=None, strict=False):
        res = super(StockQuant, self)._gather(product_id, location_id, lot_id, package_id, owner_id, strict)
        if lot_id:
            res.update(
                {
                    'product_mrp': lot_id.product_mrp.id,
                    'customer_locations': lot_id.customer_locations.id
                }
            )

        return res

    # @api.model
    # def create(self, vals):
    #     """ Override to handle the "inventory mode" and create a quant as
    #     superuser the conditions are met.
    #     """
    #     res = super(StockQuant, self).create(vals)
    #     return res


class StockMove(models.Model):
    _inherit = "stock.move"

    product_mrp = fields.Many2one('stock.mrp.product.report', string='MRP', store=True)
    customer_locations = fields.Many2one('location.code', 'Locations', ondelete='set null')


    def _prepare_move_line_vals(self, quantity=None, reserved_quant=None):
        res = super(StockMove, self)._prepare_move_line_vals(quantity, reserved_quant)
        res.update({'product_mrp': self.product_mrp.id})
        return res


class StockScrap(models.Model):
    _inherit = 'stock.scrap'

    product_mrp = fields.Many2one('stock.mrp.product.report', string='MRP', store=True)

    def _prepare_move_values(self):
        vals = super(StockScrap, self)._prepare_move_values()
        if self.product_mrp:
            vals.update({'move_line_ids': [(0, 0, {'product_id': self.product_id.id,
                                      'product_uom_id': self.product_uom_id.id,
                                      'qty_done': self.scrap_qty,
                                      'location_id': self.location_id.id,
                                      'location_dest_id': self.scrap_location_id.id,
                                      'package_id': self.package_id.id,
                                      'owner_id': self.owner_id.id,
                                      'lot_id': self.lot_id.id,
                                      'product_mrp': self.product_mrp.id})],})

        return vals


class StockReturnPickingLine(models.TransientModel):
    _inherit = "stock.return.picking.line"

    product_mrp = fields.Many2one('stock.mrp.product.report', string='MRP', store=True)

class ReturnPicking(models.TransientModel):
    _inherit = 'stock.return.picking'

    def _prepare_move_default_values(self, return_line, new_picking):
        res=super(ReturnPicking, self)._prepare_move_default_values(return_line, new_picking)
        res.update({'product_mrp': return_line.product_mrp.id})
        return res

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'


    def _prepare_procurement_values(self, group_id=False):
        res = super(SaleOrderLine, self)._prepare_procurement_values(group_id)
        res.update({'product_mrp': self.product_mrp.id})
        return res

class StockRuleInherit(models.Model):
    _inherit = 'stock.rule'

    def _get_stock_move_values(self, product_id, product_qty, product_uom, location_id, name, origin,
                                   values, group_id):
        res = super(StockRuleInherit, self)._get_stock_move_values(product_id, product_qty, product_uom,
                                                                       location_id,
                                                                       name, origin, values, group_id)
        res['product_mrp'] = group_id.get('product_mrp', False)
        return res