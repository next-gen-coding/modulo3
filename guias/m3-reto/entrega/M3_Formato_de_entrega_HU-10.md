**Certificado en Desarrollo de software con IA Generativa**
**M3. Pruebas Automatizadas y Aseguramiento de la Calidad**

# Reto: Implementando QA Segura con Herramientas de IA

**Alumno:** José Juan Martínez Morales
**Proyecto entregado:** Fábrica de software con agentes de IA · Historia HU-10 «Solicitar vacaciones»
**Repositorio:** https://github.com/josemtzco/modulo3 (rama `main`, carpeta `m3-sistemas_agenticos`)
**Fecha:** 7 de noviembre de 2026

### Objetivos del reto
- Diseñar pruebas automatizadas unitarias para asegurar la calidad del software usando IA.
- Evaluar vulnerabilidades de seguridad en código generado por herramientas de IA mediante análisis estático y dinámico.
- Implementar configuraciones de seguridad avanzadas para herramientas de IA en proyectos de desarrollo profesional.

**Duración:** 2 horas

### Instrucciones
- Configura un proyecto de desarrollo con herramientas de IA aplicando las mejores prácticas de seguridad estudiadas en el módulo, incluyendo archivos de reglas y configuraciones.
- Implementa un módulo de autenticación de usuarios utilizando asistencia de IA que incluya validación de entrada con schemas, hash seguro de contraseñas, manejo de tokens JWT y rate limiting.
- Diseña y ejecuta una suite de pruebas automatizadas que incluya pruebas unitarias con 80%+ de cobertura, pruebas de seguridad específicas y pruebas de integración para el flujo de autenticación completo.
- Configura un pipeline de CI/CD básico con gates de seguridad que incluya análisis estático de código y validación de vulnerabilidades.
- Documenta el proceso de desarrollo asistido por IA y entrega el código fuente en un repositorio de GitHub con documentación correspondiente.

> **Nota de alcance.** Esta plantilla es la de otro reto. Entrego el reto de «Construcción de Sistemas Agénticos»: una fábrica de seis agentes de IA que convierte la historia HU-10 en código probado y desplegado. Cada sección responde con su equivalente en ese proyecto.

---

## 1. Configuración del Proyecto y Herramientas de IA

**a) Herramientas de IA seleccionadas y configuración inicial:**

Claude Code + Agent SDK (agentes que escriben código), API de Anthropic con Claude Sonnet (agentes de texto), LangGraph (orquestación) y Claude Code interactivo (solo para ajustar la fábrica).
Windows 11 con Python 3.12 (`uv`), Playwright, Docker Desktop y Node 24. Claves en `.env` no versionado.

*Evidencia:* `README.md` (instalación) y `requirements.txt`.

**b) Configuraciones de seguridad implementadas (.cursorrules, prompt engineering):**

`CLAUDE.md` y `app/CLAUDE.md` como archivos de reglas. Cada agente tiene rol y límites explícitos, y la historia entra como contenido no confiable tras el filtro `filtrar_historia`.
Hooks `PreToolUse` (`confinar_escritura`, `confinar_lectura`, `comandos_permitidos`, `auditar`), sin WebFetch ni WebSearch, con `max_turns=80` y `max_budget_usd`.

**c) Mejores prácticas de seguridad aplicadas:**

Mínimo privilegio (`ESCRITURA` y `PROGRAMAS` por agente), sin internet, secretos fuera del código (cambié una clave real que estaba en `.env.example`) y plan aprobado por una persona.
Defensa en profundidad, bucles con límite y auditoría en `auditoria.jsonl`; nunca edité a mano `app/` ni `salida/`.

---

## 2. Implementación del Módulo de Autenticación

> La app no tiene inicio de sesión por regla de negocio (regla 7). El módulo equivalente es **HU-10 Solicitar vacaciones**.

**a) Componentes de autenticación desarrollados con asistencia de IA:**

La fábrica generó HU-10 sin edición manual: backend FastAPI + SQLAlchemy + SQLite, frontend React y despliegue con Docker Compose.
Endpoints `POST` y `GET /api/empleados/{id}/vacaciones` con días hábiles calculados en el servidor y las reglas de antigüedad y tope de 12 días.

*Evidencia:* `app/`, `salida/HU-10/reporte.md` y captura `05-ui-solicitud-exitosa.png`.

**b) Validación de entrada con schemas y hash seguro de contraseñas:**

Modelos Pydantic v2 en la API (422 automático y `{"detail": "..."}` con mensajes exactos). Las salidas de los agentes también se validan con schemas (`validar_gherkin`, `PlanPruebas`).
Hash: no aplica, no hay usuarios ni contraseñas.

**c) Implementación de tokens JWT y rate limiting:**

JWT: no aplica, no hay sesiones.
Rate limiting en los agentes: 5 USD por llamada, 80 turnos, 15 pasos, 3 intentos de reflexión, 2 de construcción y 2 ciclos de triage.

---

## 3. Suite de Pruebas Automatizadas

**a) Pruebas unitarias diseñadas y porcentaje de cobertura alcanzado:**

Un test por caso (`CP-xx`) en `tests/api/test_hu_10.py` (pytest) y `tests/e2e/test_hu_10_e2e.py` (Playwright); pasaron todos **[confirmar: «N passed», `evidencias/pytest-final.txt`]**.
Cobertura de requisitos del 100 % (regla → escenario → caso → test) y 18 de 18 OK en `comprobar_hu10.py`. No medí cobertura de líneas.

**b) Pruebas de seguridad específicas:**

Ataque con la historia HU-99 (prompt injection): ingenuo **[confirmar] de 3**, endurecido **0 de 3** **[confirmar, Paso 18]**. Con todas las defensas, `filtrar_historia` la bloqueó y `BANDERA-DEMO` tuvo 0 coincidencias en `app/`.

*Evidencia:* `evidencias/lab4b-*.txt`, `salida/bloqueada/reporte.md` y captura `07-hu99-bloqueada.png`.

**c) Pruebas de integración para el flujo de autenticación completo:**

E2E con Playwright y pruebas de API con estado contra la app en Docker (5 días deja 7, 7 más deja 0, 1 más da 400). La fábrica terminó en **Estado: LISTA**.

*Evidencia:* `evidencias/pytest-final.txt`, `evidencias/hu10-comprobacion.txt` y capturas `05` y `06`.

---

## 4. Pipeline de CI/CD y Gates de Seguridad

**a) Configuración del pipeline de CI/CD implementado:**

Grafo LangGraph `flujos/flujo_s4.py`, de la historia al despliegue con Docker, con pausa humana para aprobar el plan y triage de fallas. Se ejecuta con `python -m flujos.flujo_s4 historias/HU-10-solicitar-vacaciones.md`.

**b) Análisis estático de código y herramientas de validación utilizadas:**

Estático: `validar_gherkin`, `validar_plan`, `pytest --collect-only` y `npm run build`.
Dinámico: `verificar_backend`, `verificar_despliegue`, `ejecutar_pruebas` y los hooks `PreToolUse`.

**c) Gates de seguridad y criterios de validación establecidos:**

Ocho gates: filtro de entrada, Gherkin, casos, aprobación humana, hooks, build, despliegue y pruebas.
Si uno falla, el flujo no avanza; las pruebas fallidas pasan a triage (máx. 2 ciclos) y luego a **ESCALAR A UNA PERSONA**.

---

## 5. Documentación del Proceso y Lecciones Aprendidas

**a) Prompts utilizados y estrategias de prompt engineering aplicadas:**

Prompts versionados en `agentes/`, más el comentario con que rechacé el primer plan. Estrategias: rol con límites, contexto en archivos, contrato en esquema de herramienta, reflexión con evaluador y prompt hardening.

*Evidencia:* `evidencias/README.md`, «Prompts utilizados».

**b) Proceso de desarrollo asistido por IA documentado:**

Entorno, ajuste de la fábrica, HU-01 a HU-03, ataque HU-99 y HU-10 (rechacé el primer plan, aprobé el segundo, terminó en **LISTA**). Ejecuciones de HU-10: **[confirmar en `evidencias/borrador-ejecuciones.md`]**.

**c) Lecciones aprendidas sobre calidad, seguridad y uso de IA en desarrollo:**

El código decide, no el agente: los validadores deterministas valen más que «ya terminé». El prompt endurecido no basta; detienen el ataque el filtro y los hooks.
Se corrige al agente, no su resultado. Mejoraría auditando a todos los agentes y agregando CI.

---

## 6. Repositorio y Documentación Técnica

**a) URL del repositorio de GitHub:**

https://github.com/josemtzco/modulo3 (rama `main`, carpeta `m3-sistemas_agenticos`)

**b) Estructura del proyecto y documentación incluida:**

`agentes/`, `flujos/`, `seguridad/`, `contexto/`, `historias/`, `app/`, `salida/`, `evidencias/` y `auditoria.jsonl`. Documentación: `README.md`, `CHANGELOG.md`, `CLAUDE.md`, `decisiones.md` y `seguridad.md`.

**c) Instrucciones de instalación y ejecución:**

```powershell
uv venv --python 3.12; .venv\Scripts\Activate.ps1
uv pip install -r requirements.txt; python -m playwright install chromium
Copy-Item .env.example .env   # agregar ANTHROPIC_API_KEY, MODEL, PRESUPUESTO_USD
python -m flujos.flujo_s4 historias\HU-10-solicitar-vacaciones.md
```

Con Docker abierto, la app queda en http://localhost:8080. Pruebas: `cd app && python -m pytest tests -q`.

---

<!-- QUITAR ESTA SECCIÓN ANTES DE PASAR AL WORD -->
## Datos a confirmar (antes de pasar al Word)

- **3a:** «N passed» y 0 fallas → `evidencias/pytest-final.txt`.
- **3b:** ingenuo X de 3 y endurecido 0 de 3 → `evidencias/lab4b-1-prompt-hardening.txt`.
- **5b:** número de ejecuciones de HU-10 → `evidencias/borrador-ejecuciones.md`.
- **2a, 3c, 4a:** Estado LISTA → `salida/HU-10/reporte.md`.
