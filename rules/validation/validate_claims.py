from knowledgenet.scanner import ruledef
from knowledgenet.rule import Rule, Condition
from knowledgenet.controls import insert
from knowledgenet.helper import assign

from autoins.entities import Policy

@ruledef
def rm_inactive_policies():
    return Rule(id='rm-inactive-pols', repository='autoclaims', ruleset='001-validation',
        when=Condition(of_type=Policy, matches_exp=lambda ctx, this: assign(ctx, c1=this)),
        then=lambda ctx: print('hello'))
