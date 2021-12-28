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

