import uuid
from knowledgenet.scanner import ruledef
from knowledgenet.rule import Rule, Fact, Event, Collection
from knowledgenet.controls import insert, update, delete
from knowledgenet.helper import assign, factset, node

from autoins.entities import Adj, Action
from autoins.util import record_action_event

@ruledef
def create_action_event_handler():
    return Rule(when=Event(group='onAction', var='event'),
                then=lambda ctx: record_action_event(ctx.event))

@ruledef
def no_policy():
    return Rule(run_once=True, when=Fact(of_type=Adj, var='adj',
                    matches=lambda ctx,this: not this.policy),
                    then=lambda ctx: insert(ctx, Action(str(uuid.uuid4()), 'NOPLY', ctx.adj.claim.id, 
                                            'd', 'no policy found', 0.00, rank=1000)))

@ruledef
def no_incidence_report():
    return Rule(run_once=True, when=Fact(of_type=Adj, var='adj', 
                    matches=lambda ctx,this: not this.incidence_report),
                    then=lambda ctx: insert(ctx, Action(str(uuid.uuid4()), 'NOPLR', ctx.adj.claim.id, 
                                            'd', 'no incidence report', 0.00, rank=999)))

@ruledef
def no_driver():
    return Rule(run_once=True, when=Fact(of_type=Adj, var='adj', 
                    matches=lambda ctx,this: not this.driver),
                    then=lambda ctx: insert(ctx, Action(str(uuid.uuid4()), 'NODRV', ctx.adj.claim.id, 
                                            'd', 'no driver', 0.00, rank=998)))

@ruledef
def bypass_rules_with_validation_error():
    def bypass_rules_with_validation_error_rhs(ctx):
        ctx.adj.bypass.add('all')
        update(ctx, ctx.adj)
    return Rule(order=1, retrigger_on_update=False,
        when=[
            Fact(of_type=Adj, var='adj'),
            Collection(group='action-collector', 
                    matches=[lambda ctx,this: this.adj == ctx.adj,  
                            lambda ctx,this: len(this.collection) > 0])], 
        then=bypass_rules_with_validation_error_rhs)
