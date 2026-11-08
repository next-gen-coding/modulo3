# Reglas de negocio · Gestión de empleados

## Datos de un empleado

| Campo | Regla |
| --- | --- |
| id | Entero, lo asigna el sistema |
| numero_empleado | Lo asigna el sistema con el formato EMP-0001, consecutivo; no se edita |
| nombre | Obligatorio, de 2 a 80 caracteres |
| correo | Obligatorio, termina en @empresa.com, único; se guarda en minúsculas; no se edita |
| puesto | Obligatorio, de 2 a 60 caracteres |
| departamento | Uno de: Tecnología, Ventas, Finanzas, Recursos Humanos, Operaciones |
| fecha_ingreso | Obligatoria; no puede ser una fecha futura |
| estado | «activo» al registrar; «baja» al dar de baja |
| fecha_baja | Solo cuando el estado es «baja»; no puede ser anterior a la fecha de ingreso |
| creado_en | Fecha y hora de registro, la asigna el sistema |

## Reglas

1. No puede haber dos empleados con el mismo correo, sin importar mayúsculas. El intento responde 409 con el mensaje «El correo ya está registrado».
2. Un correo que no termina en @empresa.com responde 422 con el mensaje «Usa el correo corporativo @empresa.com».
3. Cualquier otro dato inválido responde 422 y la pantalla muestra qué campo corregir.
4. Una fecha de ingreso futura responde 422 con el mensaje «La fecha de ingreso no puede ser futura».
5. Dar de baja no borra al empleado: cambia su estado a «baja», guarda la fecha de baja y sigue apareciendo en el directorio.
6. Un empleado dado de baja no se puede editar. El intento responde 409 con el mensaje «No se puede editar a un empleado dado de baja».
7. La aplicación no tiene inicio de sesión: está fuera del alcance de este módulo.

# Reglas de vacaciones (HU-10)

Fuente: Guía del reto · HU-10. El tope de 12 días es fijo y no crece con la antigüedad.

| # | Regla | Si no se cumple |
| --- | --- | --- |
| 1 | **Antigüedad:** la fecha de inicio debe ser igual o posterior al primer aniversario de `fecha_ingreso` (si ese día no existe, como un 29 de febrero, se toma el 1 de marzo) | 422 · «Necesitas al menos un año de antigüedad para solicitar vacaciones» |
| 2 | **Días hábiles:** solo cuentan lunes a viernes que no sean festivos oficiales | 422 · «El periodo no incluye días hábiles» |
| 3 | **Tope anual:** 12 días hábiles por año calendario; usar exactamente los que quedan sí está permitido | 422 · «La solicitud excede tus días disponibles: te quedan N» |
| 4 | La fecha de fin no puede ser anterior a la de inicio | 422 · «La fecha de fin no puede ser anterior a la de inicio» |
| 5 | Las dos fechas deben estar en el mismo año calendario | 422 · «Las vacaciones se solicitan dentro de un mismo año» |
| 6 | El empleado debe existir | 404 · «Empleado no encontrado» |

- `dias_habiles` lo calcula el sistema (backend); el empleado solo envía las dos fechas en formato AAAA-MM-DD.
- Los días del periodo se cuentan incluyendo la fecha de inicio y la de fin.
- Los días usados en un año son la suma de `dias_habiles` de las solicitudes registradas en ese año. Los días no usados no pasan al año siguiente.
- En el mensaje de la regla 3, `N` es el número de días que quedan en el año antes de esta solicitud (por ejemplo «te quedan 0» o «te quedan 8»).

## Ejemplos

| Caso | Resultado |
| --- | --- |
| Ingreso 2025-12-21, inicio 2026-12-21 | Sí: cumple exactamente un año |
| Ingreso 2025-12-21, inicio 2026-12-18 | 422 antigüedad |
| Ingreso 2024-02-29, inicio 2025-02-28 | 422 antigüedad (el aniversario es el 1 de marzo de 2025) |
| Ingreso 2024-02-29, inicio 2025-03-03 (lunes) | Sí |
| Lunes 16 al viernes 20 de marzo de 2026 | 4 días hábiles (16 de marzo festivo) |
| Lunes 21 al jueves 31 de diciembre de 2026 | 8 días hábiles (Navidad festivo) |
| 2026-09-14 al 2026-09-18 | 4 días hábiles (16 de septiembre festivo) |
| Sábado 4 al domingo 5 de abril de 2026 | 422 «El periodo no incluye días hábiles» |
| Usados 0, pide 6 al 10 de julio de 2026 (5) | 201; quedan 7 |
| Usados 5, pide 13 al 21 de julio de 2026 (7) | 201; quedan 0 (usa exactamente lo que queda) |
| Usados 12, pide cualquier día hábil | 422 «La solicitud excede tus días disponibles: te quedan 0» |
| Usados 4, pide 9 días hábiles | 422 «La solicitud excede tus días disponibles: te quedan 8» |

## Días festivos oficiales (LFT, art. 74)

| Festivo | 2026 | 2027 |
| --- | --- | --- |
| Año Nuevo | jue 1 ene | vie 1 ene |
| Día de la Constitución | lun 2 feb | lun 1 feb |
| Natalicio de Benito Juárez | lun 16 mar | lun 15 mar |
| Día del Trabajo | vie 1 may | sáb 1 may |
| Día de la Independencia | mié 16 sep | jue 16 sep |
| Día de la Revolución | lun 16 nov | lun 15 nov |
| Navidad | vie 25 dic | sáb 25 dic |

Un festivo que cae en sábado o domingo no cambia nada: ese día ya no contaba.

Para cualquier año se calculan con la misma regla del artículo 74: 1 de enero, primer lunes de febrero, tercer lunes de marzo, 1 de mayo, 16 de septiembre, tercer lunes de noviembre y 25 de diciembre (más el 1 de octubre en los años de cambio del Ejecutivo federal: 2024, 2030…).
