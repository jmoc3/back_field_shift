from django.contrib import admin
from django.urls import path
from usuarios.views import RegistroView, LoginView
from analisis.views import AnalisisView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/registro", RegistroView.as_view(), name="registro"),
    path("api/v1/login", LoginView.as_view(), name="login"),
    path("api/v1/analisis", AnalisisView.as_view(), name="analisis"),
]