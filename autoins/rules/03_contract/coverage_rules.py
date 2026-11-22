from knowledgenet.decorator import ruledef
from knowledgenet.rule import Rule, Fact
from knowledgenet.controls import insert
from knowledgenet.ftypes import Row

from autoins.entities import Request
from autoins.util import create_action, execute, rule_config

@ruledef
def insufficient_liability_coverage():
    '''
    Deny when the policy's liability coverage falls below the statutory minimum for the
    driver's licensing state, as given by a 'state_min_liability' Table/Row (see
    state_min_liability.csv). Each state is its own independent Row fact rather than one
    opaque lookup object - contrast with BlueBook in rules/05_finalization/pricing_rules.py.
    '''
    return Rule(when=[Fact(named='contract-ruleset', var='ruleset_context'),
                      Fact(of_type=Request, var='request',
                            matches=[
                                lambda ctx,this: execute(ctx,ctx.ruleset_context,this),
                                lambda ctx,this: this.group is not None and this.driver is not None]),
                      Fact(of_type=Row, var='min_coverage_row',
                            matches=lambda ctx,this:
                                this.table.name == 'state_min_liability'
                                and this.columns[0] == ctx.request.driver.license_state
                                and ctx.request.group.liability_coverage < this.columns[1])],
                then=lambda ctx: insert(ctx, create_action(ctx, ctx.ruleset_context, ctx.request)))
