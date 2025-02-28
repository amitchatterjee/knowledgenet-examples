import uuid
from knowledgenet.scanner import ruledef
from knowledgenet.rule import Rule, Collection, Event
from knowledgenet.controls import insert, update
from knowledgenet.helper import assign

from autoins.entities import Action, ExecutionContext
from autoins.util import record_action_event

@ruledef
def pay_on_no_action():
    '''
    When a claim has no actions associated with it, pay the claim.
    '''
    return Rule(run_once=True,
        when=Collection(group='action-collector', 
                    matches=[lambda ctx,this: not len(this.collection),  
                            lambda ctx,this: assign(ctx, exec_context=this.exec_context)]),
        then=lambda ctx: insert(ctx, Action(str(uuid.uuid4()), 'PAYCL', 
                                            ctx.exec_context.claim.id, 'pay', 'pay', 
                                            ctx.exec_context.incidence_report.liability_percent, inactive=False)))

@ruledef
def select_action():
    '''
    select the best action and make it active
        #1. sort actions by rank (desc) and pay_percent (asc)
        #2. pick the first action and make inactive = False
    '''
    def select_action_rhs(ctx):
        actions = list(ctx.actions)
        actions.sort(key=lambda a: (-a.rank, a.pay_percent))
        actions[0].inactive = False
        update(ctx, actions[0])
    return Rule(run_once=True, order=1,
        when=Collection(group='action-collector', 
                    matches=lambda ctx,this: assign(ctx, actions=this.collection)),
        then=select_action_rhs)

@ruledef
def create_action_event_handler():
    return Rule(order=1, when=Event(group='onAction', var='event'),
                then=lambda ctx: record_action_event(ctx, ctx.event))
