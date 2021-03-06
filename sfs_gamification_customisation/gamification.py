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

import logging
from openerp.osv import fields, osv

from openerp.tools.safe_eval import safe_eval
from datetime import date, datetime, timedelta
from tools.translate import _

_logger = logging.getLogger(__name__)

class gamification_goal_plan(osv.Model):
    _inherit = 'gamification.goal.plan'
    def check_challenge_reward(self, cr, uid, plan_ids, force=False, context=None):
        """Actions for the end of a challenge

        If a reward was selected, grant it to the correct users.
        Rewards granted at:
            - the end date for a challenge with no periodicity
            - the end of a period for challenge with periodicity
            - when a challenge is manually closed
        (if no end date, a running challenge is never rewarded)
        (if any of the goals is achieved)
        """
        from addons.gamification import plan
        context = context or {}
        for game_plan in self.browse(cr, uid, plan_ids, context=context):
            (start_date, end_date) = plan.start_end_date_for_period(game_plan.period, game_plan.start_date, game_plan.end_date)
            yesterday = date.today() - timedelta(days=1)
            if end_date == yesterday.isoformat() or force:
                # open chatter message
                message_body = _("The challenge %s is finished." % game_plan.name)

                # reward for everybody succeeding
                rewarded_users = []
                if game_plan.reward_id:
                    for user in game_plan.user_ids:
                        reached_goal_ids = self.pool.get('gamification.goal').search(cr, uid, [
                            ('plan_id', '=', game_plan.id),
                            ('user_id', '=', user.id),
                            ('start_date', '=', start_date),
                            ('end_date', '=', end_date),
                            ('state', '=', 'reached')
                        ], context=context)
                        if reached_goal_ids :
                            self.reward_user(cr, uid, user.id, game_plan.reward_id.id, context)
                            rewarded_users.append(user)

                    if rewarded_users:
                        message_body += _("<br/>Reward (badge %s) for every succeeding user was sent to %s." % (game_plan.reward_id.name, ", ".join([user.name for user in rewarded_users])))
                    else:
                        message_body += _("<br/>Nobody has succeeded to reach every goal, no badge is rewared for this challenge.")

                # reward bests
                if game_plan.reward_first_id:
                    (first_user, second_user, third_user) = self.get_top3_users(cr, uid, game_plan, context)
                    if first_user:
                        self.reward_user(cr, uid, first_user.id, game_plan.reward_first_id.id, context)
                        message_body += _("<br/>Special rewards were sent to the top competing users. The ranking for this challenge is :")
                        message_body += "<br/> 1. %s - %s" % (first_user.name, game_plan.reward_first_id.name)
                    else:
                        message_body += _("Nobody reached the required conditions to receive special badges.")

                    if second_user and game_plan.reward_second_id:
                        self.reward_user(cr, uid, second_user.id, game_plan.reward_second_id.id, context)
                        message_body += "<br/> 2. %s - %s" % (second_user.name, game_plan.reward_second_id.name)
                    if third_user and game_plan.reward_third_id:
                        self.reward_user(cr, uid, third_user.id, game_plan.reward_second_id.id, context)
                        message_body += "<br/> 3. %s - %s" % (third_user.name, game_plan.reward_third_id.name)
                        
                self.message_post(cr, uid, game_plan.id, body=message_body, context=context)
        return True
    
gamification_goal_plan()

class gamification_goal_type(osv.osv):
    _inherit = 'gamification.goal.type'
    _columns = {
                'product_category_field': fields.char('Product Category Field', char=128)
                }
gamification_goal_type()

class gamification_goal(osv.osv):
    _inherit = 'gamification.goal'
    
    def _get_goal(self, cr, uid, ids, context=None):
        gamification_goal_pool = self.pool.get('gamification.goal')
        goal_ids = gamification_goal_pool.search(cr, uid, [('type_id', 'in', ids)], context=context)
        return goal_ids
    
    def _get_product_cat(self, cr, uid, ids, name, args, context=None):
        res = {}
        for goal in self.browse(cr, uid, ids, context=context):
            res[goal.id] = False
            try:
                if goal.type_id.computation_mode in ['sum', 'count'] and goal.type_id.product_category_field:
                    obj = self.pool.get(goal.type_id.model_id.model)
                    field_date_name = goal.type_id.field_date_name
                    domain = safe_eval(goal.type_id.domain, {'user': goal.user_id})
                    ref_value_ids = obj.search(cr, uid, domain, context=context, limit=1)
                    if ref_value_ids:
                        ref_value_id = ref_value_ids[0]
                        ref_value_obj = obj.browse(cr, uid, ref_value_id, context=context)
                        ref_value_data = eval('ref_value_obj.' + goal.type_id.product_category_field)
                        res[goal.id] = ref_value_data
                    else:
                        for ele in domain:
                            if ele[0] == goal.type_id.product_category_field:
                                res[goal.id] = ele[2]
            except:
                _logger.warning("Error Occurred in goal category calculation!!!!!")
        return res
    
    _columns = {
                'product_category_id': fields.function(_get_product_cat, type='many2one',
                                                       relation='product.category', string="Product Category",
                                                       store={
                                                              'gamification.goal': (lambda self, cr, uid, ids, c={}: ids, ['type_id'], 5),
                                                              'gamification.goal.type': (_get_goal, ['model_id', 'product_category_field', 'domain'], 5)
                                                              })
                }
    
gamification_goal()
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
