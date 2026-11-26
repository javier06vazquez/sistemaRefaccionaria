from django.views import View
from django.shortcuts import render
from django.db.models import F, Sum
from django.utils import timezone

from inventario.models.catalogo.categoria_producto import CategoriaProducto
from inventario.models.catalogo.marca_producto import MarcaProducto
from inventario.models.contactoProveedor_modelo import ContactoProveedor
from inventario.models.producto_modelo import Producto
from inventario.models.provedorEmpresa_modelo import ProveedorEmpresa
from inventario.models.venta_modelo import Venta
from inventario.services.inventario_service import InventarioService
InventarioService.valor_inventario()


class DashboardView(View):
    def get(self, request):
        hoy = timezone.localdate()
        # Ventas de hoy
        ventas_hoy = Venta.objects.filter(fecha__date=hoy, estado="activa")
        total_ventas_hoy = ventas_hoy.aggregate(total=Sum("total"))["total"] or 0
        cantidad_ventas_hoy = ventas_hoy.count()

        # Inventario
        total_productos = Producto.objects.count()
        productos_stock_bajo = Producto.objects.filter(
            stock__lte=F("stock_minimo"), stock__gt=0
        ).select_related("categoria")[:8]
        total_stock_bajo = Producto.objects.filter(stock__lte=F("stock_minimo")).count()
        total_agotados = Producto.objects.filter(stock=0).count()

        # Catálogo
        total_marcas = MarcaProducto.objects.count()
        total_proveedores = ProveedorEmpresa.objects.count()
        total_categorias = CategoriaProducto.objects.count()
        total_contactos = ContactoProveedor.objects.count()
        productos_con_iva = Producto.objects.filter(tiene_iva=True).count()

        context = {
            "titulo": "Dashboard",
            "total_ventas_hoy": total_ventas_hoy,
            "cantidad_ventas_hoy": cantidad_ventas_hoy,
            "total_productos": total_productos,
            "productos_stock_bajo": productos_stock_bajo,
            "total_stock_bajo": total_stock_bajo,
            "total_agotados": total_agotados,
            "total_marcas": total_marcas,
            "total_proveedores": total_proveedores,
            "total_categorias": total_categorias,
            "total_contactos": total_contactos,
            "productos_con_iva": productos_con_iva,
        }
        es_admin = (
            request.user.is_superuser
            or request.user.groups.filter(name="Administrador").exists()
        )
        context["puede_ver_inversion"] = es_admin
        if es_admin:
            context["inversion"] = InventarioService.valor_inventario()
            
        return render(request, "dashboard/dashboard.html", context)

