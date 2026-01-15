from rest_framework.authentication import BaseAuthentication
from rest_framework import exceptions
from django.conf import settings
from django.contrib.auth import get_user_model
import jwt


class JWTCustomAuthentication(BaseAuthentication):
    """Custom DRF authentication that accepts the project's PyJWT tokens.

    It expects an Authorization header: "Bearer <token>" where the token
    is signed with the Django `SECRET_KEY` and contains a claim with the
    user id (commonly `user_id`). This class is defensive and will try
    several common claim names.
    """

    def authenticate(self, request):
        auth_header = request.META.get('HTTP_AUTHORIZATION') or ''
        auth_header = auth_header.strip()
        if not auth_header:
            return None
        parts = auth_header.split()
        if len(parts) != 2 or parts[0].lower() != 'bearer':
            return None
        token = parts[1]

        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise exceptions.AuthenticationFailed('Token has expired')
        except jwt.InvalidTokenError:
            raise exceptions.AuthenticationFailed('Invalid token')
        except Exception as e:
            raise exceptions.AuthenticationFailed('Token decode error')

        # Determine claim name for user id (support common variants)
        user_claim = 'user_id'
        simple_jwt = getattr(settings, 'SIMPLE_JWT', None)
        if isinstance(simple_jwt, dict):
            user_claim = simple_jwt.get('USER_ID_CLAIM') or simple_jwt.get('user_id') or user_claim

        user_id = payload.get(user_claim) or payload.get('userId') or payload.get('sub') or payload.get('id')
        if not user_id:
            raise exceptions.AuthenticationFailed('Token missing user identifier')

        User = get_user_model()
        try:
            user = User.objects.get(pk=int(user_id))
        except Exception:
            raise exceptions.AuthenticationFailed('User not found')

        # Some custom user models may not implement the Django-provided
        # `is_authenticated` property; ensure it's present and truthy.
        if not hasattr(user, 'is_authenticated'):
            setattr(user, 'is_authenticated', True)

        return (user, None)

    def authenticate_header(self, request):
        return 'Bearer'
