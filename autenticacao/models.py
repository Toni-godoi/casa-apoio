from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager

# Create your models here.
class GerenciarUsuario(BaseUserManager):

    def create_user(self, nome, loginUsuario, email, telefone=None, senha=None):
        
        if not email:
            raise ValueError("email obrigatorio")
        if not loginUsuario:
            raise ValueError("Login para usuário obrigatório")
        
        usuario = self.model(
            username=loginUsuario,
            email = self.normalize_email(email),
            nome = nome,
            loginUsuario = loginUsuario,
            telefone = telefone,
        )

        usuario.set_password(senha)
        usuario.save(using=self._db)
        return usuario
    
    def create_superuser(self, nome, loginUsuario, email, password=None):

        usuario = self.create_user(
            nome=nome,
            loginUsuario=loginUsuario,
            email=email,
            senha=password
        )

        usuario.is_staff = True
        usuario.is_superuser = True
        usuario.is_admin = True
        usuario.save(using=self._db)
        return usuario

class Usuario(AbstractUser):
    nome = models.CharField(max_length=20)
    loginUsuario = models.CharField(max_length=10, unique=True)
    telefone = models.CharField(max_length=11, null=True)
    email = models.EmailField(max_length=80, unique=True)
    oidc_sub = models.CharField(max_length=255, unique=True, null=True, blank=True)
    dataCriacao = models.DateField(auto_now_add=True)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nome', 'loginUsuario']

    objects = GerenciarUsuario()
