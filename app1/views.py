

# Standard library
import os
import json
import re
from io import BytesIO
from string import ascii_uppercase
from abc import ABC, abstractmethod

# Third-party libs
import qrcode
import cv2
import numpy as np
import fitz
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

# Django
from django.conf import settings
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.http import HttpResponse, HttpResponseNotAllowed
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import (
    FormView, TemplateView, ListView, CreateView, DetailView
)

# Local
from .forms import ClientesForm, ZapatoForm, QRFileUploadForm
from .models import Cliente, Zapato, Pedido
from app1.services.qr_reader import QRReaderFacade
# -----------------------------
# Manejo de errores CSRF
# -----------------------------
class CsrfFailureView(View):
    template_name = 'csrf_error.html'

    def get(self, request, reason=""):
        # Muestra la plantilla de error con el motivo
        return render(request, self.template_name, {'reason': reason})

    def post(self, request, reason=""):
        # Misma respuesta para POST
        return self.get(request, reason)

# Exporta un callable para el middleware de CSRF
csrf_failure = CsrfFailureView.as_view()

# -----------------------------
# Autenticación
# -----------------------------
# ===== Login =====
class LoginView(FormView):
    template_name = "login.html"                 # tu misma plantilla
    form_class = AuthenticationForm              # usa los name="username" y name="password" de siempre
    success_url = reverse_lazy("landing")

    # Template Method: punto de extensión para decidir a dónde redirigir según el usuario
    def get_success_url_for_user(self, user):
        """
        Cambia la redirección según rol/permisos si lo necesitas.
        Por ahora, mantenemos 'landing'.
        """
        return str(self.success_url)

    def form_valid(self, form):
        username = form.cleaned_data.get("username")
        password = form.cleaned_data.get("password")

        user = authenticate(self.request, username=username, password=password)
        if user is not None:
            login(self.request, user)
            messages.success(self.request, f"¡Bienvenido, {user.username}!")
            return redirect(self.get_success_url_for_user(user))
        # Si no autenticó, tratamos como inválido para mantener la UX
        return self.form_invalid(form)

    def form_invalid(self, form):
        # Mantengo la variable 'error' para NO romper tu plantilla actual.
        context = self.get_context_data(form=form, error="Credenciales inválidas")
        return self.render_to_response(context)

# ===== Logout =====
class LogoutView(View):
    def post(self, request, *args, **kwargs):
        logout(request)
        messages.info(request, "Sesión cerrada correctamente.")
        return redirect("login")

    # Permitimos GET por si tu botón es un enlace simple
    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)
 
# imports nuevos
from django.views.generic import TemplateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from string import ascii_uppercase

# -----------------------------
# Landing (requiere login)
# -----------------------------
class LandingView(LoginRequiredMixin, TemplateView):
    template_name = "landing.html"


# -----------------------------
# Categorías (listado)
# -----------------------------
class CategoriasView(TemplateView):
    template_name = "categorias.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["categorias"] = [
            {"nombre": "Apache Hombre", "imagen": "images/apacheH1.png", "url": "apache_hombre"},
            {"nombre": "Apolo Hombre", "imagen": "images/apoloH1.png", "url": "apolo_hombre"},
            {"nombre": "Amaka Hombre", "imagen": "images/amakaH1.png", "url": "amaka_hombre"},
            {"nombre": "Nautico Hombre", "imagen": "images/nauticoH1.png", "url": "nautico_hombre"},
            {"nombre": "Bota Hombre", "imagen": "images/botaH1.png", "url": "bota_hombre"},
            {"nombre": "Casual Hombre", "imagen": "images/casualH1.png", "url": "casual_hombre"},
            {"nombre": "Apache Mujer", "imagen": "images/apacheM1.png", "url": "apache_mujer"},
            {"nombre": "Bota Mujer", "imagen": "images/botaM1.png", "url": "bota_mujer"},
        ]
        return ctx


# -----------------------------
# Vista genérica de categoría
# (mismo comportamiento que tu categoria_view)
# -----------------------------
COLORES = ['Negro', 'Gris', 'Azul', 'Verde', 'Amarillo']
TALLAS = [36, 37, 38, 39, 40, 41, 42, 43, 44, 45]

class BaseCategoriaView(TemplateView):
    """
    Subclases deben definir:
      - nombre_modelo = "Apache" / "Apolo" / ...
      - sexo_abreviado = "H" o "M"
    """
    template_name = ""          # lo definimos dinámicamente en get_template_names
    nombre_modelo = None
    sexo_abreviado = None

    def get_template_names(self):
        sexo = 'hombre' if self.sexo_abreviado == 'H' else 'mujer'
        return [f"categories/{self.nombre_modelo.lower()}_{sexo}.html"]

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        sexo_completo = 'Hombre' if self.sexo_abreviado == 'H' else 'Mujer'
        sufijo = 'H' if self.sexo_abreviado == 'H' else 'M'
        zapatos = [
            {"nombre": f"{self.nombre_modelo} {sexo_completo}", "imagen": f"images/{self.nombre_modelo}{sufijo}{i}.png"}
            for i in range(1, 6)
        ]
        letras = list(ascii_uppercase[:len(zapatos)])

        ctx.update({
            "zapatos_con_letras": zip(zapatos, letras),
            "colores": COLORES,
            "tallas": TALLAS,
            "sexo": sexo_completo,
        })
        return ctx


# -----------------------------
# Clases específicas por categoría (mantienen misma lógica/URLs)
# -----------------------------
class ApacheHombreView(BaseCategoriaView):
    nombre_modelo = "Apache"
    sexo_abreviado = "H"

class ApoloHombreView(BaseCategoriaView):
    nombre_modelo = "Apolo"
    sexo_abreviado = "H"

class AmakaHombreView(BaseCategoriaView):
    nombre_modelo = "Amaka"
    sexo_abreviado = "H"

class NauticoHombreView(BaseCategoriaView):
    nombre_modelo = "Nautico"
    sexo_abreviado = "H"

class BotaHombreView(BaseCategoriaView):
    nombre_modelo = "Bota"
    sexo_abreviado = "H"

class CasualHombreView(BaseCategoriaView):
    nombre_modelo = "Casual"
    sexo_abreviado = "H"

class ApacheMujerView(BaseCategoriaView):
    nombre_modelo = "Apache"
    sexo_abreviado = "M"

class BotaMujerView(BaseCategoriaView):
    nombre_modelo = "Bota"
    sexo_abreviado = "M"


# (Patrón pequeño: Mixin para centralizar el contexto del carrito)
class CarritoContextMixin:
    """
    Mixin para inyectar en el contexto:
    - pedido (desde sesión)
    - clientes (para selects, etc.)
    """
    def get_carrito(self):
        return self.request.session.get('pedido', {})

    def get_clientes(self):
        return Cliente.objects.all()

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx.setdefault('pedido', self.get_carrito())
        ctx.setdefault('clientes', self.get_clientes())
        return ctx


class VerClientesView(LoginRequiredMixin, ListView):
    model = Cliente
    template_name = 'ver_clientes.html'
    context_object_name = 'clientes'   # <— coincide con tu HTML


class CrearClientesView(LoginRequiredMixin, CreateView):
    template_name = 'crear_cliente.html'
    form_class = ClientesForm
    success_url = reverse_lazy('ver_clientes')

    def form_valid(self, form):
        # Validación: no duplicar por nombre (misma lógica que tenías)
        nombre = form.cleaned_data.get('nombre')
        if Cliente.objects.filter(nombre=nombre).exists():
            messages.error(self.request, "El cliente ya existe.")
            return self.form_invalid(form)
        response = super().form_valid(form)
        messages.success(self.request, "Cliente creado exitosamente.")
        return response


class VerCarritoView(LoginRequiredMixin, CarritoContextMixin, TemplateView):
    template_name = 'ver_carrito.html'
    # CarritoContextMixin ya añade 'pedido' y 'clientes' al contexto.

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




# --- Pequeña utilidad para construir la referencia ---
class ReferenciaBuilder:
    """
    Encapsula la regla actual de construcción de la clave:
    {2 primeras del modelo}{talla}{inicial color}{sexo inicial}{letra}
    """
    @staticmethod
    def build(modelo: str, talla: str, color: str, sexo: str, letra: str) -> str:
        modelo = (modelo or "").strip()
        talla = str(talla or "").strip()
        color = (color or "").strip()
        sexo = (sexo or "").strip()
        letra = (letra or "").strip().upper()

        letra_sexo = sexo[:1].upper()
        return f"{modelo[:2].upper()}{talla}{(color[:1] or '').upper()}{letra_sexo}{letra}"

# --- Vista basada en clase para agregar al pedido ---
class AgregarPedidoView(LoginRequiredMixin, View):
    """
    Reemplaza a la función agregar_pedido manteniendo la misma lógica y la misma redirección.
    Espera POST con: modelo, color, talla, sexo, imagen, requerimientos, observaciones, letra.
    """
    def post(self, request):
        modelo = request.POST.get('modelo')
        color = request.POST.get('color')
        talla = request.POST.get('talla')
        sexo = request.POST.get('sexo')
        imagen = request.POST.get('imagen')
        requerimientos = request.POST.get('requerimientos')
        observaciones = request.POST.get('observaciones')
        letra = request.POST.get('letra', '').upper()

        # 1) clave base / idZapato
        clave_base = ReferenciaBuilder.build(modelo, talla, color, sexo, letra)
        letra_sexo = (sexo or '')[:1].upper()

        # 2) pedido en sesión
        pedido = request.session.get('pedido', {})

        # 3) si el item ya existe con mismas opciones -> incrementa cantidad
        for pid, item in pedido.items():
            if (
                item.get('modelo') == modelo and
                item.get('color') == color and
                str(item.get('talla')) == str(talla) and
                item.get('sexo') == letra_sexo and
                item.get('letra', '') == letra
            ):
                pedido[pid]['cantidad'] = int(pedido[pid].get('cantidad', 1)) + 1
                break
        else:
            # nuevo ítem
            pedido[clave_base] = {
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

        # 4) crea/recupera Zapato en BD (misma lógica que tenías)
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

        # 5) guarda sesión y redirige
        request.session['pedido'] = pedido
        messages.success(request, "Producto agregado al carrito.")
        return redirect('ver_carrito')

    def get(self, request):
        # Esta vista solo acepta POST
        return HttpResponseNotAllowed(['POST'])


class PedidoPDFBuilder:
    """Pequeño helper para construir el PDF del pedido (Facade/Utility)."""
    def __init__(self, pedido, cliente, zapato_info):
        self.pedido = pedido
        self.cliente = cliente
        self.zapato_info = zapato_info

    def build_pdf_bytesio(self):
        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=letter)

        # Título y cabecera
        c.setFont("Helvetica-Bold", 16)
        c.drawString(200, 750, f"Pedido #{self.pedido.id}")
        c.setFont("Helvetica", 12)
        c.drawString(50, 730, f"Cliente: {self.cliente.nombre}")
        c.drawString(50, 710, f"Fecha: {self.pedido.fecha_creacion.strftime('%Y-%m-%d %H:%M:%S')}")
        c.drawString(50, 690, f"Observaciones: {self.pedido.observaciones}")

        # Detalle zapatos
        y = 650
        for info in self.zapato_info:
            if y < 100:
                c.showPage()
                y = 750
            c.drawString(50, y,        f"Id: {info['id']}")
            c.drawString(50, y - 20,   f"Referencia: {info['referencia']}")
            c.drawString(50, y - 40,   f"Modelo: {info['modelo']}")
            c.drawString(50, y - 60,   f"Talla: {info['talla']}")
            c.drawImage(info['qr_path'], 400, y - 70, width=100, height=100)
            y -= 120

        c.save()
        buffer.seek(0)
        return buffer


class GenerarPedidoView(LoginRequiredMixin, View):
    """
    Reemplaza a la función generar_pedido conservando el mismo comportamiento:
    - Lee carrito en sesión
    - Crea Pedido
    - Asocia Zapatos (estado 'Pendientes' -> 'Producción')
    - Genera QRs y PDF
    - Limpia carrito
    - Devuelve PDF inline
    """
    def post(self, request):
        pedido_data = request.session.get('pedido', {})
        if not pedido_data:
            messages.error(request, "No hay productos en el carrito.")
            return redirect('ver_carrito')

        comentario = request.POST.get('comentario', '')
        cliente_nombre = request.POST.get('cliente')
        try:
            cliente = Cliente.objects.get(nombre=cliente_nombre)
        except Cliente.DoesNotExist:
            messages.error(request, "El cliente seleccionado no existe.")
            return redirect('ver_carrito')

        # Guarda comentario en sesión (como ya hacías)
        request.session['comentario'] = comentario

        pedido = Pedido.objects.create(
            empleado=request.user,
            cliente=cliente,
            fecha_creacion=timezone.now(),
            observaciones=comentario,
        )

        qr_paths = []
        zapato_info = []

        # Mueve zapatos 'Pendientes' del carrito a este pedido y a 'Producción'
        for ref_id, producto in pedido_data.items():
            cantidad = int(producto.get('cantidad', 1))
            zapatos = Zapato.objects.filter(referencia=ref_id, estado='Pendientes')[:cantidad]

            for z in zapatos:
                z.pedido = pedido
                z.estado = 'Producción'
                z.save()

                qr_img = generar_codigo_qr(z)
                qr_path = guardar_qr(z, qr_img)
                qr_paths.append(qr_path)

                zapato_info.append({
                    'id': z.id,
                    'referencia': z.referencia,
                    'modelo': z.modelo,
                    'talla': z.talla,
                    'sexo': z.sexo,
                    'color': z.color,
                    'requerimientos': z.requerimientos,
                    'observaciones': z.observaciones,
                    'estado': z.estado,
                    'qr_path': qr_path,
                })

        # Construir PDF (mismo contenido de antes, encapsulado)
        pdf_builder = PedidoPDFBuilder(pedido, cliente, zapato_info)
        pdf_buffer = pdf_builder.build_pdf_bytesio()

        # Guardar PDF en disco (misma ruta que usabas)
        pdf_path = os.path.join(settings.MEDIA_ROOT, 'pdf_pedidos', f"pedido_{pedido.id}.pdf")
        os.makedirs(os.path.dirname(pdf_path), exist_ok=True)
        with open(pdf_path, 'wb') as f:
            f.write(pdf_buffer.getvalue())

        # Limpiar carrito
        if 'pedido' in request.session:
            del request.session['pedido']
            request.session.modified = True

        # Respuesta inline
        response = HttpResponse(pdf_buffer, content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="pedido_{pedido.id}.pdf"'
        messages.success(request, f"Pedido #{pedido.id} generado exitosamente.")
        return response

    def get(self, request):
        return HttpResponseNotAllowed(['POST'])



# ====== LISTAR PEDIDOS ======
class PedidoListView(LoginRequiredMixin, ListView):
    model = Pedido
    template_name = 'ver_pedidos.html'
    context_object_name = 'pedidos'

    def get_queryset(self):
        return Pedido.objects.select_related('cliente').all()


# ====== ZAPATOS DE UN PEDIDO ======
class PedidoZapatosView(LoginRequiredMixin, DetailView):
    model = Pedido
    pk_url_kwarg = 'pedido_id'
    template_name = 'ver_zapatos_pedido.html'
    context_object_name = 'pedido'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        pedido = self.object
        ctx['zapatos'] = Zapato.objects.filter(pedido=pedido)
        ctx['pdf_url'] = f"{settings.MEDIA_URL}pdf_pedidos/pedido_{pedido.id}.pdf"
        return ctx


# ====== Infraestructura carrito (Command Pattern) ======
class CartService:
    KEY = 'pedido'
    def __init__(self, request):
        self.request = request
        self.session = request.session
        self.cart = self.session.get(self.KEY, {})

    def save(self):
        self.session[self.KEY] = self.cart
        self.session.modified = True

    def clear(self):
        if self.KEY in self.session:
            del self.session[self.KEY]
            self.session.modified = True


class CartCommand(ABC):
    def __init__(self, cart_service):
        self.cart = cart_service

    @abstractmethod
    def execute(self):
        ...


class RemoveItemCommand(CartCommand):
    def __init__(self, cart_service, producto_id):
        super().__init__(cart_service)
        self.producto_id = producto_id

    def execute(self):
        # mismo comportamiento que tenías: borrar en DB por referencia
        Zapato.objects.filter(referencia=self.producto_id).delete()
        # quitar del carrito en sesión
        if self.producto_id in self.cart.cart:
            del self.cart.cart[self.producto_id]
        self.cart.save()


class ClearCartCommand(CartCommand):
    def __init__(self, cart_service, producto_id=None):
        super().__init__(cart_service)
        self.producto_id = producto_id  # opcional, tu versión antigua borraba por ref antes de vaciar

    def execute(self):
        if self.producto_id:
            Zapato.objects.filter(referencia=self.producto_id).delete()
        self.cart.clear()


class UpdateQtyCommand(CartCommand):
    def __init__(self, cart_service, producto_id, nueva_cantidad):
        super().__init__(cart_service)
        self.producto_id = producto_id
        self.nueva_cantidad = nueva_cantidad

    def execute(self):
        pedido = self.cart.cart
        if self.producto_id in pedido and self.nueva_cantidad:
            try:
                cantidad = int(self.nueva_cantidad)
                if cantidad >= 1:
                    pedido[self.producto_id]['cantidad'] = cantidad
                    # mismo comportamiento: crear registros extra en DB
                    for _ in range(cantidad - 1):
                        Zapato.objects.create(
                            referencia=self.producto_id,
                            modelo=pedido[self.producto_id]['modelo'],
                            talla=pedido[self.producto_id]['talla'],
                            sexo=pedido[self.producto_id]['sexo'],
                            color=pedido[self.producto_id]['color'],
                            requerimientos=pedido[self.producto_id]['requerimientos'],
                            observaciones=pedido[self.producto_id]['observaciones'],
                        )
                    self.cart.save()
            except ValueError:
                pass


# ====== Vistas de acciones (POST) ======
class EliminarPedidoView(View):
    def post(self, request):
        producto_id = request.POST.get('producto_id')
        cart = CartService(request)
        RemoveItemCommand(cart, producto_id).execute()
        messages.success(request, 'Producto eliminado del carrito.')
        return redirect('ver_carrito')

    def get(self, request):
        return redirect('landing')


class EliminarTodoPedidoView(View):
    def post(self, request):
        producto_id = request.POST.get('producto_id')  # tu implementación lo usaba para borrar en DB
        cart = CartService(request)
        ClearCartCommand(cart, producto_id).execute()
        messages.success(request, 'Pedido eliminado con éxito.')
        return redirect('ver_carrito')

    def get(self, request):
        return redirect('landing')


class ActualizarPedidoView(View):
    def post(self, request):
        producto_id = request.POST.get('producto_id')
        nueva_cantidad = request.POST.get('cantidad')
        cart = CartService(request)
        UpdateQtyCommand(cart, producto_id, nueva_cantidad).execute()
        return redirect('ver_carrito')

    def get(self, request):
        return redirect('landing')
    

# -----------------------------
# =========================
# CARGAR QR (dos pasos)
# =========================
# views.py (solo el fragmento relevante de CargarQRView.post)

class CargarQRView(LoginRequiredMixin, View):
    template_name = "cargar_qr.html"

    def get(self, request):
        form = QRFileUploadForm()
        estados = ['Bodega', 'Pendientes', 'Producción', 'Anulado', 'Completado', 'Entregado']
        return render(request, self.template_name, {"form": form, "estados": estados})

    def post(self, request):
        estados = ['Bodega', 'Pendientes', 'Producción', 'Anulado', 'Completado', 'Entregado']

        # Paso 2: actualizar estado
        if 'estado_nuevo' in request.POST:
            estado_nuevo = request.POST.get('estado_nuevo')
            zapato_ids = request.POST.getlist('zapato_info')
            actualizados = []
            for zid in zapato_ids:
                try:
                    z = Zapato.objects.get(id=zid)
                    z.estado = estado_nuevo
                    z.save()
                    actualizados.append(z)
                except Zapato.DoesNotExist:
                    continue

            mensaje = f"{len(actualizados)} zapato(s) actualizado(s) a '{estado_nuevo}'."
            return render(request, self.template_name, {
                "resultado": actualizados,
                "mensaje": mensaje,
                "estados": estados
            })

        # Paso 1: subir archivo
        form = QRFileUploadForm(request.POST, request.FILES)
        if not form.is_valid():
            return render(request, self.template_name, {"form": form, "mensaje": "Archivo no válido.", "estados": estados})

        archivo = form.cleaned_data["archivo"]
        facade = QRReaderFacade()
        payloads = facade.extract_payloads(archivo)

        if not payloads:
            return render(request, self.template_name, {"form": QRFileUploadForm(), "mensaje": "No se detectaron zapatos válidos en el archivo.", "estados": estados})

        zapatos, zapato_infos = [], []
        for p in payloads:
            # Buscamos por ID si viene en el payload; si no, podríamos agregar fallback por referencia
            if p.id:
                try:
                    z = Zapato.objects.get(id=p.id)
                    zapatos.append(z)
                    zapato_infos.append(str(z.id))
                    continue
                except Zapato.DoesNotExist:
                    pass
            # Fallback opcional por referencia:
            # z = Zapato.objects.filter(referencia=p.referencia).first()
            # if z:
            #     zapatos.append(z)
            #     zapato_infos.append(str(z.id))

        if not zapatos:
            return render(request, self.template_name, {"form": QRFileUploadForm(), "mensaje": "No se encontraron coincidencias en la base de datos.", "estados": estados})

        return render(request, self.template_name, {
            "zapatos": zapatos,
            "zapato_infos": zapato_infos,
            "estados": estados,
            "mostrar_estado": True
        })


# =========================
# VER STOCK (con filtros)
# =========================
# views.py
class VerStockView(LoginRequiredMixin, View):
    template_name = "ver_stock.html"

    def _base_context(self):
        return {
            "referencias": Zapato.objects.values_list("referencia", flat=True).distinct(),
            "modelos": Zapato.objects.values_list("modelo", flat=True).distinct(),
            "tallas": Zapato.objects.values_list("talla", flat=True).distinct(),
            "colores": Zapato.objects.values_list("color", flat=True).distinct(),
        }

    def get(self, request):
        context = self._base_context()
        context.update({
            "zapatos": Zapato.objects.all(),
            "total": Zapato.objects.count(),
            # seleccionados vacíos en GET
            "referencia_sel": "",
            "modelo_sel": "",
            "talla_sel": "",
            "color_sel": "",
            "sexo_sel": [],
            "estado_sel": [],
        })
        return render(request, self.template_name, context)

    def post(self, request):
        filtros = {}
        referencia_sel = request.POST.get("referencia", "")
        modelo_sel     = request.POST.get("modelo", "")
        talla_sel      = request.POST.get("talla", "")
        color_sel      = request.POST.get("color", "")
        sexo_sel       = request.POST.getlist("sexo")
        estado_sel     = request.POST.getlist("estado")

        if referencia_sel:
            filtros["referencia"] = referencia_sel
        if modelo_sel:
            filtros["modelo"] = modelo_sel
        if talla_sel:
            filtros["talla"] = talla_sel
        if sexo_sel:
            filtros["sexo__in"] = sexo_sel
        if color_sel:
            filtros["color"] = color_sel
        if estado_sel:
            filtros["estado__in"] = estado_sel

        zapatos = Zapato.objects.filter(**filtros) if filtros else Zapato.objects.all()

        context = self._base_context()
        context.update({
            "zapatos": zapatos,
            "total": zapatos.count(),
            # devolver lo seleccionado para “persistir” el filtro en el form
            "referencia_sel": referencia_sel,
            "modelo_sel": modelo_sel,
            "talla_sel": talla_sel,
            "color_sel": color_sel,
            "sexo_sel": sexo_sel,
            "estado_sel": estado_sel,
        })
        return render(request, self.template_name, context)


# =============================
# Búsqueda de productos
# =============================
from django.db.models import Q
from .models import Zapato
from django.views import View

class BuscarProductosView(LoginRequiredMixin, View):
    template_name = "buscar_productos.html"

    def get(self, request):
        query = request.GET.get("q", "").strip()

        qs = Zapato.objects.all()
        if query:
            qs = qs.filter(
                Q(referencia__icontains=query) |
                Q(modelo__icontains=query) |
                Q(color__icontains=query) |
                Q(sexo__icontains=query[:1].upper())  
            )

        resultados = []
        for z in qs.order_by("modelo", "sexo", "referencia"):
           
            if z.imagen:
                z.imagen_categoria = z.imagen
            else:
                sufijo = 'H' if z.sexo == 'H' else 'M'
                z.imagen_categoria = f"images/{z.modelo}{sufijo}1.png"
            resultados.append(z)

        return render(request, self.template_name, {
            "resultados": resultados,
            "query": query,
            "colores": COLORES,
            "tallas": TALLAS,
        })

