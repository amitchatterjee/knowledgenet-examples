import logging
import uuid
from knowledgenet.scanner import ruledef
from knowledgenet.rule import Rule, Fact, Collection, Event
from knowledgenet.controls import insert, update
from knowledgenet.helper import assign

from autoins.entities import Action, Adj
from autoins.util import record_action_event

@ruledef
def create_action_event_handler():
    return Rule(when=Event(on_types=Action, var='event'),
                then=lambda ctx: record_action_event(ctx.event))

@ruledef
def pay_on_no_action():
    '''
    When a claim has no actions associated with it, pay the claim.
    '''
    return Rule(run_once=True,
        when=Collection(group='action-collector', 
                    matches=[lambda ctx,this: not len(this.collection),  
                            lambda ctx,this: assign(ctx, adj=this.adj)]),
        then=lambda ctx: insert(ctx, Action(str(uuid.uuid4()), 'PAYC', ctx.adj.claim.id, 'p', 'pay', 
                            ctx.adj.police_report.liability_percent, inactive=False)))

@ruledef
def select_action():
    '''
    select the best action and make it active
        #1. sort actions by rank (desc) and pay_percent (asc)
        #2. pick the first action and make inactive = False
    '''
    def select_action_rhs(ctx):
        actions = list(ctx.actions)
        actions.sort(key=lambda a: (-a.rank, a.pay_percent))
        actions[0].inactive = False
        update(ctx, actions[0])
    return Rule(run_once=True, order=1,
        when=Collection(group='action-collector', 
                    matches=lambda ctx,this: assign(ctx, actions=this.collection, adj=this.adj)),
        then=select_action_rhs)

@ruledef
def compute_payment():
    '''
    Compute payment based on the pay_percent, deductibles, and coverage
    '''
    def compute_payment_rhs(ctx):
        payable = max((ctx.adj.claim.claimed_amount * ctx.action.pay_percent) 
                      - ctx.adj.policy.deductible if ctx.adj.policy else 0.0, 0.0)
        balance = max(ctx.adj.policy.max_coverage - sum([each.paid_amount for each in ctx.adj.history]), 0.0) \
            if ctx.adj.policy else 0.0
        ctx.action.pay_amount = min(balance, payable)
        update(ctx, ctx.action)
    return Rule(run_once=True, order=2,
        when=[Fact(of_type=Adj, var='adj'), 
            Fact(of_type=Action, var='action', 
                    matches=lambda ctx,this: not this.inactive and this.pay_percent > 0 and ctx.adj.claim.id == this.claim_id)],
        then=compute_payment_rhs)