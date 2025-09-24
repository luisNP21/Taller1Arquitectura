from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Empleado

class EmpleadoAdmin(UserAdmin):
    model = Empleado
    list_display = ['username', 'nombre', 'apellido', 'cedula']
    fieldsets = UserAdmin.fieldsets + (
        ('Datos personales', {'fields': ('cedula', 'nombre', 'apellido')}),
    )

admin.site.register(Empleado, EmpleadoAdmin)
