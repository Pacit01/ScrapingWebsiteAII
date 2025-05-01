from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

app_name = 'main'  # This sets the application namespace

urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('carga/', views.carga, name='carga'),
    path('jugadores/', views.lista_jugadores, name='lista_jugadores'),
    path('jugadores/<int:jugador_id>/', views.detalle_jugador, name='detalle_jugador'),
    path('buscar/whoosh/', views.buscar_jugadores_whoosh, name='buscar_jugadores_whoosh'),
    path('buscar/django/', views.buscar_jugadores_django, name='buscar_jugadores_django'),
    path('buscar/premio/', views.buscar_por_premio, name='buscar_por_premio'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='main:inicio'), name='logout'),
]