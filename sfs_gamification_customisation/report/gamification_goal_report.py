# -*- encoding: utf-8 -*-
##############################################################################
#
#    Copyright (c) 2014 SF Soluciones.
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

import tools
from osv import  osv
import openerp.addons.decimal_precision as dp

class gamification_goal_report(osv.osv):
    _name = 'gamification.goal.report'
    _auto = False
    
    def init(self, cr):
        tools.drop_view_if_exists(cr, 'gamification_goal_report')
        cr.execute(""" 
                   create or replace view gamification_goal_report as (
                       SELECT
                            ggpl.id as id,
                            ggp.start_date AS start_date,
                            ggp.end_date AS end_date,
                            ru.id AS user_id,
                            gl.product_category_id AS product_category_id,
                            imf.field_description AS type_id,
                            ggpl.target_goal AS target_goal
                        FROM
                            res_users ru
                        LEFT JOIN user_ids ui ON ui.res_users_id = ru.id
                        join gamification_goal_plan ggp ON ggp.id = ui.gamification_goal_plan_id
                        LEFT JOIN gamification_goal_planline ggpl ON ggpl.plan_id = ggp.id
                        LEFT JOIN gamification_goal_type ggt ON ggt.id = ggpl.type_id
                        LEFT JOIN gamification_goal gl ON gl.id = (SELECT gl1.id FROM gamification_goal gl1 WHERE gl1.type_id = ggt.id limit 1)
                        LEFT JOIN ir_model_fields imf ON imf.id = ggt.field_id
                        ORDER BY ru.id
                        )
                   """)
        

    
gamification_goal_report()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: