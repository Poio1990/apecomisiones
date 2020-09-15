import datetime
from datetime import date, datetime
from django.db import transaction
from django.forms import formset_factory
from io import BytesIO
from django.db.utils import IntegrityError
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.views.generic import View, CreateView, DeleteView, ListView, TemplateView, FormView
from django.http import HttpResponse, JsonResponse, request
from django.core.exceptions import ObjectDoesNotExist
from .models import *
from .forms import *
from usuarios.forms import UserForm
from usuarios.models import User
from django.contrib.auth.decorators import login_required
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, letter
from reportlab.lib.units import cm, inch
from reportlab.lib import colors
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.rl_config import defaultPageSize
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY, TA_RIGHT, TA_CENTER
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Image, Spacer
from django.core import serializers
import pdb


class ReportePdfSolicitud(View):
    """Regresa Pdf"""

    def get(self, request, *args, **kwargs):
        solicitud = Solicitud.objects.get(pk=kwargs['pk'])
        integrantes = Integrantes_x_Solicitud.objects.filter(
            solicitud_id=kwargs['pk'])

        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)

        PAGE_WIDTH = defaultPageSize[0]
        PAGE_HEIGHT = defaultPageSize[1]

        text = 'Solicitud de comisión'

        width = stringWidth(text, 'Helvetica', 16)
        x = (PAGE_WIDTH/2)-(width/2)

        # Header
        c.setLineWidth(.3)
        c.setFont('Helvetica', 18)
        c.drawString(x, 800, text)
        c.setFont('Helvetica', 12)

        fecha = date.today().strftime("%d/%m/%Y")

        c.drawString(400, 770, 'Fecha de pedido: ' + str(fecha))

        alto = 745
        for i in range(len(integrantes)):
            c.drawString(30, alto, 'Apellido y Nombre'+'     ' +
                         integrantes[i].user.get_full_name())
            c.drawString(360, alto, 'N° Afiliado a SEMPRE' +
                         '         ' + integrantes[i].user.num_afiliado)
            alto = alto - 25

        c.drawString(30, 570, 'Motivo de la comisión: ')
        # Funcion que agrega saltos de linea a 'motivo' para que se pinte en el pdf
        j = 0
        n = 87
        story = ''
        for i in range(len(solicitud.motivo)):
            if solicitud.motivo[i] == '\n':
                n = i + 86
            if i == n:
                story = story + solicitud.motivo[j:n] + '\n'
                j = n
                n = n + 86
        story = story + solicitud.motivo[j:len(solicitud.motivo)]

        # Texto que va contenido dentro de los detalles de trabajo
        textobject = c.beginText()
        textobject.setTextOrigin(35, 555)
        textobject.setFont("Courier", 10)
        textobject.textLines(story)
        c.drawText(textobject)

        fecha_inicio = datetime.strptime(
            str(solicitud.fech_inicio), "%Y-%m-%d").strftime("%d/%m/%Y")

        c.setFont('Helvetica', 12)
        c.drawString(30, 370, 'Fecha de iniciación: ' +
                     str(fecha_inicio))
        c.drawString(320, 370, 'Duracón prevista: ' +
                     solicitud.duracion_prevista)
        c.drawString(
            30, 340, 'Lugar de residencia durante la comisión: '+solicitud.ciudad.ciudad)
        c.drawString(30, 310, 'Medio de transporte')
        c.drawString(200, 310, 'Unidad de legajo: ' +
                     solicitud.transporte.num_legajo)
        c.drawString(400, 310, 'Patente: '+solicitud.transporte.patente)
        c.drawString(30, 280, 'Gastos a solicitar: $' +
                     str(solicitud.gastos_previstos))
        c.drawString(30, 250, 'Comisión ordenada por: ' +
                     solicitud.solicitante.get_full_name())

        c.drawString(500, 20, 'Firma')
        c.line(465, 32, 570, 32)

        c.save()
        pdf = buffer.getvalue()
        buffer.close()
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = 'filename=Solicitud.pdf'
        return response

    def post(self, request, *args, **kwargs):

        pk = request.POST.getlist('afiliado[]')
        num_afiliados = request.POST.getlist('num_afiliado[]')
        motivo = request.POST['motivo']

        fech_inicio = request.POST['fech_inicio']
        duracion_prevista = request.POST['duracion_prevista']
        pk_ciudad = request.POST['ciudad']
        transporte = request.POST['transporte']
        #patente = request.POST['patente']
        gastos_previstos = request.POST['gastos_previstos']

        # este for recupera los usuarios cuyos id estan contenidos en la lista pk
        nombre = []
        for i in range(len(pk)-1):
            pk1 = str(pk[i])
            nombre.append(User.objects.get(pk=pk1))

        ciudad = Ciudad.objects.get(id_ciudad=pk_ciudad)

        num_legajo_transporte = Transporte.objects.get(
            id_transporte=transporte)

        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)

        PAGE_WIDTH = defaultPageSize[0]
        PAGE_HEIGHT = defaultPageSize[1]

        text = 'Solicitud de comisión'

        width = stringWidth(text, 'Helvetica', 16)
        x = (PAGE_WIDTH/2)-(width/2)

        # Header
        c.setLineWidth(.3)
        c.setFont('Helvetica', 18)
        c.drawString(x, 800, text)
        c.setFont('Helvetica', 12)

        fecha = date.today().strftime("%d/%m/%Y")

        c.drawString(400, 770, 'Fecha de pedido: ' + str(fecha))

        alto = 745
        for i in range(len(pk)-1):
            c.drawString(30, alto, 'Apellido y Nombre'+'       ' +
                         nombre[i].last_name + '  '+nombre[i].first_name)
            c.drawString(360, alto, 'N° Afiliado a SEMPRE' +
                         '         ' + num_afiliados[i])
            alto = alto - 25

        c.drawString(30, 570, 'Motivo de la comisión: ')
        # Funcion que agrega saltos de linea a 'motivo' para que se pinte en el pdf
        j = 0
        n = 87
        story = ''
        for i in range(len(motivo)):
            if motivo[i] == '\n':
                n = i + 88
            if i == n:
                story = story + motivo[j:n] + '\n'
                j = n
                n = n + 86
        story = story + motivo[j:len(motivo)]

        # Texto que va contenido dentro de los detalles de trabajo
        textobject = c.beginText()
        textobject.setTextOrigin(35, 555)
        textobject.setFont("Courier", 10)
        textobject.textLines(story)
        c.drawText(textobject)

        c.setFont('Helvetica', 12)
        c.drawString(30, 370, 'Fecha de iniciación: '+fech_inicio)
        c.drawString(320, 370, 'Duracón prevista: '+duracion_prevista+' días')
        c.drawString(
            30, 340, 'Lugar de residencia durante la comisión: ' + ciudad.ciudad)
        c.drawString(30, 310, 'Medio de transporte')
        c.drawString(200, 310, 'Unidad de legajo: ' +
                     num_legajo_transporte.num_legajo)
        c.drawString(400, 310, 'Patente: ' + num_legajo_transporte.patente)
        c.drawString(30, 280, 'Gastos a solicitar: $' + gastos_previstos)
        c.drawString(30, 250, 'Anticipo ordenado por: ' +
                     request.user.last_name + '  ' + request.user.first_name)

        c.drawString(500, 20, 'Firma')
        c.line(465, 32, 570, 32)
        c.save()
        pdf = buffer.getvalue()
        buffer.close()
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = 'filename=Solicitud.pdf'
        return response


class ReportePdfAnticipo(View):

    def get(self, request, *args, **kwargs):
        anticipo = Anticipo.objects.get(pk=kwargs['pk'])
        itineraio = Itineraio.objects.filter(anticipo_id=kwargs['pk'])
        det_trabajo = DetalleTrabajo.objects.get(anticipo_id=kwargs['pk'])
        int_x_ant = Integrantes_x_Anticipo.objects.filter(
            anticipo_id=kwargs['pk'])
        
        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)

        PAGE_WIDTH = defaultPageSize[0]
        PAGE_HEIGHT = defaultPageSize[1]

        text = 'Rendición de comisión'

        width = stringWidth(text, 'Helvetica', 16)
        x = (PAGE_WIDTH/2)-(width/2)

        # Header
        c.setLineWidth(.3)
        c.setFont('Helvetica', 18)
        c.drawString(x, 800, text)

        alto = 770

        c.setFont('Helvetica', 12)
        for i in range(len(int_x_ant)):
            c.drawString(30, alto, 'Apellido y Nombre'+'     ' +
                         int_x_ant[i].user.get_full_name())
            c.drawString(360, alto, 'N° Afiliado a SEMPRE' +
                         '         ' + int_x_ant[i].user.num_afiliado)
            alto = alto - 25

        fecha_inicio = datetime.strptime(
            str(anticipo.fech_inicio), "%Y-%m-%d").strftime("%d/%m/%Y")
        fecha_fin = datetime.strptime(
            str(anticipo.fech_fin), "%Y-%m-%d").strftime("%d/%m/%Y")

        c.drawString(30, 620, 'Fecha de inicio: ' + fecha_inicio)
        c.drawString(320, 620, 'Fecha de finalización: ' + fecha_fin)
        c.drawString(
            30, 595, 'Lugar de residencia durante la comisión: ' + int_x_ant[0].anticipo.ciudad.ciudad)
        c.drawString(30, 570, 'Medio de transporte')
        c.drawString(200, 570, 'Unidad de legajo: ' +
                     int_x_ant[0].anticipo.transporte.num_legajo)
        c.drawString(400, 570, 'Patente: ' +
                     int_x_ant[0].anticipo.transporte.patente)
        c.drawString(30, 545, 'Gastos: $' + str(int_x_ant[0].anticipo.gastos))

        # tabla.encabezado
        styles = getSampleStyleSheet()
        styleBH = styles["Normal"]
        styleBH.fontSize = 10

        nombre = Paragraph('''Apellido y Nombre''', styleBH)
        dia = Paragraph('''Día''', styleBH)
        mes = Paragraph('''Mes''', styleBH)
        sal = Paragraph('''Salida de''', styleBH)
        h1 = Paragraph('''Horario''', styleBH)
        llegada = Paragraph('''Llegada de''', styleBH)
        h2 = Paragraph('''Horario''', styleBH)

        data = []
        data.append([nombre, dia, mes, sal, h1, llegada, h2])

        styleN = styles["BodyText"]
        styleN.alignment = TA_CENTER
        styleN.fontSize = 7

        # tabla.contenico
        comisiones = []
        for i in range(len(itineraio)):
            comisiones.append({'name': itineraio[i].nombre_afiliado, 'b1': itineraio[i].dia, 'b2': itineraio[i].mes, 'b3': itineraio[i].salida,
                               'b4': itineraio[i].hora_salida, 'b5': itineraio[i].llegada, 'b6': itineraio[i].hora_llegada, })

        hight1 = 505

        for part in comisiones:
            this_part = [part['name'], part['b1'], part['b2'],
                         part['b3'], part['b4'], part['b5'], part['b6']]
            data.append(this_part)
            hight1 = hight1 - 18

        width, height = A4
        table = Table(data, colWidths=[
                      5 * cm, 1.5 * cm, 1.5 * cm, 3.8 * cm, 1.7 * cm, 3.8 * cm, 1.7 * cm])
        table.setStyle(TableStyle([
            ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
            ('BOX', (0, 0), (-1, -1), 0.25, colors.black), ]))

        table.wrapOn(c, width, height)
        table.drawOn(c, 30, hight1)

        # informe de comision
        c.setFont('Helvetica', 16)
        c.drawString(30, 245, 'Informe de Anticipo ')

        #c.setFont('Helvetica', 12)
        #c.drawString(32, 220, 'km Salida: '+str(det_trabajo.km_salida))
        #c.drawString(180, 220, 'km Llegada: '+str(det_trabajo.km_llegada))
        # c.drawString(350, 220, 'Total km recorrido: ' +
        #            str(det_trabajo.km_llegada-det_trabajo.km_salida))

        # Lineas Verticales
        c.line(30, 237, 30, 50)
        c.line(565, 50, 565, 237)

        # Lineas Horizontales
        c.line(30, 237, 565, 237)
        #c.line(30, 210, 565, 210)
        c.line(30, 50, 565, 50)

        c.setFont('Helvetica', 12)
        c.drawString(35, 220, 'NOTA: ')

        # Funcion que agrega saltos de linea
        j = 0
        n = 87
        story = ''
        for i in range(len(det_trabajo.detalle_trabajo)):
            if det_trabajo.detalle_trabajo[i] == '\n':
                n = i + 87
            if i == n:
                story = story + det_trabajo.detalle_trabajo[j:n] + '\n'
                j = n
                n = n + 87
        story = story + \
            det_trabajo.detalle_trabajo[j:len(det_trabajo.detalle_trabajo)]

        # Texto que va contenido dentro de los detalles de trabajo
        textobject = c.beginText()
        textobject.setTextOrigin(35, 208)
        textobject.setFont("Courier", 10)
        textobject.textLines(story)
        c.drawText(textobject)

        firm = 'Firma:'
        width = stringWidth(firm, 'Helvetica', 12)
        c.setFont('Helvetica', 12)
        x = (PAGE_WIDTH/2)-(width/2)
        c.drawString(x, 15, firm)
        c.line(200, 27, 400, 27)
        c.showPage()

        c.save()
        pdf = buffer.getvalue()
        buffer.close()
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = 'filename=Anticipo.pdf'
        return response

    def post(self, request, *args, **kwargs):

        fech_inicio = request.POST['fech_inicio']
        fech_fin = request.POST['fech_fin']
        pk = request.POST.getlist('afiliado[]')
        num_afiliados = request.POST.getlist('num_afiliado[]')
        # ciudad
        pk_ciudad = request.POST['ciudad']
        # comision

        transporte = request.POST['transporte']
        #patente = request.POST.get('patente')
        gastos = request.POST.get('gastos')

        # Itinerario
        nombres = request.POST.getlist('name[]')
        dias = request.POST.getlist('dia[]')
        meses = request.POST.getlist('mes[]')
        salidas = request.POST.getlist('salida[]')
        llegadas = request.POST.getlist('llegada[]')
        horas_salida = request.POST.getlist('hora_salida[]')
        horas_llegada = request.POST.getlist('hora_llegada[]')

        # Detalle de trabajo
        km_salida = request.POST['km_salida']
        km_llegada = request.POST['km_llegada']
        km_total = request.POST['km_total']
        detalle_trabajo = request.POST['detalle_trabajo']

        # este for recupera los usuarios cuyos id estan contenidos en la lista pk
        nombre = []
        for i in range(len(pk)-1):
            pk1 = str(pk[i])
            nombre.append(User.objects.get(pk=pk1))

        num_legajo_transporte = Transporte.objects.get(
            id_transporte=transporte)
        ciudad = Ciudad.objects.get(id_ciudad=pk_ciudad)

        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)

        PAGE_WIDTH = defaultPageSize[0]
        PAGE_HEIGHT = defaultPageSize[1]

        text = 'Rendicion de comisión N° ___________'

        width = stringWidth(text, 'Helvetica', 16)
        x = (PAGE_WIDTH/2)-(width/2)

        # Header
        c.setLineWidth(.3)
        c.setFont('Helvetica', 18)
        c.drawString(x, 800, text)

        c.setFont('Helvetica', 12)

        alto = 770
        for i in range(len(pk)-1):
            c.drawString(30, alto, 'Apellido y Nombre'+'       ' +
                         nombre[i].last_name + '  '+nombre[i].first_name)
            c.drawString(360, alto, 'N° Afiliado a SEMPRE' +
                         '         ' + num_afiliados[i])
            alto = alto - 25

        c.drawString(30, 620, 'Fecha de inicio: ' + fech_inicio)
        c.drawString(320, 620, 'Fecha de finalización: ' + fech_fin)
        c.drawString(
            30, 595, 'Lugar de residencia durante la comisión: ' + ciudad.ciudad)
        c.drawString(30, 570, 'Medio de transporte')
        c.drawString(200, 570, 'Unidad de legajo: ' +
                     num_legajo_transporte.num_legajo)
        c.drawString(400, 570, 'Patente: ' +num_legajo_transporte.patente)
        c.drawString(30, 545, 'Gastos: $' + gastos)

        # tabla.encabezado
        styles = getSampleStyleSheet()
        styleBH = styles["Normal"]
        styleBH.fontSize = 10

        nombre = Paragraph('''Apellido y Nombre''', styleBH)
        dia = Paragraph('''Día''', styleBH)
        mes = Paragraph('''Mes''', styleBH)
        sal = Paragraph('''Salida de''', styleBH)
        h1 = Paragraph('''Horario''', styleBH)
        llegada = Paragraph('''Llegada de''', styleBH)
        h2 = Paragraph('''Horario''', styleBH)

        data = []
        data.append([nombre, dia, mes, sal, h1, llegada, h2])

        styleN = styles["BodyText"]
        styleN.alignment = TA_CENTER
        styleN.fontSize = 7

        # tabla.contenido
        comisiones = []
        for i in range(len(nombres)):
            comisiones.append({'name': nombres[i], 'b1': dias[i], 'b2': meses[i], 'b3': salidas[i],
                               'b4': horas_salida[i], 'b5': llegadas[i], 'b6': horas_llegada[i], })

        hight1 = 505

        for part in comisiones:
            this_part = [part['name'], part['b1'], part['b2'],
                         part['b3'], part['b4'], part['b5'], part['b6']]
            data.append(this_part)
            hight1 = hight1 - 18

        width, height = A4
        table = Table(data, colWidths=[
                      5 * cm, 1.5 * cm, 1.5 * cm, 3.8 * cm, 1.7 * cm, 3.8 * cm, 1.7 * cm])
        table.setStyle(TableStyle([
            ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
            ('BOX', (0, 0), (-1, -1), 0.25, colors.black), ]))

        table.wrapOn(c, width, height)
        table.drawOn(c, 30, hight1)

        # informe de comision
        c.setFont('Helvetica', 16)
        c.drawString(30, 245, 'Informe de Anticipo ')

        c.setFont('Helvetica', 12)
        #c.drawString(32, 220, 'km Salida: '+km_salida)
        #c.drawString(180, 220, 'km Llegada: '+km_llegada)
        #c.drawString(350, 220, 'Total km recorrido: '+km_total)

        # Lineas Verticales
        c.line(30, 237, 30, 50)
        c.line(565, 50, 565, 237)

        # Lineas Horizontales
        c.line(30, 237, 565, 237)
        #c.line(30, 210, 565, 210)
        c.line(30, 50, 565, 50)

        c.setFont('Helvetica', 12)
        c.drawString(35, 220, 'Nota: ')

        # Funcion que agrega saltos de linea
        j = 0
        n = 87
        story = ''
        for i in range(len(detalle_trabajo)):
            if detalle_trabajo[i] == '\n':
                n = i + 87
            if i == n:
                story = story + detalle_trabajo[j:n] + '\n'
                j = n
                n = n + 87
        story = story + detalle_trabajo[j:len(detalle_trabajo)]

        # Texto que va contenido dentro de los detalles de trabajo
        textobject = c.beginText()
        textobject.setTextOrigin(35, 208)
        textobject.setFont("Courier", 10)
        textobject.textLines(story)
        c.drawText(textobject)

        firm = 'Firma:'
        width = stringWidth(firm, 'Helvetica', 12)
        c.setFont('Helvetica', 12)
        x = (PAGE_WIDTH/2)-(width/2)
        c.drawString(x, 15, firm)
        c.line(200, 27, 400, 27)
        c.showPage()

        c.save()
        pdf = buffer.getvalue()
        buffer.close()
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = 'filename=Anticipo.pdf'
        return response


class SolicitudAnticipo(SuccessMessageMixin, CreateView):
    model = Solicitud
    template_name = 'comisiones/solicitud.html'
    form_class = SolicitudForm
    context_object_name = 'solicitud'
    success_message = "Solicitud de anticipo creada exitosamente"
    success_url = reverse_lazy('comisiones:historico_comisiones')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['users'] = User.objects.all().order_by('last_name')
        return context

    def post(self, request, *args, **kwargs):
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        if form.is_valid():
            solicitud = form.save(commit=False)
            solicitud.solicitante = self.request.user
            solicitud.save()
            pk_users = self.request.POST.getlist('afiliado[]')
            for i in range(len(pk_users)-1):
                Integrantes_x_Solicitud.objects.create(
                    solicitud=solicitud, user_id=pk_users[i])
            return self.form_valid(form)
        else:
            self.object = None
            context = self.get_context_data(**kwargs)
            context['form'] = form
            return render(request,self.template_name,context)



class RendicionAnticipo(SuccessMessageMixin, CreateView):
    model = Anticipo
    template_name = 'comisiones/historico_solicitud.html'
    form_class = RendicionForm
    context_object_name = 'rendicion'
    success_message = "Rendición de anticipo creada exitosamente"
    success_url = reverse_lazy('comisiones:historico_comisiones')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['users'] = User.objects.all().order_by('last_name')
        context['detalle'] = DetalleTrabajoForm
        return context
    
    def post(self, request, *args, **kwargs):
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        detalle = DetalleTrabajoForm(request.POST)
        if form.is_valid() and detalle.is_valid():
            f = form.save()
            d = detalle.save(commit=False)
            d.anticipo = f
            d.save()
            # Itinerario -> remplazar por formset mas adelante al igual que users
            nombres = request.POST.getlist('name[]')
            dias = request.POST.getlist('dia[]')
            meses = request.POST.getlist('mes[]')
            salidas = request.POST.getlist('salida[]')
            llegadas = request.POST.getlist('llegada[]')
            horas_salida = request.POST.getlist('hora_salida[]')
            horas_llegada = request.POST.getlist('hora_llegada[]')

            for i in range(len(nombres)):
                Itineraio.objects.create(
                    anticipo=f, nombre_afiliado=nombres[i], dia=dias[i], mes=meses[i],
                        hora_salida=horas_salida[i], hora_llegada=horas_llegada[i], salida=salidas[i], llegada=llegadas[i])

            pk_users = self.request.POST.getlist('afiliado[]')
            for i in range(len(pk_users)-1):
                Integrantes_x_Anticipo.objects.create(
                    anticipo=f, user_id=pk_users[i])
            return self.form_valid(form)
        else:
            self.object = None
            context = self.get_context_data(**kwargs)
            context['form'] = form
            context['detalle'] = detalle
            return render(request,self.template_name,context)
        


@login_required
@transaction.atomic
def confeccionAnticipo(request):
    users = User.objects.all().order_by('last_name')
    rendicion = RendicionForm()
    transportes = Transporte.objects.all()
    detalle = DetalleTrabajoForm()
    return render(request, 'comisiones/rendicion.html', {
        'users': users,
        'rendicion': rendicion,
        'transportes': transportes,
        'detalle': detalle,
    })


class Historicos(ListView):
    model = Anticipo
    context_object_name = 'anticipos'
    template_name = 'comisiones/historico.html'

    def get_queryset(self):
        return Anticipo.objects.filter(integrantes_x_anticipo__user=self.request.user.id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['solicitudes'] = Solicitud.objects.filter(
            integrantes_x_solicitud__user=self.request.user.pk)
        context['solicitudes_pedidas'] = Solicitud.objects.filter(
            solicitante_id=self.request.user.pk)
        return context


class EliminarAnticipo(DeleteView):
    model = Anticipo
    context_object_name = 'anticipo'
    template_name = 'comisiones/eliminar_anticipo.html'
    success_url = reverse_lazy('comisiones:historico_comisiones')
    success_message = "Anticipo de comisión eliminado exitosamente"

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        integrantes_x_anticipo = Integrantes_x_Anticipo.objects.filter(
            anticipo_id=self.kwargs['pk'])
        integrantes_x_anticipo.delete()
        return super(EliminarAnticipo, self).delete(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['entity'] = 'Anticipo'
        context['list_url'] = reverse_lazy('comisiones:historico_comisiones')
        return context


class EliminarSolicitud(DeleteView):
    model = Solicitud
    context_object_name = 'solicitud'
    template_name = 'comisiones/eliminar_solicitud.html'
    success_url = reverse_lazy('comisiones:historico_comisiones')
    success_message = "Solicitud de comisión eliminada exitosamente"

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        integrantes_x_solicitud = Integrantes_x_Solicitud.objects.filter(
            solicitud_id=self.kwargs['pk'])
        integrantes_x_solicitud.delete()
        return super(EliminarSolicitud, self).delete(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['entity'] = 'Solicitud'
        context['list_url'] = reverse_lazy('comisiones:historico_comisiones')
        return context


@login_required
def archivar(request):
    if request.method == 'POST':
        # usuarios
        pk_users = request.POST.getlist('afiliado[]')
        # ciudad
        pk_ciudad = request.POST['ciudad']
        # comision
        fech_inicio = request.POST['fech_inicio']
        fech_fin = request.POST['fech_fin']
        pk_transporte = request.POST['transporte']
        patente = request.POST.get('patente')
        gastos = request.POST.get('gastos')
        # Itinerario
        nombres = request.POST.getlist('name[]')
        dias = request.POST.getlist('dia[]')
        meses = request.POST.getlist('mes[]')
        salidas = request.POST.getlist('salida[]')
        llegadas = request.POST.getlist('llegada[]')
        horas_salida = request.POST.getlist('hora_salida[]')
        horas_llegada = request.POST.getlist('hora_llegada[]')
        # Detalle de trabajo
        km_salida = request.POST['km_salida']
        km_llegada = request.POST['km_llegada']
        detalle_trabajo = request.POST['detalle_trabajo']

        fecha_inicio = datetime.strptime(
            str(fech_inicio), "%d/%m/%Y").strftime("%Y-%m-%d")
        fecha_fin = datetime.strptime(
            str(fech_fin), "%d/%m/%Y").strftime("%Y-%m-%d")

        # Crear anticpo en la BD
        nuevo_anticipo = Anticipo(ciudad_id=pk_ciudad,
                                  transporte_id=pk_transporte, fech_inicio=fecha_inicio, fech_fin=fecha_fin, gastos=gastos)
        nuevo_anticipo.save()

        for i in range(len(nombres)):
            Itineraio.objects.create(
                anticipo=nuevo_anticipo, nombre_afiliado=nombres[i], dia=dias[i], mes=meses[i],
                hora_salida=horas_salida[i], hora_llegada=horas_llegada[i], salida=salidas[i], llegada=llegadas[i])

        if km_llegada and km_salida:
            DetalleTrabajo.objects.create(
                anticipo=nuevo_anticipo, km_salida=km_salida, km_llegada=km_llegada, detalle_trabajo=detalle_trabajo)
        else:
            DetalleTrabajo.objects.create(
                anticipo=nuevo_anticipo, detalle_trabajo=detalle_trabajo)

        for i in range(len(pk_users)):
            Integrantes_x_Anticipo.objects.create(
                anticipo=nuevo_anticipo, user_id=pk_users[i])
        messages.success(
            request, ('Rendición de anticipo creada exitosamente'))
        return redirect('comisiones:historico_comisiones')
    return render(request, 'comisiones/rendicion.html')


"""@login_required
def archivarSolicitud(request):
    if request.method == 'POST':
        # usuarios
        pk_users = request.POST.getlist('afiliado[]')
        # solicitud
        motivo = request.POST['motivo']
        fech_inicio = request.POST['fech_inicio']
        duracion_prevista = request.POST['duracion_prevista']
        pk_ciudad = request.POST['ciudad']
        pk_transporte = request.POST['transporte']
        gastos_previstos = request.POST['gastos_previstos']

        # Crear anticpo en la BD
        nueva_solicitud = Solicitud(ciudad_id=pk_ciudad,
                                    transporte_id=pk_transporte, fech_inicio=fech_inicio, duracion_prevista=duracion_prevista,
                                    motivo=motivo, gastos_previstos=gastos_previstos, solicitante=request.user)
        nueva_solicitud.save()

        for i in range(len(pk_users)):
            Integrantes_x_Solicitud.objects.create(
                solicitud=nueva_solicitud, user_id=pk_users[i])
        messages.success(
            request, ('Solicitud de anticipo creada exitosamente'))
        return redirect('comisiones:historico_comisiones')
    return render(request, 'comisiones/confeccion_solicitud_comision.html')"""


@login_required
def get_patente(request):
    pk_transporte = request.GET.get('transporte', None)
    data = list(Transporte.objects.filter(pk=pk_transporte).values('patente'))
    return JsonResponse({'data': data})


@login_required
def get_num_afiliado(request):
    pk = request.GET.get('pk')
    data = list(User.objects.filter(pk=pk).values('num_afiliado'))
    return JsonResponse({'data': data})
