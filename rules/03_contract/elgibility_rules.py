import logging
import uuid
from knowledgenet.scanner import ruledef
from knowledgenet.rule import Rule, Fact, Event
from knowledgenet.controls import insert, update, delete
from knowledgenet.helper import assign

from autoins.entities import Adj, Action
from autoins.util import record_action_event

def bypass(ctx, this):
    return 'all' in this.bypass or 'contract' in this.bypass

@ruledef
def inactive_policy():
    return Rule(when=Fact(of_type=Adj, var='adj', 
                    matches=[lambda ctx,this: not bypass(ctx,this),
                        lambda ctx,this: 
                            not this.policy.start_date <= this.claim.accident_date <= this.policy.end_date]),
        then=lambda ctx: insert(ctx, Action(str(uuid.uuid4()), 'NOACT', ctx.adj.claim.id, 
                                            'd', 'policy inactive', 0.00)))

@ruledef
def create_action_event_handler():
    return Rule(order=1, when=Event(group='onAction', var='event'),
                then=lambda ctx: record_action_event(ctx, ctx.event))