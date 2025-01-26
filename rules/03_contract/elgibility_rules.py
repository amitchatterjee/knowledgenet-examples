import logging
import uuid
from knowledgenet.scanner import ruledef
from knowledgenet.rule import Rule, Fact, Event
from knowledgenet.controls import insert
from knowledgenet.helper import session

from autoins.entities import Adj, Action
from autoins.util import bypass, record_action_event

@ruledef
def inactive_policy():
    return Rule(when=Fact(of_type=Adj, var='adj', 
                    matches=[lambda ctx,this: not bypass(ctx,this),
                        lambda ctx,this: 
                            not this.policy.start_date <= this.incidence_report.accident_date <= this.policy.end_date]),
        then=lambda ctx: insert(ctx, Action(str(uuid.uuid4()), 'NOACT', ctx.adj.claim.id, 
                                            'd', 'policy inactive', 0.00)))

@ruledef
def late_filing():
    return Rule(when=Fact(of_type=Adj, var='adj',
                    matches=[lambda ctx,this: not bypass(ctx,this),
                         lambda ctx,this: (this.claim.filing_date - this.incidence_report.accident_date).days > 90]),
                then=lambda ctx: insert(ctx, Action(str(uuid.uuid4()), 'LATFL', ctx.adj.claim.id, 
                                                    'd', 'late filing', 0.00)))

# AI-genrated rule: Create a @ruledef function like above that inserts an Action when the vin on the Adj.claim object does not match the vin on the Adj.incidence_report object
@ruledef
def vin_mismatch():
    return Rule(when=Fact(of_type=Adj, var='adj',
                    matches=[lambda ctx,this: not bypass(ctx,this),
                            lambda ctx,this: this.claim.vin != this.incidence_report.vin]),
                then=lambda ctx: insert(ctx, Action(str(uuid.uuid4()), 'VINMIS', ctx.adj.claim.id, 
                                    'd', 'claim/incidence-report vin mismatch', 0.00)))
                    
@ruledef
def create_action_event_handler():
    return Rule(order=1, when=Event(group='onAction', var='event'),
                then=lambda ctx: record_action_event(ctx, ctx.event))