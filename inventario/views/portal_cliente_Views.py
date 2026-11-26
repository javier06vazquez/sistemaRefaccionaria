import json
import logging

from django.http import Http404, JsonResponse
from django.shortcuts import render

from inventario.services.credito_service import CreditoService

logger = logging.getLogger(__name__)


def _cliente_de(request):
    """
    Devuelve el cliente de crédito de QUIEN INICIÓ SESIÓN.
    Nunca se toma un id de la URL: así un cliente no puede ver a otro.
    """
    cliente = getattr(request.user, "cliente_credito", None)
    if cliente is None:
        raise Http404("Este usuario no tiene una cuenta de crédito.")
    return cliente


def mi_credito(request):
    """Estado de cuenta del cliente que inició sesión."""
    cliente = _cliente_de(request)

    resultado = CreditoService.historial_por_periodo(cliente)
    movimientos = [m for m in reversed(resultado["movimientos"]) if not m["cancelado"]]

    return render(request, "credito/cliente_detalle.html", {
        "titulo": "Mi crédito",
        "cliente": cliente,
        "movimientos": movimientos,
        "saldo_actual": CreditoService.calcular_saldo(cliente),
        "es_portal": True,   # ← oculta lo que solo ve el administrador
    })


def mi_credito_registrar_cargo(request):
    """El cliente registra un cargo en SU PROPIA cuenta. Solo cargos, nunca abonos."""
    if request.method != "POST":
        return JsonResponse({"estado": "error", "mensaje": "Método no permitido"})

    cliente = _cliente_de(request)

    try:
        data = json.loads(request.body)
        monto = float(data.get("monto", 0))
        if monto <= 0:
            return JsonResponse({"estado": "error", "mensaje": "El monto debe ser mayor a cero."})

        CreditoService.registrar_cargo(
            cliente_id=cliente.id,          # ← de la sesión, NO del navegador
            monto=monto,
            concepto=data.get("concepto", ""),
            usuario=request.user,
            productos=data.get("productos", []),
        )
        return JsonResponse({"estado": "ok"})

    except (ValueError, json.JSONDecodeError):
        return JsonResponse({"estado": "error", "mensaje": "Los datos del cargo no son válidos."})
    except Exception:
        logger.exception("Error al registrar cargo desde el portal del cliente")
        return JsonResponse({"estado": "error", "mensaje": "Ocurrió un error. Intenta de nuevo."})