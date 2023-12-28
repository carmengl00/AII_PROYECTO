from django import forms

class BusquedaPorPrecio(forms.Form):
    rango = forms.FloatField(label="Precio máximo", widget=forms.NumberInput, required=True)