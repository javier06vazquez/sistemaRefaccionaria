from django.db import transaction
from inventario.models import Producto, MovimientoInventario
from decimal import Decimal

from django.db.models import DecimalField, ExpressionWrapper, F, Sum
IVA = Decimal("0.16")
class InventarioService:

    @staticmethod
    @transaction.atomic
    def registrar_entrada(producto_id, cantidad, motivo, observaciones='', usuario=None):
        producto = Producto.objects.select_for_update().get(id=producto_id)
        producto.stock += cantidad
        producto.save()
        return MovimientoInventario.objects.create(
            producto=producto, tipo='ENTRADA', cantidad=cantidad,
            motivo=motivo, observaciones=observaciones, usuario=usuario,
        )

    @staticmethod
    @transaction.atomic
    def registrar_salida(producto_id, cantidad, motivo, observaciones='', usuario=None):
        producto = Producto.objects.select_for_update().get(id=producto_id)
        if producto.stock < cantidad:
            raise ValueError(f"Stock insuficiente para {producto.nombre}. Disponible: {producto.stock}")
        producto.stock -= cantidad
        producto.save()
        return MovimientoInventario.objects.create(
            producto=producto, tipo='SALIDA', cantidad=cantidad,
            motivo=motivo, observaciones=observaciones, usuario=usuario,
        )

    @staticmethod
    @transaction.atomic
    def registrar_multiple(tipo, items, usuario=None):
        """
        tipo: 'ENTRADA' o 'SALIDA'
        items: lista de dicts [{producto_id, cantidad, motivo, observaciones}, ...]
        Si CUALQUIER producto falla (ej. stock insuficiente), se cancela todo el lote.
        """
        resultados = []
        for item in items:
            if tipo == 'ENTRADA':
                mov = InventarioService.registrar_entrada(
                    producto_id=item['producto_id'],
                    cantidad=item['cantidad'],
                    motivo=item['motivo'],
                    observaciones=item.get('observaciones', ''),
                    usuario=usuario,
                )
            else:
                mov = InventarioService.registrar_salida(
                    producto_id=item['producto_id'],
                    cantidad=item['cantidad'],
                    motivo=item['motivo'],
                    observaciones=item.get('observaciones', ''),
                    usuario=usuario,
                )
            resultados.append(mov)
        return resultados
    
    @staticmethod
    def valor_inventario():
        """
        Cuánto dinero hay invertido en mercancía: suma de stock × precio_compra
        de los productos con existencias. precio_compra se guarda SIN IVA.
        """
        valor = ExpressionWrapper(
            F("stock") * F("precio_compra"),
            output_field=DecimalField(max_digits=14, decimal_places=2),
        )
        sin_iva = (
            Producto.objects.filter(stock__gt=0).aggregate(total=Sum(valor))["total"]
            or Decimal("0")
        )
        return {
            "sin_iva": sin_iva,
            "con_iva": (sin_iva * (1 + IVA)).quantize(Decimal("0.01")),
        }