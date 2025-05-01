from django.db import models

class Jugador(models.Model):
    nombre = models.CharField(max_length=100)
    equipo = models.CharField(max_length=100, null=True, blank=True)
    
    def __str__(self):
        return self.nombre

class Estadistica(models.Model):
    jugador = models.ForeignKey(Jugador, on_delete=models.CASCADE, related_name='estadisticas')
    puntos = models.FloatField(null=True, blank=True)
    rebotes = models.FloatField(null=True, blank=True)
    asistencias = models.FloatField(null=True, blank=True)
    robos = models.FloatField(null=True, blank=True)
    tapones = models.FloatField(null=True, blank=True)
    
    def __str__(self):
        return f"Estadísticas de {self.jugador.nombre}"

class Premio(models.Model):
    jugador = models.ForeignKey(Jugador, on_delete=models.CASCADE, related_name='premios')
    nombre_premio = models.CharField(max_length=100)
    año = models.CharField(max_length=7)
    
    def __str__(self):
        return f"{self.nombre_premio} ({self.año}) - {self.jugador.nombre}"

    class Meta:
        ordering = ['-año']
        unique_together = ['jugador', 'nombre_premio', 'año']