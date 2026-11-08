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

# Convenciones de vacaciones (HU-10)

Fuente: Guía del reto · HU-10. Mismo backend (FastAPI + SQLite) y frontend (React); extiende HU-01 a HU-03 sin cambiar su comportamiento. Reglas en `contexto/reglas_vacaciones.md`.

## Datos

- El empleado ya tiene `fecha_ingreso` (HU-01).
- Nueva tabla `vacaciones`: `id`, `empleado_id`, `fecha_inicio`, `fecha_fin`, `dias_habiles`.
- Las fechas viajan como texto `AAAA-MM-DD`.

## API

| Método y ruta | Cuerpo | Respuesta correcta |
| --- | --- | --- |
| `POST /api/empleados/{id}/vacaciones` | `{"fecha_inicio": "AAAA-MM-DD", "fecha_fin": "AAAA-MM-DD"}` | 201 con `id`, `empleado_id`, `fecha_inicio`, `fecha_fin`, `dias_habiles` y `dias_disponibles` (los que quedan después de esta solicitud) |
| `GET /api/empleados/{id}/vacaciones?anio=AAAA` | — | 200 con `anio`, `dias_por_anio` (12), `dias_usados`, `dias_disponibles` y `solicitudes` (cada una con `id`, `empleado_id`, `fecha_inicio`, `fecha_fin`, `dias_habiles`) |

- Si no se manda `anio`, se usa el año en curso.
- Los errores tienen la forma `{"detail": "mensaje"}`, con el código y el mensaje exactos de `contexto/reglas_vacaciones.md`.
- Orden de validación (se devuelve el primer error que aplique): 1) empleado existe (404); 2) fin no anterior a inicio; 3) mismo año; 4) antigüedad; 5) días hábiles; 6) tope anual. Es decir: se valida el año, el orden de las fechas y la antigüedad antes de contar días.
- Una fecha con formato inválido la rechaza FastAPI con su 422 automático.

## Pantalla

En la pantalla, cada empleado activo del directorio tiene un botón para abrir sus vacaciones. Al abrirlas se ven los días disponibles del año, el formulario y la lista de solicitudes. Al registrar, el empleado ve cuántos días hábiles se le descontaron y cuántos le quedan; si hay error, se muestra el `detail` exacto de la API.

| Elemento | data-testid |
| --- | --- |
| Botón en la fila del directorio | `vacaciones-empleado-{id}` |
| Fechas | `vacaciones-fecha-inicio`, `vacaciones-fecha-fin` |
| Botón solicitar | `vacaciones-solicitar` |
| Días disponibles del año (solo el número) | `vacaciones-disponibles` |
| Lista de solicitudes | `tabla-vacaciones`, `fila-vacaciones-{id}`, `dias-vacaciones-{id}` |
| Mensajes | `mensaje-exito`, `mensaje-error` |

Texto de éxito en `mensaje-exito`: `Solicitud registrada: N días hábiles. Te quedan M días disponibles.`
