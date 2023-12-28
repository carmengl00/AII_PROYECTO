from django.conf import settings
from django.shortcuts import render
from principal.forms import BusquedaPorPrecio
from principal.models import Juego

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



