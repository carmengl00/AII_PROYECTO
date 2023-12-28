from django.db import models

# Create your models here.
class Juego(models.Model):
    nombre = models.CharField(max_length=50)
    marca = models.CharField(max_length=50)
    precio = models.FloatField()
    descripcion = models.TextField()
    stock = models.BooleanField(default=True)
    referencia = models.CharField(max_length=20)

class Puntuacion(models.Model):
    usuario = models.TextField()
    puntuacion = models.FloatField()
    juego_id = models.PositiveIntegerField()
    juego_nombre = models.TextField()