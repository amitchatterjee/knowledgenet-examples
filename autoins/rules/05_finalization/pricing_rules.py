import logging
import uuid
from knowledgenet.decorator import ruledef
from knowledgenet.rule import Rule, Fact, Collection, Event
from knowledgenet.controls import insert, update
from knowledgenet.helper import assign

from autoins.bluebook import BlueBook
from autoins.entities import Request, Action

@ruledef
def compute_collision_payment():
    '''
    Compute payment based on lowest estimate, pay_percent, deductibles, and coverage
    '''
    def compute_collision_payment_rhs(ctx):
        lowest_estimate = min(ctx.request.estimates, key=lambda est: est.amount)
        est_automobile_value = ctx.bluebook_value if ctx.bluebook_value is not None else 1000000.00
        lowest_amount = min(lowest_estimate.amount, est_automobile_value)
        payable = max((lowest_amount * ctx.action.pay_percent) 
                      - ctx.request.group.collision_deductible if ctx.request.group else 0.0, 0.0)
        balance = max(ctx.request.group.collision_coverage - sum([each.paid_amount for each in ctx.request.collision_history]), 0.0) \
            if ctx.request.group else 0.0
        ctx.action.pay_amount = min(balance, payable)
        update(ctx, ctx.action)
    return Rule(run_once=True, order=2,
        when=[Fact(of_type=Request, var='request', matches=lambda ctx,this: this.claim.type == 'collision'), 
            Fact(of_type=Action, var='action', 
                matches=lambda ctx,this: not this.inactive and this.pay_percent > 0 and ctx.request.claim.id == this.claim_id),
            Fact(of_type=BlueBook,
                 matches=lambda ctx,this: assign(ctx, bluebook_value=this.lookup(ctx.request.automobile.make, ctx.request.automobile.model,ctx.request.automobile.year)))],
        then=compute_collision_payment_rhs)

@ruledef
def compute_liability_payment():
    '''
    Compute payment based on lowest estimate, pay_percent, and coverage for liability claims
    '''
    def compute_liability_payment_rhs(ctx):
        lowest_estimate = min(ctx.request.estimates, key=lambda est: est.amount)
        est_automobile_value = ctx.bluebook_value if ctx.bluebook_value is not None else 1000000.00
        lowest_amount = min(lowest_estimate.amount, est_automobile_value)
        payable = max((lowest_amount * (1.0 - ctx.action.pay_percent)), 0.0)
        balance = max(ctx.request.group.liability_coverage - sum([each.paid_amount for each in ctx.request.liability_history]), 0.0) \
            if ctx.request.group else 0.0
        ctx.action.pay_amount = min(balance, payable)
        update(ctx, ctx.action)
    return Rule(run_once=True, order=2,
        when=[Fact(of_type=Request, var='request', 
                   matches=lambda ctx,this: this.claim.type == 'liability'), 
            Fact(of_type=Action, var='action', 
                matches=lambda ctx,this: not this.inactive and this.pay_percent > 0 and ctx.request.claim.id == this.claim_id),
            Fact(of_type=BlueBook,
                 matches=lambda ctx,this: assign(ctx, bluebook_value=this.lookup(ctx.request.automobile.make, ctx.request.automobile.model,ctx.request.automobile.year)))],
        then=compute_liability_payment_rhs)