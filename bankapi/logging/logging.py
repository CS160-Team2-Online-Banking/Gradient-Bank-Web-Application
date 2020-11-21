from bankapi.models import *
from django.db.models.functions import Now
import ipaddress


def get_request_ip(request, auth_token):
    ip = auth_token.get("REMOTE_ADDR", request.META.get('REMOTE_ADDR'))
    return ipaddress.ip_address(ip)  # just get the remote address
    #return ipaddress.ip_address(request.META.get('REMOTE_ADDR'))  # just get the remote address


def ip6_to_string(ip6):
    return ipaddress.ip_address(ip6).compressed


def ip4_to_string(ip4):
    return ipaddress.ip_address(ip4).compressed


def create_event(request, auth_token, event_type, data_id=None):
    user_id = auth_token["user_id"]
    ip = get_request_ip(request, auth_token)

    user = Customer.objects.filter(pk=user_id).first()
    if user is None:
        raise ValueError("AuthToken User ID specified is invalid")

    event = EventLog(intiator_user_id=user.pk,
                     event_type=event_type[0],
                     event_time=Now())

    if data_id is not None:
        event.data_id = data_id

    if ip.version == 4:
        event.ip4_address = ip.packed
    elif ip.version == 6:
        event.ip6_address = ip.packed

    return event


def log_event(request, auth_token, event_type, data_id=None):
    event = create_event(request, auth_token, event_type, data_id)
    event.save()
