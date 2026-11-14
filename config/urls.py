from django.contrib import admin
from django.urls import path
from usuarios.views import RegistroView, LoginView, UsuarioView
from analisis.views import AnalisisView
from data.views import CultivosView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/registro", RegistroView.as_view(), name="registro"),
    path("api/v1/login", LoginView.as_view(), name="login"),
    path("api/v1/analisis", AnalisisView.as_view(), name="analisis"),
    path("api/v1/user", UsuarioView.as_view(), name="user"),
    path("api/v1/cultivos", CultivosView.as_view(), name="cultivos"),
]
