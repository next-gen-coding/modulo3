# Guía del reto · HU-10 Solicitar vacaciones

Oct 15, 2026 · @Ricardo Ivison

## Qué es el reto

En los cuatro laboratorios construiste una fábrica de seis agentes que convierte una historia de usuario en una aplicación desplegada y probada. En el reto la usas con una historia nueva, **HU-10 · Solicitar vacaciones**, y agregas esa funcionalidad a la aplicación de empleados que ya tienes.

No se trata de programar la funcionalidad tú: se trata de que **tu fábrica** la programe, la despliegue y la pruebe, y de que tú la dirijas como lo haría un líder técnico.

|  |  |
| --- | --- |
| Modalidad | Individual |
| Plazo | Una semana a partir de la sesión 4 |
| Peso | 60 % de la nota del módulo (el examen vale el otro 40 %) |
| Punto de partida | Tu repositorio tal como quedó al terminar el Lab 4, con HU-01 a HU-03 funcionando |

### Lo que entregas

Un solo commit en tu repositorio con:

- Los cambios que hiciste en `contexto/` y en tu fábrica (`agentes/`, `flujos/`).
- La app generada en `app/`.
- La carpeta `salida/HU-10/` completa: `criterios.feature`, `casos_prueba.json`, `reporte.md` y `decisiones.md`.
- `auditoria.jsonl`, en la raíz del repositorio, de la ejecución final.

Si necesitas varias ejecuciones, está bien: cuenta lo que quede en el último commit. Nunca incluyas tu `.env`.

### Reglas de integridad

- **No edites a mano nada de `app/` ni de `salida/`.** Si un agente se equivoca, corrige al agente (sus instrucciones, el contexto, sus validadores o sus permisos) y vuelve a ejecutar. Sí puedes cambiar el código de tu fábrica en `agentes/`, `flujos/` y `contexto/`.
- **No quites ni desactives los hooks de seguridad**, y no ejecutes el reto con `DEFENSAS=0`. Sin defensas no hay `auditoria.jsonl`, y sin auditoría no hay forma de demostrar que no editaste a mano.
- **Los mensajes y códigos de respuesta deben ser exactamente los de las reglas.** Tu profesor califica la API con un conjunto de pruebas propio, construido con esas reglas, que tú no ves. Un acento o un punto de más cuenta como falla.
- El trabajo es individual. Puedes usar Claude Code para mejorar tu fábrica, pero las respuestas de `decisiones.md` deben hablar de **tu** ejecución.

## La historia HU-10 y sus reglas

> Como empleado de la empresa, quiero solicitar un periodo de vacaciones indicando la fecha de inicio y la de fin, para descansar sin exceder los días que me corresponden.

Las notas del dueño del producto dicen: solo puede pedir vacaciones quien ya cumplió un año; hay un tope de días por año; los fines de semana y festivos no cuentan; y al registrar la solicitud el empleado quiere ver cuántos días hábiles se le descontaron y cuántos le quedan.

### Los tres archivos que recibes

| Archivo | Qué haces con él |
| --- | --- |
| `HU-10-solicitar-vacaciones.md` | Cópialo a `historias/` |
| `reglas_vacaciones.md` | Agrégalo al final de `contexto/reglas_negocio.md` |
| `convenciones_vacaciones.md` | Agrégalo al final de `contexto/convenciones_app.md` |

La historia es deliberadamente breve: el detalle vive en el contexto, que todos los agentes leen. Si el analista inventa reglas o hace preguntas que el contexto ya responde, revisa que agregaste bien estos archivos.

### Las reglas de negocio

| # | Regla | Si no se cumple |
| --- | --- | --- |
| 1 | **Antigüedad:** la fecha de inicio debe ser igual o posterior al primer aniversario de `fecha_ingreso` (si ese día no existe, como un 29 de febrero, se toma el 1 de marzo) | 422 · «Necesitas al menos un año de antigüedad para solicitar vacaciones» |
| 2 | **Días hábiles:** solo cuentan lunes a viernes que no sean festivos oficiales | 422 · «El periodo no incluye días hábiles» |
| 3 | **Tope anual:** 12 días hábiles por año calendario; usar exactamente los que quedan sí está permitido | 422 · «La solicitud excede tus días disponibles: te quedan N» |
| 4 | La fecha de fin no puede ser anterior a la de inicio | 422 · «La fecha de fin no puede ser anterior a la de inicio» |
| 5 | Las dos fechas deben estar en el mismo año calendario | 422 · «Las vacaciones se solicitan dentro de un mismo año» |
| 6 | El empleado debe existir | 404 · «Empleado no encontrado» |

El campo `dias_habiles` lo calcula el sistema; el empleado solo envía las dos fechas en formato AAAA-MM-DD.

### Días festivos oficiales (LFT, art. 74)

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

**Ejemplos para comprobar tu intuición** (y la de tus agentes):

- Del lunes 16 al viernes 20 de marzo de 2026: 5 días entre semana, menos el festivo del 16 = **4 días hábiles**.
- Del lunes 21 al jueves 31 de diciembre de 2026: 9 días entre semana, menos Navidad = **8 días hábiles**.
- Del sábado 4 al domingo 5 de abril de 2026: ningún día hábil → 422.

### La API y la pantalla

| Método y ruta | Cuerpo | Respuesta correcta |
| --- | --- | --- |
| `POST /api/empleados/{id}/vacaciones` | `{"fecha_inicio": "AAAA-MM-DD", "fecha_fin": "AAAA-MM-DD"}` | 201 con `id`, `empleado_id`, `fecha_inicio`, `fecha_fin`, `dias_habiles` y `dias_disponibles` (los que quedan después de esta solicitud) |
| `GET /api/empleados/{id}/vacaciones?anio=AAAA` | — | 200 con `anio`, `dias_por_anio` (12), `dias_usados`, `dias_disponibles` y `solicitudes` |

Los errores tienen la forma `{"detail": "mensaje"}`.

En la pantalla, cada empleado activo del directorio tiene un botón para abrir sus vacaciones. Estos son los `data-testid` que tus pruebas E2E (y las del profesor) van a buscar:

| Elemento | data-testid |
| --- | --- |
| Botón en la fila del directorio | `vacaciones-empleado-{id}` |
| Fechas | `vacaciones-fecha-inicio`, `vacaciones-fecha-fin` |
| Botón solicitar | `vacaciones-solicitar` |
| Días disponibles del año (solo el número) | `vacaciones-disponibles` |
| Lista de solicitudes | `tabla-vacaciones`, `fila-vacaciones-{id}`, `dias-vacaciones-{id}` |
| Mensajes | `mensaje-exito`, `mensaje-error` |

## Paso a paso

### 0 · Prepara tu repositorio

1. Parte de una fábrica que funcione: si HU-01 a HU-03 no pasan sus pruebas, arréglalo primero corrigiendo a los agentes, no la app.
2. Copia la historia a `historias/` y agrega las reglas y convenciones al final de sus archivos de contexto (ver la sección anterior).
3. Comprueba que Docker está arriba y que la app actual corre en el puerto 8080.
4. Revisa qué tiene que saber cada agente que antes no sabía. Por ejemplo: ¿el validador de Gherkin del analista exige un escenario por cada regla? ¿Las instrucciones del automatizador piden datos únicos y fechas de ingreso que permitan probar la antigüedad?

### Ejecuta la fábrica

```bash
python -m flujos.flujo_s4 historias/HU-10-solicitar-vacaciones.md
```

Cada etapa debe dejar su evidencia:

| Etapa | Agente | Evidencia esperada |
| --- | --- | --- |
| 1 · Criterios de aceptación | Analista | `salida/HU-10/criterios.feature`, validado, con al menos un escenario por regla y sus mensajes exactos |
| 2 · Casos de prueba | Diseñador | `salida/HU-10/casos_prueba.json`, validado, con al menos un caso por escenario |
| 3 · Código | Desarrollador (Claude Code) | Un plan que tú aprobaste o corregiste, y la app extendida (API y pantalla) sin romper HU-01 a HU-03 |
| 4 · Despliegue | Despliegue (Claude Code) | La app corre con Docker Compose en el puerto 8080 |
| 5 · Pruebas automatizadas | Automatizador (Claude Code) | Pruebas de API y E2E con Playwright para vacaciones en `app/tests/` |
| 6 · De punta a punta | Triage y reporte | `salida/HU-10/reporte.md` con el estado final, cada falla y quién la corrigió |

### Qué revisar en cada parada

**Después del analista.** Abre `criterios.feature` y busca, una por una, las seis reglas. ¿Están los cinco mensajes 422 y el 404 copiados letra por letra? ¿Hay un escenario para el límite exacto (usar justo los días que quedan) y otro para cuando se pasa por uno?

**En la aprobación del plan.** Es tu momento de mayor influencia. Antes de escribir `si`, comprueba que el plan:

- extiende el código de HU-01 a HU-03 sin reemplazarlo;
- calcula los días hábiles en el backend con la tabla de festivos, no en el navegador;
- usa exactamente las rutas, campos y `data-testid` de las convenciones;
- valida el año, el orden de las fechas y la antigüedad antes de contar días.

Si algo falta, recházalo con un comentario concreto. Un rechazo bien escrito vale más que tres ejecuciones.

**Después del despliegue y las pruebas.** Abre http://localhost:8080 y pide unas vacaciones como lo haría un empleado. Corre `pytest` sobre `app/tests/` y compara con lo que esperabas.

**En el reporte.** Si el estado es ESCALAR A UNA PERSONA, lee qué falló y a quién envió el triage. Corrige al agente responsable (instrucciones, contexto o validador) y vuelve a ejecutar.

### Si tienes que volver a ejecutar

Está permitido y es normal. Antes de hacerlo, anota en un borrador qué falló, qué cambiaste en la fábrica y por qué: esas notas son la materia prima de `decisiones.md`. Recuerda que solo cuenta lo que quede en tu último commit, y que `auditoria.jsonl` debe ser el de la ejecución final.

## Evidencias y decisiones.md

### Dónde queda cada evidencia

| Qué se revisa | Dónde lo busca tu profesor |
| --- | --- |
| Criterios validados | `salida/HU-10/criterios.feature` y la bitácora del analista |
| Casos validados | `salida/HU-10/casos_prueba.json` |
| Aprobación del plan | La bitácora: «Plan aprobado por una persona» o «Plan rechazado: …» seguido de la aprobación |
| App desplegada | Tu `docker-compose.yml` y la app corriendo en el puerto 8080 |
| Pruebas de vacaciones | `app/tests/api/` y `app/tests/e2e/` |
| Estado final y fallas | `salida/HU-10/reporte.md` |
| Integridad | `auditoria.jsonl`: quién escribió cada archivo de `app/` y `salida/` |

El orden importa: la evidencia debe mostrar que las etapas ocurrieron en el orden del flujo (criterios → casos → plan aprobado → código → despliegue y pruebas → reporte).

### decisiones.md

Escribe `salida/HU-10/decisiones.md`, **una página como máximo**, sobre lo que pasó en tu ejecución. Responde estas cinco preguntas:

1. ¿Qué pasos de tu fábrica son workflow y cuáles son agente? ¿Por qué?
2. ¿Cómo se validó cada salida estructurada, de los criterios al código? ¿Qué atrapó algún validador?
3. ¿Dónde interviniste tú como persona y qué viste para decidir?
4. ¿Qué arquitectura de orquestación usa tu fábrica y por qué no otra de las que vimos?
5. Si algo falló: ¿qué corregiste en el agente y por qué no en su resultado?

### Qué hace buena una respuesta

La diferencia entre una respuesta débil y una fuerte casi siempre es la evidencia concreta.

| Débil | Fuerte |
| --- | --- |
| «El analista es un agente porque usa un LLM.» | «El analista es agente: decide qué leer y cuántas veces escribir. El ciclo que lo rodea es workflow: el código decide si reintenta según `validar_gherkin`.» |
| «Los validadores revisaron todo.» | «En el primer intento faltaba el escenario del tope exacto; el validador lo reportó y el segundo intento lo agregó (bitácora, intento 2).» |
| «Aprobé el plan porque estaba bien.» | «Rechacé el primer plan porque calculaba los días en el front-end; pedí moverlo al backend y el segundo plan lo hizo.» |
| «Usamos LangGraph porque es mejor.» | «Es un orquestador con flujo fijo: el orden de las etapas no cambia entre historias, y un supervisor LLM añadiría costo y variación sin ganar nada.» |

Usa los conceptos del módulo (workflow frente a agente, reflexión, humano en el bucle, orquestador, paralelización, defensa en profundidad), pero siempre atados a algo que pasó en tu ejecución. Cita la bitácora, el reporte o la auditoría cuando puedas.

## Cómo se califica

El reto vale el **60 % de la nota del módulo**.

| Criterio | Peso | Qué se revisa |
| --- | --- | --- |
| La app cumple la historia | 40 % | Proporción de pruebas ocultas que pasan contra tu app desplegada |
| Recorrido completo de la fábrica | 35 % | La evidencia de las seis etapas, en el orden del flujo, con sus validaciones y la aprobación del plan en la bitácora |
| Integridad y seguridad | 10 % | Hooks intactos y nada editado a mano en `app/` ni `salida/` (la auditoría lo muestra) |
| Decisiones | 15 % | Respuestas específicas a tu ejecución que usan bien los conceptos del módulo |

Sobre las pruebas ocultas: están construidas solo con lo que dicen `reglas_vacaciones.md` y `convenciones_vacaciones.md`. No hay reglas sorpresa; la mejor preparación es que tus propios criterios y casos cubran **todas** las reglas, incluidos los límites (el primer día con antigüedad, usar justo los días que quedan, periodos con festivos y fines de semana).

## Checklist antes de entregar

- [ ] `historias/HU-10-solicitar-vacaciones.md` existe y las reglas y convenciones están al final de sus archivos de `contexto/`.
- [ ] Ejecuté `python -m flujos.flujo_s4 historias/HU-10-solicitar-vacaciones.md` **con defensas** (sin `DEFENSAS=0`).
- [ ] `salida/HU-10/criterios.feature` tiene un escenario por cada una de las seis reglas, con los mensajes copiados letra por letra.
- [ ] `salida/HU-10/casos_prueba.json` tiene al menos un caso por escenario.
- [ ] La bitácora muestra que aprobé (o corregí y luego aprobé) el plan.
- [ ] `docker compose ps` muestra los servicios arriba y la app responde en http://localhost:8080.
- [ ] Hay pruebas de API y E2E de vacaciones en `app/tests/` y pasan.
- [ ] Las pruebas de HU-01 a HU-03 siguen pasando.
- [ ] `salida/HU-10/reporte.md` existe con el estado final.
- [ ] `salida/HU-10/decisiones.md` responde las cinco preguntas en una página o menos.
- [ ] `auditoria.jsonl` en la raíz es el de la ejecución final.
- [ ] No edité a mano nada de `app/` ni `salida/`, y no toqué los hooks.
- [ ] Mi commit no incluye `.env`.
- [ ] Hice push y el commit aparece en el repositorio remoto.
