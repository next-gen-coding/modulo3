# Reglas de vacaciones (HU-10)

Reglas de negocio para solicitar vacaciones. Son una versión simplificada para el curso: el tope de 12 días es fijo y no crece con la antigüedad.

## Regla 1 · Antigüedad

- El empleado debe tener **al menos un año cumplido** desde su `fecha_ingreso` a la `fecha_inicio` de las vacaciones.
- Se cumple el año el mismo día y mes del año siguiente: quien ingresó el `2025-12-21` cumple un año el `2026-12-21`.
- Si la fecha de ingreso es un 29 de febrero, el aniversario en un año no bisiesto es el 1 de marzo.

| fecha_ingreso | fecha_inicio | ¿Puede? |
|---|---|---|
| 2025-12-21 | 2026-12-21 | Sí: cumple exactamente un año |
| 2025-12-21 | 2026-12-18 | No: le faltan días |
| 2024-03-10 | 2026-07-06 | Sí |

## Regla 2 · Tope anual

- Cada empleado tiene **12 días hábiles por año calendario** (del 1 de enero al 31 de diciembre).
- Los días usados en el año son la suma de los días hábiles de todas sus solicitudes registradas en ese año.
- Una solicitud se acepta si sus días hábiles son **menores o iguales** a los que quedan: se puede usar exactamente lo que queda.
- Los días que no se usan no pasan al año siguiente.
- Un periodo no puede cruzar de un año a otro: si alguien quiere del 28 de diciembre al 8 de enero, hace dos solicitudes.

| Días usados en el año | Solicitud | Resultado |
|---|---|---|
| 0 | 6 al 10 de julio de 2026 (5 días hábiles) | Aceptada; quedan 7 |
| 5 | 13 al 21 de julio de 2026 (7 días hábiles) | Aceptada; quedan 0 |
| 12 | Cualquier periodo con días hábiles | Rechazada: quedan 0 días hábiles |
| 4 | 9 días hábiles | Rechazada: quedan 8 días hábiles |

## Regla 3 · Días hábiles

- Un día es hábil si **no es sábado, no es domingo y no es festivo oficial**.
- Los días del periodo se cuentan **incluyendo** la fecha de inicio y la de fin.
- Si el periodo no tiene ningún día hábil (por ejemplo, un fin de semana), la solicitud se rechaza.

| Periodo | Días hábiles | Por qué |
|---|---|---|
| 2026-12-21 al 2026-12-31 | 8 | El 25 de diciembre es festivo; dos fines de semana no cuentan |
| 2026-09-14 al 2026-09-18 | 4 | El 16 de septiembre es festivo |
| 2026-07-11 al 2026-07-12 | 0 | Sábado y domingo: se rechaza |

## Festivos oficiales

Días de descanso obligatorio de la Ley Federal del Trabajo, artículo 74. Cuando un festivo cae en sábado o domingo no se recorre: simplemente ese día ya no contaba.

| Festivo | 2026 | 2027 |
|---|---|---|
| Año Nuevo | 2026-01-01 (jueves) | 2027-01-01 (viernes) |
| Día de la Constitución (primer lunes de febrero) | 2026-02-02 | 2027-02-01 |
| Natalicio de Benito Juárez (tercer lunes de marzo) | 2026-03-16 | 2027-03-15 |
| Día del Trabajo | 2026-05-01 (viernes) | 2027-05-01 (sábado) |
| Día de la Independencia | 2026-09-16 (miércoles) | 2027-09-16 (jueves) |
| Revolución Mexicana (tercer lunes de noviembre) | 2026-11-16 | 2027-11-15 |
| Navidad | 2026-12-25 (viernes) | 2027-12-25 (sábado) |

Notas:
- El 1 de octubre solo es festivo cada seis años, cuando cambia el Poder Ejecutivo federal; no ocurre en 2026 ni en 2027.
- La jornada electoral federal de 2027 es el domingo 6 de junio; como cae en domingo, no cambia el conteo.
- Para años fuera de esta tabla, la API puede rechazar la solicitud (ver `convenciones_vacaciones.md`).