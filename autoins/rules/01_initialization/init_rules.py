from knowledgenet.decorator import ruledef
from knowledgenet.rule import Rule, Fact, Collection
from knowledgenet.controls import insert, update, delete
from knowledgenet.container import Collector

from autoins.entities import Request, Automobile, Claim, Driver, Estimate, Group, IncidenceReport, Policy, Action
from autoins.util import echo

# #########################################################################
# Rule order: 0
# Set of rules that builds the Request object for each claim that has 
# been received and joins with the policy 
# ##########################################################################
@ruledef
def create_request():    
    return Rule(when=Fact(of_type=Claim, var='claim', 
                matches=lambda ctx,this: this.status == 'received'),
        then=lambda ctx: insert(ctx, Request(claim=ctx.claim)))

@ruledef
def join_request_with_policy():
    def join_request_with_policy_rhs(ctx):
        ctx.request.policy = ctx.policy
        update(ctx, ctx.request)
    return Rule(run_once=True,
        when=[Fact(of_type=Request, var='request'),
                Fact(of_type=Policy, var='policy', 
                    matches=lambda ctx, this: ctx.request.claim.policy_id == this.id)],
        then=join_request_with_policy_rhs)

# #########################################################################
# Rule order: 1
# Set of rules that builds the Request object for each claim that has been received 
# ##########################################################################
@ruledef
def join_request_with_group():
    def join_request_with_group_rhs(ctx):
        ctx.request.group = ctx.group
        update(ctx, ctx.request)
    return Rule(run_once=True, order=1,
        when=[Fact(of_type=Request, var='request'),
              Fact(of_type=Group, var='group', 
                   matches=lambda ctx,this: ctx.request.policy and ctx.request.policy.group_id == this.id)],
        then=join_request_with_group_rhs)

@ruledef
def join_request_with_driver():
    def join_request_with_driver_rhs(ctx):
        ctx.request.driver = ctx.driver
        update(ctx, ctx.request)
    return Rule(run_once=True, order=1,
        when=[Fact(of_type=Request, var='request'),
                Fact(of_type=Driver, var='driver', 
                    matches=lambda ctx, this: ctx.request.claim.driver_id == this.id)],
        then=join_request_with_driver_rhs)

@ruledef
def join_request_with_automobile():
    def join_request_with_automobile_rhs(ctx):
        ctx.request.automobile = ctx.automobile
        update(ctx, ctx.request)
    return Rule(run_once=True, order=1,
        when=[Fact(of_type=Request, var='request'),
                Fact(of_type=Automobile, var='automobile', 
                    matches=lambda ctx, this: ctx.request.claim.vin == this.vin)],
        then=join_request_with_automobile_rhs)

@ruledef
def join_request_with_incidence_report():
    def join_request_with_incidence_report_rhs(ctx):
        ctx.request.incidence_report = ctx.incidence_report
        update(ctx, ctx.request)
    return Rule(run_once=True, order=1,
        when=[Fact(of_type=Request, var='request'),
                Fact(of_type=IncidenceReport, var='incidence_report', 
                    matches=lambda ctx, this: ctx.request.claim.incidence_report_id == this.id)],
        then=join_request_with_incidence_report_rhs)

# #########################################################################
# Rule order: 2
# Add collectors
# ##########################################################################
@ruledef
def create_collision_history_collector():
    '''
    Create collectors that collect history (past) of claims of type, collision, for each claim being processed. We are interested in the paid amount
    '''
    return Rule(run_once=True, order=2,
        when=Fact(of_type=Request, var='request'),
        then=lambda ctx: 
            insert(ctx, 
                    Collector(of_type=Claim, group='collision-history-collector', request=ctx.request,
                        filter=[lambda this,claim: claim.status == 'approved',
                                lambda this,claim: this.request.policy and this.request.policy.id == claim.policy_id,
                                lambda this,claim: this.request.claim.filing_date.year == claim.filing_date.year])))

@ruledef
def create_liability_history_collector():
    '''
    Create collectors that collect history (past) of claims of type, liability, for each claim being processed. We are interested in the paid amount
    '''
    return Rule(run_once=True, order=2,
        when=Fact(of_type=Request, var='request'),
        then=lambda ctx: 
            insert(ctx, 
                    Collector(of_type=Claim, group='liability-history-collector', request=ctx.request,
                        filter=[lambda this,claim: claim.status == 'approved',
                                lambda this,claim: claim.type == 'liability',
                                lambda this,claim: this.request.policy and this.request.policy.id == claim.policy_id,
                                lambda this,claim: this.request.claim.filing_date.year == claim.filing_date.year])))

@ruledef
def create_estimate_collector():
    '''
    Create collectors that collect all estimates for a claim being processed
    '''
    return Rule(run_once=True, order=2,
        when=Fact(of_type=Request, var='request'),
        then=lambda ctx: 
            insert(ctx, 
                    Collector(of_type=Estimate, group='estimate-collector', request=ctx.request,
                        filter=lambda this,estimate: estimate.claim_id == ctx.request.claim.id)))

# #########################################################################
# Rule order: 3
# Enrich Request with collected data
# ########################################################################## 
@ruledef
def add_collision_history_to_request():
    '''
    Add all history records to the request so that other rulesets can get the history information from the request object itself
    '''
    def add_collision_history_to_request_rhs(ctx):
        ctx.request.collision_history = ctx.hist.collection
        update(ctx, ctx.request)
    return Rule(order=3, run_once=True,
        when=(Fact(of_type=Request, var='request'),
                Collection(group='collision-history-collector', var='hist', matches=lambda ctx,this: ctx.request == this.request)),
        then=add_collision_history_to_request_rhs)

@ruledef
def add_liability_history_to_request():
    '''
    Add all liability history records to the request so that other rulesets can get the history information from the request object itself
    '''
    def add_liability_history_to_request_rhs(ctx):
        ctx.request.liability_history = ctx.hist.collection
        update(ctx, ctx.request)
    return Rule(order=3, run_once=True,
        when=(Fact(of_type=Request, var='request'),
                Collection(group='liability-history-collector', var='hist', matches=lambda ctx,this: ctx.request == this.request)),
        then=add_liability_history_to_request_rhs)

@ruledef
def add_estimates_to_request():
    '''
    Add all estimates to the request so that other rulesets can get estimates from the request object itself
    '''
    def add_estimates_to_request_rhs(ctx):
        ctx.request.estimates = ctx.estimate.collection
        update(ctx, ctx.request)
    return Rule(order=3, run_once=True,
        when=(Fact(of_type=Request, var='request'),
                Collection(group='estimate-collector', var='estimate', matches=lambda ctx,this: ctx.request == this.request)),
        then=add_estimates_to_request_rhs)

# #########################################################################
# Rule order: 4
# Prepares for the next ruleset to run by cleaning up uneeded objects,
# adding new collectors, etc.
# ########################################################################## 
@ruledef 
def del_collision_history_collector():
    '''
    The work of the collision history collectors are done 
    '''
    return Rule(order=4,
            when=Collection(group='collision-history-collector', var='hist'),
            then=lambda ctx: delete(ctx, ctx.hist))

@ruledef 
def del_liability_history_collector():
    '''
    The work of the liability history collectors are done 
    '''
    return Rule(order=4,
            when=Collection(group='liability-history-collector', var='hist'),
            then=lambda ctx: delete(ctx, ctx.hist))

@ruledef 
def del_estimate_collector():
    '''
    The work of the estimate collectors are done 
    '''
    return Rule(order=4,
            when=Collection(group='estimate-collector', var='estimate'),
            then=lambda ctx: delete(ctx, ctx.estimate))

@ruledef
def create_action_collector():
    '''
    Create a collection that collects all the actions for each claim being processed
    '''
    return Rule(order=4,
        when=Fact(of_type=Request, var='request'),
        then=lambda ctx: insert(ctx, 
                                Collector(of_type=Action, group='action-collector', 
                                        request=ctx.request, 
                                        filter=lambda this,action: this.request.claim.id == action.claim_id)))