from django.db import models

# Create your models here.
class Juego(models.Model):
    nombre = models.CharField(max_length=50)
    marca = models.CharField(max_length=50)
    precio = models.FloatField()
    descripcion = models.TextField()
    stock = models.BooleanField(default=True)
    referencia = models.CharField(max_length=20)

