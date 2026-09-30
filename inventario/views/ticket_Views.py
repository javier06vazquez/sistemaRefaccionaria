import json

from django.views import View
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic.edit import CreateView, UpdateView
from inventario.forms.configuracionTicket import ConfiguracionTicketForm
from inventario.models.catalogo.marca_producto import MarcaProducto
from inventario.models.configuracionTicket_modelo import ConfiguracionTicket
from inventario.models.detalleVenta_modelo import DetalleVenta
from inventario.models.venta_modelo import Venta
from django.http import JsonResponse
from django.db.models import F, ProtectedError
from django.views.generic import ListView
from django.shortcuts import get_object_or_404


def detalle_venta_nota(request, id):
    venta = get_object_or_404(Venta, id=id)
    detalles = venta.detalles.all()  
    configuracion = ConfiguracionTicket.objects.first()  # Obtener la configuración del ticket

    return render(
        request,
        "puntoVenta/detalleVentaNota.html",
        {
            "venta": venta,
            "detalles": detalles,
            "configuracion": configuracion,  # Pasar la configuración al template
        },
    )

def imprimir_ticket(request, id):
    venta = get_object_or_404(Venta, id=id)
    detalles = venta.detalles.all()

    return render(
        request,
        "ticket_venta.html",
        {
            "venta": venta,
            "detalles": detalles,
        },
    )

def configuracion_ticket(request):
    configuracion = ConfiguracionTicket.objects.first()
    if request.method == "POST":
        form = ConfiguracionTicketForm(request.POST, instance=configuracion)
        if form.is_valid():
            form.save()
            return redirect("inventario:ventas_historial")  # Redirige a la vista de punto de venta después de guardar
    else:
        form = ConfiguracionTicketForm(instance=configuracion)

    return render(request, "puntoVenta/configuracionTicket.html", {"form": form})
