import jwt
import hashlib
from accounts.models import CustomUser
from bankapi.models import Customer
from bankapi.authentication.auth import encrpyt_auth_token


def is_customer(user):
    """is_customer
    Check if the user is in the Customer database.
    User need to match its customer id with the Customer model.
    Args:
        user: a Django User object
    Returns:
        True: user is in Customer
        False: user not in Customer 
    """
    try:
        this_user = CustomUser.objects.get(email=user.email)
        print('>>>>>>>>>>>>>>>>')
        print(f'primary id: {this_user.id}')
        print('>>>>>>>>>>>>>>>>')
    except CustomUser.DoesNotExist as e:
        # ananymous user
        return False
    # if user with this customer_id exists in Customer
    return Customer.objects.filter(customer_id=this_user.id).exists()


def add_customer(user):
    """add_customer
    Add valid CustomUser to Customer by passing the customer_id to CustomUser.
    If Customer doesn't exist, create new Customer form CustomUser and link.
    Args:
        user: valid CustomUser
    Returns:
        True: add succeed
        False: add failed
    """
    try:
        this_user = CustomUser.objects.get(email=user.email)
        print('>>>>>>>>>>>>>>>>')
        print(f'type of user_model: {type(this_user)}')
        print(f'customer_id: {this_user.id}')
        print('>>>>>>>>>>>>>>>>')
    except CustomUser.DoesNotExist as e:
        # user not valid -> something wrong with the user authentication check
        return False

    # using CustomUser id as customer_id
    print('>>>>>>>>>>>>>>>>>>>>>>>>>>')
    print('Checking user ...')
    print(f'user.email: {this_user.email}')
    print(f'user.username: {this_user.username}')
    customer_id = this_user.id

    print(f'customer_id: {customer_id}')

    print('<<<<<<<<<<<<<<<<<<<<<<<<<<<')
    print('New Customer ...')
    print(f'customer_id: {customer_id}')
    print(f'customer_name: {user.username}')
    # should get more information from user
    print(f'customer_phone: {1231231234}')
    print(f'customer_email: {user.email}')
    print(f'customer_ssn: {123121234}')
    print(f'customer_address: Somewhere on Mars')
    print('<<<<<<<<<<<<<<<<<<<<<<<<<<<')
    new_customer = Customer.objects.create(
        customer_id=customer_id,
        customer_name=user.username,
        customer_phone=1231231234,
        customer_email=user.email,
        customer_ssn=123121234,
        customer_address='Somewhere on Mars'
    )
    new_customer.save()
    print('>>>>>>>>>>>>>>>>>>>>>>>>>>')

    return Customer.objects.filter(customer_id=this_user.id).exists()


def get_bankapi_token(user, day_expire=1):
    """get_bankapi_token
    User user id from Django as user_id in token. Get a encrypted token from bankapi
    Args:
        user: the user requesting for a token
        day_expire: number of day to expire
    Returns:
        token: the access token from bankapi
    """
    # get user id
    user_id = user.id
    expiration = day_expire * 24 * 60 * 60
    print('>>>>>>>>>>>>>>>>>>')
    print('getting token ...')
    print(f'user_id: {user_id}')
    print('>>>>>>>>>>>>>>>>>>')
    token = encrpyt_auth_token(user_id, expiration)
    return token


def add_bankapi_token(request, token):
    """add_bankapi_token
    Add bankapi token into the session of this request
    Args:
        request: the request asking for bankapi token
        token: the bankapi token
    Returns:
        request with token in session
    """
    request.session['bankapi_token'] = token
    return request
