import uuid
from knowledgenet.scanner import ruledef
from knowledgenet.rule import Rule, Fact, Event
from knowledgenet.controls import insert

from autoins.entities import ExecutionContext
from autoins.util import create_action, execute, record_action_event, rule_config

@ruledef
def inactive_policy():
    return Rule(when=[Fact(named='contract-ruleset', var='ruleset_context'),
                      Fact(of_type=ExecutionContext, var='exec_context', 
                            matches=[lambda ctx,this: execute(ctx,ctx.ruleset_context,this),
                                lambda ctx,this: 
                                    not this.policy.start_date <= this.incidence_report.accident_date <= this.policy.end_date])],
        then=lambda ctx: insert(ctx, create_action(ctx, ctx.ruleset_context, ctx.exec_context)))

@ruledef
def late_filing():
    return Rule(when=[Fact(named='contract-ruleset', var='ruleset_context'),
                      Fact(of_type=ExecutionContext, var='exec_context',
                            matches=[lambda ctx,this: execute(ctx,ctx.ruleset_context,this),
                                    lambda ctx,this: (this.claim.filing_date - this.incidence_report.accident_date).days > rule_config(ctx, ctx.ruleset_context, ctx.exec_context)['within']])],
                then=lambda ctx: insert(ctx, create_action(ctx, ctx.ruleset_context, ctx.exec_context)))

# AI-generated rule: Create a rule function that inserts an Action object when and ExecutionContext.claim of type, collision, has a vin that does not match the vins in the ExecutionContext.policy.automobiles object 
@ruledef
def vin_mismatch():
    return Rule(when=[Fact(named='contract-ruleset', var='ruleset_context'),
                      Fact(of_type=ExecutionContext, var='exec_context',
                            matches=[lambda ctx,this: execute(ctx,ctx.ruleset_context,this),
                                    lambda ctx,this: this.claim.type == 'collision',
                                    lambda ctx,this: this.claim.vin not in [auto for auto in this.policy.automobiles]])],
                then=lambda ctx: insert(ctx,create_action(ctx, ctx.ruleset_context, ctx.exec_context)))
@ruledef
def create_action_event_handler():
    return Rule(order=1, when=Event(group='onAction', var='event'),
                then=lambda ctx: record_action_event(ctx, ctx.event))