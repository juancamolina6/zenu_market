# ZenuMarket — Guía de instalación

Proyecto desarrollado con **Django** (Python). Esta guía explica cómo configurar el entorno de desarrollo desde cero.

---

## Requisitos previos

Antes de empezar, instalar los siguientes programas:

| Programa | Versión mínima | Descarga |
|----------|---------------|---------|
| Python   | 3.11 o superior | [python.org/downloads](https://python.org/downloads) |
| Git      | Cualquiera reciente | [git-scm.com/downloads](https://git-scm.com/downloads) |
| VS Code  | Cualquiera reciente | [code.visualstudio.com](https://code.visualstudio.com) |

> **Importante (Windows):** Durante la instalación de Python, marcar la casilla **"Add Python to PATH"** antes de continuar.

---

## Extensiones recomendadas de VS Code

Una vez instalado VS Code, buscar e instalar estas extensiones:

- **Python** — de Microsoft (obligatoria)
- **Django** — resaltado de sintaxis para templates
- **GitLens** — historial de cambios del equipo

---

## Instalación paso a paso

### 1. Configurar Git con tu identidad

Abrir la terminal y ejecutar (reemplazar con tus datos):

```bash
git config --global user.name "Tu Nombre"
git config --global user.email "tu@email.com"
```

### 2. Clonar el repositorio

```bash
git clone https://github.com/tu-usuario/zenumarket.git
cd zenumarket
```

### 3. Crear el entorno virtual

```bash
python -m venv venv
```

> El entorno virtual es una instalación aislada de Python solo para este proyecto. Garantiza que todos usen las mismas versiones de las librerías.

### 4. Activar el entorno virtual

**Windows:**
```bash
venv\Scripts\activate
```

**Mac / Linux:**
```bash
source venv/bin/activate
```

Cuando el entorno esté activo, verás `(venv)` al inicio de la línea en la terminal. Este paso hay que repetirlo **cada vez** que abras una terminal nueva.

### 5. Instalar las dependencias

```bash
pip install -r requirements.txt
```

Esto instala automáticamente todas las librerías que el proyecto necesita.

### 6. Crear el archivo `.env`

Crear un archivo llamado `.env` en la raíz del proyecto (mismo nivel que `manage.py`) con el siguiente contenido:

```
SECRET_KEY=django-insecure-cambia-esto-por-una-clave-real
DEBUG=True
```

> **¿Para qué sirve el `.env`?** Guarda información sensible como contraseñas y claves secretas que no deben subirse a GitHub. Cada integrante del equipo tiene su propio archivo `.env` en su computadora. El equipo comparte los valores por un canal privado (WhatsApp, Discord, etc.), nunca por GitHub.

> **Nota:** El profesor o líder del equipo compartirá los valores correctos del `.env` por un canal privado.

### 7. Aplicar las migraciones de la base de datos

```bash
python manage.py migrate
```

Esto crea la base de datos local con todas las tablas necesarias.

### 8. Crear un superusuario (administrador)

```bash
python manage.py createsuperuser
```

Seguir las instrucciones en pantalla para definir usuario y contraseña. Este usuario tendrá acceso al panel de administración.

### 9. Correr el servidor de desarrollo

```bash
python manage.py runserver
```

Abrir el navegador en:

- **Aplicación:** http://127.0.0.1:8000
- **Panel admin:** http://127.0.0.1:8000/admin

---

## Flujo de trabajo con Git (trabajo en equipo)

Antes de empezar a trabajar cada día:

```bash
# 1. Asegurarse de estar en la rama principal
git checkout main

# 2. Traer los últimos cambios del repositorio
git pull origin main
```

Cuando termines de trabajar en algo:

```bash
# 1. Ver qué archivos cambiaste
git status

# 2. Agregar los cambios
git add .

# 3. Guardar los cambios con un mensaje descriptivo
git commit -m "Agrega modelo de Producto con categoría"

# 4. Subir al repositorio
git push origin main
```

---

## Estructura del proyecto

```
zenumarket/
├── zenumarket/           # Configuración principal de Django
│   ├── settings.py       # Configuración general (base de datos, apps, etc.)
│   ├── urls.py           # URLs principales del proyecto
│   └── wsgi.py           # Punto de entrada para producción
├── products/             # App de productos
├── orders/               # App de pedidos y carrito
├── users/                # App de usuarios (cliente, vendedor)
├── static/               # Archivos CSS, JS e imágenes estáticas
├── templates/            # Plantillas HTML base
├── media/                # Archivos subidos por usuarios (imágenes)
├── venv/                 # Entorno virtual (NO se sube a GitHub)
├── .env                  # Variables secretas (NO se sube a GitHub)
├── .gitignore            # Archivos ignorados por Git
├── manage.py             # Comando principal de Django
└── requirements.txt      # Lista de dependencias del proyecto
```

---

## Solución de problemas frecuentes

**`python` no se reconoce como comando (Windows)**
→ Reinstalar Python marcando la opción "Add Python to PATH".

**`(venv)` no aparece en la terminal**
→ El entorno virtual no está activo. Ejecutar el paso 4 nuevamente.

**Error al correr `migrate`**
→ Verificar que el archivo `.env` existe y tiene el formato correcto.

**Puerto 8000 ocupado**
→ Correr el servidor en otro puerto: `python manage.py runserver 8080`

---

## Equipo

| Nombre | Rol |
|--------|-----|
|        | Líder / Backend principal |
|        | Colaborador |
|        | Colaborador |

---

*Cualquier duda, abrir un Issue en el repositorio o contactar al líder del equipo.*
