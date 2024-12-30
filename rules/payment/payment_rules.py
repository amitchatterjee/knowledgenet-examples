import uuid
from knowledgenet.scanner import ruledef
from knowledgenet.rule import Rule, Condition
from knowledgenet.controls import insert, update, delete
from knowledgenet.helper import assign
from knowledgenet.ftypes import Collector

from autoins.entities import Action

ruleset='004-payment'

@ruledef
def select_action():
    def select(ctx):
        if len(ctx.actions) == 0:
            insert(ctx, Action(str(uuid.uuid4()), 'NOCHG', ctx.claim_id, 'p', 'pay', 0.00))
        else:
            # TODO select the best action
            return
    return Rule(id='select-action', repository='autoclaims', ruleset=ruleset, run_once=True,
        when=Condition(of_type=Collector, group='action-collector', 
                    matches=lambda ctx,this: assign(ctx, actions=this.collection, claim_id=this.claim_id)),
        then=select)