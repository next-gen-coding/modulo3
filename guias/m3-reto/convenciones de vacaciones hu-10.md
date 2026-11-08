# Convenciones de vacaciones (HU-10)

Complementa `contexto/convenciones_app.md`: mismo backend (FastAPI + SQLite), mismo frontend (React) y las mismas reglas de estilo. Las reglas de negocio estÃ¡n en `contexto/reglas_vacaciones.md`.

## Datos

- El empleado necesita una `fecha_ingreso` (texto `YYYY-MM-DD`). Si el modelo de HU-01 todavÃ­a no la tiene, se agrega como campo del empleado sin cambiar el comportamiento de HU-01 a HU-03.
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

`dias_restantes` son los dÃ­as hÃ¡biles que le quedan al empleado en el aÃ±o de la solicitud, ya descontada esta.

### Consultar el saldo del aÃ±o

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

Si no se manda `anio`, se usa el aÃ±o en curso.

## Errores: mensajes exactos

Todos los errores responden con el formato estÃ¡ndar de FastAPI, `{"detail": "<mensaje>"}`, con **exactamente** estos cÃ³digos y textos. El orden de la tabla es el orden en que se validan: se devuelve el primer error que aplique.

| Caso | CÃ³digo | `detail` |
|---|---|---|
| El empleado no existe | 404 | `Empleado no encontrado` |
| El empleado estÃ¡ dado de baja | 409 | `No se pueden solicitar vacaciones para un empleado dado de baja` |
| `fecha_fin` es anterior a `fecha_inicio` | 400 | `La fecha de fin no puede ser anterior a la fecha de inicio` |
| El periodo cruza de un aÃ±o a otro | 400 | `Las vacaciones deben estar dentro de un mismo aÃ±o calendario` |
| El aÃ±o no estÃ¡ en la tabla de festivos | 400 | `Solo se pueden solicitar vacaciones en 2026 y 2027` |
| Regla 1: menos de un aÃ±o de antigÃ¼edad | 400 | `Se requiere al menos un aÃ±o de antigÃ¼edad a la fecha de inicio` |
| Regla 3: el periodo no tiene dÃ­as hÃ¡biles | 400 | `El periodo no incluye dÃ­as hÃ¡biles` |
| Regla 2: rebasa los dÃ­as disponibles | 400 | `La solicitud excede los dÃ­as disponibles: quedan N dÃ­as hÃ¡biles` |

En el Ãºltimo mensaje, `N` es el nÃºmero de dÃ­as que quedan en el aÃ±o de la solicitud, por ejemplo `quedan 4 dÃ­as hÃ¡biles` o `quedan 0 dÃ­as hÃ¡biles`. Siempre se escribe `dÃ­as hÃ¡biles`, tambiÃ©n cuando `N` es 1.

Una fecha con formato invÃ¡lido la rechaza FastAPI con su `422` automÃ¡tico; no hace falta un mensaje propio.

## Pantalla

- En el directorio de empleados, cada empleado activo tiene un botÃ³n **Solicitar vacaciones** que abre el formulario.
- El formulario muestra el saldo del aÃ±o y, al enviar, el resultado: el mensaje de Ã©xito o el `detail` exacto del error que devolviÃ³ la API.

`data-testid` obligatorios, para las pruebas E2E:

| Elemento | `data-testid` |
|---|---|
| BotÃ³n que abre el formulario (uno por empleado) | `vacaciones-abrir-{empleado_id}` |
| Campo de fecha de inicio | `vacaciones-fecha-inicio` |
| Campo de fecha de fin | `vacaciones-fecha-fin` |
| BotÃ³n de enviar | `vacaciones-enviar` |
| DÃ­as disponibles en el aÃ±o | `vacaciones-disponibles` |
| Mensaje de resultado (Ã©xito o error) | `vacaciones-mensaje` |

Mensaje de Ã©xito exacto en `vacaciones-mensaje`: `Solicitud registrada: N dÃ­as hÃ¡biles. Te quedan M dÃ­as hÃ¡biles en AAAA.`