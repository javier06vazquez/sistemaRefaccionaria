from decimal import Decimal, InvalidOperation

from django.db import transaction

from inventario.models import Producto, Venta, DetalleVenta
from inventario.services.credito_service import CreditoService


class VentaService:

    @staticmethod
    def _limpiar_carrito(carrito):
        """
        Valida cada renglón que manda el navegador y lo convierte a datos seguros.
        Nunca confiamos en los números del navegador: el subtotal y el total
        se vuelven a calcular aquí.

        Cada renglón puede ser:
          - un producto registrado:  {"id": 15, "nombre": "...", "cantidad": 2, "precio": 120}
          - un concepto libre:       {"id": None, "nombre": "Mano de obra", "cantidad": 1, "precio": 200}
        """
        renglones = []
        for item in carrito:
            try:
                cantidad = int(item.get("cantidad", 0))
                precio = Decimal(str(item.get("precio", 0))).quantize(Decimal("0.01"))
            except (ValueError, TypeError, InvalidOperation):
                raise ValueError("Hay una cantidad o un precio inválido en la nota.")

            if cantidad <= 0:
                raise ValueError("La cantidad debe ser mayor a cero.")
            if precio < 0:
                raise ValueError("El precio no puede ser negativo.")

            producto_id = item.get("id") or None
            descripcion = str(item.get("nombre", "")).strip()[:200]

            if producto_id is None and not descripcion:
                raise ValueError("Un concepto libre necesita descripción.")

            renglones.append({
                "producto_id": producto_id,
                "descripcion": descripcion,
                "cantidad": cantidad,
                "precio": precio,
                "subtotal": precio * cantidad,
            })
        return renglones

    @staticmethod
    @transaction.atomic
    def registrar_venta(carrito, es_credito=False, cliente_credito_id=None,
                        usuario=None, descontar_stock=True):
        """
        Registra una venta (contado o crédito).
        descontar_stock: el switch del punto de venta. False = no toca inventario.

        Devuelve {'tipo': 'credito'} o {'tipo': 'contado', 'venta_id': X}
        """
        if not carrito:
            raise ValueError("La nota está vacía.")
        if es_credito and not cliente_credito_id:
            raise ValueError("Selecciona un cliente de crédito.")

        renglones = VentaService._limpiar_carrito(carrito)
        descontar = bool(descontar_stock)

        # 1) Productos registrados: tomar el nombre REAL de la base de datos
        #    y, solo si el switch está prendido, descontar stock.
        for r in renglones:
            if r["producto_id"] is None:
                continue  # concepto libre: no toca inventario

            producto = Producto.objects.select_for_update().get(id=r["producto_id"])
            r["descripcion"] = producto.nombre

            if descontar:
                if producto.stock < r["cantidad"]:
                    raise ValueError(f"Stock insuficiente para {producto.nombre}.")
                producto.stock -= r["cantidad"]
                producto.save()

        total = sum(r["subtotal"] for r in renglones)

        # 2) Camino CRÉDITO: se carga a la cuenta del cliente
        if es_credito:
            nombres = ", ".join(f"{r['cantidad']}x {r['descripcion']}" for r in renglones)
            productos_detalle = [
                {
                    "producto_id": r["producto_id"],
                    "concepto": r["descripcion"],
                    "cantidad": r["cantidad"],
                    "precio": float(r["precio"]),
                    # Al cancelar el cargo, solo se regresa stock si aquí se descontó
                    "descontado": descontar and r["producto_id"] is not None,
                }
                for r in renglones
            ]
            CreditoService.registrar_cargo(
                cliente_id=cliente_credito_id,
                monto=total,
                concepto=f"Venta a crédito: {nombres}",
                usuario=usuario,
                productos=productos_detalle,
            )
            return {"tipo": "credito"}

        # 3) Camino CONTADO: crea la Venta y sus renglones
        venta = Venta.objects.create(
            total=total,
            estado="activa",
            usuario=usuario,
            descuenta_stock=descontar,
        )
        for r in renglones:
            DetalleVenta.objects.create(
                venta=venta,
                producto_id=r["producto_id"],
                descripcion=r["descripcion"],
                cantidad=r["cantidad"],
                precio=r["precio"],
                subtotal=r["subtotal"],
            )
        return {"tipo": "contado", "venta_id": venta.id}
    
    @staticmethod
    @transaction.atomic
    def cancelar_venta(venta_id):
        """Cancela una venta. Regresa stock solo si esa venta lo había descontado."""
        venta = Venta.objects.select_for_update().get(id=venta_id)

        if venta.estado == "cancelada":
            raise ValueError("La venta ya está cancelada.")

        if venta.descuenta_stock:
            for d in venta.detalles.filter(producto__isnull=False):
                producto = Producto.objects.select_for_update().get(id=d.producto_id)
                producto.stock += d.cantidad
                producto.save()

        venta.estado = "cancelada"
        venta.save()
        return venta