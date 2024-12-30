import uuid
from knowledgenet.scanner import ruledef
from knowledgenet.rule import Rule, Condition
from knowledgenet.controls import insert, update
from knowledgenet.helper import assign
from knowledgenet.ftypes import Collector

from autoins.entities import Action, Adj

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
        # TODO: Compute payment based on the pay_percent, deductibles, and coverage. The coverage part is not done yet - will need history of previous payments to compute this.
        balance = (ctx.adj.claim.amount * ctx.action.pay_percent) - ctx.adj.policy.deductible
        ctx.action.pay_amount = balance if balance > 0.0 else 0.0
        update(ctx, ctx.action)
    return Rule(id='compute-payment', repository='autoclaims', ruleset=ruleset, run_once=True, order=1,
        when=[Condition(of_type=Adj, matches=lambda ctx,this: assign(ctx, adj=this)),
            Condition(of_type=Action, matches=lambda ctx,this: 
                      not this.inactive and ctx.adj.claim.id == this.claim_id and assign(ctx, action=this))],
        then=compute)