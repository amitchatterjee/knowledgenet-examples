from knowledgenet.decorator import ruledef
from knowledgenet.rule import Rule, Fact, Event, Collection
from knowledgenet.controls import insert, update
from knowledgenet.helper import assign

from autoins.entities import Request
from autoins.util import create_action, record_action_event

@ruledef
def no_policy():
    return Rule(run_once=True, 
                when=[Fact(named='validation-ruleset', var='ruleset_context'),
                      Fact(of_type=Request, var='exec_context',
                        matches=lambda ctx,this: not this.policy)],
                    then=lambda ctx: insert(ctx, create_action(ctx, ctx.ruleset_context, ctx.exec_context)))

@ruledef
def no_incidence_report():
    return Rule(run_once=True, 
                when=[Fact(named='validation-ruleset', var='ruleset_context'),
                    Fact(of_type=Request, var='exec_context', 
                    matches=lambda ctx,this: not this.incidence_report)],
                    then=lambda ctx: insert(ctx, create_action(ctx, ctx.ruleset_context, ctx.exec_context)))

@ruledef
def no_driver():
    return Rule(run_once=True, 
                when=[Fact(named='validation-ruleset', var='ruleset_context'),
                    Fact(of_type=Request, var='exec_context', 
                    matches=lambda ctx,this: not this.driver)],
                then=lambda ctx: insert(ctx, create_action(ctx, ctx.ruleset_context, ctx.exec_context)))

@ruledef
def no_automobile():
    return Rule(run_once=True, 
                when=[Fact(named='validation-ruleset', var='ruleset_context'),
                      Fact(of_type=Request, var='exec_context', 
                    matches=lambda ctx,this: not this.automobile)],
                then=lambda ctx: insert(ctx, create_action(ctx, ctx.ruleset_context, ctx.exec_context)))

@ruledef 
def insufficient_estimates():
    '''
    For non-approved vendors, at least three estimates are required, for approved vendors, at least one estimate is required
    '''
    return Rule(run_once=True, 
                when=[Fact(named='validation-ruleset', var='ruleset_context'),
                      Fact(of_type=Request, var='exec_context', 
                        matches=[lambda ctx,this: len(this.estimates) < 3,
                                lambda ctx,this: len([e for e in this.estimates if e.certified]) == 0])],
                then=lambda ctx: insert(ctx, create_action(ctx, ctx.ruleset_context, ctx.exec_context)))

@ruledef
def bypass_rules_with_validation_error():
    def bypass_rules_with_validation_error_rhs(ctx):
        ctx.exec_context.bypass.add('all')
        update(ctx, ctx.exec_context)
    return Rule(order=1, retrigger_on_update=False,
        when=[
            Fact(of_type=Request, var='exec_context'),
            Collection(group='action-collector', 
                    matches=[lambda ctx,this: this.exec_context == ctx.exec_context,  
                            lambda ctx,this: this.size() > 0])], 
        then=bypass_rules_with_validation_error_rhs)

@ruledef
def create_action_event_handler():
    return Rule(order=1,
            when=Event(group='onAction', var='event'),
            then=lambda ctx: record_action_event(ctx, ctx.event))
