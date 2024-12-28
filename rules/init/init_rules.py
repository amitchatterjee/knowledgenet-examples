from knowledgenet.scanner import ruledef
from knowledgenet.rule import Rule, Condition
from knowledgenet.controls import insert, update, delete
from knowledgenet.helper import assign
from knowledgenet.ftypes import Collector

from autoins.entities import Action, Adj, Claim, Driver, PoliceReport, Policy
ruleset = '001-init'
@ruledef
def create_adj():    
    return Rule(id='create-adj', repository='autoclaims', ruleset=ruleset,
        when=Condition(of_type=Claim, matches=lambda ctx,this: this.status == 'pending' 
                       and assign(ctx, claim=this)),
        then=lambda ctx: insert(ctx, Adj(ctx.claim)))

@ruledef
def add_policy_to_adj():
    def add_policy_to_adj_claim(ctx):
        ctx.adj.policy = ctx.policy
        update(ctx, ctx.adj)
    return Rule(id='add-policy-to-adj', repository='autoclaims', ruleset=ruleset, 
            run_once=True,
        when=[Condition(of_type=Adj, matches=lambda ctx,this: assign(ctx, adj=this)),
              Condition(of_type=Policy, matches=lambda ctx,this: ctx.adj.claim.policy_id == this.id 
                        and assign(ctx, policy=this))],
        then=add_policy_to_adj_claim)

@ruledef
def add_driver_to_adj():
    def add_driver_to_adj(ctx):
        ctx.adj.driver = ctx.driver
        update(ctx, ctx.adj)
    return Rule(id='add-driver-to-adj', repository='autoclaims', ruleset=ruleset,
            run_once=True,
        when=[Condition(of_type=Adj, matches=lambda ctx,this: assign(ctx, adj=this)),
              Condition(of_type=Driver, matches=lambda ctx,this: ctx.adj.claim.driver_id == this.id 
                        and assign(ctx, driver=this))],
        then=add_driver_to_adj)

@ruledef
def add_police_report_to_adj():
    def add_police_report_to_adj(ctx):
        ctx.adj.police_report = ctx.police_report
        update(ctx, ctx.adj)
    return Rule(id='add-police_report-to-adj', repository='autoclaims', ruleset=ruleset,
            run_once=True,
        when=[Condition(of_type=Adj, matches=lambda ctx,this: assign(ctx, adj=this)),
              Condition(of_type=PoliceReport, matches=lambda ctx,this: ctx.adj.claim.police_report== this.id 
                        and assign(ctx, police_report=this))],
        then=add_police_report_to_adj)

@ruledef
def create_action_collector():
    return Rule(id='create-action-collector', repository='autoclaims', ruleset=ruleset,
                run_once=True, order=1,
        when=Condition(of_type=Adj, matches=lambda ctx,this: assign(ctx, adj=this)),
        then=lambda ctx: insert(ctx, Collector(of_type=Action, group='action-collector', 
                                    adj=ctx.adj, 
                                    filter=lambda this,action: this.adj.claim.id == action.claim_id)))

