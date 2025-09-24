import os
import django

# Configura el entorno de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'zodiak_inventory.settings')
django.setup()

from .models import Zapato, Pedido

# Borra todos los registros de las tablas Zapato y Pedido
Zapato.objects.all().delete()
Pedido.objects.all().delete()

print("Todos los registros de Zapato y Pedido han sido eliminados.")