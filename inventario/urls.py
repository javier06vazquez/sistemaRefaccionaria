from django.urls import path
from inventario.views import cierreCaja_Views, inventarioMovimientos_Views
from .views import ProveedorListaView, CategoriaListaView, ProveedorDetalleView, producto_Views, DashboardView
from . import views
from .views.proveedor_Views import ProveedorCrearView, ProveedorEditarView
from .views import kardex_Views
from inventario.views import credito_Views




app_name = 'inventario'

urlpatterns = [
    path('', DashboardView.as_view(), name='index'), 
    
    #PRODUCTO
    path('producto/producto_lista/', producto_Views.ProductoListaView.as_view(), name='productoLista'),
    path('producto/producto_detalle/<int:id_producto>/', producto_Views.ProductoDetalleView.as_view(), name='productoDetalle'),
    path('producto/producto_crear/', producto_Views.ProductoCrearView.as_view(), name='productoCrear'),
    path('producto/producto_editar/<int:pk>/', producto_Views.ProductoEditarView.as_view(), name='editarProducto'),
    path('eliminarProducto/<int:pk>/',producto_Views.EliminarProductoAjax,name='eliminarProductoAjax'),
    path('productos/exportar/', producto_Views.ExportarProdutosExcel, name='exportarProductosExcel'),
    path('productos/buscar_ajax/', producto_Views.buscar_productos_ajax, name='buscar_productos_ajax'),
    path('producto/alertas_stock/', producto_Views.AlertasStockView.as_view(), name='alertasStock'),

    
    #PROVEEDOR EMPRESA
    path('proveedorEmpresa/proveedorEmpresa_lista/', ProveedorListaView.as_view(), name='proveedorEmpresaLista'),
    path('proveedorEmpresa/proveedorEmpresa_detalle/<int:id_proveedor>/', ProveedorDetalleView, name='proveedorEmpresaDetalle'),
    path('proveedorEmpresa/proveedorEmpresa_crear/', ProveedorCrearView.as_view(), name='proveedorEmpresaCrear'),
    path('proveedorEmpresa/proveedorEmpresa_editar/<int:pk>/', ProveedorEditarView.as_view(), name='proveedorEmpresaEditar'),
    path('eliminarProveedor/<int:pk>/',views.EliminarProveedorAjax,name='eliminarProveedorAjax'),
    
    
    #PROVEEDOR CONTACTO
    path('contactoProveedor/contactoProveedor_lista/', views.ContactoProveedorListaView.as_view(), name='contactoProveedorLista'),
    path('contactoProveedor/contactoProveedor_detalle/<int:id_contacto_proveedor>/', views.ContactoProveedorDetalleView, name='contactoProveedorDetalle'),
    path('contactoProveedor/contactoProveedor_crear/', views.ContactoProveedorCrearView.as_view(), name='contactoProveedorCrear'),
    path('contactoProveedor/contactoProveedor_editar/<int:pk>/', views.ContactoProveedorEditarView.as_view(), name='contactoProveedorEditar'),
    path('contacto_proveedor/<int:pk>/', views.EliminarContactoProveedorAjax, name='eliminarContactoProveedorAjax'),
    
    #CATEGORIAS
    path('categoriaProducto/categoria_lista/', CategoriaListaView.as_view(), name='categoriaLista'),
    path('categoriaProducto/categoria_detalle/<int:id_categoria>/', views.CategoriaDetalleView, name='categoriaDetalle'),
    path('categoriaProducto/categoria_crear/', views.CategoriaCrearView.as_view(), name='categoriaCrear'),
    path('categoriaProducto/categoria_editar/<int:pk>/', views.CategoriaEditarView.as_view(), name='categoriaEditar'),
    path('categoriaProducto/<int:pk>/', views.EliminarCategoriaAjax, name='eliminarCategoriaAjax'),
    
    #MARCA PRODUCTO
    path('marcaProducto/marca_lista/', views.MarcaProductoView.as_view(), name='marcaProductoLista'),
    path('marcaProducto/marca_detalle/<int:id_marca>/', views.MarcaProductoDetalleView.as_view(), name='marcaProductoDetalle'),
    path('marcaProducto/marca_crear/', views.MarcaProductoCrearView.as_view(), name='marcaProductoCrear'),
    path('marcaProducto/marca_editar/<int:pk>/', views.MarcaProductoEditarView.as_view(), name='marcaProductoEditar'),
    path('eliminarMarca/<int:pk>/',views.EliminarMarcaAjax,name='eliminarMarcaAjax'),

    
    #VENTA
    path('venta/', views.VentaView, name='venta'),
    path("guardar_venta/", views.GuardarVenta.as_view(), name="guardar_venta"),
    path("ventas_historial/", views.ventas_historial, name="ventas_historial"),
    path('venta/<int:id>/', views.detalle_venta_nota, name='detalle_venta_nota'),
    path("venta/<int:id>/ticket/",views.imprimir_ticket,name="imprimir_ticket",),
    path("cancelar_venta/<int:id>/", views.cancelar_venta, name="cancelar_venta"),
    path('ventas_views/', producto_Views.buscar_productos_ajax, name='buscar_productos_ajax'),

    
    #CONFIGURACION TICKET
    path("configuracion_ticket/", views.configuracion_ticket, name="configuracion_ticket"),
    
    #DASHBOARD
    path('dashboard/dashboard/',views.DashboardView.as_view(),name='dashboard'),
    
    #Movimientos de inventario
    path('inventarioMovimiento/entrada/', inventarioMovimientos_Views.EntradaInventarioView.as_view(), name='entrada_inventario'), # type: ignore
    path('inventarioMovimiento/salida/', inventarioMovimientos_Views.SalidaInventarioView.as_view(), name='salida_inventario'),
    path('inventarioMovimiento/historial/', inventarioMovimientos_Views.MovimientosHistorialView.as_view(), name='historial_movimientos'),
    path('inventarioMovimiento/historial/pdf/', views.historial_pdf, name='historial_movimientos_pdf'),
    
    #Kardex de producto
    path('kardex/kardex/', kardex_Views.KardexProductoView.as_view(), name='kardex_producto'),
    path('kardex/kardex_pdf/<int:producto_id>/pdf/', kardex_Views.kardex_pdf, name='kardex_producto_pdf'),
    
    #CIERRE DE CAJA
    path('cierre_caja/', cierreCaja_Views.CierreCajaListView.as_view(), name='cierre_caja_lista'),
    path('cierre_caja/cerrar/', cierreCaja_Views.cerrar_caja, name='cerrar_caja'),
    path('cierre_caja/<int:cierre_id>/ventas/', cierreCaja_Views.ventas_de_cierre, name='ventas_de_cierre'),
    path('venta/<int:venta_id>/detalle_ajax/', cierreCaja_Views.detalle_venta_ajax, name='detalle_venta_ajax'),
    
    #clientes de credito
    path('credito/cliente_lista/', credito_Views.ClientesCreditoListView.as_view(), name='clientes_credito_lista'),
    path('credito/cliente_detalle/<int:cliente_id>/', credito_Views.DetalleClienteCreditoView.as_view(), name='detalle_cliente_credito'),
    path('credito/clientes/<int:cliente_id>/movimiento/', credito_Views.registrar_movimiento_credito, name='registrar_movimiento_credito'),
    path('credito/clientes/buscar_ajax/', credito_Views.buscar_clientes_credito_ajax, name='buscar_clientes_credito_ajax'),
    path('credito/clientes/<int:cliente_id>/pdf/', credito_Views.detalle_cliente_credito_pdf, name='detalle_cliente_credito_pdf'),
    path('credito/movimiento/<int:movimiento_id>/cancelar/', credito_Views.cancelar_movimiento_credito, name='cancelar_movimiento_credito'),
    path('eliminarCliente/<int:pk>/',views.EliminarClienteAjax,name='eliminarClienteAjax'),
    path('credito/movimiento/<int:movimiento_id>/nota/', credito_Views.nota_movimiento_credito_pdf, name='nota_credito_pdf'),
    path('credito/cliente/<int:cliente_id>/corte/', credito_Views.corte_saldo_cliente_pdf, name='corte_saldo_cliente_pdf'),
    path('credito/movimiento/<int:movimiento_id>/editar/', credito_Views.editar_movimiento_credito, name='editar_movimiento_credito'),
    path('credito/movimiento/<int:movimiento_id>/obtener/', credito_Views.obtener_movimiento_credito, name='obtener_movimiento_credito'),

]
