from django.contrib.auth.decorators import login_required, user_passes_test
from .models import CustomUser
mngr_login_required = user_passes_test(lambda u: u.is_active and u.type == CustomUser.UserTypes.TYPE_MANAGER, login_url="/employee/login")
cstmr_login_required = user_passes_test(lambda u: u.is_active and u.type == CustomUser.UserTypes.TYPE_CUSTOMER, login_url="/customer/login")
usr_loggedout_required = user_passes_test(lambda u: not u.is_active, login_url="/")


def customer_login_required(view_func):
    return login_required(cstmr_login_required(view_func))


def manager_login_required(view_func):
    return login_required(mngr_login_required(view_func))


def user_loggedout_required(view_func):
    return usr_loggedout_required(view_func)