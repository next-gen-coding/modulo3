# Decisiones · HU-10 Solicitar vacaciones

Ejecución real con `claude-haiku-4-5` y presupuesto de 5 USD. Hubo dos ejecuciones; la 1 está en `evidencias/ejecucion-1/` y la 2 en `salida/HU-10/`.

**1. ¿Qué es workflow y qué es agente?**
Son agentes el analista, el diseñador, el desarrollador (plan y construcción), el de despliegue, el automatizador y el triage: cada uno decide qué leer, qué escribir y cuántas veces. Es workflow el filtro de entrada, el orden de las etapas, los reintentos que decide el validador, la verificación (`/api/salud` y el build), la paralelización de despliegue y automatización, y el ciclo de pruebas → triage → corrección → escalamiento. El orden no cambia entre historias, así que lo decide el código.

**2. ¿Cómo se validó cada salida?**
- **Criterios:** `validar_gherkin` exige los 6 mensajes de la Guía. En la ejecución 2 rechazó el intento 1 (dos escenarios sin `Dado`) y el intento 2 pasó (`validaciones.md`).
- **Casos:** Pydantic `PlanPruebas`, con un caso por escenario. Pasó al primer intento.
- **Código:** `verificar_app`, después la trazabilidad de CP-xx en las pruebas, y al final pytest + Playwright contra Docker como árbitro: 18 de 23 en verde.
- **App:** `comprobar_hu10.py` contra las tablas de la Guía dio **0 fallas**.

**3. ¿Dónde intervine como persona?**
- **Ejecución 1:** rechacé el primer plan porque daba de baja con `DELETE` y usaba festivos fijos. El segundo plan lo corrigió y lo aprobé.
- **Escalamiento de la ejecución 1:** el log de Docker mostraba un 500 por `Vacacion.fecha_inicio.year` en SQLAlchemy.
- **Ejecución 2:** rechacé el plan que decía «implementación completa» y proponía sembrar datos con ids fijos.
- **Construcción de la ejecución 2:** el agente agotó su presupuesto con el código ya corregido. Lo comprobé con `comprobar_hu10` y di la etapa por completada en el checkpoint (`update_state`), para no pagar otra construcción.
- **Escalamiento final:** los 5 fallos eran datos erróneos de las pruebas. Por ejemplo, CP-02 consume del 2 al 6 de febrero sin contar el festivo del día 2.

**4. ¿Qué arquitectura de orquestación usa y por qué?**
Un grafo de LangGraph con supervisor determinista, encadenamiento, enrutamiento, paralelización y evaluador-optimizador. Tiene `SqliteSaver` con `thread_id` por historia, y eso permitió retomar tres veces con `--reintentar` sin repetir etapas. Usa HITL con `interrupt` para el plan y para el escalamiento. Un supervisor LLM agregaría costo y, como mostró el triage, también errores de enrutamiento.

**5. ¿Qué corregí en los agentes y por qué no en su resultado?**
- **Desarrollador:** filtra el año como texto, prueba con curl en el puerto 8011 y no en el 8000 (el contenedor viejo lo confundía y le costó 60 turnos), y construye la base de empleados si falta.
- **Automatizador:** escribe pruebas síncronas; las E2E `async def` fallaban.
- **Límites de Claude Code:** `max_turns` pasó de 30 a 60, y el presupuesto por llamada lo fui ajustando.

El triage culpó al desarrollador cuando el error estaba en las pruebas; queda como mejora para el agente. No toqué `app/` ni `salida/` porque se regeneran; lo que perdura es la instrucción.
