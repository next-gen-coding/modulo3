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
