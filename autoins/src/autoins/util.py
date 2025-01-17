import logging

def record_action_event(event):
    logging.info("Action event: added: %s, updated: %s, deleted: %s", 
                    event.added, event.updated, event.deleted)
    event.reset()
