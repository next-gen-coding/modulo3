# Plan ejecutable · Reto M3 · HU-10 (sin intervención humana)

Fecha: 2026-11-08. Reemplaza en la práctica a `plan-reto-m3.md` (43 pasos manuales). Lo ejecuta Claude en rol de estudiante.
Fábrica: `m3-sistemas_agenticos/`. Fuente de verdad de HU-10: `convenciones` + `reglas` (la Guía dice que las pruebas ocultas salen de ahí). Dudas → `preguntas-hu10.md`.

| # | Fase | Qué se hace | Verificación |
|---|---|---|---|
| 0 | Entorno | `.venv` 3.12 + requirements + `langgraph-checkpoint-sqlite` + chromium; Docker Desktop arriba; clave probada | `docker info`, llamada a la API |
| 1 | Ajustar fábrica | `verificacion.py` (npm en Windows) · analista: lee convenciones, historia entre `<historia_no_confiable>`, mensajes exactos obligatorios, `validaciones.md` · diseñador/automatizador/desarrollador: instrucciones de HU-10 · `flujo_s4`: `SqliteSaver` + `thread_id` + modo no interactivo (`--respuesta`) · docstrings · `.gitignore` deja versionar `auditoria.jsonl` | imports OK, validador detecta faltantes |
| 2 | Base HU-01..03 | `flujo_s4` por historia; el plan se revisa y se aprueba con `--respuesta si` | `reporte.md` = LISTA ×3 |
| 3 | Seguridad HU-99 | `prompt_hardening` (ingenuo vs endurecido) · analista solo · `flujo_s4` con defensas → BLOQUEADA · buscar `BANDERA-DEMO` en `app/` | `salida/bloqueada/reporte.md` |
| 4 | HU-10 | Copiar historia (reparando codificación) a `historias/`; reglas y convenciones al final de `contexto/`; rotar `auditoria.jsonl`; correr flujo; revisar criterios; aprobar/rechazar plan; comprobación independiente `evidencias/comprobar_hu10.py` | `reporte.md` LISTA, 0 fallas |
| 5 | Documentación | `salida/HU-10/decisiones.md`, `salida/seguridad.md`, README (Mac/Linux/Windows), CHANGELOG, `evidencias/` (prompts, grafo, auditoría, reflexión), formato de entrega | checklist de la Guía |
| 6 | Commit | Un commit `feat(reto): HU-10 ...` sin `.env`. **Push no** (lo hace el usuario) | `git show --stat` |

Reglas: nunca editar a mano `app/` ni `salida/` (salvo `decisiones.md` y `seguridad.md`); si un agente falla, se corrige el agente y se re-ejecuta; nunca `DEFENSAS=0` en la fábrica.
