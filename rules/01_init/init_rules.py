from knowledgenet.scanner import ruledef
from knowledgenet.rule import Rule, Fact, Collection
from knowledgenet.controls import insert, update, delete
from knowledgenet.collector import Collector
from knowledgenet.ftypes import EventFact

from autoins.entities import Action, Adj, Claim, Driver, PoliceReport, Policy, Anchor

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
def create_history_collector():
    '''
    Create a collector that collects history (past) claims for any adjudcated claims. We are interested in the paid amount
    '''
    return Rule(run_once=True,
        when=Fact(of_type=Adj, var='adj'),
        then=lambda ctx: 
            insert(ctx, 
                    Collector(of_type=Claim, group='history-collector', adj=ctx.adj,
                        filter=[lambda this,claim: claim.status == 'approved',
                                lambda this,claim: this.adj.policy and this.adj.policy.id == claim.policy_id,
                                lambda this,claim: this.adj.claim.accident_date.year == claim.accident_date.year])))

@ruledef
def add_policy_to_adj():
    def add_policy_to_adj_claim_rhs(ctx):
        ctx.adj.policy = ctx.policy
        update(ctx, ctx.adj)
    return Rule(run_once=True,
        when=[Fact(of_type=Adj, var='adj'),
              Fact(of_type=Policy, var='policy', 
                    matches=lambda ctx,this: ctx.adj.claim.policy_id == this.id)],
        then=add_policy_to_adj_claim_rhs)

@ruledef
def add_driver_to_adj():
    def add_driver_to_adj_rhs(ctx):
        ctx.adj.driver = ctx.driver
        update(ctx, ctx.adj)
    return Rule(run_once=True,
        when=[Fact(of_type=Adj,  var='adj'),
              Fact(of_type=Driver, var='driver', 
                    matches=lambda ctx,this: ctx.adj.claim.driver_id == this.id)],
        then=add_driver_to_adj_rhs)

@ruledef
def add_police_report_to_adj():
    def add_police_report_to_adj_rhs(ctx):
        ctx.adj.police_report = ctx.police_report
        update(ctx, ctx.adj)
    return Rule(run_once=True,
        when=[Fact(of_type=Adj, var='adj'),
              Fact(of_type=PoliceReport, var='police_report',
                        matches=lambda ctx,this: ctx.adj.claim.police_report== this.id)],
        then=add_police_report_to_adj_rhs)

# #########################################################################
# Rule order: 1
# Set of rules that adds history to the adj objects and cleans up
# ########################################################################## 

@ruledef
def add_history_to_adj():
    '''
    Add all history records to the adj so that other rulesets can get the history information from the adj object itself
    '''
    def add_history_to_adj_rhs(ctx):
        ctx.adj.history = ctx.hist.collection
        update(ctx, ctx.adj)
    return Rule(order=1, run_once=True,
        when=(Fact(of_type=Adj, var='adj'),
                Collection(group='history-collector', var='hist', matches=lambda ctx,this: ctx.adj == this.adj)),
        then=add_history_to_adj_rhs)

# #########################################################################
# Rule order: 2
# Prepares for the next ruleset to run by cleaning up uneeded objects,
# adding new collectors, etc.
# ########################################################################## 
@ruledef 
def del_history_collector():
    '''
    The work of the history collector is done 
    '''
    return Rule(order=2,
            when=Collection(group='history-collector', var='hist'),
            then=lambda ctx: delete(ctx, ctx.hist))

@ruledef
def create_action_collector():
    '''
    Create a collection that collects all the actions for a claim being adjudicated
    '''
    return Rule(order=2,
        when=Fact(of_type=Adj, var='adj'),
        then=lambda ctx: insert(ctx, 
                                Collector(of_type=Action, group='action-collector', adj=ctx.adj, 
                                    filter=lambda this,action: this.adj.claim.id == action.claim_id)))
@ruledef
def create_event_listener():
    return Rule(order=2, run_once=True,
        when=Fact(of_type=Anchor),
                then=lambda ctx: insert(ctx, EventFact(on_types=[Adj,Action])))