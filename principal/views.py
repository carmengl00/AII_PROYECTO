from django.conf import settings
from django.shortcuts import render
from principal.forms import BusquedaPorPrecio
from principal.models import Juego

from principal.populate import crear_schema, populateDB
from whoosh.index import open_dir
from whoosh.qparser import QueryParser

# Create your views here.

def inicio(request):
    return render(request, 'base.html', {'STATIC_URL': settings.STATIC_URL})


def cargar(request):
    juegos = populateDB()
    crear_schema()
    mensaje = 'Se han cargado ' + str(juegos) + ' juegos'
    return render(request, 'cargar.html', {'mensaje': mensaje, 'STATIC_URL': settings.STATIC_URL})


def lista_juegos(request):
    juegos = Juego.objects.all()
    return render(request, 'juegos.html', {'titulo': 'Lista de juegos:' , 'juegos':juegos, 'STATIC_URL': settings.STATIC_URL})


def buscar_rango(request):
    form = BusquedaPorPrecio(request.GET, request.FILES)
    if request.method=='POST':
        form = BusquedaPorPrecio(request.POST)
        if form.is_valid():
            rango1 = form.cleaned_data['rango1']
            rango2 = form.cleaned_data['rango2']

            ix=open_dir("Index")
            with ix.searcher() as searcher:
                rango_precio = '['+ str(rango1) + ' TO ' + str(rango2) +']'
                query = QueryParser("precio", ix.schema).parse(rango_precio)
                juegos = searcher.search(query, limit=None)
                mensaje = "Se han encontrado: " + str(len(juegos)) + " resultados con la sentencia " + str(rango1) + " - " + str(rango2)
                return render(request, 'buscarRango.html', {'results': juegos, 'mensaje': mensaje})
    return render(request, 'buscarRango.html',{'form':form, 'STATIC_URL': settings.STATIC_URL})
