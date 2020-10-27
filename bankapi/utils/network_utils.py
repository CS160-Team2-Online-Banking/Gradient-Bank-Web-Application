import datetime

def get_requestor_ip(request):
    return request.META.get("REMOTE_ADDR")

def encode_ip6(ip6_str):
    short_arr = list(map(lambda x: int(x,16), ip6_str.split(':')))

def get_utc_now_str():
    return datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')