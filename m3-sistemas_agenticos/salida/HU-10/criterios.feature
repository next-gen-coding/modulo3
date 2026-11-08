# language: es

Característica: Solicitar vacaciones

  Como empleado de la empresa,
  quiero solicitar un periodo de vacaciones indicando la fecha de inicio y la de fin,
  para descansar sin exceder los días que me corresponden.

  # Escenarios de éxito API

  Escenario: Solicitar vacaciones dentro del tope anual
    Dado un empleado con id 1, correo juan@empresa.com, fecha_ingreso 2024-01-15, que hace su primera solicitud en 2026
    Cuando solicita vacaciones del 6 al 10 de julio de 2026 por la API
    Entonces la API responde 201 con 5 dias_habiles y 7 dias_disponibles

  Escenario: Usar exactamente los días disponibles en el año
    Dado un empleado con id 2, correo maria@empresa.com, fecha_ingreso 2024-01-15, con 5 días usados en 2026
    Cuando solicita vacaciones del 13 al 21 de julio de 2026 por la API
    Entonces la API responde 201 con 7 dias_habiles y 0 dias_disponibles

  Escenario: El periodo incluye festivos
    Dado un empleado con id 3, correo carlos@empresa.com, fecha_ingreso 2024-01-15
    Cuando solicita vacaciones del 16 al 20 de marzo de 2026 por la API
    Entonces la API responde 201 con 4 dias_habiles (el 16 de marzo es festivo)

  Escenario: El periodo incluye fines de semana
    Dado un empleado con id 4, correo rosa@empresa.com, fecha_ingreso 2024-01-15
    Cuando solicita vacaciones del 21 de marzo al 1 de abril de 2026 por la API (sábado a miércoles)
    Entonces la API responde 201 con días hábiles sin contar fines de semana

  Escenario: Solicitar en el mes de diciembre con festivo incluido
    Dado un empleado con id 5, correo luis@empresa.com, fecha_ingreso 2024-01-15
    Cuando solicita vacaciones del 21 al 31 de diciembre de 2026 por la API (lunes a jueves)
    Entonces la API responde 201 con 8 dias_habiles (el 25 de diciembre es festivo)

  # Escenarios de error API: antigüedad

  Escenario: Rechazar solicitud sin cumplir un año
    Dado un empleado con id 6, correo ana@empresa.com, fecha_ingreso 2025-12-21
    Cuando solicita vacaciones a partir del 2025-12-18 por la API
    Entonces la API responde 422 con el mensaje «Necesitas al menos un año de antigüedad para solicitar vacaciones»

  Escenario: Permitir solicitud exactamente en el primer aniversario
    Dado un empleado con id 7, correo diego@empresa.com, fecha_ingreso 2025-12-21
    Cuando solicita vacaciones a partir del 2026-12-21 por la API
    Entonces la API responde 201

  Escenario: Rechazar solicitud un día antes del primer aniversario
    Dado un empleado con id 8, correo sofia@empresa.com, fecha_ingreso 2025-12-21
    Cuando solicita vacaciones a partir del 2026-12-20 por la API
    Entonces la API responde 422 con el mensaje «Necesitas al menos un año de antigüedad para solicitar vacaciones»

  Escenario: El aniversario de 29 de febrero se toma el 1 de marzo
    Dado un empleado con id 9, correo pedro@empresa.com, fecha_ingreso 2024-02-29
    Cuando solicita vacaciones a partir del 2025-02-28 por la API
    Entonces la API responde 422 con el mensaje «Necesitas al menos un año de antigüedad para solicitar vacaciones»

  Escenario: Permitir solicitud el 1 de marzo cuando el empleado ingresó el 29 de febrero
    Dado un empleado con id 10, correo laura@empresa.com, fecha_ingreso 2024-02-29
    Cuando solicita vacaciones a partir del 2025-03-03 (lunes) por la API
    Entonces la API responde 201

  # Escenarios de error API: fechas no válidas

  Escenario: Rechazar cuando la fecha de fin es anterior a la de inicio
    Dado un empleado con id 11, correo pablo@empresa.com, fecha_ingreso 2024-01-15
    Cuando solicita vacaciones del 2026-07-15 al 2026-07-10 por la API
    Entonces la API responde 422 con el mensaje «La fecha de fin no puede ser anterior a la de inicio»

  Escenario: Rechazar cuando las fechas están en años diferentes
    Dado un empleado con id 12, correo elena@empresa.com, fecha_ingreso 2024-01-15
    Cuando solicita vacaciones del 2025-12-20 al 2026-01-10 por la API
    Entonces la API responde 422 con el mensaje «Las vacaciones se solicitan dentro de un mismo año»

  # Escenarios de error API: días hábiles

  Escenario: Rechazar periodo que no incluye días hábiles (solo fines de semana)
    Dado un empleado con id 13, correo marcos@empresa.com, fecha_ingreso 2024-01-15
    Cuando solicita vacaciones del 4 al 5 de abril de 2026 por la API (sábado y domingo)
    Entonces la API responde 422 con el mensaje «El periodo no incluye días hábiles»

  # Escenarios de error API: tope anual

  Escenario: Rechazar cuando se solicitan más días de los disponibles
    Dado un empleado con id 14, correo isabel@empresa.com, fecha_ingreso 2024-01-15, con 12 días usados en 2026
    Cuando solicita vacaciones del 6 al 10 de julio de 2026 por la API
    Entonces la API responde 422 con el mensaje «La solicitud excede tus días disponibles: te quedan 0»

  Escenario: Rechazar cuando se piden más días de los que quedan
    Dado un empleado con id 15, correo juan2@empresa.com, fecha_ingreso 2024-01-15, con 4 días usados en 2026
    Cuando solicita vacaciones del 6 al 17 de julio de 2026 por la API (9 días hábiles)
    Entonces la API responde 422 con el mensaje «La solicitud excede tus días disponibles: te quedan 8»

  # Escenarios de error API: empleado no encontrado

  Escenario: Rechazar solicitud para empleado que no existe
    Dado un empleado con id 999 que no existe
    Cuando se intenta solicitar vacaciones por la API
    Entonces la API responde 404 con el mensaje «Empleado no encontrado»

  # Escenarios de orden de validación

  Escenario: Validar que existe el empleado antes de validar el formato de fechas
    Dado un empleado con id 998 que no existe
    Cuando se intenta solicitar vacaciones con fecha_fin anterior a fecha_inicio por la API
    Entonces la API responde 404 con el mensaje «Empleado no encontrado»

  Escenario: Validar el orden de las fechas antes de la antigüedad
    Dado un empleado con id 16, correo veronica@empresa.com, fecha_ingreso 2025-12-21
    Cuando solicita vacaciones del 2026-07-15 al 2026-07-10 por la API
    Entonces la API responde 422 con el mensaje «La fecha de fin no puede ser anterior a la de inicio»

  Escenario: Validar que el mismo año antes de validar antigüedad
    Dado un empleado con id 17, correo victor@empresa.com, fecha_ingreso 2025-12-21
    Cuando solicita vacaciones del 2025-12-20 al 2026-01-10 por la API
    Entonces la API responde 422 con el mensaje «Las vacaciones se solicitan dentro de un mismo año»

  # Escenarios de pantalla: éxito

  Escenario: Mostrar el formulario de vacaciones y registrar solicitud con éxito
    Dado un empleado activo con id 20, correo test1@empresa.com, fecha_ingreso 2024-01-15, con 0 días usados en 2026
    Cuando accede a sus vacaciones por la pantalla
    Entonces ve el campo `vacaciones-fecha-inicio` vacío, el campo `vacaciones-fecha-fin` vacío, el botón `vacaciones-solicitar` habilitado y `vacaciones-disponibles` muestra 12
    Y completa el formulario con fecha_inicio 2026-07-06 y fecha_fin 2026-07-10
    Y hace clic en `vacaciones-solicitar`
    Entonces se muestra en `mensaje-exito` el texto «Solicitud registrada: 5 días hábiles. Te quedan 7 días disponibles.»
    Y aparece la solicitud en `tabla-vacaciones` con `fila-vacaciones-{id}` y `dias-vacaciones-{id}` muestra «5»

  Escenario: Mostrar días disponibles cuando hay solicitudes anteriores
    Dado un empleado activo con id 21, correo test2@empresa.com, fecha_ingreso 2024-01-15, con 5 días usados en 2026
    Cuando accede a sus vacaciones por la pantalla
    Entonces `vacaciones-disponibles` muestra 7

  # Escenarios de pantalla: error

  Escenario: Mostrar error en la pantalla cuando se excede el tope anual
    Dado un empleado activo con id 22, correo test3@empresa.com, fecha_ingreso 2024-01-15, con 12 días usados en 2026
    Cuando accede a sus vacaciones por la pantalla
    Y completa el formulario con fecha_inicio 2026-07-06 y fecha_fin 2026-07-10
    Y hace clic en `vacaciones-solicitar`
    Entonces se muestra en `mensaje-error` el texto «La solicitud excede tus días disponibles: te quedan 0»

  Escenario: Mostrar error en la pantalla cuando no cumple antigüedad
    Dado un empleado activo con id 23, correo test4@empresa.com, fecha_ingreso 2025-12-21
    Cuando accede a sus vacaciones por la pantalla
    Y completa el formulario con fecha_inicio 2025-12-18 y fecha_fin 2025-12-20
    Y hace clic en `vacaciones-solicitar`
    Entonces se muestra en `mensaje-error` el texto «Necesitas al menos un año de antigüedad para solicitar vacaciones»
