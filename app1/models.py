# app1/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser

class Empleado(AbstractUser):
    cedula = models.CharField(max_length=15, unique=True, null=True, blank=True)
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.nombre} {self.apellido}"
    
class Zapato(models.Model):
    GENERO_CHOICES = [
        ('H', 'Hombre'),
        ('M', 'Mujer'),
    ]
    TALLAS_CHOICES = [
        ('34', '34'),
        ('35', '35'),
        ('36', '36'),
        ('37', '37'),
        ('38', '38'),
        ('39', '39'),
        ('40', '40'),
        ('41', '41'),
        ('42', '42'),
        ('43', '43'),
        ('44', '44'),
        ('45', '45'),
    ]
    MODELO_CHOICES = [
        ('Apache', 'Apache'),
        ('Apolo', 'Apolo'),
        ('Amaka', 'Amaka'),
        ('Nautico', 'Nautico'),
        ('Bota', 'Bota'),
        ('Casual', 'Casual'),
        ('Sport', 'Sport'),
    ]
    COLOR_CHOICES = [
        ('Rojo', 'Rojo'),
        ('Azul', 'Azul'),
        ('Verde', 'Verde'),
        ('Amarillo', 'Amarillo'),
    ]
    ESTADO_CHOICES = [
        ('Pendientes', 'Pendiente'),
        ('Producción', 'En Producción'),
        ('Anulado', 'Anulado'),
        ('Completado', 'Completado'),
        ('Entregado', 'Entregado'),
        ('Bodega', 'En Bodega'),
    ]
    referencia = models.CharField(max_length=20)
    # El modelo es lo mismo que la categoría del zapato
    modelo = models.CharField(max_length=10, choices=MODELO_CHOICES) # En el formulario se puede manejar a través de opciones
    talla = models.CharField(max_length=2, choices=TALLAS_CHOICES)
    sexo = models.CharField(max_length=1, choices=GENERO_CHOICES)
    color = models.CharField(max_length=10, choices=COLOR_CHOICES)
    estado = models.CharField(max_length=10, choices=ESTADO_CHOICES, default='Pendientes') # El estado por defecto es pendientes
    requerimientos = models.TextField()
    observaciones = models.TextField(default='Sin observaciones', null=True, blank=True) # El campo observaciones es opcional    
    pedido = models.ForeignKey('Pedido', on_delete=models.CASCADE, null=True, blank=True) # Relación uno a muchos con la tabla Pedido
    imagen = models.CharField(max_length=150, null=True, blank=True)

class Cliente(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    direccion = models.CharField(max_length=200)
    telefono = models.CharField(max_length=15)
    correo = models.EmailField()
    
class Pedido(models.Model):
    ESTADO_CHOICES = [
        ('Pendiente', 'Pendiente'),
        ('Completada', 'Completada'),
        ('Anulada', 'Anulada'),
    ]

    empleado = models.ForeignKey(Empleado, on_delete=models.CASCADE, null=True, blank=True) # Relación uno a muchos con la tabla Empleado
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_terminacion = models.DateTimeField(null=True, blank=True) # La fecha de terminación es opcional
    estado = models.CharField(max_length=10, choices=ESTADO_CHOICES, default='Pendiente') # El estado por defecto es pendiente
    observaciones = models.TextField(default='Sin observaciones', null=True, blank=True) # El campo observaciones es opcional
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE) # Relación uno a muchos con la tabla Cliente
