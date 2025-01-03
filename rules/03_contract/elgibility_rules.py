import uuid
from knowledgenet.scanner import ruledef
from knowledgenet.rule import Rule, Fact
from knowledgenet.controls import insert, update, delete
from knowledgenet.helper import assign

from autoins.entities import Adj, Action

@ruledef
def inactive_policy():
    return Rule(when=Fact(of_type=Adj, var='adj', 
                        matches=lambda ctx,this: this.policy
                            and not this.policy.start_date <= this.claim.accident_date <= this.policy.end_date),
        then=lambda ctx: insert(ctx, Action(str(uuid.uuid4()), 'NOACT', ctx.adj.claim.id, 
                                            'd', 'policy inactive', 0.00)))
