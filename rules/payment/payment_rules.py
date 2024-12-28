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
        if len(ctx.actions.collection) == 0:
            # insert(ctx, Action('NOCHG', ctx.adj.claim.id, 'p', 'pay', 0.00))
            return
        print(f'compute payment for {ctx.adj} - {len(ctx.actions.collection)}')
    return Rule(id='select-action', repository='autoclaims', ruleset=ruleset,
        when=Condition(of_type=Collector, group='action-collector', 
                        matches=lambda ctx,this: assign(ctx, actions=this, adj=this.adj)),
        then=select)