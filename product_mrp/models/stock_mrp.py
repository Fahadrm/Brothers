# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import tools
from odoo import api, fields, models,_
from psycopg2 import sql


class InventoryLine(models.Model):
    _inherit = 'stock.inventory.line'

    product_mrp = fields.Many2one('stock.mrp.product.report', string='MRP', store=True)

    mrp = fields.Float(string='MRP', digits='Product Price', default=0.0)

    customer_locations = fields.Many2one('location.code', 'Locations', ondelete='set null',related='product_id.product_location_ids',readonly=False,store=True)


    @api.onchange('product_mrp','customer_locations')
    def _onchange_prod_lotmrp(self):
        for lot in self:
            if lot.prod_lot_id:
                lot.prod_lot_id.product_mrp = lot.product_mrp.id
                lot.prod_lot_id.customer_locations = lot.customer_locations.id

    def _get_move_values(self, qty, location_id, location_dest_id, out):
        self.ensure_one()
        return {
            'name': _('INV:') + (self.inventory_id.name or ''),
            'product_id': self.product_id.id,
            'product_uom': self.product_uom_id.id,
            'product_uom_qty': qty,
            'date': self.inventory_id.date,
            'company_id': self.inventory_id.company_id.id,
            'inventory_id': self.inventory_id.id,
            'state': 'confirmed',
            'restrict_partner_id': self.partner_id.id,
            'location_id': location_id,
            'location_dest_id': location_dest_id,
            'move_line_ids': [(0, 0, {
                'product_id': self.product_id.id,
                'lot_id': self.prod_lot_id.id,
                'product_uom_qty': 0,  # bypass reservation here
                'product_uom_id': self.product_uom_id.id,
                'qty_done': qty,
                'package_id': out and self.package_id.id or False,
                'result_package_id': (not out) and self.package_id.id or False,
                'location_id': location_id,
                'location_dest_id': location_dest_id,
                'owner_id': self.partner_id.id,
                'product_mrp': self.product_mrp.id
            })]
        }

    # @api.model_create_multi
    # def create(self, vals_list):
    #     res = super(InventoryLine, self).create(vals_list)
    #     for vals in vals_list:
    #         if 'product_mrp' in vals:
    #             for i in res:
    #                 if i.product_mrp.name == vals['product_mrp']:
    #                     sample_settlement = self.env['stock.mrp.product.report'].create({
    #                         'sl_no': i.sl_no,
    #                         'name': i.product_mrp.name,
    #                         'product_id': i.product_id.id,
    #                         'mrp': i.product_mrp.name,
    #                         'company_id': i.company_id.id,
    #                         'move_id': i.move_id.id,
    #
    #                     })
    #     return res
    #
    #
    # def write(self,vals):
    #     res = super(InventoryLine, self).write(vals)
    #     for i in self:
    #         if i.product_mrp:
    #             sample_settlement = self.env['stock.mrp.product.report'].create({
    #                  'sl_no': i.id,
    #                 'name': i.product_mrp.name,
    #                 'product_id': i.product_id.id,
    #                 'mrp': i.product_mrp.name,
    #                 'company_id': i.company_id.id,
    #                 # 'move_id': self.id,
    #
    #             })
    #     return res



class ProductMRPReport(models.Model):
    _name = "stock.mrp.product.report"
    _description = "Product MRP"


    name = fields.Float(string='MRP',default=0.0)
    sl_no = fields.Integer(string='sl')
    product_id = fields.Many2one('product.product',string='product')
    move_id = fields.Many2one('stock.move',string="Move")
    move_line_id = fields.Many2one('stock.move.line', string="Move Line")
    company_id = fields.Many2one('res.company', string='Company')
    mrp = fields.Float(string='MRP',default=0.0,store=True)
    qty = fields.Float(string='MRP Qty Available',default=0.0,store=True)
    # qty = fields.Float(string='MRP Qty Available', compute='mrp_qty_available',default=0.0, store=True)
    lot_id = fields.Many2one('stock.production.lot',store=True)

    @api.onchange('name')
    def mrp_value(self):
        for i in self:
            i.mrp = i.name

    # @api.model_create_multi
    # def create(self, vals_list):
    #     res= super(ProductMRPReport, self).create(vals_list)
    #     return res


