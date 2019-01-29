from django.db import close_old_connections
from urllib.parse import parse_qsl
from django.contrib.auth.models import AnonymousUser
from rest_framework_jwt.serializers import VerifyJSONWebTokenSerializer
from  rest_framework.exceptions import ValidationError
class AuthMiddleware:
    """
    Custom middleware (insecure) that takes user IDs from the query string.
    """

    def __init__(self, inner):
        # Store the ASGI application we were passed
        self.inner = inner

    def __call__(self, scope):
        # Look up user from query string (you should also do things like
        # check it's a valid user ID, or if scope["user"] is already populated)
        query = dict(parse_qsl(scope["query_string"].decode('utf-8')))
        try:
            user = VerifyJSONWebTokenSerializer().validate(query)
            user = user['user']
        except ValidationError:
            user = AnonymousUser()
        close_old_connections()
        # Return the inner application directly and let it run everything else
        return self.inner(dict(scope, user=user))
