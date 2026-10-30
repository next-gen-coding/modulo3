# Convenciones de la aplicación de gestión de empleados

Este archivo se copia como `app/CLAUDE.md`. Claude Code lo lee antes de escribir código.

## Arquitectura

- `backend/`: FastAPI + SQLAlchemy 2 + SQLite, con Pydantic v2. El archivo `backend/main.py` expone la aplicación como `app`.
- La base de datos vive en `backend/datos/empleados.db`; la carpeta `datos/` se crea al arrancar si no existe.
- `backend/requirements.txt` lista las dependencias del backend.
- `frontend/`: React + Vite en JavaScript, sin librerías de componentes.
- Todo lo de la API cuelga de `/api`. Salud: `GET /api/salud` responde `{"estado": "ok"}`.

## Puertos

- Backend: 8000. Frontend en desarrollo: 5173, con proxy de `/api` hacia el puerto 8000.
- En Docker, el frontend se sirve en el puerto 8080 y redirige `/api` al servicio `backend`.
- El frontend siempre llama a la API con rutas relativas (`/api/...`).

## API

- Recurso principal: `/api/empleados`. Campos en español: `id`, `numero_empleado`, `nombre`, `correo`, `puesto`, `departamento`, `fecha_ingreso`, `estado`, `fecha_baja`, `creado_en`.
- Catálogo: `GET /api/departamentos` devuelve la lista de departamentos válidos.
- Fechas en formato ISO (`AAAA-MM-DD`).
- Errores con la forma `{"detail": "mensaje en español"}` y códigos 404, 409 o 422.
- Las historias futuras agregarán recursos nuevos (por ejemplo `/api/vacaciones`); el código debe permitir agregarlos sin reescribir lo existente.

## Selectores para pruebas (data-testid)

Todo elemento que una prueba necesite tocar lleva `data-testid` con estos nombres:

| Elemento | data-testid |
| --- | --- |
| Campos del formulario | `empleado-nombre`, `empleado-correo`, `empleado-puesto`, `empleado-departamento`, `empleado-fecha-ingreso` |
| Botón guardar | `empleado-guardar` |
| Mensajes | `mensaje-exito`, `mensaje-error` |
| Directorio y filas | `tabla-empleados`, `fila-empleado-{id}` |
| Datos por fila | `numero-empleado-{id}`, `estado-empleado-{id}` (texto «Activo» o «Baja») |
| Búsqueda y filtro | `buscar-empleados`, `filtro-departamento`, `sin-resultados` |
| Acciones por fila | `editar-empleado-{id}`, `baja-empleado-{id}` |
| Fecha de baja | `empleado-fecha-baja`, `confirmar-baja` |

## Reglas para quien programa

- Las reglas de negocio te llegan en el prompt; aquí no tienes acceso a carpetas superiores.
- Si `app/` ya tiene código de historias anteriores, extiéndelo sin romperlo.
- No agregues autenticación ni dependencias que no estén en esta lista sin justificarlo.
- Al terminar: `GET /api/salud` responde y `npm run build` termina sin errores.