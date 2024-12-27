from knowledgenet.scanner import ruledef
from knowledgenet.rule import Rule, Condition
from knowledgenet.controls import insert, update, delete
from knowledgenet.helper import assign
from knowledgenet.ftypes import Collector

from autoins.entities import AdjClaim, Claim, Driver, Policy

@ruledef
def create_adj_claims():
    return Rule(id='create-adj-claims', repository='autoclaims', ruleset='001-init',
        when=Condition(of_type=Claim, matches_exp=lambda ctx,this: this.status == 'pending' 
                       and assign(ctx, claim=this)),
        then=lambda ctx: insert(ctx, AdjClaim(ctx.claim)))

@ruledef
def add_policy_to_adj_claim():
    def add_policy_to_adj_claim(ctx):
        ctx.aclaim.policy = ctx.policy
        update(ctx, ctx.aclaim)
    return Rule(id='add-policy-to-adj-claim', repository='autoclaims', ruleset='001-init', 
            run_once=True,
        when=[Condition(of_type=AdjClaim, matches_exp=lambda ctx,this: assign(ctx, aclaim=this)),
              Condition(of_type=Policy, matches_exp=lambda ctx,this: ctx.aclaim.claim.policy_id == this.id 
                        and assign(ctx, policy=this))],
        then=add_policy_to_adj_claim)

@ruledef
def add_driver_to_adj_claim():
    def add_driver_to_adj_claim(ctx):
        ctx.aclaim.driver = ctx.driver
        update(ctx, ctx.aclaim)
    return Rule(id='add-driver-to-adj-claim', repository='autoclaims', ruleset='001-init', 
            run_once=True,
        when=[Condition(of_type=AdjClaim, matches_exp=lambda ctx,this: assign(ctx, aclaim=this)),
              Condition(of_type=Driver, matches_exp=lambda ctx,this: ctx.aclaim.claim.driver_id == this.id 
                        and assign(ctx, driver=this))],
        then=add_driver_to_adj_claim)

@ruledef
def create_action_collector():
    return Rule(id='create-action-collector', repository='autoclaims', ruleset='001-init', run_once=True,
        when=Condition(of_type=AdjClaim, matches_exp=lambda ctx,this: not this.claim.police_report 
                       and assign(ctx, adjclaim=this)),
        then=lambda ctx: insert(ctx, Collector(of_type=AdjClaim, group='action-collector', 
                                    adjclaim=ctx.adjclaim, 
                                    filter=lambda this,obj: this.adjclaim.claim.id == obj.claim.id)))

@ruledef
def del_unneeded_claim_facts():
    return Rule(id='del-unneeded-claim-facts', repository='autoclaims', ruleset='001-init', order=100,
        when=Condition(of_type=Claim, matches_exp=lambda ctx, this: assign(ctx, claim=this)),
        then=lambda ctx: delete(ctx, ctx.claim))

@ruledef
def del_unneeded_policy_facts():
    return Rule(id='del-unneeded-policy-facts', repository='autoclaims', ruleset='001-init', order=100,
        when=Condition(of_type=Policy, matches_exp=lambda ctx, this: assign(ctx, policy=this)),
        then=lambda ctx: delete(ctx, ctx.policy))

@ruledef
def del_unneeded_driver_facts():
    return Rule(id='del-unneeded-driver-facts', repository='autoclaims', ruleset='001-init', order=100,
        when=Condition(of_type=Driver, matches_exp=lambda ctx, this: assign(ctx, driver=this)),
        then=lambda ctx: delete(ctx, ctx.driver))
