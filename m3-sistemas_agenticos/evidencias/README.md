# Evidencias · Reto HU-10

Ejecución real con `claude-haiku-4-5`. Costo de la fábrica: 4.13 USD, estimación conservadora (`costo_acumulado.txt`; las llamadas que fallaron se contaron al tope).

| Evidencia | Dónde |
|---|---|
| Prompts de cada agente | `evidencias/prompts.md`, `CLAUDE.md`, `contexto/convenciones_app.md` → `app/CLAUDE.md` |
| Grafo | `flujos/salidas/grafo_flujo_s4.html`, `capturas/01-grafo-flujo-s4.png` |
| Artefactos HU-10 | `salida/HU-10/` (criterios, casos, plan, validaciones, reporte, resultados.xml) |
| Bitácora y triage | `salida/HU-10/reporte.md`; ejecución 1 en `ejecucion-1/` |
| Seguridad | `salida/seguridad.md`, `salida/bloqueada/reporte.md`, `logs/prompt_hardening.log` |
| Auditoría | `auditoria.jsonl` (231 llamadas, ejecución final), `ejecucion-1/auditoria.jsonl` y `python buscar_denegados.py` |
| Pantalla | `capturas/04-directorio.png`, `05-ui-solicitud-exitosa.png` y `06-ui-error-sin-dias-habiles.png` |
| Comprobación independiente | `python evidencias/comprobar_hu10.py` → 0 fallas |
| Logs | `evidencias/logs/` |

## Fragmento de la auditoría: intentos fuera de rol

`buscar_denegados.py` encontró escrituras del desarrollador fuera de `backend/*` y `frontend/*`. Las negó `confinar_escritura`:

```text
desarrollador  Write     test_vacaciones.py
               su rol solo permite: backend/*, frontend/*
desarrollador  Write     run_tests.py
               su rol solo permite: backend/*, frontend/*
```

## Iteraciones

Detalle en `borrador-ejecuciones.md`:
1. El analista escribía «Preguntas abiertas: Ninguna» y eso pausaba el flujo → se corrigió su SISTEMA.
2. El diseñador se cortaba por `max_tokens` → se retomó con `--reintentar`.
3. **Ejecución 1:**
   - el plan usaba `DELETE` para la baja y una lista fija de festivos → lo rechacé;
   - el desarrollador agotó los 30 turnos → se subió a 60;
   - quedó en ESCALAR: 500 por `.year` y pruebas `async`.
4. **Ejecución 2:**
   - el analista falló la validación una vez (escenarios sin `Dado`);
   - rechacé el plan que decía «implementación completa»;
   - el desarrollador agotó sus turnos y luego su presupuesto (probaba contra el puerto 8000);
   - el triage culpó al desarrollador → ESCALAR, con 18 de 23 en verde y los fallos en los datos de las pruebas.

## Hallazgos abiertos

- La pantalla no refresca el saldo ni la tabla después de registrar (captura 05). Esto también explica CP-21.
- 5 pruebas tienen datos de entrada mal calculados.
- La cobertura del backend es de 64 %.
- `starlette 0.27.0` tiene la vulnerabilidad PYSEC-2026-2280.
- bandit marcó B104 en `run_server.py`.

## Reflexión

**Qué funcionó:**
- Los validadores y los hooks: el código decidió y bloqueó escrituras fuera de rol.
- El checkpointer: se retomó tres veces sin repetir etapas.
- El HITL: los rechazos de plan con comentarios concretos corrigieron dos errores de diseño.
- La comprobación independiente: separó un fallo de la app de un fallo de las pruebas.

**Qué mejorar:**
- Darle al triage el log del backend y los datos de entrada, para que no culpe al código por pruebas mal escritas.
- Agregar a la verificación una prueba rápida de cada endpoint nuevo.
- Que el diseñador calcule los días hábiles de sus datos con la tabla de festivos.
- Con Haiku, el desarrollador gasta muchos turnos; la mejor relación costo-calidad está en las instrucciones precisas.
