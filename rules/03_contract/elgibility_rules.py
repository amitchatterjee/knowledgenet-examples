import uuid
from knowledgenet.scanner import ruledef
from knowledgenet.rule import Rule, Fact, Event
from knowledgenet.controls import insert

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

# AI-generated rule: Create a rule function that inserts an Action object when and Adj.claim of type, collision, has a vin that does not match the vins in the Adj.policy.automobiles object 
@ruledef
def vin_mismatch():
    return Rule(when=Fact(of_type=Adj, var='adj',
                    matches=[lambda ctx, this: not bypass(ctx, this),
                             lambda ctx, this: this.claim.type == 'collision',
                             lambda ctx, this: this.claim.vin not in [auto for auto in this.policy.automobiles]]),
                then=lambda ctx: insert(ctx, Action(str(uuid.uuid4()), 'AUTMIS', ctx.adj.claim.id, 
                                                    'd', 'Automobile not registred in policy', 0.00)))
@ruledef
def create_action_event_handler():
    return Rule(order=1, when=Event(group='onAction', var='event'),
                then=lambda ctx: record_action_event(ctx, ctx.event))