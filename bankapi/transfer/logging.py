from bankapi.models import *
from django.db.models.functions import Now
from django.db import transaction
from bankapi.authentication.auth import *
import json


class EventTypes:
    TRANSFER_CREATE_REQUEST = 0
    TRANSFER_REQUEST_CANCELED = 1
    AUTOPAYMENT_CREATE_REQUEST = 2
    AUTOPAYMENT_EDIT_REQUEST = 3
    AUTOPAYMENT_DELETE_REQUEST = 4


@transaction.atomic
def log_event(request, entry_type, associated_item=None):
    try:
        auth_token = decrypt_auth_token(request)
        user_id = auth_token["user_id"]
    except json.decoder.JSONDecodeError:
        return  # TODO: do something here
    except KeyError:
        return  # TODO: do something here

    log = EventLog(intiator_user_id=user_id,
                   event_type=entry_type,
                   event_time=Now())
    if associated_item:
        log.data_id = associated_item
    log.save()
