import uuid
from knowledgenet.scanner import ruledef
from knowledgenet.rule import Rule, Fact, Event
from knowledgenet.controls import insert

from autoins.entities import Adj, Action
from autoins.util import bypass, record_action_event

# AI-generated rule: Create a @ruledef function that inserts an Action when the vin on the Adj.claim object does not match the vin on the Adj.incidence_report object
@ruledef
def vin_mismatch_claim_incidence_report():
    return Rule(when=Fact(of_type=Adj, var='adj',
                    matches=[lambda ctx,this: not bypass(ctx,this),
                            lambda ctx,this: this.claim.vin != this.incidence_report.vin]),
                then=lambda ctx: insert(ctx, Action(str(uuid.uuid4()), 'VINCI', ctx.adj.claim.id, 
                                    'deny', 'claim/incidence-report vin mismatch', 0.00)))

# AI-generated rule: Create a @ruledef function that inserts an Action when the vin on the Adj.claim object does not match the vin on any elements of the Adj.estimates object
@ruledef
def vin_mismatch_claim_estimates():
    return Rule(when=Fact(of_type=Adj, var='adj',
                    matches=[lambda ctx,this: not bypass(ctx,this),
                            lambda ctx,this: any(est.vin != this.claim.vin for est in this.estimates)]),
                then=lambda ctx: insert(ctx, Action(str(uuid.uuid4()), 'VINCE', ctx.adj.claim.id, 
                                    'deny', 'claim/estimates vin mismatch', 0.00)))

@ruledef
def create_action_event_handler():
    return Rule(order=1, when=Event(group='onAction', var='event'),
                then=lambda ctx: record_action_event(ctx, ctx.event))