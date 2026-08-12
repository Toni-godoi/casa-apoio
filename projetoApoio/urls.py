"""
URL configuration for projetoApoio project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.http import HttpResponse
from django.urls import path, include
from domain.apoio import views
from django.conf.urls.static import static
from django.conf import settings
from projetoApoio.views import home

urlpatterns = [
    path("oidc/", include("mozilla_django_oidc.urls")),
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    path('apoio/', include("domain.apoio.urls")),
    path('usuario/', include("autenticacao.urls")),
    path('quarto/', include("domain.quarto.urls")),
    path('pessoa/', include("domain.pessoa.urls")),
    path('solicitacao/', include("domain.solicitacao.urls")),
]

urlpatterns += static(
    settings.STATIC_URL,
    document_root=settings.BASE_DIR / "static"
)

urlpatterns += static(
    settings.MEDIA_URL,
    document_root=settings.MEDIA_ROOT
)