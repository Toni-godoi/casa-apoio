# autenticacao/backends.py

from mozilla_django_oidc.auth import OIDCAuthenticationBackend
from .models import Usuario


class AuthentikBackend(OIDCAuthenticationBackend):

    def create_user(self, claims):

        def get_userinfo(self, access_token, id_token, payload):
            print("ACCESS TOKEN:", access_token)
            return super().get_userinfo(
                access_token,
                id_token,
                payload
            )
        
        return Usuario.objects.create_user(
            nome=claims.get("name"),
            loginUsuario=claims.get("preferred_username"),
            telefone="",
            email=claims.get("email")
        )