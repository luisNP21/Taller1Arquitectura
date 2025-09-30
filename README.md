# Zodiak Inventory — README

Guía rápida para clonar, crear entorno, instalar dependencias y ejecutar el proyecto.

---

## Requisitos

* **Python 3.13** (recomendado; funciona con 3.11+).
* **pip** y **wheel** actualizados.
* (Opcional) **MySQL** si vas a usar la BD en MySQL; por defecto puedes usar **SQLite**.
* **Git**.


---


## 1) Clonar el repositorio

```bash
git clone https://github.com/luisNP21/Taller1Arquitectura.git
cd Taller1Arquitectura
```

Si vas a trabajar en una rama propia (recomendado):

```bash
git checkout -b maria
```

---

## 2) Crear y activar entorno virtual

### Windows (PowerShell)

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
```

> Para salir del entorno: `deactivate`

---

## 3) Actualizar pip / wheel

```bash
python -m pip install --upgrade pip wheel
```

---

## 4) Instalar dependencias

```bash
pip install -r requirements.txt
```

### Si usas MySQL (opcional)

* Asegúrate de tener MySQL corriendo y credenciales válidas en `settings.py` (o variables de entorno).
* Instala el conector (si no está): `pip install mysqlclient`

  > En Windows puede requerir **Visual C++ Build Tools**.

Si no configuras MySQL, **SQLite** funciona por defecto sin pasos extra.

---

## 5) Variables y rutas de archivos

El proyecto guarda archivos en `MEDIA_ROOT` (por defecto, `media/`):

* PDFs de pedidos: `media/pdf_pedidos/`
* Códigos QR: `qr_codes/` (la app los crea si no existen)

No necesitas configuraciones especiales para desarrollo con `DEBUG=True`.

---

## 6) Migraciones y superusuario

```bash
python manage.py migrate
python manage.py createsuperuser
```

Sigue el asistente para crear el usuario admin (usuario/contraseña).

---

## 7) Ejecutar el servidor

```bash
python manage.py runserver
```

Abre: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)

---
## Nota importante

Para iniciar sesión a la hora de ejecutar puedes usar el siguiente superusuario:

- **Usuario:** `admin1`  
- **Contraseña:** `Z0d14k000`
---

## 8) Rutas principales (guía funcional)

* **/** → Login
* **/landing/** → Dashboard
* **/categorias/** → Catálogo por categorías
* **/ver_carrito/** → Carrito de pedido
* **/ver_clientes/** → Listado de clientes
* **/crear_clientes/** → Crear cliente
* **/agregar_pedido/** → Agregar ítems (POST)
* **/generar_pedido/** → Generar Pedido + PDF + QRs (POST)
* **/ver_pedidos/** → Listado de pedidos
* **/zapatos/<pedido_id>/** → Zapatos de un pedido (link al PDF)
* **/cargar_qr/** → Subir imagen/PDF con QR para actualizar estados
* **/ver_stock/** → Filtro y listado de stock

---

## 9) Flujo recomendado de prueba

1. Inicia sesión con tu **superuser**.
2. Ve a **/categorias/** y agrega productos al carrito.
3. En **/ver_carrito/** selecciona **cliente** y **comentarios**, luego **Generar pedido**:

   * Se crean **QRs** por zapato y un **PDF** del pedido en `media/pdf_pedidos/`.
4. Cuando tengas cajas etiquetadas con los QRs, usa **/cargar_qr/**:

   * Sube una **imagen o PDF** de los códigos QR para actualizar el estado de los zapatos.
5. Verifica el inventario en **/ver_stock/** con filtros por **referencia, modelo, talla, color, sexo, estado**.

---





