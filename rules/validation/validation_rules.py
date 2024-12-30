import uuid
from knowledgenet.scanner import ruledef
from knowledgenet.rule import Rule, Condition
from knowledgenet.controls import insert, update, delete
from knowledgenet.helper import assign

from autoins.entities import Adj, Action

@ruledef
def no_police_report():
    return Rule(id='no-police-report', repository='autoclaims', ruleset='002-validation',
        when=Condition(of_type=Adj, matches=lambda ctx,this: not this.police_report 
                       and assign(ctx, adj=this)),
        then=lambda ctx: insert(ctx, Action(str(uuid.uuid4()), 'NOPLR', ctx.adj.claim.id, 
                                            'd', 'no police report', 0.00)))

