from rest_framework.authentication import BaseAuthentication
from rest_framework import exceptions
from django.conf import settings
import jwt


class JWTCustomAuthentication(BaseAuthentication):
    """Custom DRF authentication that accepts the project's PyJWT tokens.

    It expects an Authorization header: "Bearer <token>" where the token
    is signed with the Django `SECRET_KEY` and contains a claim with the
    user id (commonly `user_id`). This class is defensive and will try
    several common claim names.
    
    IMPORTANTE: Esta clase devuelve directamente una instancia de CyberUser,
    por lo que request.user será un CyberUser con user_id como clave primaria.
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

        # Importar CyberUser directamente para evitar usar get_user_model
        # ya que CyberUser no extiende AbstractUser
        from apps.cyberUser.models import CyberUser
        try:
            user = CyberUser.objects.get(user_id=int(user_id))
        except CyberUser.DoesNotExist:
            raise exceptions.AuthenticationFailed('User not found')
        except Exception:
            raise exceptions.AuthenticationFailed('Error retrieving user')

        # Asegurar que el usuario tiene la propiedad is_authenticated
        if not hasattr(user, 'is_authenticated'):
            user.is_authenticated = True
        elif not callable(getattr(user, 'is_authenticated', None)):
            # Si es una propiedad, asegurar que retorna True
            pass

        return (user, payload)

    def authenticate_header(self, request):
        return 'Bearer'
