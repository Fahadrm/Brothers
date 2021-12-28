# -*- coding: utf-8 -*-

from odoo import models, fields, api,_
from odoo.exceptions import UserError, ValidationError
class BasketVerification(models.TransientModel):
    _name = 'basket.verification'
    _description = 'Basket Verification'

    name = fields.Many2one("stock.basket", string="Basket")


    def set_basket_free(self):
        print(self.name)
        for baskets in self:
            baskets.name.write({'status': 'vacant'})
            baskets.name.status='vacant'
        # return

    # def print_demo(self):
    #     print("hiiii")



