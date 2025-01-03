import uuid
from knowledgenet.scanner import ruledef
from knowledgenet.rule import Rule, Fact, Collection
from knowledgenet.controls import insert, update
from knowledgenet.helper import assign
from knowledgenet.collector import Collector

from autoins.entities import Action, Adj

@ruledef
def select_action():
    def select(ctx):
        if len(ctx.actions) == 0:
            insert(ctx, Action(str(uuid.uuid4()), 'PAYC', ctx.adj.claim.id, 'p', 'pay', 
                               ctx.adj.police_report.liability_percent, inactive=False))
        else:
            '''
            select the best action and make it active
                #1. sort actions by rank (desc) and pay_percent (asc)
                #2. pick the first action and make inactive = False
            '''
            actions = list(ctx.actions)
            actions.sort(key=lambda a: (-a.rank, a.pay_percent))
            actions[0].inactive = False
            update(ctx, actions[0])
            return
    return Rule(run_once=True,
        when=Collection(group='action-collector', 
                    matches=lambda ctx,this: assign(ctx, actions=this.collection, adj=this.adj)),
        then=select)

@ruledef
def compute_payment():
    def compute(ctx):
        # Compute payment based on the pay_percent, deductibles, and coverage
        payable = max((ctx.adj.claim.claimed_amount * ctx.action.pay_percent) 
                      - ctx.adj.policy.deductible if ctx.adj.policy else 0.0, 0.0)
        balance = max(ctx.adj.policy.max_coverage - ctx.history.sum(), 0.0) if ctx.adj.policy else 0.0
        ctx.action.pay_amount = min(balance, payable)
        update(ctx, ctx.action)
    return Rule(run_once=True, order=1,
        when=[Fact(of_type=Adj, var='adj'),
            Collection(group='history-collector', var='history', 
                        matches=lambda ctx,this: this.adj == ctx.adj),  
            Fact(of_type=Action, var='action', 
                    matches=lambda ctx,this: not this.inactive and ctx.adj.claim.id == this.claim_id)],
        then=compute)