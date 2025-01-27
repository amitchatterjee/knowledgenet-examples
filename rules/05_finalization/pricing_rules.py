import logging
import uuid
from knowledgenet.scanner import ruledef
from knowledgenet.rule import Rule, Fact, Collection, Event
from knowledgenet.controls import insert, update
from knowledgenet.helper import assign

from autoins.entities import Action, Adj
from autoins.util import record_action_event

@ruledef
def compute_collision_payment():
    '''
    Compute payment based on lowest estimate, pay_percent, deductibles, and coverage
    '''
    def compute_collision_payment_rhs(ctx):
        lowest = min(ctx.adj.estimates, key=lambda est: est.amount)
        payable = max((lowest.amount * ctx.action.pay_percent) 
                      - ctx.adj.policy.collision_deductible if ctx.adj.policy else 0.0, 0.0)
        balance = max(ctx.adj.policy.collision_coverage - sum([each.paid_amount for each in ctx.adj.collision_history]), 0.0) \
            if ctx.adj.policy else 0.0
        ctx.action.pay_amount = min(balance, payable)
        update(ctx, ctx.action)
    return Rule(run_once=True, order=2,
        when=[Fact(of_type=Adj, var='adj', matches=lambda ctx,this: this.claim.type == 'collision'), 
            Fact(of_type=Action, var='action', 
                matches=lambda ctx,this: not this.inactive and this.pay_percent > 0 and ctx.adj.claim.id == this.claim_id)],
        then=compute_collision_payment_rhs)

@ruledef
def compute_liability_payment():
    '''
    Compute payment based on lowest estimate, pay_percent, and coverage for liability claims
    '''
    def compute_liability_payment_rhs(ctx):
        lowest = min(ctx.adj.estimates, key=lambda est: est.amount)
        payable = max((lowest.amount * (1.0 - ctx.action.pay_percent)), 0.0)
        balance = max(ctx.adj.policy.liability_coverage - sum([each.paid_amount for each in ctx.adj.liability_history]), 0.0) \
            if ctx.adj.policy else 0.0
        ctx.action.pay_amount = min(balance, payable)
        update(ctx, ctx.action)
    return Rule(run_once=True, order=2,
        when=[Fact(of_type=Adj, var='adj', matches=lambda ctx,this: this.claim.type == 'liability'), 
            Fact(of_type=Action, var='action', 
                matches=lambda ctx,this: not this.inactive and this.pay_percent > 0 and ctx.adj.claim.id == this.claim_id)],
        then=compute_liability_payment_rhs)