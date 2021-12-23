# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.osv import expression
from odoo.exceptions import UserError


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    sl_no = fields.Integer(string='Sl No.',store=True)
    product_mrp = fields.Many2one('stock.mrp.product.report', string='MRP', store=True,)
    customer_locations = fields.Many2one('location.code', 'Locations', ondelete='set null')

    @api.model_create_multi
    def create(self, vals_list):
        res = super(StockMoveLine, self).create(vals_list)
        for i in res:
            exsiting_mrp_id = self.env['stock.mrp.product.report'].search([('product_id', '=', i.product_id.id),
                                                                           ('id', '=', i.product_mrp.id)])

            if exsiting_mrp_id:
                # i.write(())
                if i.picking_code == 'incoming':
                    onhand_qty = i.qty_done + exsiting_mrp_id.qty
                    exsiting_mrp_id.write({'qty': onhand_qty})
                elif i.picking_code == 'outgoing':
                    onhand_qty = exsiting_mrp_id.qty - i.qty_done
                    exsiting_mrp_id.write({'qty': onhand_qty})
                elif i.picking_code == 'internal':
                    if i.picking_id.location_id.usage == 'internal' and i.picking_id.location_dest_id.usage in ['supplier', 'customer', 'inventory', 'production', 'transit']:
                        onhand_qty = exsiting_mrp_id.qty - i.qty_done
                        exsiting_mrp_id.write({'qty': onhand_qty})
                    elif i.picking_id.location_dest_id.usage == 'internal' and i.picking_id.location_id.usage in ['supplier', 'customer', 'inventory', 'production', 'transit']:
                        onhand_qty = i.qty_done + exsiting_mrp_id.qty
                        exsiting_mrp_id.write({'qty': onhand_qty})

                else:
                    onhand_qty = i.qty_done + exsiting_mrp_id.qty
                    exsiting_mrp_id.write({'qty': onhand_qty})


            else:
                if i.product_mrp:
                # if i.product_mrp.id == vals['product_mrp']:
                    sample_settlement = self.env['stock.mrp.product.report'].create({
                    'sl_no': i.sl_no,
                    'name': i.product_mrp.name,
                    'product_id': i.product_id.id,
                    'mrp': i.product_mrp.name,
                    'company_id': i.company_id.id,
                    'move_id': i.move_id.id,
                    'move_line_id': i.id,
                    'lot_id': i.lot_id.id,
                    'qty': i.qty_done,

                })
            # if i.product_mrp:

        # for vals in vals_list:
        #     if 'product_mrp' in vals:

        return res

    def write(self, vals):
        res = super(StockMoveLine, self).write(vals)
        for i in self:
            if 'qty_done' in vals:
                exsiting_mrp_id = self.env['stock.mrp.product.report'].search([('product_id', '=', i.product_id.id),
                                                                               ('id', '=', i.product_mrp.id)])

                if exsiting_mrp_id:
                    # i.write(())
                    if i.picking_code == 'incoming':
                        onhand_qty = vals['qty_done'] + exsiting_mrp_id.qty
                        exsiting_mrp_id.write({'qty': onhand_qty})
                    elif i.picking_code == 'outgoing':
                        onhand_qty = exsiting_mrp_id.qty - vals['qty_done']
                        exsiting_mrp_id.write({'qty': onhand_qty})
                    elif i.picking_code == 'internal':
                        if i.picking_id.location_id.usage=='internal' and  i.picking_id.location_dest_id.usage in ['supplier','customer','inventory','production','transit']:
                            onhand_qty = exsiting_mrp_id.qty - vals['qty_done']
                            exsiting_mrp_id.write({'qty': onhand_qty})
                        elif i.picking_id.location_dest_id.usage == 'internal' and i.picking_id.location_id.usage in ['supplier', 'customer', 'inventory', 'production', 'transit']:
                            onhand_qty = exsiting_mrp_id.qty + vals['qty_done']
                            exsiting_mrp_id.write({'qty': onhand_qty})

                    else:
                        onhand_qty = vals['qty_done'] + exsiting_mrp_id.qty
                        exsiting_mrp_id.write({'qty': onhand_qty})


                else:
                    if i.product_mrp:
                    # if i.product_mrp.id == vals['product_mrp']:
                        sample_settlement = self.env['stock.mrp.product.report'].create({
                        'sl_no': i.sl_no,
                        'name': i.product_mrp.name,
                        'product_id': i.product_id.id,
                        'mrp': i.product_mrp.name,
                        'company_id': i.company_id.id,
                        'move_id': i.move_id.id,
                        'move_line_id': i.id,
                        'lot_id': i.lot_id.id,
                        'qty': i.qty_done,

                    })
        return res


