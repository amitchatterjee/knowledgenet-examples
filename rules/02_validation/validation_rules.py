import uuid
from knowledgenet.scanner import ruledef
from knowledgenet.rule import Rule, Fact, Evaluator, Collection
from knowledgenet.controls import insert, update, delete
from knowledgenet.helper import assign, factset, node
from knowledgenet.ftypes import Eval

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

@ruledef
def no_driver():
    return Rule(when=Fact(of_type=Adj, var='adj', 
                    matches=lambda ctx,this: not this.driver),
                    then=lambda ctx: insert(ctx, Action(str(uuid.uuid4()), 'NODRV', ctx.adj.claim.id, 
                                            'd', 'no driver', 0.00, rank=998)))

@ruledef
def bypass_rules_with_validation_error():
    def bypass_rules_with_validation_error_rhs(ctx):
        ctx.adj.bypass.add('all')
    return Rule(order=1,
        when=[
            Fact(of_type=Adj, var='adj'),
            Collection(group='action-collector', 
                    matches=[lambda ctx,this: this.adj == ctx.adj,  
                            lambda ctx,this: len(this.collection) > 0])], 
        then=bypass_rules_with_validation_error_rhs)
