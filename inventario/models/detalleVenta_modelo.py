from .producto_modelo import Producto
from .venta_modelo import Venta
from django.db import models

class DetalleVenta(models.Model):
    venta = models.ForeignKey(Venta, on_delete=models.CASCADE, related_name="detalles")

    producto = models.ForeignKey(
        Producto,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
    )
    
    descripcion = models.CharField(max_length=200, blank=True, default="")
    
    cantidad = models.PositiveIntegerField()
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    
    @property
    def nombre_mostrar(self):
        """Lo que se imprime en el ticket. Las ventas viejas no tienen descripcion."""
        if self.descripcion:
            return self.descripcion
        return self.producto.nombre if self.producto else "—"
    @property
    def codigo_mostrar(self):
        return self.producto.codigo if self.producto else "—"
    