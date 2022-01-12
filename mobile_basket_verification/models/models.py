# -*- coding: utf-8 -*-

from odoo import models, fields, api


class BasketVerification(models.TransientModel):
    _name = 'mobile.basket.verification'
    _description = 'Mobile basket verification'
    def basket_verify(self,barcode=None):
        result = {'status':False,'result':'Something wrong with basket code'}

        if barcode:
            basket_id = self.env['stock.basket'].search([('name','=',barcode),('status','=','occupy')])
            picking_id = basket_id.picking_id
            if basket_id:
                remove_basket = picking_id.write({'basket_ids':[(3,basket_id.id)]})
                basket_id.write({'status': 'vacant',
                                    'picking_id':None})
                result = {'status':True,'result':'Basket Successfully Verified & Unallocated.'}
            else:
                result = {'status':False,'result':'Basket not found'}
        return result
    def get_picking_details(self,barcode=None):
        vals = []
        if barcode:
            line_vals = []
            basket_id = self.env['stock.basket'].search([('name','=',barcode),('status','=','occupy')])
            picking_id = basket_id.picking_id
            val = {
                    'picking_id':picking_id.name,
                    'partner_id':picking_id.partner_id.name,
                    'status':True
                    }
            for lines in picking_id.move_line_ids_without_package:
                line_vals.append({
                    'lot_id':lines.lot_id.name,
                    'product_id':lines.product_id.name,
                    'qty_done':lines.qty_done,
                    'product_mrp':lines.product_mrp.name,
                    'product_uom':lines.product_uom_id.name,
                    'customer_locations':lines.customer_locations.name,
                    'expiration_date':lines.lot_id.expiration_date
                })
            val['line_ids']=line_vals
            vals.append(val)
            return val
        result = {'status':False,'result':'There is no basket found for given barcode.'}
        return result
    def action_client_action(self):
        """ Open the mobile view specialized in handling barcodes on mobile devices.
        """
        return {
            'type': 'ir.actions.client',
            'tag': 'basket_verification_client_action',
            'target': 'fullscreen',
            'params': {
                # 'model': 'mobile.basket.verification',
                # 'inventory_id': self.id,
            }
        }
        return dict(action, target='fullscreen')
