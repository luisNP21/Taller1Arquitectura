from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib import messages
from django.conf import settings
from django.utils import timezone
from string import ascii_uppercase
from django.http import JsonResponse, HttpResponse
from .forms import ClientesForm, ZapatoForm, QRFileUploadForm
from .models import Cliente, Zapato, Pedido
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from io import BytesIO
import os
import json
import qrcode
import cv2
import re
import numpy as np
from pyzbar.pyzbar import decode
from pdf2image import convert_from_bytes
from django.db.models import Q

# -----------------------------
# Manejo de errores CSRF
# -----------------------------
def csrf_failure(request, reason=""):
    # Esta vista se muestra cuando ocurre un error de verificación CSRF
    # El error CSRF generalmente ocurre cuando un formulario no tiene un token de seguridad
    return render(request, 'csrf_error.html', {'reason': reason})

# -----------------------------
# Autenticación
# -----------------------------
def login_view(request):
    # Vista que maneja el inicio de sesión del usuario
    if request.method == "POST":
        # Se obtiene el nombre de usuario y la contraseña del formulario
        username = request.POST['username']
        password = request.POST['password']

        # Se intenta autenticar al usuario
        user = authenticate(request, username=username, password=password)

        if user is not None:
            # Si la autenticación es exitosa, se inicia sesión con el usuario
            login(request, user)
            # Redirige a la vista principal después de iniciar sesión
            return redirect('landing')
        else:
            # Si la autenticación falla, se muestra un mensaje de error
            return render(request, 'login.html', {'error': 'Credenciales inválidas'})
    
    # Si la solicitud es GET, simplemente se muestra el formulario de inicio de sesión
    return render(request, 'login.html')

def logout_view(request):
    # Esta vista maneja el cierre de sesión del usuario
    logout(request)
    # Redirige al usuario de vuelta a la página de inicio de sesión
    return redirect('login')

@login_required
def landing_view(request):
    # Esta vista es la página principal a la que se accede después de iniciar sesión
    # Sólo los usuarios autenticados pueden acceder a ella
    return render(request, 'landing.html')

# -----------------------------
# Vista de categorías de zapatos
# -----------------------------

def categorias_view(request):
    # Vista que muestra todas las categorías de zapatos
    categorias = [
        {"nombre": "Apache Hombre", "imagen": "images/apacheH1.png", "url": "apache_hombre"},
        {"nombre": "Apolo Hombre", "imagen": "images/apoloH1.png", "url": "apolo_hombre"},
        {"nombre": "Amaka Hombre", "imagen": "images/amakaH1.png", "url": "amaka_hombre"},
        {"nombre": "Nautico Hombre", "imagen": "images/nauticoH1.png", "url": "nautico_hombre"},
        {"nombre": "Bota Hombre", "imagen": "images/botaH1.png", "url": "bota_hombre"},
        {"nombre": "Casual Hombre", "imagen": "images/casualH1.png", "url": "casual_hombre"},
        {"nombre": "Apache Mujer", "imagen": "images/apacheM1.png", "url": "apache_mujer"},
        {"nombre": "Bota Mujer", "imagen": "images/botaM1.png", "url": "bota_mujer"},
    ]
    # Retorna una página con las categorías de zapatos
    return render(request, 'categorias.html', {"categorias": categorias})

# -----------------------------
# Vista genérica para mostrar modelos
# -----------------------------

COLORES = ['Negro', 'Gris', 'Azul', 'Verde', 'Amarillo']
TALLAS = [36, 37, 38, 39, 40, 41, 42, 43, 44, 45]

def categoria_view(request, nombre_modelo, sexo_abreviado):
    # Esta es una vista genérica que muestra los modelos de zapatos de una categoría específica
    # 'nombre_modelo' es el nombre del modelo de zapato (por ejemplo, "Apache")
    # 'sexo_abreviado' indica si es para hombres ('H') o mujeres ('M')
    
    # Determina el sexo completo (Hombre o Mujer) a partir del valor abreviado
    sexo = 'Hombre' if sexo_abreviado == 'H' else 'Mujer'
    sufijo = 'H' if sexo_abreviado == 'H' else 'M'
    
    # Crea una lista de zapatos con nombres y rutas de imágenes
    zapatos = [
        {"nombre": f"{nombre_modelo} {sexo}", "imagen": f"images/{nombre_modelo}{sufijo}{i}.png"}
        for i in range(1, 6)  # Crea 5 modelos para cada categoría
    ]
    
    # Asigna letras a cada modelo (A, B, C, ...)
    letras = list(ascii_uppercase[:len(zapatos)])
    
    # Renderiza la plantilla correspondiente a esta categoría de zapatos
    return render(request, f"categories/{nombre_modelo.lower()}_{sexo.lower()}.html", {
        "zapatos_con_letras": zip(zapatos, letras),  # Empareja cada zapato con una letra
        "colores": COLORES,  # Colores disponibles
        "tallas": TALLAS,    # Tallas disponibles
        "sexo": sexo         # Sexo de la categoría (Hombre o Mujer)
    })

# Vistas específicas que usan la vista genérica
# Estas vistas son para categorías específicas de zapatos
def apache_hombre_view(request): return categoria_view(request, "Apache", "H")
def apolo_hombre_view(request): return categoria_view(request, "Apolo", "H")
def amaka_hombre_view(request): return categoria_view(request, "Amaka", "H")
def nautico_hombre_view(request): return categoria_view(request, "Nautico", "H")
def bota_hombre_view(request): return categoria_view(request, "Bota", "H")
def casual_hombre_view(request): return categoria_view(request, "Casual", "H")
def apache_mujer_view(request): return categoria_view(request, "Apache", "M")
def bota_mujer_view(request): return categoria_view(request, "Bota", "M")

# -----------------------------
# Vista para clientes
# -----------------------------
@login_required
def ver_clientes(request):
    # Obtener todos los clientes de la base de datos
    clientes = Cliente.objects.all()
    # Renderizar la plantilla con la lista de clientes
    return render(request, 'ver_clientes.html', {'clientes': clientes})

# -----------------------------
# Vista para clientes
# -----------------------------
@login_required
def crear_clientes(request):
    # Vista para crear un nuevo cliente
    if request.method == 'POST':
        form = ClientesForm(request.POST)
        if form.is_valid():
            # Verificar si el cliente ya existe
            nombre = form.cleaned_data['nombre']
            if Cliente.objects.filter(nombre=nombre).exists():
                messages.error(request, "El cliente ya existe.")
                return redirect('crear_clientes')
            else:
                # Guardar el nuevo cliente en la base de datos
                form.save()
                messages.success(request, "Cliente creado exitosamente.")
                return redirect('ver_clientes')
    else:
        form = ClientesForm()
    return render(request, 'crear_cliente.html', {'form': form})

# -----------------------------
# Vista para ver los pedidos
# -----------------------------
@login_required
def ver_carrito(request):
    # Muestra los productos agregados al carrito de compras
    clientes = Cliente.objects.all()  # Obtiene todos los clientes de la base de datos
    pedido = request.session.get('pedido', {})  # Obtiene el pedido actual desde la sesión
    contexto = {
        'pedido': pedido,
        'clientes': clientes,
    }
    return render(request, 'ver_carrito.html', contexto)  # Renderiza la plantilla con el pedido y los clientes

# -----------------------------
# Crear codigos QR únicos para un zapato
# ----------------------------
def generar_codigo_qr(zapato):
    """
    Genera un código QR para un zapato y devuelve la imagen.
    """
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    
    data = {
        'id': zapato.id,
        'referencia': zapato.referencia,
        'modelo': zapato.modelo,
        'talla': zapato.talla,
        'sexo': zapato.sexo,
        'color': zapato.color,
        'requerimientos': zapato.requerimientos,
        'observaciones': zapato.observaciones,
        'estado': zapato.estado,
        # 'pedido': zapato.pedido,
    }
    
    qr.add_data(json.dumps(data, ensure_ascii=False))  # Convierte los datos a JSON y los agrega al QR
    qr.make(fit=True)
    return qr.make_image(fill_color="black", back_color="white")

def guardar_qr(zapato, img):
    """
    Guarda la imagen del QR en un directorio específico.
    """
    qr_directory = 'qr_codes/'  # Directorio donde se guardarán los QR
    os.makedirs(qr_directory, exist_ok=True)  # Crea el directorio si no existe
    qr_path = os.path.join(qr_directory, f"zapato_{zapato.id}.png")
    img.save(qr_path)
    return qr_path

# -----------------------------
# Agregar producto al pedido
# Coge los formularios de cada uno de los archivos hmtl de cada uno de los modelos
# ----------------------------
@login_required
def agregar_pedido(request):
    if request.method == 'POST':
        # Recibe los datos del producto a agregar
        modelo = request.POST.get('modelo') 
        color = request.POST.get('color')
        talla = request.POST.get('talla')
        sexo = request.POST.get('sexo')
        imagen = request.POST.get('imagen')
        requerimientos = request.POST.get('requerimientos')
        observaciones = request.POST.get('observaciones')
        letra = request.POST.get("letra", "").upper()  # Obtiene la letra asociada con el modelo

        # Genera un código único para el zapato
        letra_sexo = sexo[0].upper()
        clave_base = f"{modelo[:2].upper()}{talla}{color[0].upper()}{letra_sexo}{letra}"


        # Obtiene el pedido actual desde la sesión
        pedido = request.session.get('pedido', {})
        contador = 1

        # Busca si ya existe un zapato con la misma clave base (modelo, color, talla, sexo)
        ids_existentes = [pid for pid in pedido.keys() if pid.startswith(clave_base)]
        if ids_existentes:
            # Si ya existe, se obtiene el número más alto para continuar con el siguiente ID
            numeros = [int(pid[len(clave_base):]) for pid in ids_existentes if pid[len(clave_base):].isdigit()]
            contador = max(numeros) + 1 if numeros else 1

        # Genera el ID final del zapato
        # idZapato = f"{clave_base}{str(contador).zfill(3)}"
        idZapato = f"{clave_base}"

        # Si el producto ya está en el pedido, solo se aumenta la cantidad
        for pid, item in pedido.items():
            if (
                item['modelo'] == modelo and
                item['color'] == color and
                str(item['talla']) == talla and
                item['sexo'] == letra_sexo and
                item.get('letra', '') == letra
            ):
                pedido[pid]['cantidad'] += 1
                break
        else:
            # Si el producto no está en el pedido, se agrega con cantidad 1
            pedido[idZapato] = {
                'modelo': modelo,
                'color': color,
                'talla': talla,
                'sexo': letra_sexo,
                'cantidad': 1,
                'imagen': imagen,
                'letra': letra,
                'requerimientos': requerimientos,
                'observaciones': observaciones,
            }

        # Crear o recuperar el zapato en la base de datos
        zapato, created = Zapato.objects.get_or_create(
            referencia=clave_base,
            modelo=modelo,
            talla=talla,
            sexo=letra_sexo,
            color=color,
            defaults={
                'requerimientos': requerimientos,
                'observaciones': observaciones,
            }
        )
        # Guarda el pedido actualizado en la sesión
        request.session['pedido'] = pedido
        return redirect('ver_carrito')

# -----------------------------
# Generar archivo JSON del pedido
# -----------------------------
@login_required
def generar_pedido(request):
    if request.method == 'POST':
        # Obtiene el pedido actual desde la sesión
        pedido_data = request.session.get('pedido', {})
        
        # Si no hay productos en el carrito, muestra un error
        if not pedido_data:
            messages.error(request, "No hay productos en el carrito.")
            return redirect('ver_carrito')

        # Obtiene el comentario y cliente desde el formulario
        comentario = request.POST.get('comentario', '')
        cliente_nombre = request.POST.get('cliente')  # Captura el ID del cliente desde el formulario
        print(f"Cliente ID recibido: {cliente_nombre}")

        try:
            # Busca el cliente en la base de datos por su ID
            cliente = Cliente.objects.get(nombre=cliente_nombre)
        except Cliente.DoesNotExist:
            messages.error(request, "El cliente seleccionado no existe.")
            return redirect('ver_carrito')
        # Guarda el comentario en la sesión
        request.session['comentario'] = comentario

        pedido = Pedido.objects.create(
            empleado=request.user,
            cliente=cliente,
            fecha_creacion=timezone.now(),
            observaciones=comentario,
        )

        # Lista para almacenar las rutas de los codigos QR generados
        qr_paths = []
        zapato_info = []

        # Relaciona los zapatos existentes con el pedido y actualiza su estado
        for producto_id, producto in pedido_data.items():
            cantidad = int(producto.get('cantidad', 1))
            zapatos = Zapato.objects.filter(referencia=producto_id, estado='Pendientes')[:cantidad]  # Obtiene los zapatos existentes

            for zapato in zapatos:
                zapato.pedido = pedido  # Asocia el zapato con el pedido
                zapato.estado = 'Producción'  # Cambia el estado del zapato a Producción
                zapato.save()  # Guarda los cambios en la base de datos
                # Genera el código QR para el zapato
                qr_img = generar_codigo_qr(zapato)
                qr_path = guardar_qr(zapato, qr_img)  # Guarda la imagen del QR
                qr_paths.append(qr_path)  # Agrega la ruta del QR a la lista

                # Almacena la información del zapato junto con la ruta del QR
                zapato_info.append({
                    'id': zapato.id,
                    'referencia': zapato.referencia,
                    'modelo': zapato.modelo,
                    'talla': zapato.talla,
                    'sexo': zapato.sexo,
                    'color': zapato.color,
                    'requerimientos': zapato.requerimientos,
                    'observaciones': zapato.observaciones,
                    'estado': zapato.estado,
                    'qr_path': qr_path,
                })

        # Generar el archivo PDF en memoria y guardarlo en el servidor
        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=letter)

        # Titulo del PDF
        c.setFont("Helvetica-Bold", 16)
        c.drawString(200, 750, f"Pedido #{pedido.id}")
        c.setFont("Helvetica", 12)
        c.drawString(50, 730, f"Cliente: {cliente.nombre}")
        c.drawString(50, 710, f"Fecha: {pedido.fecha_creacion.strftime('%Y-%m-%d %H:%M:%S')}")
        c.drawString(50, 690, f"Observaciones: {pedido.observaciones}")

        # Agregar información de cada zapato al PDF
        y_position = 650
        for info in zapato_info:
            if y_position < 100: # Salto de pagina si la posición es muy baja
                c.showPage()
                y_position = 750
            
            c.drawString(50, y_position, f"Id: {info['id']}")
            c.drawString(50, y_position - 20, f"Referencia: {info['referencia']}")
            c.drawString(50, y_position - 40, f"Modelo: {info['modelo']}")
            c.drawString(50, y_position - 60, f"Talla: {info['talla']}")
            c.drawImage(info['qr_path'], 400, y_position - 70, width=100, height=100)  # Agrega el QR al PDF
            y_position -= 120  # Espacio entre cada zapato
        c.save()  # Guarda el PDF

        # Guarda el PEDF en el servidor
        pdf_path = os.path.join(settings.MEDIA_ROOT, 'pdf_pedidos', f"pedido_{pedido.id}.pdf")
        os.makedirs(os.path.dirname(pdf_path), exist_ok=True)  # Crea el directorio si no existe
        
        with open(pdf_path, 'wb') as f:
            f.write(buffer.getvalue())


        # Borra el pedido de la sesión después de generarlo
        if 'pedido' in request.session:
            del request.session['pedido']
            request.session.modified = True  # Marca la sesión como modificada

        # Devuelve el PDF como respuesta HTTP para abrirlo en una pestaña
        buffer.seek(0)
        response = HttpResponse(buffer, content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="pedido_{pedido.id}.pdf"'
        # Mensaje de éxito
        messages.success(request, f"Pedido #{pedido.id} generado exitosamente.")
        return response
        # Si no se encuentra el cliente, muestra un mensaje de error
    return redirect('ver_carrito')

# -----------------------------
# Ver Pedidos
# -----------------------------
@login_required
def ver_pedidos(request):
    # Vista para ver todos los pedidos
    pedidos = Pedido.objects.select_related('cliente').all()  # Obtiene todos los pedidos de la base de datos al mismo tiempo que los clientes relacionados
    return render(request, 'ver_pedidos.html', {'pedidos': pedidos})  # Renderiza la plantilla con la lista de pedidos

# -----------------------------
# Ver los Zapatos de un pedido
# -----------------------------
@login_required
def ver_zapatos_pedido(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id)  # Obtiene el pedido por su ID

    zapatos = Zapato.objects.filter(pedido=pedido)  # Filtra los zapatos asociados a ese pedido

    # Generar la URL del PDF
    pdf_url = f"{settings.MEDIA_URL}pdf_pedidos/pedido_{pedido.id}.pdf"

    return render(request, 'ver_zapatos_pedido.html', {
        'pedido': pedido,
        'zapatos': zapatos,
        'pdf_url': pdf_url,  # Pasa la URL del PDF a la plantilla
    })  # Renderiza la plantilla con el pedido y los zapatos asociados

# -----------------------------
# Eliminar producto individual del pedido
# -----------------------------
def eliminar_pedido(request):
    if request.method == 'POST':
        producto_id = request.POST.get('producto_id')
        pedido = request.session.get('pedido', {})
        zapato_eliminar = Zapato.objects.filter(referencia=producto_id)
        if zapato_eliminar:
            zapato_eliminar.delete()
        # Si el producto está en el pedido, lo elimina
        if producto_id in pedido:
            del pedido[producto_id]
            request.session['pedido'] = pedido
            messages.success(request, 'Producto eliminado del carrito.')
        return redirect('ver_carrito')
    return redirect('landing')

# -----------------------------
# Eliminar todo el pedido
# -----------------------------
def eliminar_todo_pedido(request):
    if request.method == 'POST':
        producto_id = request.POST.get('producto_id')
        zapato_eliminar = Zapato.objects.filter(referencia=producto_id)
        if zapato_eliminar:
            zapato_eliminar.delete()
        if 'pedido' in request.session:
            del request.session['pedido']
            messages.success(request, 'Pedido eliminado con éxito.')
        else:
            messages.warning(request, 'No hay pedido que eliminar.')
        return redirect('ver_carrito')
    return redirect('landing')

# -----------------------------
# Actualizar cantidad de un producto
# -----------------------------
def actualizar_pedido(request):
    if request.method == 'POST':
        producto_id = request.POST.get('producto_id')
        nueva_cantidad = request.POST.get('cantidad')
        pedido = request.session.get('pedido', {})
        if producto_id in pedido and nueva_cantidad:
            try:
                nueva_cantidad = int(nueva_cantidad)
                if nueva_cantidad >= 1:
                    pedido[producto_id]['cantidad'] = nueva_cantidad

                    # Zapato.objects.filter(referencia=producto_id).delete()
                    # Eliminar el zapato existente
                    for i in range(nueva_cantidad - 1):
                        zapato = Zapato.objects.create(
                            referencia=producto_id,
                            modelo=pedido[producto_id]['modelo'],
                            talla=pedido[producto_id]['talla'],
                            sexo=pedido[producto_id]['sexo'],
                            color=pedido[producto_id]['color'],
                            requerimientos=pedido[producto_id]['requerimientos'],
                            observaciones=pedido[producto_id]['observaciones']
                        )
            except ValueError:
                pass
        request.session['pedido'] = pedido
    return redirect('ver_carrito')

@login_required
def cargar_qr(request):
    mensaje = ""
    resultado = []
    qr_leidos = []
    estados = ['Bodega', 'Pendiente', 'Producción', 'Anulado', 'Completado', 'Entregado']
    zapatos = []
    mostrar_estado = False

    if request.method == 'POST':
        # Paso 2: El usuario selecciona el estado
        if 'estado_nuevo' in request.POST:
            estado_nuevo = request.POST.get('estado_nuevo')
            zapato_infos = request.POST.getlist('zapato_info')
            zapatos_actualizados = []
            for zapato_id in zapato_infos:
                try:
                    zapato = Zapato.objects.get(id=zapato_id)
                    zapato.estado = estado_nuevo
                    zapato.save()
                    zapatos_actualizados.append(zapato)
                except Zapato.DoesNotExist:
                    continue
            zapato_aux = zapatos_actualizados[0]
            pedido_zapato = zapato_aux.pedido
            pedido = Pedido.objects.get(id=pedido_zapato.id)
            pedido.estado = 'Completada'
            pedido.save()
            mensaje = f"{len(zapatos_actualizados)} zapato(s) actualizado(s) a '{estado_nuevo}'."
            return render(request, 'cargar_qr.html', {
                'resultado': zapatos_actualizados,
                'mensaje': mensaje,
                'estados': estados,
            })

        # Paso 1: El usuario sube el archivo
        form = QRFileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            archivo = form.cleaned_data['archivo']
            nombre = archivo.name.lower()
            imagenes = []
            if nombre.endswith('.pdf'):
                paginas = convert_from_bytes(archivo.read())
                for pagina in paginas:
                    imagen = np.array(pagina)
                    imagenes.append(cv2.cvtColor(imagen, cv2.COLOR_RGB2BGR))
            else:
                file_bytes = np.asarray(bytearray(archivo.read()), dtype=np.uint8)
                imagen = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
                imagenes.append(imagen)

            referencias_info = []
            for img in imagenes:
                for qr in decode(img):
                    data = qr.data.decode('utf-8').strip()
                    qr_leidos.append(data)
                    data = re.sub(r'[^\x20-\x7E]+', '', data)
                    try:
                        info = json.loads(data)
                        id_zapato = info.get('id')
                        referencia = info.get('referencia')
                        modelo = info.get('modelo')
                        talla = info.get('talla')
                        sexo = info.get('sexo')
                        color = info.get('color')
                        if referencia and modelo and talla and sexo and color:
                            referencias_info.append({
                                'id_zapato': id_zapato,
                                'referencia': referencia,
                                'modelo': modelo,
                                'talla': talla,
                                'sexo': sexo,
                                'color': color,
                            })
                    except Exception:
                        continue

            zapatos = []
            zapato_infos = []
            for ref in referencias_info:
                try:
                    zapato = Zapato.objects.get(id=ref['id_zapato'])
                    zapatos.append(zapato)
                    zapato_infos.append(str(zapato.id))
                except Zapato.DoesNotExist:
                    continue
            mostrar_estado = True
            return render(request, 'cargar_qr.html', {
                'zapatos': zapatos,
                'zapato_infos': zapato_infos,
                'estados': estados,
                'mostrar_estado': mostrar_estado,
            })
        else:
            mensaje = "Archivo no válido."
    else:
        form = QRFileUploadForm()

    return render(request, 'cargar_qr.html', {
        'form': form,
        'mensaje': mensaje,
        'estados': estados,
    })

@login_required
def ver_stock(request):
    zapatos = Zapato.objects.all()
    total = 0
    if request.method == 'POST':
        filtros = {}
        referencia = request.POST.get('referencia')
        modelo = request.POST.get('modelo')
        talla = request.POST.get('talla')
        sexo = request.POST.getlist('sexo')
        color = request.POST.get('color')
        estado = request.POST.getlist('estado')
        
        if referencia:
            filtros['referencia'] = referencia
        if modelo:
            filtros['modelo'] = modelo
        if talla:
            filtros['talla'] = talla
        if sexo:
            filtros['sexo__in'] = sexo
        if color:
            filtros['color'] = color
        if estado:
            filtros['estado__in'] = estado
            
        zapatos = Zapato.objects.filter(**filtros)

    # Calcular el total de zapatos
    total = zapatos.count()
        # Para los selects, obtener valores únicos de la base de datos
    context = {
        'zapatos': zapatos,
        'referencias': Zapato.objects.values_list('referencia', flat=True).distinct(),
        'modelos': Zapato.objects.values_list('modelo', flat=True).distinct(),
        'tallas': Zapato.objects.values_list('talla', flat=True).distinct(),
        'colores': Zapato.objects.values_list('color', flat=True).distinct(),
        'total': total,
    }
    return render(request, 'ver_stock.html', context)
        