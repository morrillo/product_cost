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
from datetime import datetime

_logger = logging.getLogger(__name__)

class product_cost_history(osv.osv):
    """ Product Product """
    _name = "product.cost.history"
    _description = "Daily Product Cost History"

    def _update_cost_history(self,cr,uid,ids=None,context=None):
	
	product_cost_history_obj = self.pool.get('product.cost.history')
	product_obj = self.pool.get('product.product')
	product_ids = product_obj.search(cr,uid,[('id','>',0)])
	
	for product in product_obj.browse(cr,uid,product_ids):
		if product.bom_ids == []:
			vals_cost = {
				'product_id': product.id,
				'date': datetime.today(),
				'name': product.name,
				'cost': product.standard_price,
				}
			product_cost_history_ids = product_cost_history_obj.create(cr,uid,vals_cost)
		else:
			for bom in self.pool.get('mrp.bom').browse(cr,uid,product.bom_ids):
				vals_cost = {
					'product_id': product.id,
					'date': datetime.today(),
					'name': bom.id.name,
					'cost': bom.id.manufacturing_cost,
					}
				product_cost_history_ids = product_cost_history_obj.create(cr,uid,vals_cost)

	return None

    _columns = {
	'product_id': fields.many2one('product.product','Product'),
	'name': fields.char('Product Price Name',size=64),
	'date': fields.datetime('Cost Date Time'),
        'cost': fields.float(string='Manufacturing Cost'),
	}

product_cost_history()

class product_product(osv.osv):
    """ Product Product """
    
    _name = "product.product"
    _inherit = "product.product"

    _columns = {
	'cost_ids': fields.one2many('product.cost.history','product_id','Cost History'),
	}

product_product()
