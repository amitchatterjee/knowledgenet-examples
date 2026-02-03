from knowledgenet.decorator import ruledef
from knowledgenet.rule import Rule, Fact, Collection
from knowledgenet.controls import insert, update, delete
from knowledgenet.container import Collector

from autoins.entities2 import Request, Automobile, Claim, Driver, Estimate, Group, IncidenceReport, Policy, Action
from autoins.util import echo

# #########################################################################
# Rule order: 0
# Set of rules that builds the Request object for each claim that has 
# been received and joins with the policy 
# ##########################################################################
@ruledef
def create_exec_context():    
    return Rule(when=Fact(of_type=Claim, var='claim', 
                matches=lambda ctx,this: this.status == 'received'),
        then=lambda ctx: insert(ctx, Request(claim=ctx.claim)))

@ruledef
def join_exec_context_with_policy():
    def join_exec_context_with_policy_rhs(ctx):
        ctx.exec_context.policy = ctx.policy
        update(ctx, ctx.exec_context)
    return Rule(run_once=True,
        when=[Fact(of_type=Request, var='exec_context'),
                Fact(of_type=Policy, var='policy', 
                    matches=lambda ctx, this: ctx.exec_context.claim.policy_id == this.id)],
        then=join_exec_context_with_policy_rhs)

# #########################################################################
# Rule order: 1
# Set of rules that builds the Request object for each claim that has been received 
# ##########################################################################
@ruledef
def join_exec_context_with_group():
    def join_exec_context_with_group_rhs(ctx):
        ctx.exec_context.group = ctx.group
        update(ctx, ctx.exec_context)
    return Rule(run_once=True, order=1,
        when=[Fact(of_type=Request, var='exec_context'),
              Fact(of_type=Group, var='group', 
                   matches=lambda ctx,this: ctx.exec_context.policy and ctx.exec_context.policy.group_id == this.id)],
        then=join_exec_context_with_group_rhs)

@ruledef
def join_exec_context_with_driver():
    def join_exec_context_with_driver_rhs(ctx):
        ctx.exec_context.driver = ctx.driver
        update(ctx, ctx.exec_context)
    return Rule(run_once=True, order=1,
        when=[Fact(of_type=Request, var='exec_context'),
                Fact(of_type=Driver, var='driver', 
                    matches=lambda ctx, this: ctx.exec_context.claim.driver_id == this.id)],
        then=join_exec_context_with_driver_rhs)

@ruledef
def join_exec_context_with_automobile():
    def join_exec_context_with_automobile_rhs(ctx):
        ctx.exec_context.automobile = ctx.automobile
        update(ctx, ctx.exec_context)
    return Rule(run_once=True, order=1,
        when=[Fact(of_type=Request, var='exec_context'),
                Fact(of_type=Automobile, var='automobile', 
                    matches=lambda ctx, this: ctx.exec_context.claim.vin == this.vin)],
        then=join_exec_context_with_automobile_rhs)

@ruledef
def join_exec_context_with_incidence_report():
    def join_exec_context_with_incidence_report_rhs(ctx):
        ctx.exec_context.incidence_report = ctx.incidence_report
        update(ctx, ctx.exec_context)
    return Rule(run_once=True, order=1,
        when=[Fact(of_type=Request, var='exec_context'),
                Fact(of_type=IncidenceReport, var='incidence_report', 
                    matches=lambda ctx, this: ctx.exec_context.claim.incidence_report_id == this.id)],
        then=join_exec_context_with_incidence_report_rhs)

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
        when=Fact(of_type=Request, var='exec_context'),
        then=lambda ctx: 
            insert(ctx, 
                    Collector(of_type=Claim, group='collision-history-collector', exec_context=ctx.exec_context,
                        filter=[lambda this,claim: claim.status == 'approved',
                                lambda this,claim: this.exec_context.policy and this.exec_context.policy.id == claim.policy_id,
                                lambda this,claim: this.exec_context.claim.filing_date.year == claim.filing_date.year])))

@ruledef
def create_liability_history_collector():
    '''
    Create collectors that collect history (past) of claims of type, liability, for each claim being processed. We are interested in the paid amount
    '''
    return Rule(run_once=True, order=2,
        when=Fact(of_type=Request, var='exec_context'),
        then=lambda ctx: 
            insert(ctx, 
                    Collector(of_type=Claim, group='liability-history-collector', exec_context=ctx.exec_context,
                        filter=[lambda this,claim: claim.status == 'approved',
                                lambda this,claim: claim.type == 'liability',
                                lambda this,claim: this.exec_context.policy and this.exec_context.policy.id == claim.policy_id,
                                lambda this,claim: this.exec_context.claim.filing_date.year == claim.filing_date.year])))

@ruledef
def create_estimate_collector():
    '''
    Create collectors that collect all estimates for a claim being processed
    '''
    return Rule(run_once=True, order=2,
        when=Fact(of_type=Request, var='exec_context'),
        then=lambda ctx: 
            insert(ctx, 
                    Collector(of_type=Estimate, group='estimate-collector', exec_context=ctx.exec_context,
                        filter=lambda this,estimate: estimate.claim_id == ctx.exec_context.claim.id)))

# #########################################################################
# Rule order: 3
# Enrich Request with collected data
# ########################################################################## 
@ruledef
def add_collision_history_to_exec_context():
    '''
    Add all history records to the exec_context so that other rulesets can get the history information from the exec_context object itself
    '''
    def add_collision_history_to_exec_context_rhs(ctx):
        ctx.exec_context.collision_history = ctx.hist.collection
        update(ctx, ctx.exec_context)
    return Rule(order=3, run_once=True,
        when=(Fact(of_type=Request, var='exec_context'),
                Collection(group='collision-history-collector', var='hist', matches=lambda ctx,this: ctx.exec_context == this.exec_context)),
        then=add_collision_history_to_exec_context_rhs)

@ruledef
def add_liability_history_to_exec_context():
    '''
    Add all liability history records to the exec_context so that other rulesets can get the history information from the exec_context object itself
    '''
    def add_liability_history_to_exec_context_rhs(ctx):
        ctx.exec_context.liability_history = ctx.hist.collection
        update(ctx, ctx.exec_context)
    return Rule(order=3, run_once=True,
        when=(Fact(of_type=Request, var='exec_context'),
                Collection(group='liability-history-collector', var='hist', matches=lambda ctx,this: ctx.exec_context == this.exec_context)),
        then=add_liability_history_to_exec_context_rhs)

@ruledef
def add_estimates_to_exec_context():
    '''
    Add all estimates to the exec_context so that other rulesets can get estimates from the exec_context object itself
    '''
    def add_estimates_to_exec_context_rhs(ctx):
        ctx.exec_context.estimates = ctx.estimate.collection
        update(ctx, ctx.exec_context)
    return Rule(order=3, run_once=True,
        when=(Fact(of_type=Request, var='exec_context'),
                Collection(group='estimate-collector', var='estimate', matches=lambda ctx,this: ctx.exec_context == this.exec_context)),
        then=add_estimates_to_exec_context_rhs)

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
        when=Fact(of_type=Request, var='exec_context'),
        then=lambda ctx: insert(ctx, 
                                Collector(of_type=Action, group='action-collector', 
                                        exec_context=ctx.exec_context, 
                                        filter=lambda this,action: this.exec_context.claim.id == action.claim_id)))