from django.shortcuts import redirect, render
from django.urls import reverse


class LoginRequeridoMiddleware:
    """
    1. Exige login para cualquier página que no sea pública.
    2. Superusuarios y el grupo Administrador ven todo.
    3. Todos los demás SOLO ven las rutas de su rol (negar por defecto).
       Un usuario sin rol no ve nada.
    4. El rol Cliente solo ve /mi-credito/ (su propia cuenta).
    """

    RUTAS_PUBLICAS = [
        '/login/',
        '/logout/',
        '/admin/',
        '/static/',
        '/media/',
    ]

    RUTAS_PERMITIDAS_POR_ROL = {
        'Bodega': [
            '/inventarioMovimiento/salida/',
            '/producto/producto_lista/',
            '/producto/producto_detalle/',
            '/productos/buscar_ajax/',
        ],
        'Mostrador': [
            '/producto/producto_lista/',
            '/producto/producto_detalle/',
            '/productos/exportar/',
            '/inventarioMovimiento/salida/',
            '/inventarioMovimiento/historial/',
            '/productos/buscar_ajax/',
            '/dashboard/dashboard/',
            '/credito/cliente_lista/',
            '/credito/cliente_detalle/',
            '/credito/clientes/',
            '/credito/movimiento/',
            '/credito/cliente/',
            

        ],
        'Oficina': [
            '/dashboard/dashboard/',
            '/producto/producto_lista/',
            '/producto/producto_detalle/',
            '/producto/producto_crear/',
            '/producto/producto_editar/',
            '/eliminarProducto/',
            '/productos/buscar_ajax/',
            '/inventarioMovimiento/salida/',
            '/inventarioMovimiento/entrada/',
            '/inventarioMovimiento/historial/',
            '/proveedorEmpresa/proveedorEmpresa_lista/',
            '/proveedorEmpresa/proveedorEmpresa_detalle/',
            '/proveedorEmpresa/proveedorEmpresa_editar/',
            '/eliminarProveedor/',
            '/contactoProveedor/contactoProveedor_lista/',
            '/contactoProveedor/contactoProveedor_detalle/',
            '/contactoProveedor/contactoProveedor_crear/',
            '/contactoProveedor/contactoProveedor_editar/',
            '/contacto_proveedor/',
            '/categoriaProducto/categoria_lista/',
            '/categoriaProducto/categoria_detalle/',
            '/categoriaProducto/categoria_crear/',
            '/categoriaProducto/categoria_editar/',
            '/categoriaProducto/',
        ],
        'Cliente': [
            '/mi-credito/',
        ],
    }

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        ruta_es_publica = any(request.path.startswith(r) for r in self.RUTAS_PUBLICAS)
        
        # 1. Sin sesión y ruta no pública -> manda a login
        if not request.user.is_authenticated and not ruta_es_publica:
            return redirect(f"{reverse('login')}?next={request.path}")
        
        # 2. Con sesión: solo pasa lo que está permitido explícitamente
        if request.user.is_authenticated and not ruta_es_publica:
            grupos_usuario = set(request.user.groups.values_list('name', flat=True))

            # 2a. Acceso total: superusuario o grupo Administrador
            if request.user.is_superuser or 'Administrador' in grupos_usuario:
                return self.get_response(request)

            # 2b. Todos los demás: solo las rutas de SUS roles
            permitido = False
            for rol in grupos_usuario:
                rutas_del_rol = self.RUTAS_PERMITIDAS_POR_ROL.get(rol, [])
                if any(request.path.startswith(r) for r in rutas_del_rol):
                    permitido = True
                    break

            if not permitido:
                # Un cliente que intenta salir de su portal, regresa a él
                if 'Cliente' in grupos_usuario:
                    return redirect('/mi-credito/')
                return render(request, 'errors/sin_permiso.html', status=403)
        return self.get_response(request)