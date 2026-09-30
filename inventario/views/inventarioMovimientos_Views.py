import json
from django.shortcuts import render
from django.http import JsonResponse
from datetime import timedelta
from django.views import View
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.utils import timezone
from xhtml2pdf import pisa
from inventario.models import MovimientoInventario
from inventario.services.inventario_service import InventarioService


class EntradaInventarioView(View):
    def get(self, request):
        return render(request, 'inventarioMovimiento/entrada.html', {'titulo': 'Entrada de inventario'})

    def post(self, request):
        try:
            data = json.loads(request.body)
            items = data.get('items', [])
            if not items:
                return JsonResponse({'estado': 'error', 'mensaje': 'Agrega al menos un producto.'})

            InventarioService.registrar_multiple(
                tipo='ENTRADA',
                items=items,
                usuario=request.user if request.user.is_authenticated else None,
            )
            return JsonResponse({'estado': 'ok', 'cantidad': len(items)})
        except Exception as e:
            return JsonResponse({'estado': 'error', 'mensaje': str(e)})


class SalidaInventarioView(View):
    def get(self, request):
        return render(request, 'inventarioMovimiento/salida.html', {'titulo': 'Salida de inventario'})

    def post(self, request):
        try:
            data = json.loads(request.body)
            items = data.get('items', [])
            if not items:
                return JsonResponse({'estado': 'error', 'mensaje': 'Agrega al menos un producto.'})

            InventarioService.registrar_multiple(
                tipo='SALIDA',
                items=items,
                usuario=request.user if request.user.is_authenticated else None,
            )
            return JsonResponse({'estado': 'ok', 'cantidad': len(items)})
        except Exception as e:
            return JsonResponse({'estado': 'error', 'mensaje': str(e)})


def _filtrar_movimientos(request):
    """Aplica los filtros de fecha y tipo que vengan en el GET. Reutilizable para pantalla y PDF."""
    movimientos = MovimientoInventario.objects.select_related('producto', 'usuario').order_by('-fecha')

    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')
    tipo = request.GET.get('tipo')

    if fecha_inicio:
        movimientos = movimientos.filter(fecha__date__gte=fecha_inicio)
    if fecha_fin:
        movimientos = movimientos.filter(fecha__date__lte=fecha_fin)
    if tipo in ('ENTRADA', 'SALIDA'):
        movimientos = movimientos.filter(tipo=tipo)

    return movimientos, fecha_inicio, fecha_fin, tipo


class MovimientosHistorialView(View):
    def get(self, request):
        movimientos, fecha_inicio, fecha_fin, tipo = _filtrar_movimientos(request)

        context = {
            'titulo': 'Historial de Movimientos',
            'movimientos': movimientos[:300],  # límite razonable para no saturar la pantalla
            'fecha_inicio': fecha_inicio,
            'fecha_fin': fecha_fin,
            'tipo': tipo,
        }
        return render(request, 'inventarioMovimiento/historial.html', context)


def historial_pdf(request):
    """Genera el PDF con el mismo filtro que se esté usando en pantalla."""
    movimientos, fecha_inicio, fecha_fin, tipo = _filtrar_movimientos(request)

    html = render_to_string('inventarioMovimiento/historial_pdf.html', {
        'movimientos': movimientos,
        'fecha_inicio': fecha_inicio,
        'fecha_fin': fecha_fin,
        'tipo': tipo,
        'fecha_generacion': timezone.localtime(),
    })

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="historial_movimientos.pdf"'
    pisa.CreatePDF(html, dest=response)
    return response