# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.osv import expression
from odoo.exceptions import UserError
from collections import Counter, defaultdict



class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    sl_no = fields.Integer(string='Sl No.',store=True)
    product_mrp = fields.Many2one('stock.mrp.product.report', string='MRP', store=True,)
    customer_locations = fields.Many2one('location.code', 'Locations', ondelete='set null',related='product_id.product_location_ids',readonly=False,store=True)

    @api.onchange('product_mrp', 'customer_locations')
    def _onchange_prod_lot_mrp_move_line(self):
        for lot in self:
            if lot.lot_id:
                lot.lot_id.product_mrp = lot.product_mrp.id
                lot.lot_id.customer_locations = lot.customer_locations.id
            if lot.lot_name:
                lots=self.env['stock.production.lot'].search([('product_id','=',lot.product_id.id),('name','=',lot.lot_name)])
                for i in lots:
                    i.product_mrp = lot.product_mrp.id
                    i.customer_locations = lot.customer_locations.id





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


    def _create_and_assign_production_lot(self):
        """ Creates and assign new production lots for move lines."""
        lot_vals = []
        # It is possible to have multiple time the same lot to create & assign,
        # so we handle the case with 2 dictionaries.
        key_to_index = {}  # key to index of the lot
        key_to_mls = defaultdict(lambda: self.env['stock.move.line'])  # key to all mls
        for ml in self:
            key = (ml.company_id.id, ml.product_id.id, ml.lot_name)
            key_to_mls[key] |= ml
            if ml.tracking != 'lot' or key not in key_to_index:
                key_to_index[key] = len(lot_vals)
                lot_vals.append({
                    'company_id': ml.company_id.id,
                    'name': ml.lot_name,
                    'product_id': ml.product_id.id,
                    'product_mrp': ml.product_mrp.id,
                    'customer_locations':ml.customer_locations.id
                })

        lots = self.env['stock.production.lot'].create(lot_vals)
        for key, mls in key_to_mls.items():
            mls._assign_production_lot(lots[key_to_index[key]].with_prefetch(lots._ids))  # With prefetch to reconstruct the ones broke by accessing by index



