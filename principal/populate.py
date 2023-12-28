# -*- coding: utf-8 -*-
import os
import shutil
from principal.models import Juego, Puntuacion
import urllib.request
from bs4 import BeautifulSoup
from whoosh.index import create_in
from whoosh.fields import Schema, TEXT, BOOLEAN, ID, NUMERIC

path = "dataset"

def populateDB():
    Juego.objects.all().delete()
    i = 0
    while i<20:
        i = i + 1
        url = "https://www.raccoongames.es/es/productos/juegos-de-mesa/" + str(i)
        f = urllib.request.urlopen(url)
        s = BeautifulSoup(f, "lxml")
        juegos = s.find_all("div", class_ = "producto-lst")
        for juego in juegos:
            link = "https://www.raccoongames.es" + juego.a["href"]
            if "producto" not in link:
                continue
            else:
                f2 = urllib.request.urlopen(link)
                s2 = BeautifulSoup(f2, "lxml")
                
                ficha = s2.find("div", id = "ficha")

                nombre = ficha.find("h1").text
                marca = ficha.find("div", class_="marca").find("a").text
                
                if not marca:
                    marca = "Sin marca"

                referencia = ficha.find("div", class_="ref").text.replace("Ref. ", "").strip()

                descripcion = ficha.find("div", class_="producto-ficha")
                parrafos = descripcion.find_all("p")

                descripcion_filtrada = [p.text.strip() for p in parrafos if p.text.strip() and p != parrafos[-1]]
                
                if len(parrafos) == 1:
                    descripcion_filtrada = parrafos[0].text.strip()
                

                stock = True
                stock_div = ficha.find("div", id="sin-stock")
                if stock_div:
                    stock = False

                precio = ficha.find("span", id="precio").text.strip().replace("€", "").replace(",", ".").strip()

                m = Juego.objects.create(nombre=nombre, marca=marca, precio=precio, descripcion=descripcion_filtrada, stock=stock, referencia=referencia)

    return Juego.objects.count()   
                

def crear_schema():
    schem = Schema(nombre = TEXT(stored=True), marca = TEXT(stored=True),
                   precio = NUMERIC(stored=True), descripcion = TEXT(stored=True),
                   referencia = ID(stored=True), stock = BOOLEAN(stored=True))

    if os.path.exists("Index"):
        shutil.rmtree("Index")
    os.mkdir("Index")

    ix = create_in("Index", schema=schem)
    writer = ix.writer()
    i=0
    lista = Juego.objects.all()

    for juego in lista:
        writer.add_document(nombre=juego.nombre, marca=juego.marca, precio=juego.precio,
                            descripcion=juego.descripcion, referencia=juego.referencia, stock = juego.stock)
        i = i + 1
    writer.commit()


def populate_puntuaciones():
    Puntuacion.objects.all().delete()
    
    lista=[]
    fileobj=open(path+"\\bgg-15m-reviews.csv", "r", encoding="utf-8")
    next(fileobj)
    for line in fileobj:
        rip = line.split(",")
        if len(rip)==6:
            p=Puntuacion(usuario=rip[1],puntuacion=rip[2],juego_id=rip[4], juego_nombre=rip[5])
            lista.append(p)
    fileobj.close()
    Puntuacion.objects.bulk_create(lista)