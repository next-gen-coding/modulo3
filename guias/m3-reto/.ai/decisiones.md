# Decisiones · Reto M3 HU-10

| Fecha | Decisión | Alternativas | Por qué |
|---|---|---|---|
| 2026-11-08 | La Guía es la fuente de verdad de HU-10. Se reescribieron `contexto/reglas_vacaciones.md`, `contexto/convenciones_vacaciones.md` e `historias/HU-10` a partir de ella | Usar los archivos de convenciones/reglas recibidos (400, `dias_restantes`) | Decisión del usuario. Se eliminaron las reglas de baja (409) y de año fuera de tabla porque la Guía no las incluye |
| 2026-11-08 | Los festivos se calculan para cualquier año con la regla del art. 74 | Solo la tabla 2026–2027 | La Guía no limita los años, y el caso del 29 de febrero cae en 2025 |
| 2026-11-08 | Checkpointer `SqliteSaver` + `thread_id` = nombre de la historia; `--pausar`, `--respuesta` y `--reintentar` | InMemorySaver (no sobrevive al proceso) | Retomar sin intervención interactiva y después de un error; lo pide el reto |
| 2026-11-08 | Nodo `escalar` con `interrupt` cuando el triage agota MAX_CICLOS | Solo el reporte «ESCALAR» | HITL explícito que pide el reto |
| 2026-11-08 | Modo simulado `FABRICA_MOCK=1` (`agentes/simulado.py`) con respuestas en `mocks/` | Correr la fábrica real para cada prueba | Validar el recorrido a costo casi cero. No cuenta como ejecución real |
| 2026-11-08 | `max_tokens` del bucle: 16000 → 20000 | 32000 | Con 16000 el diseñador se cortaba; con 32000 la API exige streaming |
| 2026-11-08 | Dependencia `langgraph-checkpoint-sqlite` | Postgres (ya en requirements) | No requiere servidor |
| 2026-11-08 | Presupuesto de 5 USD: Haiku 4.5, 0.6 USD por llamada, tope global de 4.5 USD, `max_turns` 30, `MAX_CICLOS` 1, 2 intentos y `max_tokens` 16000. Ejecución real solo de HU-10 | Sonnet; correr HU-01..03 | El usuario solo tiene 5 USD; HU-01..03 por separado costarían más que todo el presupuesto |
| 2026-11-08 | Se eliminaron el modo simulado (`agentes/simulado.py`, `mocks/`) y la copia de la entrega simulada | Conservarlos como herramienta | Decisión del usuario: la entrega final es la ejecución real y se quitan las distracciones |
