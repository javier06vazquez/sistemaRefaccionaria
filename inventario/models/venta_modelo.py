from django.db import models
from django.contrib.auth.models import User


class Venta(models.Model):
    fecha = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    cierre = models.ForeignKey('CierreCaja', on_delete=models.SET_NULL, null=True, blank=True, related_name='ventas')
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)  # 👈 nuevo

    estado = models.CharField(
            max_length=20,
            default="activa"
        )
    
    def __str__(self):
        return f"Venta {self.id}"
    
    #Guarda si esta venta desconto stock. Asi, al cancelarla solo se regresa 
    #stock si de verdad se habia quitado.
    # default=true porque todas las ventas ya existentes descontaron stock, y no queremos que al cancelarlas se regrese stock.
    descuenta_stock = models.BooleanField(default=True)  # Nuevo campo para indicar si se descuenta el stock
    
    # en models/venta.py
