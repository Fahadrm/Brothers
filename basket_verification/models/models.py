# -*- coding: utf-8 -*-

from odoo import models, fields, api,_
from odoo.exceptions import UserError, ValidationError



class StockBasket(models.Model):
    _name = 'stock.basket'
    _description = 'Basket'

    name = fields.Char(string="Basket")
    picking_id = fields.Many2one('stock.picking',string="Stock Picking")
    status = fields.Selection([
        ('vacant', 'Vacant'),
        ('occupy', 'Occupy'),
    ], default="vacant", store=True, )



    @api.constrains('name')
    def _check_unique_name(self):
        for line in self:
            if line.name:
                if len(self.search([('name', '=', line.name)])) > 1:
                    raise ValidationError("Name Already Exists")
            else:
                pass


class StockPicking(models.Model):
    _inherit = "stock.picking"

    @api.depends('basket_ids')
    def _get_verification_done(self):
        for res in self:
            if len(res.basket_ids) ==0:
                self.basket_verification_done = True
            else:
                self.basket_verification_done = False
    basket_ids = fields.Many2many(comodel_name="stock.basket",string="Basket")
    # basket_ids = fields.One2many("stock.basket","picking_id",string="Basket")
    # stock_basket_id = fields.One2many("stock.basket.lines", "stock_basket_line_id", string="Basket")
    basket_verification_done = fields.Boolean(string="Basket verification done",compute='_get_verification_done')
    def write(self, vals):
        res = super(StockPicking, self).write(vals)
        for change in self.basket_ids:
            if change.name:
                basket = change.id
                customer_group = self.env['stock.basket'].browse(basket).write(
                    {
                        'status': 'occupy'
                    }
                )
                change.status ='occupy'
        return res

    def set_basket(self,picking_id,basket=None):
        basket_id = self.env['stock.basket'].search([('name','=',basket)])
        picking_id = self.env['stock.picking'].browse([picking_id])
        result = {'status':False,'result':'Something wrong with basket code'}

        if basket_id and picking_id:
            basket_alread_added = picking_id.basket_ids.filtered(lambda x: x.name == basket)
            if basket_alread_added:
                result = {'status':False,'result':'Basket already added to this picking'}
                return result
            if basket_id.status == 'occupy':
                return {'status':False,'result':'Basket is already occupied.'}

            vals = {'name':basket,'status':'occupy'}
            basket_id.write({'status':'occupy','picking_id':picking_id.id})
            write = picking_id.write({'basket_ids':[(4,basket_id.id)],})
            result = {'status':True,'result':'Basket successfully added'}
            return result

        else:
            result = {'status':False,'result':'Something wrong with basket code'}
            return result
        return result
# class StockBasketLines(models.Model):
#     _name = 'stock.basket.lines'
#     _description = 'Basket'
#
#     stock_basket_line_id = fields.Many2one("stock.basket",string="Basket")
