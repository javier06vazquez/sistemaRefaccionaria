from django.contrib import admin

from inventario.models import ClienteCredito


@admin.register(ClienteCredito)
class ClienteCreditoAdmin(admin.ModelAdmin):
    # Columnas que se ven en la lista de clientes
    list_display = ("nombre", "telefono", "usuario", "activo")
    # Caja de búsqueda por nombre
    search_fields = ("nombre",)