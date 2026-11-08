# HU-10 Â· Solicitar vacaciones

**Como** empleado de la empresa,
**quiero** solicitar dÃ­as de vacaciones indicando una fecha de inicio y una de fin,
**para** que mi solicitud quede registrada y sepa cuÃ¡ntos dÃ­as me quedan en el aÃ±o.

## Reglas de negocio

1. **AntigÃ¼edad.** Solo puede solicitar vacaciones quien tiene al menos un aÃ±o cumplido de antigÃ¼edad a la fecha de inicio de las vacaciones.
2. **Tope anual.** Cada empleado tiene 12 dÃ­as hÃ¡biles de vacaciones por aÃ±o calendario. Se puede usar exactamente lo que queda, pero no mÃ¡s.
3. **DÃ­as hÃ¡biles.** Solo cuentan los dÃ­as hÃ¡biles: no cuentan sÃ¡bados, domingos ni dÃ­as festivos oficiales.

El detalle de cada regla, con ejemplos y los festivos de 2026 y 2027, estÃ¡ en `contexto/reglas_vacaciones.md`.
La API, los mensajes de error exactos y la pantalla estÃ¡n en `contexto/convenciones_vacaciones.md`.

## Criterios de aceptaciÃ³n esperados (resumen)

- Una solicitud vÃ¡lida se registra y responde con los dÃ­as hÃ¡biles que consume y los dÃ­as que quedan en el aÃ±o.
- Una solicitud de un empleado con menos de un aÃ±o de antigÃ¼edad se rechaza con su mensaje exacto.
- Una solicitud que rebasa los dÃ­as disponibles del aÃ±o se rechaza indicando cuÃ¡ntos dÃ­as quedan.
- Los sÃ¡bados, domingos y festivos dentro del periodo no se descuentan.
- Un periodo sin ningÃºn dÃ­a hÃ¡bil se rechaza.
- Una fecha de fin anterior a la de inicio, un periodo que cruza de un aÃ±o a otro, un empleado que no existe y un empleado dado de baja se rechazan con su mensaje exacto.

## Notas

- Esta historia extiende la aplicaciÃ³n de gestiÃ³n de empleados de HU-01 a HU-03: no cambia el comportamiento de registrar, consultar, editar ni dar de baja.
- Los mensajes de error deben ser exactamente los de `contexto/convenciones_vacaciones.md`: la API se califica con pruebas automÃ¡ticas.