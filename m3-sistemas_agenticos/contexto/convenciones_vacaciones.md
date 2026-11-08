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
