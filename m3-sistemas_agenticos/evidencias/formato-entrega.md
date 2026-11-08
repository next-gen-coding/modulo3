# Formato de entrega · M3

**Alumno:** José Juan Martínez Morales
**Proyecto:** Fábrica de software con agentes de IA · Historia HU-10 «Solicitar vacaciones»
**Repositorio:** https://github.com/josemtzco/modulo3 (rama main, carpeta `m3-sistemas_agenticos`)
**Fecha:** 8 de noviembre de 2026

> Ejecución real con `claude-haiku-4-5` (unos 4.1 USD). Hubo dos ejecuciones; la final terminó en «ESCALAR A UNA PERSONA», con la app correcta y 5 pruebas con datos erróneos (ver `decisiones.md`).

## 1. Configuración del Proyecto y Herramientas de IA

**a) Herramientas de IA seleccionadas y configuración inicial**
- **Herramientas de IA:** Claude Code + Agent SDK (agentes que escriben código), la API de Anthropic (agentes de texto), LangGraph (orquestación) y Claude Code interactivo (solo para ajustar la fábrica).
- **Entorno:** Windows 11, Python 3.12 (uv), Node 24, Docker Desktop y Playwright.
- **Configuración:** el modelo y los topes se configuran en `.env`, que no se versiona.

Evidencia: `README.md` y `requirements.txt`.

**b) Configuraciones de seguridad implementadas**
- **Reglas:** `CLAUDE.md` y `app/CLAUDE.md`.
- **Agentes:** cada uno declara su rol y sus límites.
- **Entrada:** la historia pasa por `filtrar_historia` y llega como `<historia_no_confiable>`.
- **Hooks PreToolUse:** `confinar_escritura`, `confinar_lectura`, `comandos_permitidos` y `auditar`.
- **Sin internet:** WebFetch y WebSearch deshabilitados.
- **Límites:** `max_turns=60` y `max_budget_usd`.

**c) Mejores prácticas de seguridad aplicadas**
- **Mínimo privilegio:** `ESCRITURA` y `PROGRAMAS` por agente.
- **Secretos:** fuera del código; quité una clave real de `.env.example`.
- **Control humano:** el plan lo aprueba una persona.
- **Defensa en profundidad:** varias capas, bucles con límite y auditoría en `auditoria.jsonl`.
- **Sin edición manual:** nunca edité `app/` ni `salida/`; las correcciones fueron a los agentes.

## 2. Implementación del Módulo de Autenticación

**a) Componentes desarrollados con asistencia de IA**
La fábrica generó HU-10 sin edición manual:
- **Stack:** backend FastAPI + SQLAlchemy + SQLite, frontend React y despliegue con Docker Compose.
- **Endpoints:** `POST` y `GET /api/empleados/{id}/vacaciones`.
- **Reglas:** días hábiles calculados en el servidor (festivos de la LFT), antigüedad y tope de 12 días.

Evidencia: `app/`, `salida/HU-10/reporte.md` y `capturas/05-ui-solicitud-exitosa.png`.

**b) Validación de entrada con schemas y hash de contraseñas**
- **API:** modelos Pydantic v2 (422 automático) y `{"detail": "..."}` con los mensajes exactos de la Guía.
- **Salidas de los agentes:** también se validan con schemas (`validar_gherkin`, `PlanPruebas`).
- **Hash:** no aplica; la app no tiene usuarios ni contraseñas.

**c) Tokens JWT y rate limiting**
- **JWT:** no aplica; no hay sesiones.
- **Límites de los agentes:**
  - 0.5–1 USD por llamada y un tope global de 4.5 USD;
  - 60 turnos por llamada y 15 pasos por agente de texto;
  - 2 intentos de reflexión y 2 de construcción;
  - 1 ciclo de triage, después escala a una persona.

## 3. Suite de Pruebas Automatizadas

**a) Pruebas unitarias y cobertura**
- **`tests_fabrica/`:** 22 pruebas unitarias de hooks, herramientas confinadas y validadores, con 98 % de cobertura en `seguridad/hooks.py`.
- **Pruebas de API generadas:** cubren el **64 %** del backend (`evidencias/cobertura_backend.py`); queda por debajo del gate de 80 %.

**b) Pruebas de seguridad específicas**
- **`tests_fabrica/test_seguridad.py`:**
  - escrituras fuera de rol denegadas;
  - lectura de `.env` y de `secretos_demo.txt` bloqueada;
  - comandos denegados: `printenv`, `$(...)`, `cd ..` y `curl`;
  - auditoría registrada;
  - `DEFENSAS=0` solo quita las capas de seguridad;
  - validadores con mensajes exactos.
- **HU-99:** quedó BLOQUEADA y la bandera no llegó a `app/`.

**c) Pruebas de integración del flujo completo**
- **Recorrido:** el flujo de punta a punta, de la historia al reporte, despliega en Docker y corre las pruebas.
- **Resultado:** 23 pruebas de API y E2E con Playwright → **18 passed y 5 failed**; los 5 fallos son datos erróneos de las pruebas (CP-02 no descuenta el festivo del 2 de febrero) y un refresco de pantalla.
- **Comprobación independiente:** `comprobar_hu10.py` revisa la API contra las tablas de la Guía → 0 fallas.

## 4. Pipeline de CI/CD y Gates de Seguridad

**a) Configuración del pipeline**
GitHub Actions en `.github/workflows/fabrica-ci.yml`, en cada push o PR, con Python 3.12. No llama a la API de Anthropic.

**b) Análisis estático y validación de vulnerabilidades**
- **bandit:** sin hallazgos de severidad alta. Hay dos medios: B104 (`0.0.0.0` en `run_server.py`, código generado) y B314 (el XML de nuestro pytest).
- **pip-audit:** encontró `starlette 0.27.0` con PYSEC-2026-2280; se corrige con 1.1.0. El gate 3 lo detiene, y eso demuestra que el gate funciona.

**c) Gates de seguridad y criterios**
El pipeline falla si:
1. aparece un `.env` o una clave `sk-ant-` versionada;
2. bandit encuentra severidad alta;
3. pip-audit encuentra una vulnerabilidad conocida;
4. las pruebas de la fábrica bajan de 80 % de cobertura;
5. las pruebas de API del backend bajan de 80 %.

## 5. Documentación del Proceso y Lecciones Aprendidas

**a) Prompts y estrategias de prompt engineering**
Rol y límites por agente, contenido externo entre etiquetas, contratos explícitos (Gherkin y Pydantic), ejemplos en el contexto y reflexión guiada por validadores. Evidencia: `evidencias/prompts.md`.

**b) Proceso documentado**
historia → filtro → criterios → casos → plan aprobado → código → verificación → despliegue y pruebas en paralelo → triage → reporte. Evidencia: `salida/HU-10/`, `decisiones.md` y `CHANGELOG.md`.

**c) Lecciones aprendidas**
- El prompt sugiere; el hook y el validador deciden.
- Los checkpoints permiten retomar después de un error sin repetir etapas.
- Los archivos del reto se contradecían y hubo que fijar una sola fuente de verdad.
- Simular el modelo permitió probar la orquestación sin gastar antes de la ejecución real.
- El triage también se equivoca: culpó al código por pruebas mal escritas. La comprobación independiente fue la que lo aclaró.

## 6. Repositorio y Documentación Técnica

**a) URL del repositorio**
https://github.com/josemtzco/modulo3 (rama main, carpeta `m3-sistemas_agenticos`)

**b) Estructura y documentación**
- `agentes/` y `flujos/`: la fábrica.
- `seguridad/`: los hooks.
- `contexto/` e `historias/`: las entradas.
- `app/` y `salida/`: lo generado.
- `tests_fabrica/` y `evidencias/`.
- Documentación: `README.md` y `CHANGELOG.md`.

**c) Instrucciones de instalación y ejecución**
Las instrucciones para Mac, Linux y Windows están en `README.md`. Lo básico:
- **Instalar:** `uv venv --python 3.12`, `uv pip install -r requirements.txt` y `playwright install chromium`.
- **Correr la fábrica:** `python -m flujos.flujo_s4 historias/HU-10-solicitar-vacaciones.md --pausar` y luego `--respuesta si`.
- **Probar:** `cd app && pytest tests -q`.
