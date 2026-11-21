from django.views import View
from django.shortcuts import render
from inventario.models.producto_modelo import Producto
from inventario.models.venta_modelo import Venta
from django.http import JsonResponse
import json
from inventario.services.venta_service import VentaService
import logging

logger = logging.getLogger(__name__)

def VentaView(request):
    productos = Producto.objects.all()
    data = {
        "titulo": "Venta de Productos",
        "mensaje": "Bienvenido al sistema de venta de productos.",
        "productos": productos,
    }
    return render(request, "puntoVenta/venta.html", context=data)


class GuardarVenta(View):

    def post(self, request):
        try:
            data = json.loads(request.body)

            # Ya no se manda el total: el service lo calcula con los renglones
            resultado = VentaService.registrar_venta(
                carrito=data.get("carrito", []),
                es_credito=data.get("es_credito", False),
                cliente_credito_id=data.get("cliente_credito_id"),
                usuario=request.user if request.user.is_authenticated else None,
                descontar_stock=data.get("descontar_stock", True),
            )
            return JsonResponse({"ok": True, **resultado})

        except json.JSONDecodeError:
            # Va ANTES de ValueError porque JSONDecodeError es hija de ValueError:
            # Python usa el primer except que coincide.
            return JsonResponse({"ok": False, "error": "Los datos de la venta llegaron dañados."})
        except ValueError as e:
            # Errores que escribimos nosotros para el cajero: sí se muestran
            return JsonResponse({"ok": False, "error": str(e)})
        except Exception:
            # Lo inesperado se guarda en el log, no se le enseña al navegador
            logger.exception("Error al guardar venta")
            return JsonResponse({"ok": False, "error": "Ocurrió un error al guardar la venta."})     
def ventas_historial(request):
    """Trae todas las ventas del punto de venta ordenadas desde la más reciente"""
    ventas = Venta.objects.all().order_by("-fecha")
    data = {
        "titulo": "Historial de Ventas",
        "mensaje": "Todas las ventas registradas en el sistema.",
        "ventas": ventas,
    }
    return render(request, "puntoVenta/ventas_historial.html", data)

def cancelar_venta(request, id):
    if request.method != "POST":
        return JsonResponse({"estado": "error", "mensaje": "Método no permitido"})

    try:
        VentaService.cancelar_venta(id)
        return JsonResponse({"estado": "ok"})
    except Exception as e:
        return JsonResponse({"estado": "error", "mensaje": str(e)})



