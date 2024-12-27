import uuid
from knowledgenet.scanner import ruledef
from knowledgenet.rule import Rule, Condition
from knowledgenet.controls import insert, update, delete
from knowledgenet.helper import assign

from autoins.entities import AdjClaim, Action

@ruledef
def no_police_report():
    return Rule(id='no-police-report', repository='autoclaims', ruleset='002-audit',
        when=Condition(of_type=AdjClaim, matches_exp=lambda ctx,this: not this.claim.police_report 
                       and assign(ctx, adjclaim=this)),
        then=lambda ctx: insert(ctx, Action(str(uuid.uuid4()), ctx.adjclaim.claim.id, 'd', 'no-police-report', 0.00)))

