# Ejecución real (cuando el usuario la autorice) · presupuesto 5 USD

Configuración de costo mínimo: `MODEL=claude-haiku-4-5-20251001`, `PRESUPUESTO_USD=0.6` por llamada a Claude Code, `TOPE_TOTAL_USD=4.5` (acumulado en `costo_acumulado.txt`), `max_turns=30`, `MAX_CICLOS=1`, 2 intentos por validador y `max_tokens=16000`.
**Alcance por presupuesto: solo HU-10** (el desarrollador construye también la base mínima de empleados). El paso 2 (HU-01..03) se omite.

Todo se corre desde `m3-sistemas_agenticos/` con `R=../guias/m3-reto/.ai/correr.sh`, **sin** `FABRICA_MOCK`. Antes, decidir `MODEL` en `.env`.

1. **Limpiar lo simulado:** `(cd app && docker compose down -v); rm -rf app salida auditoria.jsonl checkpoints.sqlite`
2. **Base:** para cada HU-01, HU-02 y HU-03:
   - `$R -m flujos.flujo_s4 historias/<HU>.md --pausar`
   - revisar `salida/<HU>/plan_propuesto.md`
   - `$R -m flujos.flujo_s4 historias/<HU>.md --respuesta si` (o un comentario de rechazo)
   - si truena: `--reintentar`
3. **Seguridad:**
   - `$R -m ejemplos.s4_seguridad.prompt_hardening` (ingenuo vs endurecido)
   - `$R -m agentes.analista historias/HU-99-envenenada.md` (agente sin filtro)
   - `$R -m flujos.flujo_s4 historias/HU-99-envenenada.md --pausar` → BLOQUEADA
   - `grep -r BANDERA-DEMO app/` sin resultados
4. **Rotar la auditoría:** `mv auditoria.jsonl evidencias/auditoria_base.jsonl`
5. **HU-10:**
   - `--pausar`
   - revisar los criterios y el plan contra el checklist de la Guía
   - `--respuesta si` (o un rechazo concreto)
6. **Verificar:**
   - `$R evidencias/comprobar_hu10.py`
   - `cd app && pytest tests -q`
   - `$R buscar_denegados.py`
   - `docker compose ps`
7. **Documentos sobre la ejecución real:**
   - `salida/HU-10/decisiones.md`
   - `salida/seguridad.md`
   - `evidencias/README.md` (reflexión, fragmento de la auditoría y el grafo `flujos/salidas/grafo_flujo_s4.html`)
   - el Formato de entrega
8. **Sin commit** hasta que el usuario lo pida.
