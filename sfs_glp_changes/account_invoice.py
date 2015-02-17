# -*- encoding: utf-8 -*
##############################################################################
#
#    Copyright (c) 2013 SF Soluciones.
#    (http://www.sfsoluciones.com)
#    contacto@sfsoluciones.com
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
import openerp.addons.decimal_precision as dp

from openerp.osv import osv, fields

class account_invoice(osv.osv):
    _inherit = "account.invoice"
    def _get_qty(self, cr, uid, ids, name, arg, context=None):
        res = {}
        sum_qty = 0.0
        for invoice in self.browse(cr, uid, ids, context=context):
            if invoice.invoice_line:
                for line in invoice.invoice_line:
                   sum_qty += float(line.quantity)
            res[invoice.id] = sum_qty
        return res
    _columns = {
        'qty_uos': fields.float('Quantity of product'),
        'total_quantities': fields.function(_get_qty, type='float', string='Total Qtty', digits_compute=dp.get_precision('Average Cost')), 
        }
    
account_invoice()   


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:-