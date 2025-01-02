import uuid
from knowledgenet.scanner import ruledef
from knowledgenet.rule import Rule, Condition
from knowledgenet.controls import insert, update, delete
from knowledgenet.helper import assign

from autoins.entities import Adj, Action

ruleset = '002-validation'

@ruledef
def no_policy():
    return Rule(id='no-policy', repository='autoclaims', ruleset=ruleset,
        when=Condition(of_type=Adj, matches=lambda ctx,this: not this.policy 
                       and assign(ctx, adj=this)),
        then=lambda ctx: insert(ctx, Action(str(uuid.uuid4()), 'NOPLY', ctx.adj.claim.id, 
                                            'd', 'no policy found', 0.00, rank=1000)))

@ruledef
def no_police_report():
    return Rule(id='no-police-report', repository='autoclaims', ruleset=ruleset,
        when=Condition(of_type=Adj, matches=lambda ctx,this: not this.police_report 
                       and assign(ctx, adj=this)),
        then=lambda ctx: insert(ctx, Action(str(uuid.uuid4()), 'NOPLR', ctx.adj.claim.id, 
                                            'd', 'no police report', 0.00, rank=999)))
