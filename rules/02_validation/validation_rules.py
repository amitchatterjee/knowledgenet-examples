import uuid
from knowledgenet.scanner import ruledef
from knowledgenet.rule import Rule, Fact
from knowledgenet.controls import insert, update, delete
from knowledgenet.helper import assign

from autoins.entities import Adj, Action

@ruledef
def no_policy():
    return Rule(when=Fact(of_type=Adj, var='adj', 
                    matches=lambda ctx,this: not this.policy),
                    then=lambda ctx: insert(ctx, Action(str(uuid.uuid4()), 'NOPLY', ctx.adj.claim.id, 
                                            'd', 'no policy found', 0.00, rank=1000)))

@ruledef
def no_police_report():
    return Rule(when=Fact(of_type=Adj, var='adj', 
                    matches=lambda ctx,this: not this.police_report),
                    then=lambda ctx: insert(ctx, Action(str(uuid.uuid4()), 'NOPLR', ctx.adj.claim.id, 
                                            'd', 'no police report', 0.00, rank=999)))
