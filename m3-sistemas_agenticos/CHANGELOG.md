# Changelog

## 2026-11-08 · Reto HU-10

### Agentes
- **Analista:** recibe la historia entre `<historia_no_confiable>` y solo lee `contexto/`. Sus instrucciones declaran su rol y sus límites. Ahora lee las convenciones, no usa `Antecedentes`, escribe escenarios de límite y omite «Preguntas abiertas» si no hay preguntas. Tiene 3 intentos.
- **Diseñador de pruebas:** sus instrucciones declaran sus límites. Cada caso con datos acumulados parte de un empleado nuevo, y escribe el código y el `detail` exactos. Tiene 3 intentos.
- **Desarrollador:** extiende lo existente sin reemplazarlo, calcula en el backend, valida en el orden de CLAUDE.md y declara sus límites.
- **Automatizador:** cada prueba crea su propio empleado, compara con igualdad exacta, espera los mensajes en E2E y conserva las pruebas de otras historias.
- **Bucle base:** `max_tokens` pasa de 16000 a 20000. El diseñador se cortaba con 16000.

### Validadores
- `validar_gherkin` exige los mensajes exactos de cada historia (`MENSAJES_OBLIGATORIOS`, HU-10 según la Guía), sin contar los comentarios.
- Cada validación del analista y del diseñador queda en `salida/HU-xx/validaciones.md`.

### Flujo (`flujos/flujo_s4.py`)
- Checkpointer `SqliteSaver` con `thread_id` por historia, y opciones `--pausar`, `--respuesta` y `--reintentar`.
- Nodo `escalar` (HITL con `interrupt`) cuando el triage agota `MAX_CICLOS`.
- `verificacion.py`: `npm` funciona en Windows (`shutil.which`).

### Hooks
- Sin cambios en `seguridad/hooks.py`.

### Contexto
- HU-10: `historias/HU-10-solicitar-vacaciones.md` y las reglas y convenciones de la Guía, agregadas al final de `reglas_negocio.md` y `convenciones_app.md`.

### Otros
- Docstrings en todas las funciones de `agentes/` y `flujos/`.
- `buscar_denegados.py`, `evidencias/comprobar_hu10.py`, `evidencias/cobertura_backend.py`, `evidencias/capturas.py`.
- `tests_fabrica/`: 22 pruebas de seguridad (hooks, herramientas, validadores).
- CI: `.github/workflows/fabrica-ci.yml` con gates de secretos, bandit, pip-audit y cobertura ≥ 80 %.
- `auditoria.jsonl` se versiona. `.env.example` sin clave.
