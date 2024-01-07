from rest_framework.permissions import BasePermission
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import AuthenticationFailed


class CustomPermission(BasePermission):
    def has_permission(self, request, view) -> bool:
        try:
            user_auth_tuple = JWTAuthentication().authenticate(request)
            if user_auth_tuple:
                request.user, _ = user_auth_tuple
                return True
                # TODO : add logical permissions
        except AuthenticationFailed as exc:
            pass
        return False
