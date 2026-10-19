# Backlog · historias para ampliar la fábrica

Cada historia se procesa igual que HU-01 a HU-03: se copia a su propio archivo
(`historias/HU-0X-nombre.md`) y se ejecuta con `python -m flujos.flujo_s4`.
Están ordenadas de menor a mayor complejidad. Antes de usar una, agrega a
`contexto/reglas_negocio.md` las reglas nuevas que necesite.

## HU-04 · Asignar jefe directo
Como persona de Recursos Humanos, quiero asignar a cada empleado su jefe directo,
para conocer la línea de reporte.
- Un empleado no puede ser su propio jefe.
- Un empleado dado de baja no puede ser jefe de nadie.

## HU-05 · Consultar antigüedad
Como persona de Recursos Humanos, quiero ver la antigüedad de cada empleado en años y meses,
para preparar los reconocimientos por aniversario.

## HU-06 · Resumen por departamento
Como directora de Recursos Humanos, quiero ver cuántos empleados activos hay en cada departamento,
para planear las contrataciones.

## HU-07 · Organigrama
Como directora de Recursos Humanos, quiero ver el organigrama de un departamento,
para entender cómo está organizado el equipo.
