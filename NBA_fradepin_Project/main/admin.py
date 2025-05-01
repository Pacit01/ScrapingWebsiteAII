from django.contrib import admin
from main.nba.models import Jugador, Estadistica, Premio  # Importa tus modelos

# Personalizar la visualización de los modelos en el admin (opcional pero recomendado)

class JugadorAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'equipo')  # Campos a mostrar en la lista
    search_fields = ('nombre',)  # Campos por los que se puede buscar

class EstadisticaAdmin(admin.ModelAdmin):
    list_display = ('jugador', 'puntos', 'rebotes', 'asistencias', 'robos', 'tapones')
    list_filter = ('jugador',)  # Filtrar por jugador
    search_fields = ('jugador__nombre',)  # Buscar por nombre de jugador

class PremioAdmin(admin.ModelAdmin):
    list_display = ('jugador', 'nombre_premio', 'año')
    list_filter = ('nombre_premio', 'año')
    search_fields = ('jugador__nombre', 'nombre_premio')


# Registramos los modelos en el admin con sus clases personalizadas
admin.site.register(Jugador, JugadorAdmin)
admin.site.register(Estadistica, EstadisticaAdmin)
admin.site.register(Premio, PremioAdmin)