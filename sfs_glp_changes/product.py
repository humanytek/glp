# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2013-2014 ZestyBeanz Technologies Pvt Ltd(<http://www.zbeanztech.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
import openerp.addons.decimal_precision as dp
from osv import fields, osv
class product_product(osv.osv):
    _inherit = 'product.product'
    def _product_lst_price(self, cr, uid, ids, name, arg, context=None):
        res = {}
        product_uom_obj = self.pool.get('product.uom')
        for id in ids:
            res.setdefault(id, 0.0)
        for product in self.browse(cr, uid, ids, context=context):
            if 'uom' in context:
                uom = product.uos_id or product.uom_id
                res[product.id] = product_uom_obj._compute_price(cr, uid,
                        uom.id, product.list_price, context['uom'])
            else:
                res[product.id] = product.list_price
            res[product.id] =  (res[product.id] or 0.0) * (product.price_margin or 1.0) + product.price_extra
        return res
    def _total_amount_fetch(self, cr, uid, ids, name, arg, context=None):
        res = {}
        total_amount = 0.0
        for product in self.browse(cr, uid, ids, context=context):
            total_amount = float(product.qty_available) * float(product.standard_price)
            res[product.id] = total_amount
        return res
    def _product_cost_price(self, cr, uid, ids, name, arg, context=None):
        res = {}
        for product in self.browse(cr, uid, ids, context=context):
            standard_price = product.standard_price
            res[product.id] = standard_price
        return res
    def _get_moves(self, cr, uid, ids, context=None):
        result = {}
        product_ids = []
        for move in self.pool.get('stock.move').browse(cr, uid, ids, context=context):
#             if move.state == 'done':
            product_id = move.product_id.id
            product_ids.append(product_id)
        if product_ids:
            product_ids = list(set(product_ids))
        return product_ids
    def _product_available(self, cr, uid, ids, field_names=None, arg=False, context=None):
        """ Finds the incoming and outgoing quantity of product.
        @return: Dictionary of values
        """
        if not field_names:
            field_names = []
        if context is None:
            context = {}
        res = {}
        for id in ids:
            res[id] = {}.fromkeys(field_names, 0.0)
        for f in field_names:
            c = context.copy()
            if f == 'qty_available':
                c.update({ 'states': ('done',), 'what': ('in', 'out') })
            if f == 'virtual_available':
                c.update({ 'states': ('confirmed','waiting','assigned','done'), 'what': ('in', 'out') })
            if f == 'incoming_qty':
                c.update({ 'states': ('confirmed','waiting','assigned'), 'what': ('in',) })
            if f == 'outgoing_qty':
                c.update({ 'states': ('confirmed','waiting','assigned'), 'what': ('out',) })
            stock = self.get_product_available(cr, uid, ids, context=c)
            for id in ids:
                res[id][f] = stock.get(id, 0.0)
        
        return res
    def qty_set(self, cr, uid, ids, context=None):
        product_obj = self.pool.get('product.product')
        product_ids = product_obj.search(cr, uid, [], context=context)
        for product_id in product_ids:
            product_obj.write(cr, uid, product_id, {'set_qty': True}, context=context)
        return True
    _columns = {
        'set_qty': fields.boolean('Set Quantity'),
        'qty_available': fields.function(_product_available, multi='qty_available',
            type='float',  digits_compute=dp.get_precision('Product Unit of Measure'),
            string='Quantity On Hand',
            help="Current quantity of products.\n"
                 "In a context with a single Stock Location, this includes "
                 "goods stored at this Location, or any of its children.\n"
                 "In a context with a single Warehouse, this includes "
                 "goods stored in the Stock Location of this Warehouse, or any "
                 "of its children.\n"
                 "In a context with a single Shop, this includes goods "
                 "stored in the Stock Location of the Warehouse of this Shop, "
                 "or any of its children.\n"
                 "Otherwise, this includes goods stored in any Stock Location "
                 "with 'internal' type.", store={'product.product':(lambda self, cr, uid, ids, c={}: ids, [], 10),
                   'stock.move':(_get_moves,['product_id','product_uom','product_qty','prodlot_id','location_id','location_dest_id','state',],10),
                   }),
        'virtual_available': fields.function(_product_available, multi='qty_available',
            type='float',  digits_compute=dp.get_precision('Product Unit of Measure'),
            string='Forecasted Quantity',
            help="Forecast quantity (computed as Quantity On Hand "
                 "- Outgoing + Incoming)\n"
                 "In a context with a single Stock Location, this includes "
                 "goods stored in this location, or any of its children.\n"
                 "In a context with a single Warehouse, this includes "
                 "goods stored in the Stock Location of this Warehouse, or any "
                 "of its children.\n"
                 "In a context with a single Shop, this includes goods "
                 "stored in the Stock Location of the Warehouse of this Shop, "
                 "or any of its children.\n"
                 "Otherwise, this includes goods stored in any Stock Location "
                 "with 'internal' type.",store={'product.product':(lambda self, cr, uid, ids, c={}: ids, [], 10),
                   'stock.move':(_get_moves,['product_id','product_uom','product_qty','prodlot_id','location_id','location_dest_id','state',],10),
                   }),
        'incoming_qty': fields.function(_product_available, multi='qty_available',
            type='float',  digits_compute=dp.get_precision('Product Unit of Measure'),
            string='Incoming',
            help="Quantity of products that are planned to arrive.\n"
                 "In a context with a single Stock Location, this includes "
                 "goods arriving to this Location, or any of its children.\n"
                 "In a context with a single Warehouse, this includes "
                 "goods arriving to the Stock Location of this Warehouse, or "
                 "any of its children.\n"
                 "In a context with a single Shop, this includes goods "
                 "arriving to the Stock Location of the Warehouse of this "
                 "Shop, or any of its children.\n"
                 "Otherwise, this includes goods arriving to any Stock "
                 "Location with 'internal' type.",store={'product.product':(lambda self, cr, uid, ids, c={}: ids, [], 10),
                   'stock.move':(_get_moves,['product_id','product_uom','product_qty','prodlot_id','location_id','location_dest_id','state',],10),
                   }),
        'outgoing_qty': fields.function(_product_available, multi='qty_available',
            type='float',  digits_compute=dp.get_precision('Product Unit of Measure'),
            string='Outgoing',
            help="Quantity of products that are planned to leave.\n"
                 "In a context with a single Stock Location, this includes "
                 "goods leaving this Location, or any of its children.\n"
                 "In a context with a single Warehouse, this includes "
                 "goods leaving the Stock Location of this Warehouse, or "
                 "any of its children.\n"
                 "In a context with a single Shop, this includes goods "
                 "leaving the Stock Location of the Warehouse of this "
                 "Shop, or any of its children.\n"
                 "Otherwise, this includes goods leaving any Stock "
                 "Location with 'internal' type.",store={'product.product':(lambda self, cr, uid, ids, c={}: ids, [], 10),
                   'stock.move':(_get_moves,['product_id','product_uom','product_qty','prodlot_id','location_id','location_dest_id','state',],10),
                   }),
        
        'average_price': fields.function(_product_lst_price, type='float', string='Average Price', digits_compute=dp.get_precision('Average Cost'), store={'product.product':(lambda self, cr, uid, ids, c={}: ids, [], 10)}, group_operator="avg"),
#         'standard_price': fields.float('Cost', digits_compute=dp.get_precision('Product Price'), help="Cost price of the product used for standard stock valuation in accounting and used as a base price on purchase orders.", groups="base.group_user", group_operator="avg"),
        'standard_price1': fields.function(_product_cost_price, type='float', string='Standard Price', store={'product.product':(lambda self, cr, uid, ids, c={}: ids, ['standard_price'], 10)}, group_operator="avg"),
        'total_amount': fields.function(_total_amount_fetch, type='float', string='Total Cost', group_operator='sum', store={'product.product':(lambda self, cr, uid, ids, c={}: ids, ['qty_available', 'standard_price'], 10)}), 
        
        }
product_product()    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: