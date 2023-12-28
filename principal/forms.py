from django import forms

class BusquedaPorPrecio(forms.Form):
    rango = forms.FloatField(label="Precio máximo", widget=forms.NumberInput, required=True)

class BusquedaJuego(forms.Form):
    idJuego = forms.CharField(label='ID Juego', widget=forms.TextInput, required=True)
