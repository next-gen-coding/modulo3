# Convenciones de vacaciones (HU-10)

Complementa `contexto/convenciones_app.md`: mismo backend (FastAPI + SQLite), mismo frontend (React) y las mismas reglas de estilo. Las reglas de negocio están en `contexto/reglas_vacaciones.md`.

## Datos

- El empleado necesita una `fecha_ingreso` (texto `YYYY-MM-DD`). Si el modelo de HU-01 todavía no la tiene, se agrega como campo del empleado sin cambiar el comportamiento de HU-01 a HU-03.
- Nueva tabla `vacaciones`: `id`, `empleado_id`, `fecha_inicio`, `fecha_fin`, `dias_habiles`.
- Las fechas viajan siempre como texto `YYYY-MM-DD`.

## API

### Registrar una solicitud

`POST /api/empleados/{empleado_id}/vacaciones`

```json
{ "fecha_inicio": "2026-12-21", "fecha_fin": "2026-12-31" }
```

Respuesta `201`:

```json
{
  "id": 1,
  "empleado_id": 7,
  "fecha_inicio": "2026-12-21",
  "fecha_fin": "2026-12-31",
  "dias_habiles": 8,
  "dias_restantes": 4
}
```

`dias_restantes` son los días hábiles que le quedan al empleado en el año de la solicitud, ya descontada esta.

### Consultar el saldo del año

`GET /api/empleados/{empleado_id}/vacaciones?anio=2026`

Respuesta `200`:

```json
{
  "empleado_id": 7,
  "anio": 2026,
  "dias_usados": 8,
  "dias_disponibles": 4,
  "solicitudes": [
    { "id": 1, "fecha_inicio": "2026-12-21", "fecha_fin": "2026-12-31", "dias_habiles": 8 }
  ]
}
```

Si no se manda `anio`, se usa el año en curso.

## Errores: mensajes exactos

Todos los errores responden con el formato estándar de FastAPI, `{"detail": "<mensaje>"}`, con **exactamente** estos códigos y textos. El orden de la tabla es el orden en que se validan: se devuelve el primer error que aplique.

| Caso | Código | `detail` |
|---|---|---|
| El empleado no existe | 404 | `Empleado no encontrado` |
| El empleado está dado de baja | 409 | `No se pueden solicitar vacaciones para un empleado dado de baja` |
| `fecha_fin` es anterior a `fecha_inicio` | 400 | `La fecha de fin no puede ser anterior a la fecha de inicio` |
| El periodo cruza de un año a otro | 400 | `Las vacaciones deben estar dentro de un mismo año calendario` |
| El año no está en la tabla de festivos | 400 | `Solo se pueden solicitar vacaciones en 2026 y 2027` |
| Regla 1: menos de un año de antigüedad | 400 | `Se requiere al menos un año de antigüedad a la fecha de inicio` |
| Regla 3: el periodo no tiene días hábiles | 400 | `El periodo no incluye días hábiles` |
| Regla 2: rebasa los días disponibles | 400 | `La solicitud excede los días disponibles: quedan N días hábiles` |

En el último mensaje, `N` es el número de días que quedan en el año de la solicitud, por ejemplo `quedan 4 días hábiles` o `quedan 0 días hábiles`. Siempre se escribe `días hábiles`, también cuando `N` es 1.

Una fecha con formato inválido la rechaza FastAPI con su `422` automático; no hace falta un mensaje propio.

## Pantalla

- En el directorio de empleados, cada empleado activo tiene un botón **Solicitar vacaciones** que abre el formulario.
- El formulario muestra el saldo del año y, al enviar, el resultado: el mensaje de éxito o el `detail` exacto del error que devolvió la API.

`data-testid` obligatorios, para las pruebas E2E:

| Elemento | `data-testid` |
|---|---|
| Botón que abre el formulario (uno por empleado) | `vacaciones-abrir-{empleado_id}` |
| Campo de fecha de inicio | `vacaciones-fecha-inicio` |
| Campo de fecha de fin | `vacaciones-fecha-fin` |
| Botón de enviar | `vacaciones-enviar` |
| Días disponibles en el año | `vacaciones-disponibles` |
| Mensaje de resultado (éxito o error) | `vacaciones-mensaje` |

Mensaje de éxito exacto en `vacaciones-mensaje`: `Solicitud registrada: N días hábiles. Te quedan M días hábiles en AAAA.`