from django.shortcuts import render
from django.views.generic import View, CreateView, DeleteView, ListView, TemplateView
from .models import *

# Create your views here.
class LicenciaSolicitud(TemplateView):
    template_name = 'licencia.html'

class LicenciaSolicitud(CreateView):
    model = Licencia
    context_object_name = 'licencia'
    template_name = 'licencia.html'
    success_url = reverse_lazy('comisiones:historico_anticipo')



class HistoricoAnticipos(ListView):
    model = Anticipo
    context_object_name = 'anticipos'
    template_name = 'public/historico.html'

    def get_queryset(self):
        return Anticipo.objects.filter(integrantes_x_anticipo__user=self.request.user.id)