from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from .views import (
    # Auth / landing
    LoginView, LogoutView, LandingView,

    # Categorías
    CategoriasView,
    ApacheHombreView, ApoloHombreView, AmakaHombreView,
    NauticoHombreView, BotaHombreView, CasualHombreView,
    ApacheMujerView, BotaMujerView,

    # Clientes / carrito / pedidos
    VerClientesView, CrearClientesView, VerCarritoView,
    AgregarPedidoView, GenerarPedidoView,

    # Gestión de pedidos y sus zapatos
    PedidoListView, PedidoZapatosView,
    EliminarPedidoView, EliminarTodoPedidoView, ActualizarPedidoView,

    # QR / Stock
    CargarQRView, VerStockView,
)

urlpatterns = [
    # Auth
    path("", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("landing/", LandingView.as_view(), name="landing"),

    # Stock
    path("ver_stock/", VerStockView.as_view(), name="ver_stock"),

    # Clientes / carrito / pedidos
    path("ver_clientes/", VerClientesView.as_view(), name="ver_clientes"),
    path("crear_clientes/", CrearClientesView.as_view(), name="crear_clientes"),
    path("ver_carrito/", VerCarritoView.as_view(), name="ver_carrito"),
    path("agregar_pedido/", AgregarPedidoView.as_view(), name="agregar_pedido"),
    path("generar_pedido/", GenerarPedidoView.as_view(), name="generar_pedido"),

    # Listado de pedidos y detalle de zapatos de un pedido
    path("ver_pedidos/", PedidoListView.as_view(), name="ver_pedidos"),
    path("zapatos/<int:pedido_id>/", PedidoZapatosView.as_view(), name="ver_zapatos_pedido"),

    # Acciones sobre el carrito/pedido
    path("eliminar_pedido/", EliminarPedidoView.as_view(), name="eliminar_pedido"),
    path("eliminar_todo_pedido/", EliminarTodoPedidoView.as_view(), name="eliminar_todo_pedido"),
    path("actualizar_pedido/", ActualizarPedidoView.as_view(), name="actualizar_pedido"),

    # Carga de QR
    path("cargar_qr/", CargarQRView.as_view(), name="cargar_qr"),

    # Categorías (los names se mantienen)
    path("categorias/", CategoriasView.as_view(), name="categorias"),
    path("zapatos/apache_hombre/", ApacheHombreView.as_view(), name="apache_hombre"),
    path("zapatos/apolo_hombre/", ApoloHombreView.as_view(), name="apolo_hombre"),
    path("zapatos/amaka_hombre/", AmakaHombreView.as_view(), name="amaka_hombre"),
    path("zapatos/nautico_hombre/", NauticoHombreView.as_view(), name="nautico_hombre"),
    path("zapatos/bota_hombre/", BotaHombreView.as_view(), name="bota_hombre"),
    path("zapatos/casual_hombre/", CasualHombreView.as_view(), name="casual_hombre"),
    path("zapatos/apache_mujer/", ApacheMujerView.as_view(), name="apache_mujer"),
    path("zapatos/bota_mujer/", BotaMujerView.as_view(), name="bota_mujer"),
]

# Servir MEDIA en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
