import shelve
from django.conf import settings
from django.shortcuts import get_object_or_404, render
from principal.forms import BusquedaJuego, BusquedaPorPalabra, BusquedaPorPrecio
from principal.models import Juego, Puntuacion

from principal.populate import crear_schema, populateDB, populate_puntuaciones
from whoosh.index import open_dir
from whoosh.qparser import QueryParser, MultifieldParser, OrGroup

from principal.recommendations import topMatches, transformPrefs


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
                rango1 = '[TO ' + str(rango) + '}'
                query = QueryParser("precio", ix.schema).parse(rango1)
                results = searcher.search(query, limit=None)
                mensaje = "Se han encontrado: " + str(len(results)) + " resultados con un precio por debajo de " + str(rango)
                return render(request, 'buscarRango.html', {'results': results, 'mensaje': mensaje})
        else:
            print("Formulario no válido")
    return render(request, 'buscarRango.html', {'form': form, 'STATIC_URL': settings.STATIC_URL})


def buscar_nombre_descripcion(request):
    form = BusquedaPorPalabra()
    if request.method == 'POST':
        form = BusquedaPorPalabra(request.POST)
        if form.is_valid():
            palabra = form.cleaned_data['palabra']

            ix = open_dir("Index")
            with ix.searcher() as searcher:
                query = MultifieldParser(["nombre", "descripcion"], ix.schema, group=OrGroup).parse(palabra)
                results = searcher.search(query, limit=None)
                mensaje = "Se han encontrado: " + str(len(results)) + " resultados con la palabra: " + palabra
                return render(request, 'buscarPalabra.html', {'results': results, 'mensaje': mensaje, 'STATIC_URL': settings.STATIC_URL})
        else:
            print("Formulario error: ", form.errors)
    return render(request, 'buscarPalabra.html', {'form': form, 'STATIC_URL': settings.STATIC_URL})

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


def loadDict():
    prefs={}
    shelf = shelve.open("dataRS.dat")
    puntuaciones = Puntuacion.objects.all()
    for puntuacion in puntuaciones:
        user = str(puntuacion.usuario)
        juego = int(puntuacion.juego_id)
        rate = float(puntuacion.puntuacion)
        prefs.setdefault(user,{})
        prefs[user][juego] = rate
    shelf['prefs']=prefs
    shelf['ItemsPrefs']=transformPrefs(prefs)
    shelf.close

def loadRS(request):
    loadDict()
    mensaje = 'Se ha cargado el RS'
    return render(request, 'cargar.html', {'titulo': 'FIN DE CARGA DEL RS', 'mensaje': mensaje, 'STATIC_URL': settings.STATIC_URL})


def juegos_similares(request):
    form = BusquedaJuego()
    items = None
    juego = None

    if request.method == 'POST':
        form = BusquedaJuego(request.POST)
        if form.is_valid():
            idJuego = form.cleaned_data['idJuego']
            jue = get_object_or_404(Juego, pk=int(idJuego))
            nombre_juego = jue.nombre
            shelf = shelve.open("dataRS.dat")
            Prefs = shelf['ItemsPrefs']
            shelf.close()

            similares = topMatches(Prefs, int(idJuego), n=3)
            juegos = []
            similaridad = []

            idJuegos = []
            listaJuegos = set()

            for re in similares:
                juego = Puntuacion.objects.filter(juego_id=re[1])[0]
                juego = juego.juego_nombre

                listaJuegos = set.union(listaJuegos, compruebaJuego(juego))
                juegos.append(juego)
                idJuegos.append(re[1])
                similaridad.append("{:.10f}".format(re[0]))
            items = zip(juegos, similaridad, idJuegos)
            return render(request, 'juegos_similares.html', {'idJuego': idJuego, 'nombre_juego':nombre_juego, 'items': items, 'listaJuegos': listaJuegos,  'STATIC_URL': settings.STATIC_URL})
    
    return render(request, 'juegos_similares.html', {'form': form})
