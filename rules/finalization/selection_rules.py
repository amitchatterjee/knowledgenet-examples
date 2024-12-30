import uuid
from knowledgenet.scanner import ruledef
from knowledgenet.rule import Rule, Condition
from knowledgenet.controls import insert, update, delete
from knowledgenet.helper import assign
from knowledgenet.ftypes import Collector

from autoins.entities import Action

ruleset='004-finalization'

@ruledef
def select_action():
    def select(ctx):
        if len(ctx.actions) == 0:
            insert(ctx, Action(str(uuid.uuid4()), 'NOCHG', ctx.adj.claim.id, 'p', 'pay', 
                               ctx.adj.police_report.liability_percent, inactive=False))
        else:
            '''
            select the best action and make it active
                #1. sort actions by rank (asc) and pay_percent (asc)
                #2. pick the first action and make inactive = False
            '''
            actions = list(ctx.actions)
            actions.sort(key=lambda a: (a.rank, a.pay_percent))
            actions[0].inactive = False
            update(ctx, actions[0])
            return
    return Rule(id='select-action', repository='autoclaims', ruleset=ruleset, run_once=True,
        when=Condition(of_type=Collector, group='action-collector', 
                    matches=lambda ctx,this: assign(ctx, actions=this.collection, adj=this.adj)),
        then=select)

@ruledef
def compute_payment():
    def compute(ctx):
        # TODO: Compute payment based on the pay_percent, deductibles, and coverage
        print(f"Computing payment for claim {ctx.action.claim_id}")
    return Rule(id='compute-payment', repository='autoclaims', ruleset=ruleset, run_once=True, order=1,
        when=Condition(of_type=Action, matches=lambda ctx,this: not this.inactive and assign(ctx, action=this)),
        then=compute)