# Reglas de vacaciones (HU-10)

Reglas de negocio para solicitar vacaciones. Son una versiÃ³n simplificada para el curso: el tope de 12 dÃ­as es fijo y no crece con la antigÃ¼edad.

## Regla 1 Â· AntigÃ¼edad

- El empleado debe tener **al menos un aÃ±o cumplido** desde su `fecha_ingreso` a la `fecha_inicio` de las vacaciones.
- Se cumple el aÃ±o el mismo dÃ­a y mes del aÃ±o siguiente: quien ingresÃ³ el `2025-12-21` cumple un aÃ±o el `2026-12-21`.
- Si la fecha de ingreso es un 29 de febrero, el aniversario en un aÃ±o no bisiesto es el 1 de marzo.

| fecha_ingreso | fecha_inicio | Â¿Puede? |
|---|---|---|
| 2025-12-21 | 2026-12-21 | SÃ­: cumple exactamente un aÃ±o |
| 2025-12-21 | 2026-12-18 | No: le faltan dÃ­as |
| 2024-03-10 | 2026-07-06 | SÃ­ |

## Regla 2 Â· Tope anual

- Cada empleado tiene **12 dÃ­as hÃ¡biles por aÃ±o calendario** (del 1 de enero al 31 de diciembre).
- Los dÃ­as usados en el aÃ±o son la suma de los dÃ­as hÃ¡biles de todas sus solicitudes registradas en ese aÃ±o.
- Una solicitud se acepta si sus dÃ­as hÃ¡biles son **menores o iguales** a los que quedan: se puede usar exactamente lo que queda.
- Los dÃ­as que no se usan no pasan al aÃ±o siguiente.
- Un periodo no puede cruzar de un aÃ±o a otro: si alguien quiere del 28 de diciembre al 8 de enero, hace dos solicitudes.

| DÃ­as usados en el aÃ±o | Solicitud | Resultado |
|---|---|---|
| 0 | 6 al 10 de julio de 2026 (5 dÃ­as hÃ¡biles) | Aceptada; quedan 7 |
| 5 | 13 al 21 de julio de 2026 (7 dÃ­as hÃ¡biles) | Aceptada; quedan 0 |
| 12 | Cualquier periodo con dÃ­as hÃ¡biles | Rechazada: quedan 0 dÃ­as hÃ¡biles |
| 4 | 9 dÃ­as hÃ¡biles | Rechazada: quedan 8 dÃ­as hÃ¡biles |

## Regla 3 Â· DÃ­as hÃ¡biles

- Un dÃ­a es hÃ¡bil si **no es sÃ¡bado, no es domingo y no es festivo oficial**.
- Los dÃ­as del periodo se cuentan **incluyendo** la fecha de inicio y la de fin.
- Si el periodo no tiene ningÃºn dÃ­a hÃ¡bil (por ejemplo, un fin de semana), la solicitud se rechaza.

| Periodo | DÃ­as hÃ¡biles | Por quÃ© |
|---|---|---|
| 2026-12-21 al 2026-12-31 | 8 | El 25 de diciembre es festivo; dos fines de semana no cuentan |
| 2026-09-14 al 2026-09-18 | 4 | El 16 de septiembre es festivo |
| 2026-07-11 al 2026-07-12 | 0 | SÃ¡bado y domingo: se rechaza |

## Festivos oficiales

DÃ­as de descanso obligatorio de la Ley Federal del Trabajo, artÃ­culo 74. Cuando un festivo cae en sÃ¡bado o domingo no se recorre: simplemente ese dÃ­a ya no contaba.

| Festivo | 2026 | 2027 |
|---|---|---|
| AÃ±o Nuevo | 2026-01-01 (jueves) | 2027-01-01 (viernes) |
| DÃ­a de la ConstituciÃ³n (primer lunes de febrero) | 2026-02-02 | 2027-02-01 |
| Natalicio de Benito JuÃ¡rez (tercer lunes de marzo) | 2026-03-16 | 2027-03-15 |
| DÃ­a del Trabajo | 2026-05-01 (viernes) | 2027-05-01 (sÃ¡bado) |
| DÃ­a de la Independencia | 2026-09-16 (miÃ©rcoles) | 2027-09-16 (jueves) |
| RevoluciÃ³n Mexicana (tercer lunes de noviembre) | 2026-11-16 | 2027-11-15 |
| Navidad | 2026-12-25 (viernes) | 2027-12-25 (sÃ¡bado) |

Notas:
- El 1 de octubre solo es festivo cada seis aÃ±os, cuando cambia el Poder Ejecutivo federal; no ocurre en 2026 ni en 2027.
- La jornada electoral federal de 2027 es el domingo 6 de junio; como cae en domingo, no cambia el conteo.
- Para aÃ±os fuera de esta tabla, la API puede rechazar la solicitud (ver `convenciones_vacaciones.md`).