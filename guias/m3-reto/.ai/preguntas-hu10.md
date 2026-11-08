# Preguntas para aclarar (no bloquean la ejecución)

Respondí cada una con un supuesto para no detenerme. Si alguno no te sirve, dime y re-ejecuto.

1. **Guía vs convenciones.** La Guía dice 422 / `dias_disponibles` / `vacaciones-empleado-{id}`. Las convenciones dicen 400 / `dias_restantes` / `vacaciones-abrir-{id}`. **Supuesto:** mandan las convenciones y las reglas, porque la Guía dice que las pruebas ocultas salen de ahí. ¿Lo confirmas?
2. **Aprobación del plan (HITL).** La hago yo en tu rol de estudiante, revisando el plan contra el checklist de la Guía. La bitácora dirá «Plan aprobado por una persona». ¿Te sirve, o prefieres re-ejecutar HU-10 y aprobarlo tú?
3. **`.env.example` tiene una clave real versionada** (commit `6f6728d «llave temporal»`). La dejo en blanco en el commit. **Rota esa clave en la consola de Anthropic**, porque sigue en el historial de git.
4. **`auditoria.jsonl`** estaba en `.gitignore`. Lo saco de ahí para entregarlo. La auditoría de HU-01..03 queda en `evidencias/auditoria_base.jsonl` y la de la raíz es solo la ejecución final de HU-10. ¿Ok?
5. **Push y plataforma:** hago el commit pero **no** el push ni subo el Word. Eso queda para ti.
6. **Costo:** 4 ejecuciones de la fábrica, unos 20–40 USD (tope de `PRESUPUESTO_USD=2` por llamada a Claude Code).
7. **Dependencia nueva:** `langgraph-checkpoint-sqlite`, para que el flujo se pueda pausar y retomar por `thread_id`. Va a `requirements.txt`.

## Respuestas del usuario (2026-11-08)

1. La **Guía** es la fuente de verdad (422, 6 reglas, `dias_disponibles`, data-testid de la Guía).
2. El plan lo aprueba Claude en el rol de estudiante.
3. Sin commit.
4. `auditoria.jsonl` fuera de `.gitignore`: sí.
6. No correr la fábrica real hasta que todo esté validado con el modo simulado.
7. Lo demás, a criterio de Claude.
