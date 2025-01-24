from knowledgenet.scanner import ruledef
from knowledgenet.rule import Rule, Fact, Collection
from knowledgenet.controls import insert, update, delete
from knowledgenet.container import Collector

from autoins.entities import Action, Adj, Automobile, Claim, Driver, Estimate, IncidenceReport, Policy

# #########################################################################
# Rule order: 0
# Set of rules that builds the Adj object for each claim that is pending 
# including collecting historical claims
# ##########################################################################
@ruledef
def create_adj():    
    return Rule(when=Fact(of_type=Claim, var='claim', 
                matches=lambda ctx,this: this.status == 'pending'),
        then=lambda ctx: insert(ctx, Adj(ctx.claim)))

@ruledef
def join_adj_with_policy():
    def join_adj_with_policy_rhs(ctx):
        ctx.adj.policy = ctx.policy
        update(ctx, ctx.adj)
    return Rule(run_once=True,
        when=[Fact(of_type=Adj, var='adj'),
                Fact(of_type=Policy, var='policy', 
                    matches=lambda ctx, this: ctx.adj.claim.policy_id == this.id)],
        then=join_adj_with_policy_rhs)

@ruledef
def join_adj_with_driver():
    def join_adj_with_driver_rhs(ctx):
        ctx.adj.driver = ctx.driver
        update(ctx, ctx.adj)
    return Rule(run_once=True,
        when=[Fact(of_type=Adj, var='adj'),
                Fact(of_type=Driver, var='driver', 
                    matches=lambda ctx, this: ctx.adj.claim.driver_id == this.id)],
        then=join_adj_with_driver_rhs)

@ruledef
def join_adj_with_automobile():
    def join_adj_with_automobile_rhs(ctx):
        ctx.adj.automobile = ctx.automobile
        update(ctx, ctx.adj)
    return Rule(run_once=True,
        when=[Fact(of_type=Adj, var='adj'),
                Fact(of_type=Automobile, var='automobile', 
                    matches=lambda ctx, this: ctx.adj.claim.automobile_id == this.id)],
        then=join_adj_with_automobile_rhs)

@ruledef
def join_adj_with_incidence_report():
    def join_adj_with_incidence_report_rhs(ctx):
        ctx.adj.incidence_report = ctx.incidence_report
        update(ctx, ctx.adj)
    return Rule(run_once=True,
        when=[Fact(of_type=Adj, var='adj'),
                Fact(of_type=IncidenceReport, var='incidence_report', 
                    matches=lambda ctx, this: ctx.adj.claim.incidence_report_id == this.id)],
        then=join_adj_with_incidence_report_rhs)

# #########################################################################
# Rule order: 1
# Add collectors
# ##########################################################################
@ruledef
def create_collision_history_collector():
    '''
    Create collectors that collect history (past) of claims of type, collision, for an adjudicated claim. We are interested in the paid amount
    '''
    return Rule(run_once=True, order=1,
        when=Fact(of_type=Adj, var='adj'),
        then=lambda ctx: 
            insert(ctx, 
                    Collector(of_type=Claim, group='collision-history-collector', adj=ctx.adj,
                        filter=[lambda this,claim: claim.status == 'approved',
                                lambda this,claim: this.adj.policy and this.adj.policy.id == claim.policy_id,
                                lambda this,claim: this.adj.claim.filing_date.year == claim.filing_date.year])))

@ruledef
def create_liability_history_collector():
    '''
    Create collectors that collect history (past) of claims of type, liability, for an adjudicated claim. We are interested in the paid amount
    '''
    return Rule(run_once=True, order=1,
        when=Fact(of_type=Adj, var='adj'),
        then=lambda ctx: 
            insert(ctx, 
                    Collector(of_type=Claim, group='liability-history-collector', adj=ctx.adj,
                        filter=[lambda this,claim: claim.status == 'approved',
                                lambda this,claim: claim.type == 'liability',
                                lambda this,claim: this.adj.policy and this.adj.policy.id == claim.policy_id,
                                lambda this,claim: this.adj.claim.filing_date.year == claim.filing_date.year])))

@ruledef
def create_estimate_collector():
    '''
    Create collectors that collect all estimates for an adjudicated claim
    '''
    return Rule(run_once=True, order=1,
        when=Fact(of_type=Adj, var='adj'),
        then=lambda ctx: 
            insert(ctx, 
                    Collector(of_type=Estimate, group='estimate-collector', adj=ctx.adj,
                        filter=lambda this,estimate: estimate.claim_id == ctx.adj.claim.id)))

# #########################################################################
# Rule order: 2
# Enrich Adj with collected data
# ########################################################################## 
@ruledef
def add_collision_history_to_adj():
    '''
    Add all history records to the adj so that other rulesets can get the history information from the adj object itself
    '''
    def add_collision_history_to_adj_rhs(ctx):
        ctx.adj.collision_history = ctx.hist.collection
        update(ctx, ctx.adj)
    return Rule(order=2, run_once=True,
        when=(Fact(of_type=Adj, var='adj'),
                Collection(group='collision-history-collector', var='hist', matches=lambda ctx,this: ctx.adj == this.adj)),
        then=add_collision_history_to_adj_rhs)

@ruledef
def add_liability_history_to_adj():
    '''
    Add all liability history records to the adj so that other rulesets can get the history information from the adj object itself
    '''
    def add_liability_history_to_adj_rhs(ctx):
        ctx.adj.liability_history = ctx.hist.collection
        update(ctx, ctx.adj)
    return Rule(order=2, run_once=True,
        when=(Fact(of_type=Adj, var='adj'),
                Collection(group='liability-history-collector', var='hist', matches=lambda ctx,this: ctx.adj == this.adj)),
        then=add_liability_history_to_adj_rhs)

@ruledef
def add_estimates_to_adj():
    '''
    Add all estimates to the adj so that other rulesets can get estimates from the adj object itself
    '''
    def add_estimates_to_adj_rhs(ctx):
        ctx.adj.estimates = ctx.estimate.collection
        update(ctx, ctx.adj)
    return Rule(order=2, run_once=True,
        when=(Fact(of_type=Adj, var='adj'),
                Collection(group='estimate-collector', var='estimate', matches=lambda ctx,this: ctx.adj == this.adj)),
        then=add_estimates_to_adj_rhs)

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
    Create a collection that collects all the actions for a claim being adjudicated
    '''
    return Rule(order=3,
        when=Fact(of_type=Adj, var='adj'),
        then=lambda ctx: insert(ctx, 
                                Collector(of_type=Action, group='action-collector', adj=ctx.adj, 
                                    filter=lambda this,action: this.adj.claim.id == action.claim_id)))