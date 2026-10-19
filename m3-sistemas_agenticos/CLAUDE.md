# Curso: Construcción de Sistemas Agénticos (Módulo 3)

Repositorio de la «fábrica de software»: una cadena de agentes que, a partir de una historia de usuario, escribe criterios de aceptación, casos de prueba, el código de una aplicación de gestión de empleados de una empresa (base de datos, API y front-end), la despliega y la prueba de punta a punta. Cada alumno construye su propia fábrica, de forma individual.

## Estructura

- `historias/` — historias de usuario de entrada (HU-01 a HU-03; HU-99 es la historia envenenada de la sesión 4; `backlog.md` tiene historias para ampliar)
- `contexto/reglas_negocio.md` — reglas del dominio que todos los agentes respetan
- `contexto/convenciones_app.md` — stack, puertos y data-testid; se copia como `app/CLAUDE.md`
- `agentes/base.py` — bucle de agente y herramientas de archivos (sesión 1)
- `agentes/analista.py` — Agente 1: historia → `salida/HU-xx/criterios.feature` (sesión 1)
- `agentes/disenador_pruebas.py` — Agente 2: criterios → `salida/HU-xx/casos_prueba.json` (sesión 1)
- `agentes/claude_code.py` — cómo los agentes 3, 4 y 5 usan Claude Code con el Agent SDK (sesión 2)
- `agentes/desarrollador.py` — Agente 3: requisitos → `app/backend` y `app/frontend` (sesión 2)
- `agentes/despliegue.py` — Agente 4: Docker Compose (sesión 3)
- `agentes/automatizador.py` — Agente 5: casos → `app/tests` con pytest y Playwright (sesión 3)
- `agentes/triage.py` — decide qué agente corrige una prueba fallida (sesión 4)
- `flujos/flujo_s2.py`, `flujo_s3.py`, `flujo_s4.py` — el orquestador LangGraph, una versión por sesión
- `flujos/verificacion.py` — verificaciones deterministas (salud de la API, build, despliegue, pruebas)
- `seguridad/hooks.py` — hooks de rol y de seguridad para Claude Code
- `ejemplos/` — un programa corto por patrón (razonamiento, flujos y topologías) para demostrar en clase; no forman parte de la fábrica
- `app/` — la aplicación que generan los agentes; `salida/` — artefactos por historia

## Entorno y comandos

- Python 3.12 (fijado en `.python-version`), Node 20 o superior, Docker Desktop y Claude Code
- Crear entorno: `uv venv && source .venv/bin/activate && uv pip install -r requirements.txt && playwright install chromium`
- Configurar: `cp .env.example .env` y escribir `ANTHROPIC_API_KEY` y `MODEL`
- Todo se ejecuta desde la raíz como módulo, por ejemplo:
  - `python -m agentes.analista historias/HU-01-registrar-empleado.md`
  - `python -m flujos.flujo_s4 historias/HU-01-registrar-empleado.md`

## Convenciones de código

- Comentarios, nombres de dominio y mensajes al usuario en español
- Anotaciones de tipo; modelos Pydantic para toda salida estructurada
- El modelo se lee de `MODEL` en `.env`; nunca escribas identificadores de modelo fijos
- Cada paso de un agente termina en una verificación determinista; el código decide si se cumplió, no el agente
- Los errores de herramientas regresan al modelo como texto; no se silencian
- Todo bucle tiene un límite: pasos, intentos, ciclos y presupuesto en USD

## Seguridad

- Nunca escribas claves en el código; `.env` no se versiona
- Cada agente escribe solo en su carpeta: analista y diseñador en `salida/HU-xx/`, desarrollador en `app/backend` y `app/frontend`, despliegue en archivos de Docker, automatizador en `app/tests`
- No quites los hooks de `seguridad/hooks.py`; `DEFENSAS=0` solo se usa en clase para demostrar el ataque de HU-99
- Los ataques apuntan únicamente a `secretos_demo.txt`; nunca al `.env` real
- Los agentes no tienen WebFetch ni WebSearch

## Cómo trabajar en este repo

- Antes de cambiar más de un archivo, muestra un plan y espera aprobación
- Explica el porqué de cada cambio: quien lo lee está aprendiendo
- Cambios mínimos: no refactorices ni renombres lo que no se pidió
- No agregues dependencias nuevas sin preguntar
- En `agentes/base.py` no escribas ni reescribas el bucle del agente; ayuda a entender errores
- No edites a mano lo que generan los agentes en `app/` y `salida/`: corrige al agente, no su resultado
