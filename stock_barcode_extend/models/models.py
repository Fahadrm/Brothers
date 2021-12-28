# -*- coding: utf-8 -*-

from odoo import models, fields, api


class StockPicking(models.Model):
    _inherit = 'stock.picking'


    @api.model
    def _get_move_line_ids_fields_to_read(self):
        """ read() on picking.move_line_ids only returns the id and the display
        name however a lot more data from stock.move.line are used by the client
        action.
        """
        res = super(StockPicking, self)._get_move_line_ids_fields_to_read()
        res.append('product_mrp')
        res.append('customer_locations')
        res.append('expiration_date')
        return res

class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    @api.onchange('product_id', 'product_uom_id')
    def _onchange_product_id(self):
        res = super()._onchange_product_id()
        if self.product_id:
            self.customer_locations = self.product_id.product_location_ids.id
        return res




