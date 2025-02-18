import logging
import os
import uuid
import pandas as pd

from knowledgenet.helper import session

from autoins.entities import Action

def subfiles(parent):
    return [name for name in os.listdir(parent) if os.path.isfile(os.path.join(parent, name))]

def bypass(ctx, claim_context):
    return 'all' in claim_context.bypass or session(ctx).ruleset.id.split('_')[0] in claim_context.bypass

def execute(ctx, rs_context, claim_context):
    rule_context = rule_config(ctx, rs_context)
    return rs_context.config['enabled'] and rule_context['enabled'] and not bypass(ctx, claim_context)

def create_action(ctx, rs_context, claim_context):
    rule_context = rule_config(ctx, rs_context)
    return Action(str(uuid.uuid4()), 
            rule_context['reason'], 
            claim_context.claim.id,
            rule_context['action'],
            rule_context['explain'], 
            rule_context['percent'], 
            rank=rule_context['rank'])

def rule_config(ctx, rs_context):
    rule_id=ctx._node.rule.id
    return rs_context.config['rules'][rule_id]

def record_action_event(ctx, event):
    logging.info("Action event on %s: added: %s, updated: %s, deleted: %s",
                    session(ctx).ruleset,
                    event.added, event.updated, event.deleted)
    event.reset()

def load_from_csv(facts, of_type, file_path, converters=None):
    df = pd.read_csv(file_path, converters=converters, comment='#').to_dict(orient='records')
    for row in df:
        fact = of_type(**row)
        facts.add(fact)

def to_bool(txt):
    if txt.lower() in ['yes', 'true']:
        return True
    elif txt.lower() in ['no', 'false']:
        return False
    else:
        raise ValueError(f"Cannot convert {txt} to boolean")


def subdirs(parent):
    return [os.path.join(parent, name) for name in os.listdir(parent) if os.path.isdir(os.path.join(parent, name))]