from django.conf import settings
from django.shortcuts import render
from principal.forms import BusquedaPorPrecio
from principal.models import Juego, Puntuacion

from principal.populate import crear_schema, populateDB, populate_puntuaciones
from whoosh.index import open_dir
from whoosh.qparser import QueryParser


def inicio(request):
    return render(request, 'base.html', {'STATIC_URL': settings.STATIC_URL})


def cargar(request):
    juegos = populateDB()
    populate_puntuaciones()
    crear_schema()
    mensaje = 'Se han cargado ' + str(juegos) + ' juegos'
    return render(request, 'cargar.html', {'mensaje': mensaje, 'STATIC_URL': settings.STATIC_URL})


def lista_juegos(request):
    juegos = Juego.objects.all()
    return render(request, 'juegos.html', {'titulo': 'Lista de juegos:' , 'juegos':juegos, 'STATIC_URL': settings.STATIC_URL})

def buscar_precio_maximo(request):
    form = BusquedaPorPrecio()
    if request.method == 'POST':
        form = BusquedaPorPrecio(request.POST)
        if form.is_valid():
            rango = form.cleaned_data['rango']
            print("Datos del formulario:", form.cleaned_data)
            print("Rango: " + str(rango))
            ix = open_dir("Index")
            with ix.searcher() as searcher:
                query = QueryParser("precio", ix.schema).parse('[TO ' + str(rango) + '}')
                results = searcher.search(query, limit=None)
                mensaje = "Se han encontrado: " + str(len(results)) + " resultados con un precio por debajo de " + str(rango)
                return render(request, 'buscarRango.html', {'results': results, 'mensaje': mensaje})
        else:
            print("Formulario no válido")
    return render(request, 'buscarRango.html', {'form': form, 'STATIC_URL': settings.STATIC_URL})

# Esta funcion comprueba si el juego está en la base de datos
def compruebaJuego(juego):
    juegos=Juego.objects.all()
    juegonombre = juego.replace("\n", "").replace(" ", "")
    lista=set()
    for juego in juegos:
        juegonombre = juego.nombre
        if juegonombre in juegonombre.replace("\n", "").replace(" ", ""):
            if juegonombre in lista:
                continue
            else:
                lista.add(juegonombre)
    return lista

def lista_puntuaciones(request):
    puntuaciones = Puntuacion.objects.all()[1:100]
    tamano = Puntuacion.objects.count()
    listajuegos = set()
    for juego in puntuaciones:
        juegonombre = juego.juego_nombre
        listajuegos = set.union(listajuegos, (compruebaJuego(juegonombre)))
    return render(request, 'lista_puntuaciones.html', {'puntuaciones':puntuaciones, 'tamano':tamano, 'listaJuegos':listajuegos, 'STATIC_URL': settings.STATIC_URL})


