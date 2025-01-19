import logging
import pandas as pd

from knowledgenet.helper import session

def record_action_event(ctx, event):
    logging.debug("Action event on %s: added: %s, updated: %s, deleted: %s",
                    session(ctx).ruleset,
                    event.added, event.updated, event.deleted)
    event.reset()

def load_from_csv(facts, of_type, file_path, converters=None):
    df = pd.read_csv(file_path, converters=converters).to_dict(orient='records')
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