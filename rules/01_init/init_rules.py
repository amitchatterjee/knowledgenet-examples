from knowledgenet.scanner import ruledef
from knowledgenet.rule import Rule, Fact
from knowledgenet.controls import insert, update, delete
from knowledgenet.helper import assign
from knowledgenet.collector import Collector

from autoins.entities import Action, Adj, Claim, Driver, PoliceReport, Policy

@ruledef
def create_adj():    
    return Rule(when=Fact(of_type=Claim, matches=lambda ctx,this: this.status == 'pending' 
                       and assign(ctx, claim=this)),
        then=lambda ctx: insert(ctx, Adj(ctx.claim)))

@ruledef
def add_policy_to_adj():
    def add_policy_to_adj_claim(ctx):
        ctx.adj.policy = ctx.policy
        update(ctx, ctx.adj)
    return Rule(run_once=True,
        when=[Fact(of_type=Adj, matches=lambda ctx,this: assign(ctx, adj=this)),
              Fact(of_type=Policy, matches=lambda ctx,this: ctx.adj.claim.policy_id == this.id 
                        and assign(ctx, policy=this))],
        then=add_policy_to_adj_claim)

@ruledef
def add_driver_to_adj():
    def add_driver_to_adj(ctx):
        ctx.adj.driver = ctx.driver
        update(ctx, ctx.adj)
    return Rule(run_once=True,
        when=[Fact(of_type=Adj, matches=lambda ctx,this: assign(ctx, adj=this)),
              Fact(of_type=Driver, matches=lambda ctx,this: ctx.adj.claim.driver_id == this.id 
                        and assign(ctx, driver=this))],
        then=add_driver_to_adj)

@ruledef
def add_police_report_to_adj():
    def add_police_report_to_adj(ctx):
        ctx.adj.police_report = ctx.police_report
        update(ctx, ctx.adj)
    return Rule(run_once=True,
        when=[Fact(of_type=Adj, matches=lambda ctx,this: assign(ctx, adj=this)),
              Fact(of_type=PoliceReport, matches=lambda ctx,this: ctx.adj.claim.police_report== this.id 
                        and assign(ctx, police_report=this))],
        then=add_police_report_to_adj)


@ruledef
def create_history_collector():
    return Rule(order=1,
        when=Fact(of_type=Adj, matches=lambda ctx,this: assign(ctx, adj=this)),
        then=lambda ctx: insert(ctx, 
                                Collector(of_type=Claim, group='history-collector', adj=ctx.adj,
                                    value=lambda claim: claim.paid_amount,
                                    filter=lambda this,claim: claim.status == 'approved'
                                        and this.adj.policy
                                        and this.adj.policy.id == claim.policy_id
                                        and this.adj.claim.accident_date.year == claim.accident_date.year)))

@ruledef
def create_action_collector():
    return Rule(order=1,
        when=Fact(of_type=Adj, matches=lambda ctx,this: assign(ctx, adj=this)),
        then=lambda ctx: insert(ctx, 
                                Collector(of_type=Action, group='action-collector', adj=ctx.adj, 
                                    filter=lambda this,action: this.adj.claim.id == action.claim_id)))

