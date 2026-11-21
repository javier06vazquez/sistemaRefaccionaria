from django.db import transaction
from django.db.models import Sum
from inventario.models import ClienteCredito, MovimientoCredito, Producto


class CreditoService:

    @staticmethod
    def calcular_saldo(cliente):
        """Saldo positivo = el cliente te debe. Ignora movimientos cancelados."""
        cargos = MovimientoCredito.objects.filter(
            cliente=cliente, tipo='CARGO', cancelado=False
        ).aggregate(t=Sum('monto'))['t'] or 0
        abonos = MovimientoCredito.objects.filter(
            cliente=cliente, tipo='ABONO', cancelado=False
        ).aggregate(t=Sum('monto'))['t'] or 0
        return cargos - abonos

    @staticmethod
    def registrar_cargo(cliente_id, monto, concepto='', usuario=None, productos=None):
        """
        productos (opcional): lista de dicts [{producto_id, cantidad, precio}, ...]
        Se guarda directo en el campo productos_json del propio movimiento,
        para poder regresar el stock si se cancela después.
        """
        cliente = ClienteCredito.objects.get(id=cliente_id)
        return MovimientoCredito.objects.create(
            cliente=cliente, tipo='CARGO', monto=monto, concepto=concepto, usuario=usuario,
            productos_json=productos or [],
        )
        
    
    
    @staticmethod
    def registrar_abono(cliente_id, monto, concepto='', usuario=None):
        cliente = ClienteCredito.objects.get(id=cliente_id)
        return MovimientoCredito.objects.create(
            cliente=cliente, tipo='ABONO', monto=monto, concepto=concepto, usuario=usuario,
        )

    @staticmethod
    @transaction.atomic
    def cancelar_movimiento(movimiento_id):
        """
        Marca un movimiento como cancelado (no se borra, conserva el rastro).
        Si es un CARGO con productos guardados en productos_json, regresa el stock.
        """
        movimiento = MovimientoCredito.objects.select_for_update().get(id=movimiento_id)

        if movimiento.cancelado:
            raise ValueError("Este movimiento ya estaba cancelado.")
        
        if movimiento.tipo == 'CARGO' and movimiento.productos_json:
            for item in movimiento.productos_json:
                producto_id = item.get('producto_id')
                if producto_id and item.get('descontando_stock', True):
                    producto = Producto.objects.select_for_update().get(id=producto_id)
                    producto.stock += item.get('cantidad', 0)
                    producto.save()

        movimiento.cancelado = True
        movimiento.save()
        return movimiento
    
    
    @staticmethod
    def historial_con_saldo(cliente):
        movimientos = MovimientoCredito.objects.filter(cliente=cliente).order_by('fecha')
        saldo = 0
        resultado = []
        for m in movimientos:
            if not m.cancelado:
                saldo += m.monto if m.tipo == 'CARGO' else -m.monto
            resultado.append({
                'id': m.id,
                'fecha': m.fecha, 'tipo': m.tipo, 'concepto': m.concepto.replace('', '\n') if m.concepto else '',
                'cargo': m.monto if m.tipo == 'CARGO' else None,
                'abono': m.monto if m.tipo == 'ABONO' else None,
                'saldo': saldo, 'usuario': m.usuario,
                'cancelado': m.cancelado,
                'productos': m.productos_json,   # 👈 agregar esta línea en ambas funciones

                
            })
        return resultado

    @staticmethod
    def historial_por_periodo(cliente, fecha_inicio=None, fecha_fin=None):
        """
        Calcula el saldo que traía el cliente ANTES de fecha_inicio,
        y devuelve solo los movimientos DENTRO del rango, con su saldo
        corriendo desde ese punto.
        """
        todos = MovimientoCredito.objects.filter(cliente=cliente).order_by('fecha')

        saldo_inicial = 0
        movimientos_rango = []

        for m in todos:
            fecha_mov = m.fecha.date()

            if fecha_inicio and fecha_mov < fecha_inicio:
                if not m.cancelado:
                    saldo_inicial += m.monto if m.tipo == 'CARGO' else -m.monto
                continue

            if fecha_fin and fecha_mov > fecha_fin:
                continue

            movimientos_rango.append(m)

        saldo = saldo_inicial
        resultado = []
        for m in movimientos_rango:
            if not m.cancelado:
                saldo += m.monto if m.tipo == 'CARGO' else -m.monto
            resultado.append({
                'id': m.id, 'fecha': m.fecha, 'tipo': m.tipo, 'concepto': m.concepto.replace('', '\n') if m.concepto else '',
                'cargo': m.monto if m.tipo == 'CARGO' else None,
                'abono': m.monto if m.tipo == 'ABONO' else None,
                'saldo': saldo, 'cancelado': m.cancelado,
                'productos': m.productos_json,   # 👈 agregar esta línea en ambas funciones

            })

        return {'saldo_inicial': saldo_inicial, 'movimientos': resultado, 'saldo_final': saldo}

    @staticmethod
    def saldo_total_todos_los_clientes():
        total = 0
        for cliente in ClienteCredito.objects.filter(activo=True):
            total += CreditoService.calcular_saldo(cliente)
        return total
    
    @staticmethod
    def lineas_pendientes(cliente):
        """
        Devuelve la lista de conceptos que aún no se han cubierto, aplicando
        los abonos contra los cargos más antiguos primero (FIFO).
        Si un cargo se paga parcialmente, se muestra con su monto restante.
        """
        movimientos = MovimientoCredito.objects.filter(
            cliente=cliente, cancelado=False
        ).order_by('fecha')

        lineas = []
        total_abonos = 0

        for m in movimientos:
            if m.tipo == 'ABONO':
                total_abonos += float(m.monto)
                continue

            # CARGO: si tiene detalle de productos, una línea por cada concepto;
            # si no, una sola línea usando el concepto/monto del movimiento.
            if m.productos_json:
                for item in m.productos_json:
                    cantidad = float(item.get('cantidad', 1))
                    precio = float(item.get('precio', 0))
                    subtotal = item.get('subtotal', cantidad * precio)
                    lineas.append({
                        'fecha': m.fecha,
                        'concepto': item.get('concepto', '—'),
                        'cantidad': cantidad,
                        'precio': precio,
                        'subtotal': float(subtotal),
                        'pendiente': float(subtotal),
                    })
            else:
                lineas.append({
                    'fecha': m.fecha,
                    'concepto': m.concepto or '—',
                    'cantidad': 1,
                    'precio': float(m.monto),
                    'subtotal': float(m.monto),
                    'pendiente': float(m.monto),
                })

        # Aplica los abonos contra las líneas más antiguas primero
        restante = total_abonos
        for linea in lineas:
            if restante <= 0:
                break
            aplicado = min(restante, linea['pendiente'])
            linea['pendiente'] -= aplicado
            restante -= aplicado

        # Solo devolvemos lo que sigue sin cubrirse
        pendientes = [l for l in lineas if l['pendiente'] > 0.009]
        return pendientes
    
    
    @staticmethod
    @transaction.atomic
    def editar_cargo(movimiento_id, monto, concepto='', producto=None):
        """ Edita un cargo existente (conceptos y montos). No permite editar cargos cancelados"""
        movimiento = MovimientoCredito.objects.select_for_update().get(id=movimiento_id)
        
        if movimiento.cancelado:
            raise ValueError("No se puede editar un cargo cancelado.")
        if movimiento.tipo != 'CARGO':
            raise ValueError("Solo se pueden editar cargos.")
        
        movimiento.monto = monto
        movimiento.concepto = concepto
        movimiento.productos_json = producto or []
        movimiento.save()
        return movimiento