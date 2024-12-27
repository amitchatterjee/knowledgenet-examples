from knowledgenet.scanner import ruledef
from knowledgenet.rule import Rule, Condition
from knowledgenet.controls import insert, update, delete
from knowledgenet.helper import assign
from knowledgenet.ftypes import Collector

from autoins.entities import Action, Adj, Claim, Driver, Policy

@ruledef
def create_adj_claims():
    return Rule(id='create-adj-claims', repository='autoclaims', ruleset='001-init',
        when=Condition(of_type=Claim, matches=lambda ctx,this: this.status == 'pending' 
                       and assign(ctx, claim=this)),
        then=lambda ctx: insert(ctx, Adj(ctx.claim)))

@ruledef
def add_policy_to_adj_claim():
    def add_policy_to_adj_claim(ctx):
        ctx.aclaim.policy = ctx.policy
        update(ctx, ctx.aclaim)
    return Rule(id='add-policy-to-adj-claim', repository='autoclaims', ruleset='001-init', 
            run_once=True,
        when=[Condition(of_type=Adj, matches=lambda ctx,this: assign(ctx, aclaim=this)),
              Condition(of_type=Policy, matches=lambda ctx,this: ctx.aclaim.claim.policy_id == this.id 
                        and assign(ctx, policy=this))],
        then=add_policy_to_adj_claim)

@ruledef
def add_driver_to_adj_claim():
    def add_driver_to_adj_claim(ctx):
        ctx.aclaim.driver = ctx.driver
        update(ctx, ctx.aclaim)
    return Rule(id='add-driver-to-adj-claim', repository='autoclaims', ruleset='001-init', 
            run_once=True,
        when=[Condition(of_type=Adj, matches=lambda ctx,this: assign(ctx, aclaim=this)),
              Condition(of_type=Driver, matches=lambda ctx,this: ctx.aclaim.claim.driver_id == this.id 
                        and assign(ctx, driver=this))],
        then=add_driver_to_adj_claim)

@ruledef
def create_action_collector():
    return Rule(id='create-action-collector', repository='autoclaims', ruleset='001-init', 
                run_once=True, order=1,
        when=Condition(of_type=Adj, matches=lambda ctx,this: assign(ctx, adj=this)),
        then=lambda ctx: insert(ctx, Collector(of_type=Action, group='action-collector', 
                                    adj=ctx.adj, 
                                    filter=lambda this,obj: this.adj.claim.id == obj.claim_id)))


