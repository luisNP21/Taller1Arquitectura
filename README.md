# Zodiak Inventory App 🛍️

Un sistema de gestión de inventario construido con Django para administrar inventario de calzado, pedidos e información de clientes.

## 🌟 Características

- **Autenticación de Usuarios**
  - Sistema seguro de inicio/cierre de sesión
  - Control de acceso basado en roles
  - Gestión de sesiones

- **Gestión de Inventario**
  - Seguimiento de stock en tiempo real
  - Múltiples categorías de calzado (Apache, Apolo, Amaka, Nautico, Bota, Casual)
  - Catálogo específico por género (Colecciones para Hombres y Mujeres)
  - Gestión de tallas y colores
  - Seguimiento de estado del stock (Pendiente, Producción, Bodega)

- **Gestión de Pedidos**
  - Funcionalidad de carrito de compras
  - Creación y seguimiento de pedidos
  - Generación de PDF con códigos QR
  - Actualizaciones de estado de pedidos
  - Historial de pedidos por cliente

- **Gestión de Clientes**
  - Base de datos de clientes
  - Historial de pedidos por cliente
  - Gestión de información de clientes

- **Integración de Códigos QR**
  - Generación de códigos QR para productos
  - Escaneo de códigos QR para actualizaciones de inventario
  - Soporte para conversión de PDF a códigos QR

## 🛠️ Stack Tecnológico

- **Framework Backend**: Django
- **Base de Datos**: SQLite (predeterminado) / PostgreSQL (configurable)
- **Frontend**: HTML, CSS, JavaScript
- **Librerías Adicionales**:
  - ReportLab (generación de PDF)
  - QRCode (generación de códigos QR)
  - OpenCV (procesamiento de imágenes)
  - PyZBar (lectura de códigos QR)
  - pdf2image (procesamiento de PDF)

## 📋 Prerrequisitos

- Python 3.8 o superior
- pip (gestor de paquetes de Python)
- Entorno virtual (recomendado)

## 🚀 Instalación

1. Clonar el repositorio:
```bash
git clone https://github.com/yourusername/ZodiakInventoryApp.git
cd ZodiakInventoryApp
```

2. Crear y activar un entorno virtual:
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

3. Instalar dependencias:
```bash
pip install -r requirements.txt
```

4. Ejecutar migraciones:
```bash
python manage.py migrate
```

5. Crear superusuario:
```bash
python manage.py createsuperuser
```

6. Ejecutar el servidor de desarrollo:
```bash
python manage.py runserver
```

## 📁 Estructura del Proyecto

```
ZodiakInventoryApp/
├── app1/                    # Directorio principal de la aplicación
│   ├── models.py           # Modelos de base de datos
│   ├── views.py            # Lógica de vistas
│   ├── forms.py            # Definiciones de formularios
│   └── templates/          # Plantillas HTML
├── static/                 # Archivos estáticos (CSS, JS, imágenes)
├── media/                  # Archivos subidos por usuarios
├── manage.py              # Script de gestión de Django
└── requirements.txt       # Dependencias del proyecto
```

## 🔐 Variables de Entorno

Crear un archivo `.env` en el directorio raíz con las siguientes variables:

```
DEBUG=True
SECRET_KEY=tu_clave_secreta
DATABASE_URL=tu_url_de_base_de_datos
```

## 📝 Uso

1. **Acceso al Panel de Administración**
   - Navegar a `/admin` para acceder a la interfaz de administración
   - Iniciar sesión con las credenciales de superusuario

2. **Gestión de Inventario**
   - Agregar nuevos productos a través de la interfaz de administración
   - Actualizar niveles de stock
   - Seguimiento del estado de productos

3. **Procesamiento de Pedidos**
   - Crear nuevos pedidos
   - Generar códigos QR
   - Seguimiento del estado de pedidos
   - Generar informes PDF

4. **Gestión de Clientes**
   - Agregar nuevos clientes
   - Ver historial de clientes
   - Gestionar información de clientes

## 🔄 Flujo de Trabajo

1. **Creación de Pedidos**
   - Seleccionar productos
   - Agregar al carrito
   - Asignar a cliente
   - Generar pedido

2. **Proceso de Producción**
   - Escanear códigos QR
   - Actualizar estado de productos
   - Seguimiento del progreso de producción

3. **Actualizaciones de Inventario**
   - Escanear códigos QR para actualizaciones de stock
   - Actualizaciones automáticas de estado
   - Seguimiento de inventario en tiempo real

## 🤝 Contribución

1. Hacer fork del repositorio
2. Crear una rama para la nueva característica
3. Realizar cambios
4. Subir cambios a la rama
5. Crear un Pull Request

## 📄 Licencia

Este proyecto está licenciado bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para más detalles.

## 👥 Autores

- @thomasSC0607 - @JuanesAo - @Maocampog1 - @luisNP21

## 🙏 Agradecimientos

- Documentación de Django
- Documentación de ReportLab
- Biblioteca QRCode
- Comunidad de OpenCV


