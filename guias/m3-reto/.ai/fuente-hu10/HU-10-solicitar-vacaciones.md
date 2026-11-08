# HU-10 · Solicitar vacaciones

**Como** empleado de la empresa,
**quiero** solicitar días de vacaciones indicando una fecha de inicio y una de fin,
**para** que mi solicitud quede registrada y sepa cuántos días me quedan en el año.

## Reglas de negocio

1. **Antigüedad.** Solo puede solicitar vacaciones quien tiene al menos un año cumplido de antigüedad a la fecha de inicio de las vacaciones.
2. **Tope anual.** Cada empleado tiene 12 días hábiles de vacaciones por año calendario. Se puede usar exactamente lo que queda, pero no más.
3. **Días hábiles.** Solo cuentan los días hábiles: no cuentan sábados, domingos ni días festivos oficiales.

El detalle de cada regla, con ejemplos y los festivos de 2026 y 2027, está en `contexto/reglas_vacaciones.md`.
La API, los mensajes de error exactos y la pantalla están en `contexto/convenciones_vacaciones.md`.

## Criterios de aceptación esperados (resumen)

- Una solicitud válida se registra y responde con los días hábiles que consume y los días que quedan en el año.
- Una solicitud de un empleado con menos de un año de antigüedad se rechaza con su mensaje exacto.
- Una solicitud que rebasa los días disponibles del año se rechaza indicando cuántos días quedan.
- Los sábados, domingos y festivos dentro del periodo no se descuentan.
- Un periodo sin ningún día hábil se rechaza.
- Una fecha de fin anterior a la de inicio, un periodo que cruza de un año a otro, un empleado que no existe y un empleado dado de baja se rechazan con su mensaje exacto.

## Notas

- Esta historia extiende la aplicación de gestión de empleados de HU-01 a HU-03: no cambia el comportamiento de registrar, consultar, editar ni dar de baja.
- Los mensajes de error deben ser exactamente los de `contexto/convenciones_vacaciones.md`: la API se califica con pruebas automáticas.