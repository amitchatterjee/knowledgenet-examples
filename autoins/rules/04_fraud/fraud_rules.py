from knowledgenet.decorator import ruledef
from knowledgenet.rule import Rule, Fact, Event
from knowledgenet.controls import insert

from autoins.entities import Request
from autoins.util import record_action_event, create_action, execute

# AI-generated rule: Create a @ruledef function that inserts an Action when the vin on the Request.claim object does not match the vin on the Request.incidence_report object
@ruledef
def vin_mismatch_claim_incidence_report():
    return Rule(when=[Fact(named='fraud-ruleset', var='ruleset_context'),
                      Fact(of_type=Request, var='request',
                            matches=[lambda ctx,this: execute(ctx,ctx.ruleset_context,this),
                                    lambda ctx,this: this.claim.vin != this.incidence_report.vin])],
                then=lambda ctx: insert(ctx, create_action(ctx, ctx.ruleset_context, ctx.request)))

# AI-generated rule: Create a @ruledef function that inserts an Action when the vin on the Request.claim object does not match the vin on any elements of the Request.estimates object
@ruledef
def vin_mismatch_claim_estimates():
    return Rule(when=[Fact(named='fraud-ruleset', var='ruleset_context'),
                      Fact(of_type=Request, var='request',
                            matches=[lambda ctx,this: execute(ctx,ctx.ruleset_context,this),
                                lambda ctx,this: any(est.vin != this.claim.vin for est in this.estimates)])],
                then=lambda ctx: insert(ctx, create_action(ctx, ctx.ruleset_context, ctx.request)))

@ruledef
def create_action_event_handler():
    return Rule(order=1, when=Event(group='onAction', var='event'),
                then=lambda ctx: record_action_event(ctx, ctx.event))