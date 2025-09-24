from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views
from django.shortcuts import render
from .views import login_view, landing_view, logout_view, categorias_view

urlpatterns = [
    path('', login_view, name='login'),  
    path('landing/', landing_view, name='landing'),  
    path('logout/', logout_view, name='logout'), 
    
    # Pagina para ver stock
    path('ver_stock/', views.ver_stock, name='ver_stock'),
    
    #Pagina para pedidos
    
    path('agregar_pedido/', views.agregar_pedido, name='agregar_pedido'),
    path('ver_carrito/', views.ver_carrito, name='ver_carrito'), 
    path('ver_clientes/', views.ver_clientes, name='ver_clientes'), 
    path('ver_pedidos/', views.ver_pedidos, name='ver_pedidos'), 
    path('crear_clientes/', views.crear_clientes, name='crear_clientes'),
    path('eliminar_pedido/', views.eliminar_pedido, name='eliminar_pedido'),
    path('eliminar_todo_pedido/', views.eliminar_todo_pedido, name='eliminar_todo_pedido'),
    path('actualizar_pedido/', views.actualizar_pedido, name='actualizar_pedido'),
    path('generar_pedido/', views.generar_pedido, name='generar_pedido'),
    path('zapatos/<int:pedido_id>/', views.ver_zapatos_pedido, name='ver_zapatos_pedido'),
    
    
    # Página principal de categorías
    path("categorias/", categorias_view, name="categorias"),

    # Páginas individuales por categoría
    path("categorias/apache_hombre/", lambda r: render(r, "categories/apache_hombre.html"), name="apache_hombre"),
    path("categorias/apolo_hombre/", lambda r: render(r, "categories/apolo_hombre.html"), name="apolo_hombre"),
    path("categorias/amaka_hombre/", lambda r: render(r, "categories/amaka_hombre.html"), name="amaka_hombre"),
    path("categorias/nautico_hombre/", lambda r: render(r, "categories/nautico_hombre.html"), name="nautico_hombre"),
    path("categorias/bota_hombre/", lambda r: render(r, "categories/bota_hombre.html"), name="bota_hombre"),
    path("categorias/casual_hombre/", lambda r: render(r, "categories/casual_hombre.html"), name="casual_hombre"),
    path("categorias/apache_mujer/", lambda r: render(r, "categories/apache_mujer.html"), name="apache_mujer"),
    path("categorias/bota_mujer/", lambda r: render(r, "categories/bota_mujer.html"), name="bota_mujer"),


    path("zapatos/amaka_hombre/", views.amaka_hombre_view, name="amaka_hombre"),
    path("zapatos/apache_hombre/", views.apache_hombre_view, name="apache_hombre"),
    path("zapatos/apolo_hombre/", views.apolo_hombre_view, name="apolo_hombre"),
    path("zapatos/bota_hombre/", views.bota_hombre_view, name="bota_hombre"),
    path("zapatos/casual_hombre/", views.casual_hombre_view, name="casual_hombre"),
    path("zapatos/nautico_hombre/", views.nautico_hombre_view, name="nautico_hombre"),
    path("zapatos/apache_mujer/", views.apache_mujer_view, name="apache_mujer"),
    path("zapatos/bota_mujer/", views.bota_mujer_view, name="bota_mujer"),
    path('cargar_qr/', views.cargar_qr, name='cargar_qr'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

