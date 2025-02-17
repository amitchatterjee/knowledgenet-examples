from knowledgenet.scanner import ruledef
from knowledgenet.rule import Rule, Fact, Collection
from knowledgenet.controls import insert, update, delete
from knowledgenet.container import Collector

from autoins.entities import Action, ClaimContext, Automobile, Claim, Driver, Estimate, IncidenceReport, Policy

# #########################################################################
# Rule order: 0
# Set of rules that builds the ClaimContext object for each claim that has been received 
# including collecting historical claims
# ##########################################################################
@ruledef
def create_claim_context():    
    return Rule(when=Fact(of_type=Claim, var='claim', 
                matches=lambda ctx,this: this.status == 'received'),
        then=lambda ctx: insert(ctx, ClaimContext(ctx.claim)))

@ruledef
def join_claim_context_with_policy():
    def join_claim_context_with_policy_rhs(ctx):
        ctx.claim_context.policy = ctx.policy
        update(ctx, ctx.claim_context)
    return Rule(run_once=True,
        when=[Fact(of_type=ClaimContext, var='claim_context'),
                Fact(of_type=Policy, var='policy', 
                    matches=lambda ctx, this: ctx.claim_context.claim.policy_id == this.id)],
        then=join_claim_context_with_policy_rhs)

@ruledef
def join_claim_context_with_driver():
    def join_claim_context_with_driver_rhs(ctx):
        ctx.claim_context.driver = ctx.driver
        update(ctx, ctx.claim_context)
    return Rule(run_once=True,
        when=[Fact(of_type=ClaimContext, var='claim_context'),
                Fact(of_type=Driver, var='driver', 
                    matches=lambda ctx, this: ctx.claim_context.claim.driver_id == this.id)],
        then=join_claim_context_with_driver_rhs)

@ruledef
def join_claim_context_with_automobile():
    def join_claim_context_with_automobile_rhs(ctx):
        ctx.claim_context.automobile = ctx.automobile
        update(ctx, ctx.claim_context)
    return Rule(run_once=True,
        when=[Fact(of_type=ClaimContext, var='claim_context'),
                Fact(of_type=Automobile, var='automobile', 
                    matches=lambda ctx, this: ctx.claim_context.claim.vin == this.vin)],
        then=join_claim_context_with_automobile_rhs)

@ruledef
def join_claim_context_with_incidence_report():
    def join_claim_context_with_incidence_report_rhs(ctx):
        ctx.claim_context.incidence_report = ctx.incidence_report
        update(ctx, ctx.claim_context)
    return Rule(run_once=True,
        when=[Fact(of_type=ClaimContext, var='claim_context'),
                Fact(of_type=IncidenceReport, var='incidence_report', 
                    matches=lambda ctx, this: ctx.claim_context.claim.incidence_report_id == this.id)],
        then=join_claim_context_with_incidence_report_rhs)

# #########################################################################
# Rule order: 1
# Add collectors
# ##########################################################################
@ruledef
def create_collision_history_collector():
    '''
    Create collectors that collect history (past) of claims of type, collision, for each claim being processed. We are interested in the paid amount
    '''
    return Rule(run_once=True, order=1,
        when=Fact(of_type=ClaimContext, var='claim_context'),
        then=lambda ctx: 
            insert(ctx, 
                    Collector(of_type=Claim, group='collision-history-collector', claim_context=ctx.claim_context,
                        filter=[lambda this,claim: claim.status == 'approved',
                                lambda this,claim: this.claim_context.policy and this.claim_context.policy.id == claim.policy_id,
                                lambda this,claim: this.claim_context.claim.filing_date.year == claim.filing_date.year])))

@ruledef
def create_liability_history_collector():
    '''
    Create collectors that collect history (past) of claims of type, liability, for each claim being processed. We are interested in the paid amount
    '''
    return Rule(run_once=True, order=1,
        when=Fact(of_type=ClaimContext, var='claim_context'),
        then=lambda ctx: 
            insert(ctx, 
                    Collector(of_type=Claim, group='liability-history-collector', claim_context=ctx.claim_context,
                        filter=[lambda this,claim: claim.status == 'approved',
                                lambda this,claim: claim.type == 'liability',
                                lambda this,claim: this.claim_context.policy and this.claim_context.policy.id == claim.policy_id,
                                lambda this,claim: this.claim_context.claim.filing_date.year == claim.filing_date.year])))

@ruledef
def create_estimate_collector():
    '''
    Create collectors that collect all estimates for a claim being processed
    '''
    return Rule(run_once=True, order=1,
        when=Fact(of_type=ClaimContext, var='claim_context'),
        then=lambda ctx: 
            insert(ctx, 
                    Collector(of_type=Estimate, group='estimate-collector', claim_context=ctx.claim_context,
                        filter=lambda this,estimate: estimate.claim_id == ctx.claim_context.claim.id)))

# #########################################################################
# Rule order: 2
# Enrich ClaimContext with collected data
# ########################################################################## 
@ruledef
def add_collision_history_to_claim_context():
    '''
    Add all history records to the claim_context so that other rulesets can get the history information from the claim_context object itself
    '''
    def add_collision_history_to_claim_context_rhs(ctx):
        ctx.claim_context.collision_history = ctx.hist.collection
        update(ctx, ctx.claim_context)
    return Rule(order=2, run_once=True,
        when=(Fact(of_type=ClaimContext, var='claim_context'),
                Collection(group='collision-history-collector', var='hist', matches=lambda ctx,this: ctx.claim_context == this.claim_context)),
        then=add_collision_history_to_claim_context_rhs)

@ruledef
def add_liability_history_to_claim_context():
    '''
    Add all liability history records to the claim_context so that other rulesets can get the history information from the claim_context object itself
    '''
    def add_liability_history_to_claim_context_rhs(ctx):
        ctx.claim_context.liability_history = ctx.hist.collection
        update(ctx, ctx.claim_context)
    return Rule(order=2, run_once=True,
        when=(Fact(of_type=ClaimContext, var='claim_context'),
                Collection(group='liability-history-collector', var='hist', matches=lambda ctx,this: ctx.claim_context == this.claim_context)),
        then=add_liability_history_to_claim_context_rhs)

@ruledef
def add_estimates_to_claim_context():
    '''
    Add all estimates to the claim_context so that other rulesets can get estimates from the claim_context object itself
    '''
    def add_estimates_to_claim_context_rhs(ctx):
        ctx.claim_context.estimates = ctx.estimate.collection
        update(ctx, ctx.claim_context)
    return Rule(order=2, run_once=True,
        when=(Fact(of_type=ClaimContext, var='claim_context'),
                Collection(group='estimate-collector', var='estimate', matches=lambda ctx,this: ctx.claim_context == this.claim_context)),
        then=add_estimates_to_claim_context_rhs)

# #########################################################################
# Rule order: 3
# Prepares for the next ruleset to run by cleaning up uneeded objects,
# adding new collectors, etc.
# ########################################################################## 
@ruledef 
def del_collision_history_collector():
    '''
    The work of the collision history collectors are done 
    '''
    return Rule(order=3,
            when=Collection(group='collision-history-collector', var='hist'),
            then=lambda ctx: delete(ctx, ctx.hist))

@ruledef 
def del_liability_history_collector():
    '''
    The work of the liability history collectors are done 
    '''
    return Rule(order=3,
            when=Collection(group='liability-history-collector', var='hist'),
            then=lambda ctx: delete(ctx, ctx.hist))

@ruledef 
def del_estimate_collector():
    '''
    The work of the estimate collectors are done 
    '''
    return Rule(order=3,
            when=Collection(group='estimate-collector', var='estimate'),
            then=lambda ctx: delete(ctx, ctx.estimate))

@ruledef
def create_action_collector():
    '''
    Create a collection that collects all the actions for each claim being processed
    '''
    return Rule(order=3,
        when=Fact(of_type=ClaimContext, var='claim_context'),
        then=lambda ctx: insert(ctx, 
                                Collector(of_type=Action, group='action-collector', 
                                        claim_context=ctx.claim_context, 
                                        filter=lambda this,action: this.claim_context.claim.id == action.claim_id)))