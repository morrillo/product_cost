# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-today OpenERP SA (<http://www.openerp.com>)
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

from openerp.osv import fields, osv
import logging

_logger = logging.getLogger(__name__)

class mrp_bom(osv.osv):
    """ MRP Bom """
    _inherit = "mrp.bom"
    _name = "mrp.bom"

    def _get_bom_lines(self,cr,uid,bom_id = None, context = None):

	if bom_id:
		cr.execute("select id from mrp_bom where bom_id = "+str(bom_id))
		res = cr.fetchall()
		return_list = []
		for r in range(len(res)):
			return_list.append(res[r][0])
		return return_list
	return [0]

    def _calc_price(self, cr, uid, ids, context=None):

	bom = self.pool.get('mrp.bom').browse(cr,uid,ids,context=context)
       	if not bom.calculate_price:
            return bom.product_id.standard_price
       	else:
            price = 0
	    # bom_lines = self._get_bom_lines(cr,uid,bom.id)
	    bom_lines = bom.child_complete_ids
       	    if bom_lines:
		# import pdb;pdb.set_trace()
                for sbom in bom_lines:
       	            my_qty = sbom.bom_lines and 1.0 or sbom.product_qty
               	    price += self._calc_price(cr, uid, sbom.id) * my_qty
	    else:
	       	    bom_obj = self.pool.get('mrp.bom')
        	    no_child_bom = bom_obj.search(cr, uid, [('product_id', '=', bom.product_id.id), ('bom_id', '=', False)])
       	            if no_child_bom and bom.id not in no_child_bom:
	                other_bom = bom_obj.browse(cr, uid, no_child_bom)[0]
        	        if not other_bom.calculate_price:
       	        	    price += self._calc_price(cr, uid, other_bom.id) * other_bom.product_qty
	               	else:
	#               price += other_bom.product_qty * other_bom.product_id.standard_price
        	            price += other_bom.product_id.standard_price
	            else:
	#               price += bom.product_qty * bom.product_id.standard_price
		        price += bom.product_id.standard_price
	#        if no_child_bom:
	#           other_bom = bom_obj.browse(cr, uid, no_child_bom)[0]
	#           price += bom.product_qty * self._calc_price(cr, uid, other_bom)
	#        else:
	#           price += bom.product_qty * bom.product_id.standard_price
	    if bom.routing_id:
                for wline in bom.routing_id.workcenter_lines:
               	    wc = wline.workcenter_id
	            cycle = wline.cycle_nbr
                    hour = (wc.time_start + wc.time_stop + cycle * wc.time_cycle) *  (wc.time_efficiency or 1.0)
               	    price += wc.costs_cycle * cycle + wc.costs_hour * hour
	            price = self.pool.get('product.uom')._compute_price(cr,uid,bom.product_uom.id,price,bom.product_id.uom_id.id)
            if bom.bom_lines:
               	self.write(cr, uid, [bom.product_id.id], {'standard_price' : price/bom.product_qty})
	        if bom.product_uom.id != bom.product_id.uom_id.id:
        	    price = self.pool.get('product.uom')._compute_price(cr,uid,bom.product_uom.id,price,bom.product_id.uom_id.id)
  	    res = price
        return res



    def _fnct_calc_price(self, cr, uid, ids, field_name, args, context=None):

	price = 0
	res = {}
	for bom in self.browse(cr,uid,ids):
		
        	#if not bom.calculate_price:
	        #    price = bom.product_id.standard_price
        	#else:
	        price = self._calc_price(cr,uid,bom.id)
		res[bom.id] = price
        return res


    _columns = {
	'calculate_price': fields.boolean('Calculate Price'),
        'manufacturing_cost': fields.function(_fnct_calc_price, string='Manufacturing Cost'),
	'uuid': fields.char('UUID')
	}

    _defaults = {
        'calculate_price': 1,
    }


mrp_bom()
