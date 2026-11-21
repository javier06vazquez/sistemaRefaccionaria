from django.views import View
from django.shortcuts import render
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Sum, Count
from inventario.models import Venta, CierreCaja, DetalleVenta


class CierreCajaListView(View):
    def get(self, request):

        fecha_inicio = request.GET.get('fecha_inicio')
        fecha_fin = request.GET.get('fecha_fin')

        cierres = CierreCaja.objects.all()
        if fecha_inicio:
            cierres = cierres.filter(fecha_inicio__date__gte=fecha_inicio)
        if fecha_fin:
            cierres = cierres.filter(fecha_fin__date__lte=fecha_fin)

        # Ventas del día actual que aún no se han cerrado
        ventas_pendientes = Venta.objects.filter(cierre__isnull=True, estado='activa')
        total_pendiente = ventas_pendientes.aggregate(total=Sum('total'))['total'] or 0

        data = {
            "titulo": "Cierre de Caja",
            "mensaje": "Bienvenido al sistema de cierre de caja.",
            'cierres': cierres,
            'ventas_pendientes': ventas_pendientes,
            'total_pendiente': total_pendiente,
            'fecha_inicio': fecha_inicio,
            'fecha_fin': fecha_fin,
        }
        return render(request, 'cierreCaja/cierreCajaLista.html', data)


def cerrar_caja(request):
    if request.method == "POST":
        ventas = Venta.objects.filter(cierre__isnull=True, estado='activa')
        if not ventas.exists():
            return JsonResponse({'estado': 'error', 'mensaje': 'No hay ventas pendientes por cerrar.'})

        resumen = ventas.aggregate(total=Sum('total'), cantidad=Count('id'))
        primera = ventas.order_by('fecha').first()
        ultima = ventas.order_by('-fecha').first()

        cierre = CierreCaja.objects.create(
            fecha_inicio=primera.fecha,
            fecha_fin=ultima.fecha,
            total_ventas=resumen['total'],
            cantidad_ventas=resumen['cantidad'],
            usuario=request.user if request.user.is_authenticated else None,
        )
        ventas.update(cierre=cierre)

        return JsonResponse({'estado': 'ok', 'total': str(resumen['total']), 'cantidad': resumen['cantidad']})


def ventas_de_cierre(request, cierre_id):
    """Devuelve las ventas de un cierre específico (para expandir la fila)."""
    ventas = Venta.objects.filter(cierre_id=cierre_id).values('id', 'fecha', 'total')
    return JsonResponse({'ventas': list(ventas)}, safe=False)


def detalle_venta_ajax(request, venta_id):
    """Devuelve los productos de una venta específica (panel de abajo)."""
    detalles = DetalleVenta.objects.filter(venta_id=venta_id).select_related('producto')
    data = [
        {
            'producto': d.producto.mostrar,
            'cantidad': d.cantidad,
            'precio': str(d.precio),
            'subtotal': str(d.subtotal),
        }
        for d in detalles
    ]
    return JsonResponse({'detalles': data})