from django import forms


class BusquedaPorPrecio(forms.Form):
    rango1 = forms.FloatField(label="Precio mínimo")
    rango2 = forms.FloatField(label="Precio máximo", required=True)