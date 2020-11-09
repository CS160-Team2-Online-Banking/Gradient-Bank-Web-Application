from django.contrib.auth.backends import BaseBackend
import jwt


class BankAuthBackend(BaseBackend):
    def authenticate(self, request, username, password):  # auth backends like this one should return a user object
        # my crude idea of a solution would involve adding a field to the user object returned which
        # contains a JWT token. This would be used to access the API methods.
        # we don't need to use this for now
        pass

# this might not even be necessary though...
# instead, we could simply create a link between teh stored user_ids in our bank database and the custom user we created
# then, when an application wants to make a request to the bankAPI, it will need to build/retrieve an authentication
# token for the server.


def build_customer_auth_token(user):
    # TODO: using our user-model (which will have connection to the bank customer table) construct the auth token string
    pass
