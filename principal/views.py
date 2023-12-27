from django.conf import settings
from django.shortcuts import render
from principal.models import Juego

from principal.populate import crear_schema, populateDB

# Create your views here.

def inicio(request):
    return render(request, 'base.html')


def cargar(request):
    juegos = populateDB()
    crear_schema()
    mensaje = 'Se han cargado ' + str(juegos) + ' juegos'
    return render(request, 'cargar.html', {'mensaje': mensaje, 'STATIC_URL': settings.STATIC_URL})


def lista_juegos(request):
    juegos = Juego.objects.all()
    return render(request, 'juegos.html', {'titulo': 'Lista de juegos:' , 'juegos':juegos})
