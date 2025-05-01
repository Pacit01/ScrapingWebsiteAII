from django import forms
from .models import Premio

class BusquedaJugadorForm(forms.Form):
    query = forms.CharField(
        label='Buscar jugador',
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )




class BusquedaPorPremioForm(forms.Form):
    premio = forms.ChoiceField(
        label='Premio',
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'}),
        
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Get unique prize names from the database
        premios_unicos = Premio.objects.values_list('nombre_premio', flat=True).distinct().order_by('nombre_premio')
        self.fields['premio'].choices = [('', 'Seleccione un premio')] + [(p, p) for p in premios_unicos]