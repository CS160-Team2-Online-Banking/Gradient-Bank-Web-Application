import datetime
from bankapi.models import EventLog


def get_requestor_ip(request):
    return request.META.get("REMOTE_ADDR")


def encode_ip6(ip6_str):
    short_arr = list(map(lambda x: int(x,16), ip6_str.split(':')))


def get_utc_now_str():
    return datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')


def get_datetime_from_str(date_str):
    return datetime.datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')


def build_event(user_id, ip4, ip6, event_type, request_time):
    new_event = EventLog(intiator_user_id=user_id,
                         ip6_address=ip6,
                         ip4_address=ip4,
                         event_type_id=event_type,
                         event_time=request_time)
    return new_event
