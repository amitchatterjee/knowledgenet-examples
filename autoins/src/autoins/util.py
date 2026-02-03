from datetime import datetime
import logging
import os
import uuid

from knowledgenet.helper import session

from autoins.entities import Action

def echo(ctx, message):
    print(message)
    return True

def subfiles(parent):
    return [name for name in os.listdir(parent) if os.path.isfile(os.path.join(parent, name))]

def bypass(ctx, request):
    return 'all' in request.bypass or session(ctx).ruleset.id.split('_')[0] in request.bypass

def execute(ctx, rs_context, request):
    rule_context = rule_config(ctx, rs_context, request)
    group_id = request.group.id if request.group else "default"
    rs_enabled = rs_context.config.get(group_id, rs_context.config['default'])['enabled']
    return rs_enabled and rule_context['enabled'] and not bypass(ctx, request)

def create_action(ctx, rs_context, request):
    rule_context = rule_config(ctx, rs_context, request)
    return Action(id=str(uuid.uuid4()), 
            code=rule_context['reason'], 
            claim_id=request.claim.id,
            action=rule_context['action'],
            explain=rule_context['explain'], 
            pay_percent=rule_context['percent'], 
            rank=rule_context['rank'])

def rule_config(ctx, rs_context, request):
    rule_id=ctx._node.rule.id
    group_id = request.group.id if request.group else "default"
    rule_ctx = rs_context.config.get(group_id, rs_context.config['default']).get('rules', rs_context.config['default']['rules']).get(rule_id, rs_context.config['default']['rules'][rule_id])
    return rule_ctx
 
def record_action_event(ctx, event):
    logging.info("Action event on %s: added: %s, updated: %s, deleted: %s",
                    session(ctx).ruleset,
                    event.added, event.updated, event.deleted)
    event.reset()

def to_datetime(d):
    return datetime.strptime(d, '%Y-%m-%d') if d else None

def to_bool(txt):
    if txt.lower() in ['yes', 'true']:
        return True
    elif txt.lower() in ['no', 'false']:
        return False
    else:
        raise ValueError(f"Cannot convert {txt} to boolean")

def subdirs(parent):
    return [os.path.join(parent, name) for name in os.listdir(parent) if os.path.isdir(os.path.join(parent, name))]