from django.db import models
from django.contrib.auth.models import User

class ClienteCredito(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    telefono = models.CharField(max_length=20, blank=True)
    contacto = models.CharField(max_length=100, blank=True)
    notas = models.TextField(blank=True)
    activo = models.BooleanField(default=True)
    creado = models.DateTimeField(auto_now_add=True)
    
# El usuario con el que ESTE cliente inicia sesión para ver su crédito.
    # null=True: la mayoría de los clientes no tienen acceso al sistema.
    usuario = models.OneToOneField(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="cliente_credito",
    )
    
    class Meta:
        ordering = ['nombre']

    def __str__(self):
        return self.nombre