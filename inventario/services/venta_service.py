from django.db import transaction
from inventario.models import Producto, Venta, DetalleVenta
from inventario.services.credito_service import CreditoService


class VentaService:

    @staticmethod
    @transaction.atomic
    def registrar_venta(carrito, total, es_credito=False, cliente_credito_id=None, usuario=None):
        """
        Registra una venta (contado o crédito) y descuenta el stock.

        carrito: lista de dicts [{id, nombre, cantidad, precio, subtotal}, ...]
        total: total de la venta
        es_credito: True si se carga a la cuenta de un cliente de crédito
        cliente_credito_id: ID del cliente (obligatorio si es_credito=True)
        usuario: quien registra la venta

        Devuelve un dict con el resultado: {'tipo': 'credito'} o {'tipo': 'contado', 'venta_id': X}
        """
        if not carrito:
            raise ValueError("El carrito está vacío.")

        if es_credito and not cliente_credito_id:
            raise ValueError("Selecciona un cliente de crédito.")

        # 1) Descuenta stock — esto aplica igual para contado y crédito
        for item in carrito:
            producto = Producto.objects.select_for_update().get(id=item["id"])
            if producto.stock < item["cantidad"]:
                raise ValueError(f"Stock insuficiente para {producto.nombre}.")
            producto.stock -= item["cantidad"]
            producto.save()

        # 2) Camino CRÉDITO: no se crea una Venta, se carga a la cuenta del cliente
        if es_credito:
            nombres = ", ".join(
                [f"{item['cantidad']}x {item['nombre']}" for item in carrito]
            )
            concepto = f"Venta a crédito: {nombres}"

            productos_detalle = [
                {
                    "producto_id": item["id"],
                    "concepto": item["nombre"],
                    "cantidad": item["cantidad"],
                    "precio": item["precio"],
                }
                for item in carrito
            ]

            CreditoService.registrar_cargo(
                cliente_id=cliente_credito_id,
                monto=total,
                concepto=concepto,
                usuario=usuario,
                productos=productos_detalle,
            )
            return {"tipo": "credito"}

        # 3) Camino CONTADO: crea la Venta y sus DetalleVenta
        venta = Venta.objects.create(
            total=total,
            estado="activa",
            usuario=usuario,
        )
        for item in carrito:
            DetalleVenta.objects.create(
                venta=venta,
                producto_id=item["id"],
                cantidad=item["cantidad"],
                precio=item["precio"],
                subtotal=item["subtotal"],
            )
        return {"tipo": "contado", "venta_id": venta.id}
    
    @staticmethod
    @transaction.atomic
    def cancelar_venta(venta_id):
        """
        Cancela una venta y regresa el stock de los productos vendidos.
        """
        venta = Venta.objects.select_for_update().get(id=venta_id)

        if venta.estado == "cancelada":
            raise ValueError("La venta ya está cancelada.")

        detalles = DetalleVenta.objects.filter(venta=venta)
        for d in detalles:
            producto = d.producto
            producto.stock += d.cantidad
            producto.save()

        venta.estado = "cancelada"
        venta.save()