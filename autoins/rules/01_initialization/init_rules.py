from knowledgenet.decorator import ruledef
from knowledgenet.rule import Rule, Fact, Collection
from knowledgenet.controls import insert, update, delete
from knowledgenet.container import Collector

from autoins.entities import Request, Automobile, Claim, Driver, Estimate, Group, IncidenceReport, Policy, Action
from autoins.util import echo

@ruledef
def create_action_collector():
    '''
    Create a collection that collects all the actions for each claim being processed
    '''
    return Rule(order=4,
        when=Fact(of_type=Request, var='request'),
        then=lambda ctx: insert(ctx, 
                                Collector(of_type=Action, group='action-collector', 
                                        request=ctx.request, 
                                        filter=lambda this,action: this.request.claim.id == action.claim_id)))