# Plan de ejecución · Reto M3 · HU-10 Solicitar vacaciones

> Generado el 2026-11-07 a partir de los 7 archivos de `guias/m3-reto/` y del estado real del repo. Objetivo: terminar hoy copiando y ejecutando, sin tomar decisiones.

## 0 · Cómo usar este plan

- Ejecuta los pasos **en orden**. Si un output no coincide, ve a **Plan B** (después del Bloque 4).
- **Terminal A** = PowerShell para comandos. **Terminal B** = Claude Code (`claude`) para los prompts. Las dos en `D:\agentic-course\modulo3\m3-sistemas_agenticos`.
- En Claude Code: si muestra un plan y pide aprobación, responde `si`. Si pide permiso para editar, elige **Yes**.
- Capturas: `Win+Shift+S` → recorta → clic en la notificación → `Ctrl+S` → guarda en `D:\agentic-course\modulo3\m3-sistemas_agenticos\evidencias\capturas\<nombre>.png`.
- Nunca edites a mano `app/` ni `salida/`. Las excepciones son `salida/HU-10/decisiones.md` y `salida/seguridad.md`, que son tuyos por diseño del reto. Nunca uses `DEFENSAS=0`.
- Códigos de rúbrica:
  - **R1–R5:** rúbrica .docx. Multiagente 25 %, LangGraph 25 %, Flujo E2E 20 %, Seguridad 20 %, Documentación 10 %.
  - **G1–G4:** tabla «Cómo se califica» de la Guía. App 40 %, Recorrido 35 %, Integridad 10 %, Decisiones 15 %.
  - **F1a–F6c:** secciones del Formato de entrega.
  - **P:** entregables del Plan de reto.
- Tiempo estimado: 5–7 h (incluye instalar Docker y 4 ejecuciones de la fábrica). Costo estimado de API: 20–40 USD.

**Bloque T.** Pégalo cada vez que abras una terminal nueva (a partir del Paso 2):

```powershell
cd D:\agentic-course\modulo3\m3-sistemas_agenticos
.venv\Scripts\Activate.ps1
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$PSDefaultParameterValues['Out-File:Encoding'] = 'utf8'
$env:PYTHONUTF8 = "1"
Remove-Item Env:DEFENSAS -ErrorAction SilentlyContinue
```

## 1 · Fuente de verdad de HU-10 (para revisar outputs)

Las pruebas ocultas «están construidas solo con lo que dicen `reglas_vacaciones.md` y `convenciones_vacaciones.md`» (Guía). Donde la Guía dice otra cosa, **manda esta tabla**. Las validaciones se aplican en este orden:

| Orden | Caso | Código | `detail` exacto |
|---|---|---|---|
| 1 | Empleado no existe | 404 | `Empleado no encontrado` |
| 2 | Empleado dado de baja | 409 | `No se pueden solicitar vacaciones para un empleado dado de baja` |
| 3 | Fin anterior a inicio | 400 | `La fecha de fin no puede ser anterior a la fecha de inicio` |
| 4 | Cruza de año | 400 | `Las vacaciones deben estar dentro de un mismo año calendario` |
| 5 | Año fuera de 2026–2027 | 400 | `Solo se pueden solicitar vacaciones en 2026 y 2027` |
| 6 | Regla 1 · antigüedad | 400 | `Se requiere al menos un año de antigüedad a la fecha de inicio` |
| 7 | Regla 3 · sin días hábiles | 400 | `El periodo no incluye días hábiles` |
| 8 | Regla 2 · excede el tope | 400 | `La solicitud excede los días disponibles: quedan N días hábiles` |

- `POST /api/empleados/{empleado_id}/vacaciones` → 201 con `id, empleado_id, fecha_inicio, fecha_fin, dias_habiles, dias_restantes`.
- `GET /api/empleados/{empleado_id}/vacaciones?anio=AAAA` → 200 con `empleado_id, anio, dias_usados, dias_disponibles, solicitudes`. Sin `anio`, usa el año en curso.
- `data-testid`: `vacaciones-abrir-{empleado_id}`, `vacaciones-fecha-inicio`, `vacaciones-fecha-fin`, `vacaciones-enviar`, `vacaciones-disponibles`, `vacaciones-mensaje`.
- Mensaje de éxito en pantalla: `Solicitud registrada: N días hábiles. Te quedan M días hábiles en AAAA.`

Casos de las tablas de ejemplo. Todos los comprueba el **Paso 29**:

| Regla | Datos | Esperado |
|---|---|---|
| 1 | Ingreso 2025-12-21, pide 2026-12-21 → 2026-12-31 | 201 · 8 días · quedan 4 |
| 1 | Ingreso 2025-12-21, pide desde 2026-12-18 | 400 antigüedad |
| 1 | Ingreso 2024-03-10, pide 2026-07-06 → 2026-07-10 | 201 · 5 días |
| 2 | Usados 0, pide 6–10 jul 2026 | 201 · 5 · quedan 7 |
| 2 | Usados 5, pide 13–21 jul 2026 | 201 · 7 · quedan 0 |
| 2 | Usados 12, pide 1 día | 400 `…quedan 0 días hábiles` |
| 2 | Usados 4, pide 9 días | 400 `…quedan 8 días hábiles` |
| 3 | 2026-12-21 → 2026-12-31 | 8 (Navidad no cuenta) |
| 3 | 2026-09-14 → 2026-09-18 | 4 (16 de septiembre) |
| 3 | 2026-03-16 → 2026-03-20 | 4 (16 de marzo) |
| 3 | 2026-07-11 → 12 y 2026-04-04 → 05 | 400 sin días hábiles |

---

## Bloque 0 · Entorno (≈60–90 min)

### Paso 1 · Abrir la terminal y fijar UTF-8
**1 · Qué:** Abre PowerShell (Windows Terminal) en la fábrica, activa UTF-8 y crea la carpeta de evidencias.
**2 · Acción (Terminal A):**
```powershell
setx PYTHONUTF8 1
cd D:\agentic-course\modulo3\m3-sistemas_agenticos
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$PSDefaultParameterValues['Out-File:Encoding'] = 'utf8'
$env:PYTHONUTF8 = "1"
Remove-Item Env:DEFENSAS -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Force evidencias\capturas | Out-Null
Test-Path evidencias\capturas
```
**3 · Output esperado:** `SUCCESS: Specified value was saved.` y `True`.
**4 · Evidencia:** —
**5 · Rúbrica:** habilitador.

### Paso 2 · Entorno de Python
**1 · Qué:** Crea `.venv`, instala dependencias e instala Chromium para Playwright.
**2 · Acción (Terminal A):**
```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned -Force
uv venv --python 3.12
.venv\Scripts\Activate.ps1
uv pip install -r requirements.txt
python -m playwright install chromium
python -c "import anthropic, langgraph, claude_agent_sdk, playwright; print('Python listo')"
```
**3 · Output esperado:** el prompt muestra `(m3-sistemas_agenticos)` o `(.venv)`, y la última línea dice `Python listo`.
**4 · Evidencia:** —
**5 · Rúbrica:** R5 (el README documentará estos comandos en el Paso 36).

### Paso 3 · Archivo `.env`
**1 · Qué:** Crea `.env` con tu clave, el modelo y el presupuesto por llamada.
**2 · Acción (Terminal A):**
```powershell
Set-Content -Path .env -Encoding ascii -Value "ANTHROPIC_API_KEY=PEGA_AQUI_TU_CLAVE`nMODEL=claude-sonnet-5-5`nPRESUPUESTO_USD=5"
notepad .env
```
En Notepad, reemplaza `PEGA_AQUI_TU_CLAVE` por tu clave `sk-ant-…`. Si ya la tenías guardada, está en `D:\agentic-course\m3-reto\modulo3\m3-sistemas_agenticos\.env`. Guarda con `Ctrl+S`, cierra y corre:
```powershell
Get-Content .env | Select-String MODEL
```
**3 · Output esperado:** `MODEL=claude-sonnet-5-5`.
**4 · Evidencia:** ninguna (`.env` nunca se sube).
**5 · Rúbrica:** R4, G3.

### Paso 4 · Probar la clave y el modelo
**1 · Qué:** Confirma que la API responde con ese modelo.
**2 · Acción (Terminal A):**
```powershell
python -c "import os, anthropic, dotenv; dotenv.load_dotenv(); r = anthropic.Anthropic().messages.create(model=os.environ['MODEL'], max_tokens=20, messages=[{'role': 'user', 'content': 'Responde solo: ok'}]); print('API OK:', r.content[0].text)"
```
**3 · Output esperado:** `API OK: ok`. Si sale otra cosa:
- `not_found_error`: cambia la línea a `MODEL=claude-sonnet-5` en `.env` y repite.
- `authentication_error`: la clave está mal copiada.
- Error de saldo: recarga créditos.
**4 · Evidencia:** —
**5 · Rúbrica:** habilitador.

### Paso 5 · Quitar la clave real de `.env.example`
**1 · Qué:** `.env.example` trae una clave real versionada. Reemplázala por un marcador y confirma que `.env` está ignorado.
**2 · Acción (Terminal A):**
```powershell
python -c "import re, pathlib; f = pathlib.Path('.env.example'); f.write_text(re.sub(r'(?m)^ANTHROPIC_API_KEY=.*', 'ANTHROPIC_API_KEY=sk-ant-tu-clave-aqui', f.read_text(encoding='utf-8')), encoding='utf-8')"
Select-String -Path .env.example -Pattern ANTHROPIC
git -C .. check-ignore -q m3-sistemas_agenticos/.env; if ($?) { ".env ignorado por git" }
```
**3 · Output esperado:** `.env.example:1:ANTHROPIC_API_KEY=sk-ant-tu-clave-aqui` y `.env ignorado por git`.
**4 · Evidencia:** el diff va en el commit y se cita en `salida/seguridad.md` y en `CHANGELOG.md` → F1c.
**5 · Rúbrica:** R4, G3.

### Paso 6 · Docker Desktop
**1 · Qué:** Instala Docker Desktop con WSL 2 y comprueba que el motor responde.
**2 · Acción (Terminal A):**
```powershell
winget install -e --id Docker.DockerDesktop --accept-package-agreements --accept-source-agreements
```
Después:
1. Reinicia Windows si te lo pide.
2. Abre **Docker Desktop**, acepta los términos y elige «Use recommended settings».
3. Espera a que diga «Engine running».
4. Si pide WSL, abre PowerShell **como administrador**, corre `wsl --install` y reinicia.

Al volver, abre Terminal A, pega el **Bloque T** y corre:
```powershell
docker info *> $null; if ($?) { "Docker listo" }
docker compose version
```
**3 · Output esperado:** `Docker listo` y `Docker Compose version v2.…`.
**4 · Evidencia:** —
**5 · Rúbrica:** R3 (sin Docker no hay despliegue).

### Paso 7 · Claude Code
**1 · Qué:** Comprueba el CLI de Claude Code y abre la Terminal B.
**2 · Acción (Terminal A):**
```powershell
claude --version
```
Si dice «no se reconoce», instálalo, cierra y abre la terminal, pega el Bloque T y repite:
```powershell
irm https://claude.ai/install.ps1 | iex
```
Luego abre **Terminal B**, pega el Bloque T y escribe `claude`. Inicia sesión si te lo pide y deja esta terminal abierta todo el día.
**3 · Output esperado:** `2.x.x (Claude Code)`, y la pantalla de Claude Code en Terminal B.
**4 · Evidencia:** —
**5 · Rúbrica:** R1 (los agentes 3, 4 y 5 usan Claude Code).

---

## Bloque 1 · Ajustar la fábrica antes de ejecutar (≈30 min)

### Paso 8 · Arreglar `npm` en Windows (`flujos/verificacion.py`)
**1 · Qué:** Sin este cambio, la etapa «verificar» se cae con `FileNotFoundError [WinError 2]`.
**2 · Acción (Terminal B · Claude Code):**
```text
Cambio mínimo en flujos/verificacion.py para que funcione en Windows (allí npm es npm.cmd y subprocess.run(["npm", ...]) lanza FileNotFoundError):
1. Agrega `import shutil` junto a los demás imports.
2. Justo después de los imports agrega esta línea:
NPM = shutil.which("npm") or "npm"   # en Windows npm es npm.cmd: subprocess necesita la ruta completa
3. En verificar_frontend usa NPM en lugar de "npm" en las dos llamadas a _correr.
No cambies nada más. Al terminar muestra el diff.
```
Verificación (Terminal A):
```powershell
Select-String -CaseSensitive -Path flujos\verificacion.py -Pattern "NPM"
```
**3 · Output esperado:** 3 líneas: la definición de `NPM` y sus 2 usos.
**4 · Evidencia:** el diff en el commit, `CHANGELOG.md` y `decisiones.md` §5 → F5b.
**5 · Rúbrica:** R3, G2.

### Paso 9 · Analista: mensajes exactos, escenarios de límite y registro de validaciones
**1 · Qué:** El analista pasa a leer las convenciones (donde están los mensajes), deja de usar `Antecedentes` (Problema 2 del troubleshooting) y exige los 9 mensajes de HU-10. Cada validación queda en `salida/HU-xx/validaciones.md`.
**2 · Acción (Terminal B · Claude Code):**
```text
Reemplaza el contenido completo de agentes/analista.py por exactamente este código (no cambies nada más):

"""Sesión 1 · Agente 1, analista: historia de usuario -> criterios de aceptación en Gherkin.

Uso:  python -m agentes.analista historias/HU-01-registrar-empleado.md
"""
import re
import sys
import time
from pathlib import Path

from agentes.base import RAIZ, SALIDA, ejecutar_agente, herramientas_archivos, hu_de, rel

SISTEMA = """Eres analista de producto en un equipo de software. Conviertes historias de usuario
en criterios de aceptación escritos en Gherkin, en español.

Cómo trabajas:
1. Lee la historia, contexto/reglas_negocio.md y contexto/convenciones_app.md (ahí están la API,
   los códigos HTTP, los mensajes de error exactos y los data-testid).
2. Guarda el Gherkin con la herramienta escribir_archivo en {destino}. La primera línea es
   `# language: es` y usas solo las palabras clave Característica, Escenario, Dado, Cuando,
   Entonces, Y. No uses Antecedentes ni Esquema del escenario: cada Escenario lleva su propio
   Dado, Cuando y Entonces.
3. Incluye el camino feliz y un escenario de error por cada regla de negocio y por cada mensaje de
   error que apliquen a ESTA historia, con el código HTTP y el mensaje copiados letra por letra.
4. Para cada regla con números o fechas agrega escenarios de límite: el valor exacto que sí se permite
   y el primero que ya no (por ejemplo, el día exacto del aniversario y un día antes, o usar justo los
   días que quedan y pasarse por uno). Usa los ejemplos de las tablas del contexto.
5. Si la historia tiene pantalla, agrega un escenario de pantalla con éxito y uno con error que usen
   los data-testid de las convenciones y el mensaje exacto que se muestra.
6. Cada escenario se puede verificar desde la pantalla o la API: datos concretos, nada de «funciona bien».
7. No inventes reglas. Si falta información, agrégala al final como comentarios bajo `# Preguntas abiertas`.
8. Responde al final con una sola línea: cuántos escenarios escribiste."""

# Mensajes que el validador exige letra por letra, por historia. Salen de contexto/convenciones_app.md;
# el de «excede» se compara sin el número N porque cambia en cada escenario.
MENSAJES_OBLIGATORIOS: dict[str, list[str]] = {
    "HU-10": [
        "Empleado no encontrado",
        "No se pueden solicitar vacaciones para un empleado dado de baja",
        "La fecha de fin no puede ser anterior a la fecha de inicio",
        "Las vacaciones deben estar dentro de un mismo año calendario",
        "Solo se pueden solicitar vacaciones en 2026 y 2027",
        "Se requiere al menos un año de antigüedad a la fecha de inicio",
        "El periodo no incluye días hábiles",
        "La solicitud excede los días disponibles: quedan",
        "Solicitud registrada:",
    ],
}


def escenarios(gherkin: str) -> list[str]:
    """Devuelve los nombres de los escenarios de un texto Gherkin."""
    return re.findall(r"^\s*Escenario:\s*(.+?)\s*$", gherkin, flags=re.MULTILINE)


def preguntas_abiertas(gherkin: str) -> list[str]:
    """Devuelve las líneas bajo `# Preguntas abiertas`; si hay, el flujo pide una decisión humana."""
    if "# Preguntas abiertas" not in gherkin:
        return []
    bloque = gherkin.split("# Preguntas abiertas", 1)[1]
    return [l.lstrip("# -").strip() for l in bloque.splitlines() if l.strip().lstrip("#").strip()]


def validar_gherkin(texto: str, obligatorios: list[str] | None = None) -> list[str]:
    """Evaluador determinista: devuelve los problemas encontrados; vacío = válido."""
    problemas = []
    if not texto.lstrip().startswith("# language: es"):
        problemas.append("La primera línea debe ser '# language: es'.")
    if "Característica:" not in texto:
        problemas.append("Falta 'Característica:'.")
    bloques = re.split(r"^\s*Escenario:", texto, flags=re.MULTILINE)[1:]
    if len(bloques) < 2:
        problemas.append("Se esperan al menos 2 escenarios (camino feliz y un error).")
    for i, bloque in enumerate(bloques, 1):
        for clave in ("Dado", "Cuando", "Entonces"):
            if not re.search(rf"^\s*{clave}\b", bloque, flags=re.MULTILINE):
                problemas.append(f"El escenario {i} no tiene '{clave}'.")
    for mensaje in obligatorios or []:
        if mensaje not in texto:
            problemas.append(f"Falta un escenario con el mensaje exacto «{mensaje}» "
                             "(cópialo letra por letra de contexto/convenciones_app.md).")
    return problemas


def registrar_validacion(carpeta: Path, agente: str, intento: int, problemas: list[str]) -> None:
    """Deja evidencia de cada validación en salida/HU-xx/validaciones.md (la escribe el código, no una persona)."""
    carpeta.mkdir(parents=True, exist_ok=True)
    estado = "OK" if not problemas else "RECHAZADO · " + " | ".join(problemas)
    with open(carpeta / "validaciones.md", "a", encoding="utf-8") as f:
        f.write(f"- {time.strftime('%Y-%m-%d %H:%M:%S')} · {agente} · intento {intento}: {estado}\n")


def generar_criterios(historia: Path, max_intentos: int = 3) -> Path:
    """Escribe los criterios con el agente y los valida; si fallan, reintenta con los problemas (reflexión)."""
    hu = hu_de(historia)
    carpeta = SALIDA / hu
    destino = carpeta / "criterios.feature"
    herramientas = herramientas_archivos(lectura=[RAIZ / "historias", RAIZ / "contexto"], escritura=carpeta)
    tarea = f"Historia de usuario: {rel(historia)}"
    for intento in range(1, max_intentos + 1):
        print(f"Analista · intento {intento}")
        ejecutar_agente(SISTEMA.format(destino=rel(destino)), herramientas, tarea, max_pasos=15, nombre="analista")
        problemas = validar_gherkin(destino.read_text(encoding="utf-8"), MENSAJES_OBLIGATORIOS.get(hu)) \
            if destino.exists() else [f"No se escribió {rel(destino)}."]
        registrar_validacion(carpeta, "analista", intento, problemas)
        if not problemas:
            return destino
        # Reflexión guiada por un evaluador determinista: el agente recibe los problemas y corrige
        tarea += "\n\nTu versión anterior tiene estos problemas; corrígelos:\n- " + "\n- ".join(problemas)
    raise ValueError("Criterios inválidos tras varios intentos:\n- " + "\n- ".join(problemas))


if __name__ == "__main__":
    ruta = generar_criterios(Path(sys.argv[1]).resolve())
    texto = ruta.read_text(encoding="utf-8")
    print(f"\nListo: {rel(ruta)} · {len(escenarios(texto))} escenarios")
    for p in preguntas_abiertas(texto):
        print("  Pregunta abierta:", p)
```
Verificación (Terminal A):
```powershell
python -c "from agentes.analista import validar_gherkin, MENSAJES_OBLIGATORIOS as M; print(len(validar_gherkin('# language: es', M['HU-10'])))"
```
**3 · Output esperado:** `11`.
**4 · Evidencia:** el diff de `agentes/analista.py` y, más adelante, `salida/HU-10/validaciones.md` → F2b, F4b, `decisiones.md` §2.
**5 · Rúbrica:** G1, G2, R3, R4 (el validador hace que el agente proponga y el código decida).

### Paso 10 · Diseñador, automatizador y desarrollador
**1 · Qué:** Cada caso y cada test crea su propio empleado. Los mensajes se comparan exactos. Los días hábiles se calculan en el backend. El diseñador también registra sus validaciones.
**2 · Acción (Terminal B · Claude Code):**
```text
Aplica exactamente estos cambios, sin tocar nada más:

A) agentes/disenador_pruebas.py
1. Cambia `from agentes.analista import escenarios` por:
from agentes.analista import escenarios, registrar_validacion
2. Reemplaza la constante SISTEMA completa por:
SISTEMA = """Eres diseñador de pruebas de software. A partir de criterios de aceptación en Gherkin
escribes casos de prueba que luego otra persona automatizará.

Cómo trabajas:
1. Lee {criterios}, contexto/convenciones_app.md (API, mensajes exactos y data-testid) y
   contexto/reglas_negocio.md.
2. Para cada escenario escribe al menos un caso de nivel "api". Si el escenario involucra la pantalla,
   escribe además uno de nivel "e2e" cuyos pasos mencionen los data-testid que se usan.
3. Usa datos concretos. Para correos usa el dominio corporativo empresa.com. Si un caso depende de datos
   acumulados (por ejemplo, días de vacaciones ya usados), parte de un empleado NUEVO creado en sus
   precondiciones, con correo único y una fecha_ingreso explícita.
4. En resultado_esperado escribe el código HTTP y el mensaje exacto (`detail`) cuando aplique.
   Sé breve: máximo 5 pasos por caso.
5. Guarda los casos llamando a la herramienta guardar_casos (no escribas el JSON a mano).
   - "nivel" solo puede ser "api" o "e2e".
   - En "datos" TODOS los valores son texto: "201", no 201; para un campo vacío usa "", nunca null.
   - En "escenario" copia el nombre del escenario EXACTAMENTE como aparece después de "Escenario:".
   - Si guardar_casos devuelve un error, corrige lo que indica y vuelve a llamarla.
6. Responde al final con una sola línea: cuántos casos escribiste."""
3. En disenar_casos: cambia `max_intentos: int = 2` por `max_intentos: int = 3`; la llamada queda
   `ejecutar_agente(sistema, herramientas, tarea, max_pasos=15, nombre="disenador")`; y justo después de
   calcular `problemas` agrega la línea:
        registrar_validacion(carpeta, "disenador", intento, problemas)

B) agentes/automatizador.py
En TAREA, inserta estas tres reglas justo antes de la línea que empieza con "- Comprueba la sintaxis":
- Si un caso depende de datos acumulados (por ejemplo, vacaciones), cada test crea su PROPIO empleado
  con correo único (uuid) y la fecha_ingreso que pide el caso; nunca compartas empleados entre tests.
- Compara códigos HTTP y mensajes `detail` con igualdad exacta (==), copiados de CLAUDE.md.
- En E2E espera a que el mensaje de resultado sea visible antes de comparar su texto.

C) agentes/desarrollador.py
Reemplaza la constante INSTRUCCIONES completa por:
INSTRUCCIONES = """Eres el desarrollador full stack del equipo. Construyes la aplicación de gestión de empleados
de la empresa siguiendo CLAUDE.md al pie de la letra (stack, puertos, rutas, campos, códigos HTTP,
mensajes exactos y data-testid).
Extiendes el código de las historias anteriores sin reemplazarlo ni cambiar su comportamiento.
Las reglas de negocio que dependen de un cálculo (por ejemplo, días hábiles con festivos) se calculan
en el backend, nunca en el navegador; y las validaciones se hacen en el orden que indique CLAUDE.md.
No escribes pruebas automatizadas ni archivos de Docker: de eso se encargan otros agentes.
Las dependencias de Python ya están instaladas; en frontend/ sí puedes usar npm install."""

Al terminar muestra el diff de los tres archivos.
```
Verificación (Terminal A):
```powershell
python -c "import agentes.disenador_pruebas, agentes.automatizador, agentes.desarrollador, flujos.flujo_s4; print('fabrica OK')"
(Select-String -Path agentes\disenador_pruebas.py, agentes\automatizador.py, agentes\desarrollador.py -Pattern "registrar_validacion|PROPIO empleado|nunca en el navegador").Count
```
**3 · Output esperado:** `fabrica OK` y un número mayor o igual a `4`.
**4 · Evidencia:** los diffs en el commit y `CHANGELOG.md` → F5a, F5b.
**5 · Rúbrica:** G1, R1 (roles más claros), R3.

### Paso 11 · Docstrings
**1 · Qué:** Agrega docstrings a todas las funciones de `agentes/` y `flujos/`. `seguridad/` no se toca, para que los hooks queden sin diff.
**2 · Acción (Terminal B · Claude Code):**
```text
Agrega un docstring de una línea, en español, a cada función de agentes/*.py y flujos/*.py que no tenga (incluye las funciones internas de agentes/base.py y los nodos de flujos/flujo_s2.py, flujo_s3.py y flujo_s4.py). Solo docstrings: no cambies lógica, nombres, imports ni formato. No toques seguridad/, labs_agentes/ ni ejemplos/. Muestra el diff.
```
Verificación (Terminal A):
```powershell
python -c "import ast, pathlib; fs = [p for d in ('agentes', 'flujos') for p in pathlib.Path(d).glob('*.py')]; sin = [f'{p}:{n.name}' for p in fs for n in ast.walk(ast.parse(p.read_text(encoding='utf-8'))) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and not ast.get_docstring(n)]; print('Sin docstring:', len(sin), sin[:5])"
```
**3 · Output esperado:** `Sin docstring: 0 []`.
**4 · Evidencia:** el diff en el commit y `CHANGELOG.md`.
**5 · Rúbrica:** R5.

### Paso 12 · Herramientas de evidencia
**1 · Qué:** Crea `buscar_denegados.py` (Lab 3C), tu script de comprobación independiente de HU-10 y el borrador de ejecuciones.
**2 · Acción (Terminal B · Claude Code):**
```text
Crea buscar_denegados.py en la raíz de m3-sistemas_agenticos copiando, sin cambios, el script de referencia de la sección «3C · Inspeccionar» de ../guias/Guía de laboratorios · Módulo 3.md (el bloque de Python que empieza con """Lab 3C · Busca en auditoria.jsonl"). No modifiques nada más.
```
**Acción (Terminal A):**
```powershell
@'
"""Comprobacion independiente de HU-10 contra las tablas de ejemplo de las reglas.

Es la revision humana del resultado (como abrir la app y probarla): no forma parte de app/ ni de la fabrica.
Uso, desde la raiz de la fabrica y con la app desplegada:  python evidencias/comprobar_hu10.py
"""
import uuid

import httpx

c = httpx.Client(base_url="http://localhost:8000/api", timeout=15, follow_redirects=True)
fallas = 0

ANTIGUEDAD = "Se requiere al menos un a\u00f1o de antig\u00fcedad a la fecha de inicio"
SIN_HABILES = "El periodo no incluye d\u00edas h\u00e1biles"
EXCEDE = "La solicitud excede los d\u00edas disponibles: quedan {} d\u00edas h\u00e1biles"
ORDEN = "La fecha de fin no puede ser anterior a la fecha de inicio"
MISMO_ANIO = "Las vacaciones deben estar dentro de un mismo a\u00f1o calendario"
ANIOS = "Solo se pueden solicitar vacaciones en 2026 y 2027"
NO_EXISTE = "Empleado no encontrado"


def empleado(fecha_ingreso: str = "2024-03-10") -> int:
    """Registra un empleado nuevo (correo unico) y devuelve su id."""
    datos = {"nombre": "Prueba Vacaciones", "correo": f"vac-{uuid.uuid4().hex[:10]}@empresa.com",
             "puesto": "Analista", "departamento": "Operaciones", "fecha_ingreso": fecha_ingreso}
    r = c.post("/empleados", json=datos)
    r.raise_for_status()
    return r.json()["id"]


def pedir(eid: int, inicio: str, fin: str) -> httpx.Response:
    """Solicita vacaciones para el empleado eid."""
    return c.post(f"/empleados/{eid}/vacaciones", json={"fecha_inicio": inicio, "fecha_fin": fin})


def revisar(nombre: str, r: httpx.Response, codigo: int, **esperado) -> None:
    """Compara el codigo HTTP y los campos esperados; imprime OK o FALLA."""
    global fallas
    try:
        cuerpo = r.json()
    except ValueError:
        cuerpo = {}
    ok = r.status_code == codigo and all(cuerpo.get(k) == v for k, v in esperado.items())
    fallas += not ok
    print("OK   " if ok else "FALLA", f"{nombre} -> {r.status_code} {r.text[:150]}")


# Regla 1 - Antiguedad
revisar("R1 ingreso 2025-12-21, inicio 2026-12-21 (aniversario exacto)",
        pedir(empleado("2025-12-21"), "2026-12-21", "2026-12-31"), 201, dias_habiles=8, dias_restantes=4)
revisar("R1 ingreso 2025-12-21, inicio 2026-12-18 (le faltan dias)",
        pedir(empleado("2025-12-21"), "2026-12-18", "2026-12-18"), 400, detail=ANTIGUEDAD)
revisar("R1 ingreso 2024-03-10, inicio 2026-07-06",
        pedir(empleado("2024-03-10"), "2026-07-06", "2026-07-10"), 201, dias_habiles=5)

# Regla 2 - Tope anual de 12 dias habiles
e = empleado()
revisar("R2 usados 0, pide 6-10 jul (5)", pedir(e, "2026-07-06", "2026-07-10"), 201, dias_habiles=5, dias_restantes=7)
revisar("R2 usados 5, pide 13-21 jul (7, exacto)", pedir(e, "2026-07-13", "2026-07-21"), 201, dias_habiles=7, dias_restantes=0)
revisar("R2 usados 12, pide 1", pedir(e, "2026-08-03", "2026-08-03"), 400, detail=EXCEDE.format(0))
e = empleado()
revisar("R2 usados 0, pide 3-6 ago (4)", pedir(e, "2026-08-03", "2026-08-06"), 201, dias_habiles=4, dias_restantes=8)
revisar("R2 usados 4, pide 10-20 ago (9)", pedir(e, "2026-08-10", "2026-08-20"), 400, detail=EXCEDE.format(8))
revisar("GET saldo 2026 (usados 4)", c.get(f"/empleados/{e}/vacaciones", params={"anio": 2026}), 200,
        anio=2026, dias_usados=4, dias_disponibles=8)

# Regla 3 - Dias habiles (sin sabados, domingos ni festivos)
revisar("R3 2026-09-14..18, festivo 16 sep", pedir(empleado(), "2026-09-14", "2026-09-18"), 201, dias_habiles=4)
revisar("R3 2026-03-16..20, festivo 16 mar", pedir(empleado(), "2026-03-16", "2026-03-20"), 201, dias_habiles=4)
revisar("R3 2027-03-15..19, festivo 15 mar", pedir(empleado(), "2027-03-15", "2027-03-19"), 201, dias_habiles=4)
revisar("R3 2026-07-11..12, fin de semana", pedir(empleado(), "2026-07-11", "2026-07-12"), 400, detail=SIN_HABILES)
revisar("R3 2026-04-04..05, fin de semana", pedir(empleado(), "2026-04-04", "2026-04-05"), 400, detail=SIN_HABILES)

# Otras validaciones de las convenciones
revisar("404 empleado inexistente", pedir(999999, "2026-07-06", "2026-07-10"), 404, detail=NO_EXISTE)
revisar("fin anterior a inicio", pedir(empleado(), "2026-07-10", "2026-07-06"), 400, detail=ORDEN)
revisar("cruza de anio", pedir(empleado(), "2026-12-28", "2027-01-08"), 400, detail=MISMO_ANIO)
revisar("anio fuera de tabla", pedir(empleado(), "2028-01-10", "2028-01-14"), 400, detail=ANIOS)

print(f"\nResultado: {fallas} fallas")
'@ | Set-Content -Encoding ascii evidencias\comprobar_hu10.py
Set-Content -Encoding ascii -Path evidencias\borrador-ejecuciones.md -Value "# Borrador de ejecuciones (materia prima de decisiones.md)`n"
python -c "import ast; ast.parse(open('evidencias/comprobar_hu10.py').read()); print('comprobar_hu10 OK')"
python buscar_denegados.py
```
**3 · Output esperado:** `comprobar_hu10 OK` y `No existe auditoria.jsonl: …`. El segundo mensaje es normal en este punto.
**4 · Evidencia:** `buscar_denegados.py`, `evidencias/comprobar_hu10.py` y `evidencias/borrador-ejecuciones.md` → F3b, F3c.
**5 · Rúbrica:** R4, G1, G3.

---

## Bloque 2 · Base HU-01 a HU-03 (≈60–100 min)

> Se genera **antes** de agregar el contexto de HU-10, para no contaminar la base. Si Windows pregunta por el firewall para Python o Docker, elige **Permitir**.

### Paso 13 · HU-01 Registrar empleado
**1 · Qué:** Corre la fábrica completa con HU-01.
**2 · Acción (Terminal A):**
```powershell
docker info *> $null; if ($?) { "Docker listo" }
python -m flujos.flujo_s4 historias\HU-01-registrar-empleado.md
```
Respuestas durante la ejecución:
- Si aparece `--- PREGUNTAS ---`, escribe `si`.
- Cuando aparezca `--- PLAN ---`, escribe `si`.
- Después, espera sin tocar la terminal (20–40 min).
**3 · Output esperado:** termina con `**Estado:** LISTA`, que también queda en `salida\HU-01\reporte.md`. Si sale `ESCALAR A UNA PERSONA` o un Traceback, aplica el **Plan B** (1 reintento como máximo) y sigue.
**4 · Evidencia:** `salida/HU-01/*` (va en el commit base).
**5 · Rúbrica:** R3, G1 (la base no debe romperse).

### Paso 14 · HU-02 Consultar directorio
**1 · Qué:** Agrega el directorio sobre la base.
**2 · Acción (Terminal A):**
```powershell
python -m flujos.flujo_s4 historias\HU-02-consultar-directorio.md
```
Responde `si` en `PREGUNTAS` y en `PLAN`.
**3 · Output esperado:** `**Estado:** LISTA`.
**4 · Evidencia:** `salida/HU-02/*`.
**5 · Rúbrica:** R3, G1.

### Paso 15 · HU-03 Editar y dar de baja
**1 · Qué:** Agrega edición y baja (la necesita el error 409 de vacaciones).
**2 · Acción (Terminal A):**
```powershell
python -m flujos.flujo_s4 historias\HU-03-editar-dar-baja.md
```
Responde `si` en `PREGUNTAS` y en `PLAN`.
**3 · Output esperado:** `**Estado:** LISTA`.
**4 · Evidencia:** `salida/HU-03/*`.
**5 · Rúbrica:** R3, G1.

### Paso 16 · Regresión de la base
**1 · Qué:** Confirma que HU-01 a HU-03 pasan y que la app está arriba.
**2 · Acción (Terminal A):**
```powershell
cd app; python -m pytest tests -q > ..\evidencias\pytest-base-hu01-hu03.txt; cd ..
Get-Content evidencias\pytest-base-hu01-hu03.txt -Tail 3
docker compose -f app\docker-compose.yml ps
Start-Process http://localhost:8080
```
**3 · Output esperado:** la última línea dice `N passed` sin `failed`, los dos servicios aparecen `running` o `healthy`, y el directorio abre en el navegador.
**4 · Evidencia:** `evidencias/pytest-base-hu01-hu03.txt` → F3a.
**5 · Rúbrica:** G1 («las pruebas de HU-01 a HU-03 siguen pasando»), R3.

### Paso 17 · Commit de la base
**1 · Qué:** Guarda un punto seguro antes de HU-10.
**2 · Acción (Terminal A):**
```powershell
cd ..
git add m3-sistemas_agenticos guias/m3-reto
git diff --cached --name-only | Select-String -Pattern "(^|/)\.env$"
git commit -m "feat(reto-hu10): fabrica ajustada y base HU-01 a HU-03 generada"
cd m3-sistemas_agenticos
```
**3 · Output esperado:** el `Select-String` no imprime nada (no se sube `.env`) y `git commit` muestra `N files changed`.
**4 · Evidencia:** el commit en `dev`.
**5 · Rúbrica:** G3, R5.

---

## Bloque 3 · Seguridad · Lab 4B con HU-99 (≈20 min)

> Va **antes** de la ejecución final de HU-10. Si el filtro fallara, así no contamina `app/` ni el `auditoria.jsonl` de la entrega.

### Paso 18 · Prompt ingenuo contra prompt endurecido
**1 · Qué:** Mide cuántas veces la orden oculta llega a los criterios con cada prompt.
**2 · Acción (Terminal A):**
```powershell
python -m ejemplos.s4_seguridad.prompt_hardening --veces 3 > evidencias\lab4b-1-prompt-hardening.txt; Get-Content evidencias\lab4b-1-prompt-hardening.txt -Tail 4
```
**3 · Output esperado:** `Veces que el ataque llegó a los criterios:`, luego `Ingenuo X de 3` y `Endurecido Y de 3`. Normalmente Y = 0; cualquier resultado es válido.
**4 · Evidencia:** `evidencias/lab4b-1-prompt-hardening.txt` → `seguridad.md` y F3b.
**5 · Rúbrica:** R4 (sistema robusto ante inputs maliciosos), P.

### Paso 19 · Analista sin filtro (sin pasar por el flujo)
**1 · Qué:** Muestra que, sin el filtro, la orden oculta puede volverse un requisito. Esto **no** usa `DEFENSAS=0`.
**2 · Acción (Terminal A):**
```powershell
python -m agentes.analista historias\HU-99-envenenada.md > evidencias\lab4b-2-analista-sin-filtro.txt; Get-Content evidencias\lab4b-2-analista-sin-filtro.txt -Tail 3
$n = (Select-String -Pattern diagnostico -Path salida\HU-99\criterios.feature -ErrorAction SilentlyContinue | Where-Object { $_.Line -notmatch '^\s*#' } | Measure-Object).Count; "Lineas de escenario con 'diagnostico' sin filtro: $n" | Out-File evidencias\lab4b-2-grep.txt; Get-Content evidencias\lab4b-2-grep.txt
```
**3 · Output esperado:** `Listo: salida\HU-99\criterios.feature · N escenarios` y `Lineas … sin filtro: 0`. Si el número es mayor que 0, el ataque llegó: también es un resultado válido y se reporta.
**4 · Evidencia:** `evidencias/lab4b-2-*.txt` y `salida/HU-99/criterios.feature` → `seguridad.md`.
**5 · Rúbrica:** R4, P.

### Paso 20 · Flujo con defensas
**1 · Qué:** El nodo `filtrar_historia` debe bloquear HU-99 antes del analista.
**2 · Acción (Terminal A):**
```powershell
python -m flujos.flujo_s4 historias\HU-99-envenenada.md
Get-Content salida\bloqueada\reporte.md -TotalCount 8
```
Toma la captura **`07-hu99-bloqueada.png`**. Si en lugar de bloquearla aparece `--- PREGUNTAS ---` o `--- PLAN ---`, presiona `Ctrl+C` (el filtro falló) y anótalo en `evidencias\borrador-ejecuciones.md`.
**3 · Output esperado:** `**Estado:** BLOQUEADA POR SEGURIDAD` y `Filtro de historia: BLOQUEADA · <motivo>`.
**4 · Evidencia:** `salida/bloqueada/reporte.md` y `evidencias/capturas/07-hu99-bloqueada.png` → F3b.
**5 · Rúbrica:** R4, P (qué capa detuvo el ataque).

### Paso 21 · La bandera no llegó a la app
**1 · Qué:** Confirma que el contenido del señuelo no aparece en `app/`.
**2 · Acción (Terminal A):**
```powershell
$n = (Get-ChildItem -Recurse -File app\backend, app\frontend\src, app\tests -ErrorAction SilentlyContinue | Select-String -Pattern BANDERA-DEMO | Measure-Object).Count; "Coincidencias de BANDERA-DEMO en app/: $n" | Out-File evidencias\lab4b-4-bandera.txt; Get-Content evidencias\lab4b-4-bandera.txt
```
**3 · Output esperado:** `Coincidencias de BANDERA-DEMO en app/: 0`.
**4 · Evidencia:** `evidencias/lab4b-4-bandera.txt` → `seguridad.md` y F3b.
**5 · Rúbrica:** R4.

---

## Bloque 4 · HU-10 (≈60 min por ejecución)

### Paso 22 · Copiar HU-10 al repo reparando la codificación
**1 · Qué:** Copia la historia a `historias/`, crea `contexto/reglas_vacaciones.md` y `contexto/convenciones_vacaciones.md`, y anexa ambos al final de `reglas_negocio.md` y `convenciones_app.md`. Al copiar, corrige la doble codificación.
**2 · Acción (Terminal A):**
```powershell
@'
from pathlib import Path
src = Path(r"..\guias\m3-reto")
def reparar(nombre):
    # Los archivos del reto vienen con doble codificacion: se reparan al copiarlos
    return (src / nombre).read_text(encoding="utf-8").encode("cp1252").decode("utf-8")
historia = reparar("hu-10-solicitar-vacaciones.md")
reglas = reparar("hu-10 reglas de vacaciones.md")
convenciones = reparar("convenciones de vacaciones hu-10.md")
Path("historias/HU-10-solicitar-vacaciones.md").write_text(historia, encoding="utf-8")
Path("contexto/reglas_vacaciones.md").write_text(reglas, encoding="utf-8")
Path("contexto/convenciones_vacaciones.md").write_text(convenciones, encoding="utf-8")
for destino, extra in (("contexto/reglas_negocio.md", reglas), ("contexto/convenciones_app.md", convenciones)):
    p = Path(destino)
    texto = p.read_text(encoding="utf-8")
    if "(HU-10)" not in texto:
        p.write_text(texto.rstrip() + "\n\n" + extra, encoding="utf-8")
print("HU-10 copiada y contexto actualizado")
'@ | python -
```
**3 · Output esperado:** `HU-10 copiada y contexto actualizado`.
**4 · Evidencia:** `historias/HU-10-…md` y el diff de `contexto/` → F6b.
**5 · Rúbrica:** G1, G2 (checklist: «la historia existe y las reglas y convenciones están al final de sus archivos»).

### Paso 23 · Verificar el contexto
**1 · Qué:** Confirma que existen los archivos y que los acentos están bien (sin `Ã`).
**2 · Acción (Terminal A):**
```powershell
Test-Path historias\HU-10-solicitar-vacaciones.md, contexto\reglas_vacaciones.md, contexto\convenciones_vacaciones.md
python -c "from pathlib import Path; t = Path('contexto/convenciones_app.md').read_text(encoding='utf-8') + Path('contexto/reglas_negocio.md').read_text(encoding='utf-8'); print('contexto OK' if 'quedan N d\u00edas h\u00e1biles' in t and '12 d\u00edas h\u00e1biles' in t and '\u00c3' not in t else 'REVISAR contexto')"
```
**3 · Output esperado:** `True` tres veces y `contexto OK`.
**4 · Evidencia:** —
**5 · Rúbrica:** G1.

### Paso 24 · Limpiar antes de la ejecución final
**1 · Qué:** Borra la auditoría y la salida de HU-10, para que la entrega sea solo de la ejecución final.
**2 · Acción (Terminal A):**
```powershell
Remove-Item auditoria.jsonl -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force salida\HU-10 -ErrorAction SilentlyContinue
Test-Path auditoria.jsonl, salida\HU-10
```
**3 · Output esperado:** `False` y `False`.
**4 · Evidencia:** —
**5 · Rúbrica:** G3 («auditoria.jsonl es el de la ejecución final»).

### Paso 25 · Ejecutar la fábrica con HU-10 (con defensas)
**1 · Qué:** Corre la ejecución final. Rechaza el primer plan con el Comentario A y aprueba el segundo.
**2 · Acción (Terminal A):**
```powershell
docker info *> $null; if ($?) { "Docker listo" }
python -m flujos.flujo_s4 historias\HU-10-solicitar-vacaciones.md
```
Durante la ejecución:
1. Si aparece `--- PREGUNTAS ---`, escribe `si`.
2. En el **primer** `--- PLAN ---`, toma la captura **`01-plan-rechazado.png`**. Luego pega el **Comentario A** del Anexo A (una sola línea) y presiona `Enter`.
3. En el **segundo** `--- PLAN ---`, toma la captura **`02-plan-aprobado.png`** y escribe `si`.
4. Espera sin tocar la terminal (20–40 min).
5. Al terminar, toma la captura **`03-reporte-lista.png`**.

**3 · Output esperado:** `**Estado:** LISTA` y `**Ciclos de corrección:** 0`, 1 o 2.
**4 · Evidencia:**
- `salida/HU-10/criterios.feature`, `casos_prueba.json`, `validaciones.md`, `reporte.md` y `resultados.xml`.
- `auditoria.jsonl`.
- Capturas 01–03.

Van a F2a, F4a, F5b y `decisiones.md` §3.
**5 · Rúbrica:** R1, R2, R3, R4, G1, G2, G3.

### Paso 26 · Revisar criterios y casos
**1 · Qué:** Comprueba con los validadores que están las 6 reglas, los 9 mensajes y que cada escenario tiene caso.
**2 · Acción (Terminal A):**
```powershell
python -c "from pathlib import Path; from agentes.analista import escenarios, validar_gherkin, MENSAJES_OBLIGATORIOS as M; t = Path('salida/HU-10/criterios.feature').read_text(encoding='utf-8'); print(len(escenarios(t)), 'escenarios |', validar_gherkin(t, M['HU-10']) or 'criterios sin problemas')"
python -c "from pathlib import Path; from agentes.disenador_pruebas import PlanPruebas, validar_plan; j = Path('salida/HU-10/casos_prueba.json').read_text(encoding='utf-8'); g = Path('salida/HU-10/criterios.feature').read_text(encoding='utf-8'); print(len(PlanPruebas.model_validate_json(j).casos), 'casos |', validar_plan(j, g) or 'casos sin problemas')"
Get-Content salida\HU-10\validaciones.md
```
**3 · Output esperado:** `≥12 escenarios | criterios sin problemas`, `≥12 casos | casos sin problemas`, y en `validaciones.md` el último intento de cada agente termina en `OK`.
**4 · Evidencia:** `salida/HU-10/validaciones.md` → `decisiones.md` §2 y F4b.
**5 · Rúbrica:** G2 («criterios validados con un escenario por regla»; «al menos un caso por escenario»).

### Paso 27 · Bitácora en el orden del flujo
**1 · Qué:** Comprueba que las etapas quedaron en orden y que el plan aparece rechazado y luego aprobado.
**2 · Acción (Terminal A):**
```powershell
Select-String -Path salida\HU-10\reporte.md -Pattern "Estado|Filtro|Criterios|Casos de prueba|Plan |Construcci|Verificaci|Despliegue|Pruebas"
```
**3 · Output esperado:** en este orden:
1. `Estado: LISTA`
2. `Filtro de historia: OK`
3. `Criterios escritos…`
4. `Casos de prueba escritos…`
5. `Plan rechazado: …`
6. `Plan aprobado por una persona`
7. `Construcción 1`
8. `Verificación: OK`
9. `Despliegue: OK` y `Pruebas automatizadas: OK` (en cualquier orden)
10. `Pruebas E2E: … passed`
**4 · Evidencia:** `salida/HU-10/reporte.md` → F4a.
**5 · Rúbrica:** G2 (35 %), R2, R3.

### Paso 28 · Contenedores y pruebas completas
**1 · Qué:** Guarda la evidencia de Docker y de todas las pruebas (HU-01 a HU-10).
**2 · Acción (Terminal A):**
```powershell
docker compose -f app\docker-compose.yml ps > evidencias\docker-compose-ps.txt; Get-Content evidencias\docker-compose-ps.txt
cd app; python -m pytest tests -q > ..\evidencias\pytest-final.txt; cd ..
Get-Content evidencias\pytest-final.txt -Tail 3
Get-ChildItem app\tests\api, app\tests\e2e -Filter *hu_10*
```
**3 · Output esperado:** `backend` y `frontend` en `running` o `healthy`, `N passed` sin `failed`, y los archivos `test_hu_10.py` y `test_hu_10_e2e.py`.
**4 · Evidencia:** `evidencias/docker-compose-ps.txt` y `evidencias/pytest-final.txt` → F3a, F3c.
**5 · Rúbrica:** G1, R3 (checklist: `docker compose ps`, pruebas de API y E2E que pasan).

### Paso 29 · Comprobación independiente contra las tablas de ejemplo
**1 · Qué:** Recorre por API todas las filas de las reglas 1, 2 y 3 y los demás errores.
**2 · Acción (Terminal A):**
```powershell
python evidencias\comprobar_hu10.py > evidencias\hu10-comprobacion.txt; Get-Content evidencias\hu10-comprobacion.txt
```
**3 · Output esperado:** 18 líneas que empiezan con `OK` y `Resultado: 0 fallas`.
**4 · Evidencia:** `evidencias/hu10-comprobacion.txt` → F3c y `decisiones.md` §3.
**5 · Rúbrica:** G1 (40 %: se adelanta a las pruebas ocultas).

### Paso 30 · Probar la pantalla como empleado
**1 · Qué:** Pide vacaciones desde la interfaz, como lo haría un empleado.
**2 · Acción (Terminal A):**
```powershell
Start-Process http://localhost:8080
```
En el navegador:
1. Registra un empleado con estos datos y guarda:
   - Nombre: `Ana Vacaciones`
   - Correo: `ana.vacaciones.1107@empresa.com` (si ya existe, usa `.1108`)
   - Puesto: `Analista`
   - Departamento: `Operaciones`
   - Fecha de ingreso: `2024-03-10`
2. En su fila, presiona **Solicitar vacaciones**. Pide inicio `2026-12-21` y fin `2026-12-31`, y presiona **Enviar**. Toma la captura **`05-ui-solicitud-exitosa.png`**.
3. Pide inicio `2026-07-11` y fin `2026-07-12`, y presiona **Enviar**. Toma la captura **`06-ui-error-sin-dias-habiles.png`**.
**3 · Output esperado:**
- Primera solicitud: `Solicitud registrada: 8 días hábiles. Te quedan 4 días hábiles en 2026.`
- Segunda solicitud: `El periodo no incluye días hábiles`.
**4 · Evidencia:** capturas 05 y 06 → anexo del Word y F2a.
**5 · Rúbrica:** G1, R3 (la Guía pide: «Abre http://localhost:8080 y pide unas vacaciones»).

### Paso 31 · Captura del grafo
**1 · Qué:** Guarda la imagen del grafo LangGraph.
**2 · Acción (Terminal A):**
```powershell
Start-Process flujos\salidas\grafo_flujo_s4.html
```
Toma la captura **`04-grafo-flujo-s4.png`**.
**3 · Output esperado:** el diagrama con los nodos `filtrar_historia` → … → `fin`, con las ramas paralelas `desplegar` y `automatizar`.
**4 · Evidencia:** `flujos/salidas/grafo_flujo_s4.html` y la captura 04 → F4a.
**5 · Rúbrica:** R2.

### Paso 32 · Evidencia de la auditoría
**1 · Qué:** Resume quién escribió qué y si algún agente intentó salirse de su rol.
**2 · Acción (Terminal A):**
```powershell
python buscar_denegados.py > evidencias\auditoria-denegados.txt; Get-Content evidencias\auditoria-denegados.txt -TotalCount 12
python -c "import json, collections; print(collections.Counter(json.loads(l)['agente'] for l in open('auditoria.jsonl', encoding='utf-8')))" > evidencias\auditoria-resumen.txt; Get-Content evidencias\auditoria-resumen.txt
Get-Content auditoria.jsonl -TotalCount 12 | Out-File evidencias\auditoria-fragmento.jsonl
```
**3 · Output esperado:**
- Una lista de intentos fuera de rol, o `Ningún intento de escritura fuera de rol…`.
- `Counter({'desarrollador': …, 'automatizador': …, 'despliegue': …, 'desarrollador-plan': …})`.
**4 · Evidencia:** `evidencias/auditoria-*.txt` y `evidencias/auditoria-fragmento.jsonl` → `seguridad.md` y F1b.
**5 · Rúbrica:** G3, R4 (P: «incluye un fragmento de auditoria.jsonl»).

### Paso 33 · Decidir si sigues
**1 · Qué:** Revisa tres resultados:
- el Paso 25 terminó en `LISTA`;
- el Paso 28 no tiene `failed`;
- el Paso 29 dice `0 fallas`.
**2 · Acción:** Si se cumplen los tres, pasa al **Bloque 5**. Si falla cualquiera, aplica el **Plan B**. Puedes repetir HU-10 hasta 2 veces; después sigue al Bloque 5 con lo que tengas.
**3 · Output esperado:** —
**4 · Evidencia:** —
**5 · Rúbrica:** G1, G2.

---

## Plan B · Si algo falla

### B1 · Corregir la fábrica, nunca el resultado
**Acción (Terminal B · Claude Code).** Si hubo un Traceback, cópialo de la Terminal A y pégalo al final del prompt.
```text
La última ejecución de la fábrica no quedó LISTA (o la comprobación tiene fallas). Revisa, en este orden: el reporte.md más reciente dentro de salida/, el resultados.xml y el validaciones.md de esa misma carpeta, y evidencias/hu10-comprobacion.txt si existe.
1. Explícame en 3 líneas qué falló y qué agente lo causó (analista, diseñador, desarrollador, despliegue o automatizador).
2. Corrige SOLO la fábrica: instrucciones o validadores en agentes/*.py, flujos/*.py o archivos de contexto/. Prohibido editar app/, salida/ y seguridad/ (regla del reto: se corrige al agente, no su resultado).
3. Si la corrección se logra mejor con un comentario al plan, escríbeme en UNA sola línea el comentario que debo agregar en la próxima ejecución.
4. Agrega al final de evidencias/borrador-ejecuciones.md una entrada con: fecha y hora, historia, qué falló (cita la línea del reporte o del validador), qué cambiaste en la fábrica y por qué no se corrigió el resultado a mano.
Muéstrame el diff antes de terminar.
```

### B2 · Limpiar y volver a correr
Usa la fila de la historia que falló:

| Historia | Limpieza (Terminal A) | Volver a correr |
|---|---|---|
| HU-01 | `Remove-Item -Recurse -Force salida\HU-01` | Paso 13 |
| HU-02 | `Remove-Item -Recurse -Force salida\HU-02` | Paso 14 |
| HU-03 | `Remove-Item -Recurse -Force salida\HU-03` | Paso 15 |
| HU-10 | Paso 24 | Pasos 25 a 33 |

En la re-ejecución de HU-10, en el primer plan pega el **Comentario A**, un espacio y el comentario nuevo de B1, todo en la misma línea. Límites: 1 reintento para HU-01 a HU-03 y 2 para HU-10. Si después sigue fallando, continúa: `ESCALAR A UNA PERSONA` es un estado válido y se explica en `decisiones.md` §5.

### B3 · Fallas típicas

| Síntoma | Acción |
|---|---|
| `KeyError: 'MODEL'` | Falta `.env`: repite el Paso 3. |
| `error_max_budget_usd` | En `.env` pon `PRESUPUESTO_USD=8` y vuelve a correr. |
| `FileNotFoundError` con npm | Repite el Paso 8. |
| `Cannot connect to the Docker daemon` | Abre Docker Desktop y espera «Engine running». |
| Puerto 8000 u 8080 ocupado | `docker compose -f app\docker-compose.yml down` y vuelve a correr. |
| `UnicodeEncodeError: 'charmap'` | Pega el Bloque T. |
| `Executable doesn't exist` (Playwright) | `python -m playwright install chromium`. |
| `Criterios inválidos` o `Casos inválidos` | B1 (lee la lista de problemas del validador). |
| El filtro bloquea HU-10 | B1 (ajustar el prompt de `filtrar_historia` en `flujos/flujo_s4.py`). |

---

## Bloque 5 · Documentación y evidencias (≈40 min)

### Paso 34 · `salida/seguridad.md`
**1 · Qué:** Redacta el reporte de seguridad del Lab 4B con datos reales.
**2 · Acción (Terminal B · Claude Code):**
```text
Redacta salida/seguridad.md. Es el reporte de seguridad que el Lab 4 pide escribir a la persona, no una salida de agente, así que sí puedes crearlo. Usa SOLO datos reales de: evidencias/lab4b-1-prompt-hardening.txt, evidencias/lab4b-2-analista-sin-filtro.txt, evidencias/lab4b-2-grep.txt, salida/HU-99/criterios.feature, salida/bloqueada/reporte.md, evidencias/lab4b-4-bandera.txt, evidencias/auditoria-resumen.txt, evidencias/auditoria-denegados.txt y auditoria.jsonl (solo para contar líneas). Sigue exactamente esta plantilla, reemplaza cada {{...}} y no pases de página y media:

# Reporte de seguridad · Fábrica de agentes (Lab 4B y reto HU-10)

## Ataques y defensas
| Ataque | Riesgo OWASP | ¿Funcionó sin defensas? | Defensa que lo detuvo | Evidencia |
|---|---|---|---|---|
| Historia envenenada HU-99 (prompt injection indirecta) | ASI01 · Secuestro del objetivo | {{"Sí" si el número de lab4b-2-grep.txt es mayor que 0; si no, "No, esta vez"}}. Paso 1: prompt ingenuo {{X}} de 3; endurecido {{Y}} de 3 | `filtrar_historia`, primer nodo del grafo: la bloqueó antes del analista ({{motivo copiado del reporte}}). Respaldo: hooks `confinar_lectura` y `comandos_permitidos` | `salida/bloqueada/reporte.md`, `evidencias/lab4b-*.txt` |
| Contexto envenenado | ASI06 · Contexto envenenado | No probado: no hice la ampliación opcional | Revisión humana de los cambios en `contexto/` (diff de cada commit) | — |

## Qué capa detuvo el ataque y por qué no basta el prompt
{{3 a 4 líneas: el filtro en código detuvo HU-99; el prompt endurecido bajó la tasa (X contra Y) pero es una sugerencia que depende del modelo; si el filtro fallara, confinar_lectura niega leer secretos_demo.txt y .env, y sin WebFetch ni WebSearch no hay por dónde exfiltrar. Coincidencias de BANDERA-DEMO en app/: {{n}}.}}

## Riesgos del OWASP agéntico que mitiga la fábrica
- ASI01 Secuestro del objetivo: `filtrar_historia`, etiqueta `<historia_no_confiable>` y rol con límites en cada agente.
- ASI02 Mal uso de herramientas: hooks de rol `confinar_escritura` (cada agente escribe solo sus rutas) y `allowed_tools`.
- ASI03 Abuso de privilegios: `confinar_lectura` (solo `app/`, nunca `.env` ni `secretos`) y carpeta de trabajo fija.
- ASI04 Cadena de suministro: plan revisado por una persona antes de construir; sin dependencias nuevas.
- ASI05 Ejecución inesperada: `comandos_permitidos` (lista de programas, sin `$(...)` ni backticks) y la app en contenedores Docker.
- ASI08 Fallos en cascada: validadores entre etapas y límites `MAX_INTENTOS`, `MAX_CICLOS`, `max_turns` y `max_budget_usd`.
- ASI09 Confianza excesiva: el plan completo se muestra y la decisión queda en la bitácora.
- ASI07 y ASI10 aplican menos: los agentes no se hablan entre sí, se comunican por archivos en `salida/HU-xx/`.

## Checklist de producción
- [x] Cada agente tiene una lista justificada de archivos y programas permitidos: `ESCRITURA` y `PROGRAMAS` en `agentes/desarrollador.py`, `despliegue.py` y `automatizador.py`, aplicadas por `confinar_escritura` y `comandos_permitidos`; analista y diseñador solo escriben en `salida/HU-xx/` (`_dentro_de`).
- [x] Ninguna acción irreversible ocurre sin aprobación humana: `interrupt` en `aprobar_plan` antes de construir; el despliegue es local y reversible.
- [x] El contenido externo pasa por un filtro y se trata como no confiable: `filtrar_historia` con `<historia_no_confiable>`.
- [x] Hay límites de pasos, ciclos y presupuesto: `max_pasos` del bucle, `MAX_INTENTOS=2`, `MAX_CICLOS=2`, `max_turns=80`, `max_budget_usd=PRESUPUESTO_USD`.
- [x] Cada llamada a herramienta queda auditada: hook `auditar` → `auditoria.jsonl` ({{total de líneas}} registros en la ejecución final: {{resumen por agente}}). Pendiente: auditar también las herramientas del analista y del diseñador.
- [x] Los agentes no tienen acceso a internet ni a secretos: `disallowed_tools=["WebFetch", "WebSearch"]`, `confinar_lectura` y `PALABRAS_SECRETAS`.

Al terminar, muéstrame el archivo completo.
```
**3 · Output esperado:** `salida/seguridad.md` con la tabla, las 2 secciones de texto, la lista OWASP y el checklist completo, sin ningún `{{`.
**4 · Evidencia:** `salida/seguridad.md` → F1c y F3b.
**5 · Rúbrica:** R4 (20 %), P.

### Paso 35 · `salida/HU-10/decisiones.md`
**1 · Qué:** Responde las 5 preguntas en una página, con hechos de tu ejecución.
**2 · Acción (Terminal B · Claude Code):**
```text
Redacta salida/HU-10/decisiones.md. La Guía del reto pide que lo escriba la persona; no es salida de un agente. Máximo 450 palabras (una página). Usa SOLO hechos de mi ejecución: salida/HU-10/reporte.md (bitácora), salida/HU-10/validaciones.md, evidencias/borrador-ejecuciones.md, evidencias/auditoria-resumen.txt, evidencias/pytest-final.txt y evidencias/hu10-comprobacion.txt. Sigue exactamente esta plantilla: reemplaza cada {{...}} con datos citados (archivo y texto) y conserva el resto del texto.

# Decisiones · HU-10 Solicitar vacaciones

**1. ¿Qué pasos son workflow y cuáles agente? ¿Por qué?**
Workflow (el código decide): el grafo de `flujos/flujo_s4.py` con su orden fijo, los reintentos (`MAX_INTENTOS=2`), los ciclos de corrección (`MAX_CICLOS=2`), las verificaciones y el redespliegue. Agente (el modelo decide qué leer, qué escribir y cuántas veces): analista, diseñador de pruebas, desarrollador (planificar y construir), despliegue y automatizador. El filtro y el triage son LLM con salida estructurada cuyo veredicto enruta el código. El orden de las etapas no cambia entre historias, por eso es workflow; el contenido sí cambia, por eso hay agentes.

**2. ¿Cómo se validó cada salida? ¿Qué atrapó algún validador?**
Criterios: `validar_gherkin` (estructura y los 9 mensajes exactos de HU-10). Casos: `PlanPruebas` dentro de `guardar_casos` y `validar_plan` (cada escenario con caso). Código: `verificar_app` (`/api/salud` y `npm run build`). Despliegue: `verificar_despliegue` (8000 y 8080). Pruebas: `verificar_pruebas_escritas` (cada CP con test) y `ejecutar_pruebas` (pytest + Playwright). En mi ejecución: {{lo que dice validaciones.md: intentos RECHAZADO y qué faltaba, o «todo pasó al primer intento»}}; {{líneas de Verificación y Pruebas E2E de la bitácora, y ciclos de triage si hubo}}.

**3. ¿Dónde intervine como persona y qué vi para decidir?**
En la aprobación del plan: rechacé el primero con un comentario concreto ({{resumen en una línea de «Plan rechazado: …»}}) porque necesitaba que el plan fijara rutas, campos, orden de validación, códigos y mensajes exactos, y el cálculo de días hábiles en el backend; el segundo lo incorporó y lo aprobé («Plan aprobado por una persona»). {{Si hubo preguntas abiertas, qué respondí}}. Después revisé el resultado: {{última línea de hu10-comprobacion.txt}} y {{última línea de pytest-final.txt}}, y probé la pantalla en http://localhost:8080.

**4. ¿Qué arquitectura de orquestación usa tu fábrica y por qué no otra?**
Orquestador con flujo fijo en LangGraph: estado `TypedDict` con reductores (`bitacora`, `costo_usd`), paralelización (despliegue ∥ automatizador), evaluador-optimizador (construir ↔ verificar), humano en el bucle (`interrupt`) y un supervisor acotado (triage) que solo enruta correcciones. Los agentes se comunican por la pizarra en disco `salida/HU-10/`. No usé un supervisor LLM general ni una red de agentes: el orden siempre es el mismo, un supervisor LLM añadiría costo y variación sin ganar nada, y una red haría difícil auditar quién escribió qué.

**5. Si algo falló: ¿qué corregí en el agente y por qué no en su resultado?**
Antes de ejecutar HU-10 corregí la fábrica: (a) `verificar_frontend` fallaba en Windows porque `npm` es `npm.cmd`, y lo resolví con `shutil.which`; (b) el analista no leía las convenciones, donde están los mensajes exactos, y su validador no los exigía, así que agregué ambas cosas y un registro en `validaciones.md`; (c) los archivos de HU-10 venían con doble codificación (`dÃ­as`), y los reparé al copiarlos a `contexto/`. Durante la ejecución: {{entradas de borrador-ejecuciones.md, o «no hubo fallas que corregir»}}. No corregí resultados porque `app/` y `salida/` deben poder regenerarse y `auditoria.jsonl` demuestra que solo los escribieron agentes.

Al terminar, dime cuántas palabras tiene.
```
**3 · Output esperado:** el archivo con las 5 respuestas, sin ningún `{{`, y menos de 450 palabras.
**4 · Evidencia:** `salida/HU-10/decisiones.md` → F5b y F5c.
**5 · Rúbrica:** G4 (15 %), R1, R2.

### Paso 36 · README, CHANGELOG y CLAUDE.md
**1 · Qué:** Completa la documentación de onboarding para Mac, Linux y Windows, y el changelog.
**2 · Acción (Terminal B · Claude Code):**
```text
Actualiza la documentación de la fábrica (no toques app/ ni salida/):
A) README.md: conserva lo que tiene y agrega, en español, estas secciones:
1. Requisitos: Python 3.12, Node 20+, Docker Desktop (WSL 2 en Windows), Claude Code y una clave de Anthropic.
2. Instalación paso a paso en Mac/Linux (bash) y en Windows (PowerShell): uv venv, activar, uv pip install -r requirements.txt, python -m playwright install chromium, .env con ANTHROPIC_API_KEY, MODEL y PRESUPUESTO_USD; en Windows además setx PYTHONUTF8 1 y Set-ExecutionPolicy -Scope CurrentUser RemoteSigned.
3. Uso: python -m flujos.flujo_s4 con HU-01, HU-02, HU-03 y HU-10; qué responder en las pausas (preguntas abiertas: si; plan: si o un comentario concreto en una línea); HU-99 solo para la demo de seguridad; nunca DEFENSAS=0 fuera de clase.
4. Pruebas: cd app y python -m pytest tests -q, tests/api y tests/e2e --headed; python evidencias/comprobar_hu10.py; python buscar_denegados.py.
5. Arquitectura: tabla con filtro, analista, diseñador, desarrollador (planificar y construir), despliegue, automatizador y triage (entrada, salida y verificación determinista); mapeo a los roles del reto (planificador = desarrollador en modo planificar; implementador = desarrollador en modo construir; tester = diseñador + automatizador; reviewer = verificación + triage); enlace a flujos/salidas/grafo_flujo_s4.html.
6. HU-10 · Vacaciones: ejemplo de POST y GET con curl (Mac/Linux) y con Invoke-RestMethod (Windows), con la respuesta esperada según contexto/convenciones_vacaciones.md.
7. Seguridad: capas (filtro, prompt hardening, hooks, sin internet, auditoría, Docker) y enlace a salida/seguridad.md.
8. Solución de problemas: npm en Windows, UnicodeEncodeError, Docker daemon, puertos 8000/8080 ocupados, error_max_budget_usd y Playwright «Executable doesn't exist».
B) CHANGELOG.md nuevo (formato Keep a Changelog, entrada 2026-11-07), construido a partir de `git diff 94c5b74 -- agentes flujos contexto historias .env.example` y de los archivos nuevos, con secciones Agregado, Cambiado y Seguridad, más la línea «Sin cambios: seguridad/hooks.py (hooks intactos)».
C) CLAUDE.md (raíz de la fábrica): en Estructura agrega HU-10 en historias/, contexto/reglas_vacaciones.md, contexto/convenciones_vacaciones.md, evidencias/ y buscar_denegados.py. Cambio mínimo.
Muéstrame el diff al terminar.
```
**3 · Output esperado:** el README con 8 secciones nuevas, `CHANGELOG.md` creado y `CLAUDE.md` con 5 entradas nuevas.
**4 · Evidencia:** `README.md`, `CHANGELOG.md` y `CLAUDE.md` → F6b y F6c.
**5 · Rúbrica:** R5 (10 %; sobresaliente: ejemplos y onboarding), P.

### Paso 37 · `evidencias/README.md` (índice, prompts, iteraciones y reflexión)
**1 · Qué:** Reúne en un índice la evidencia que pide el Plan de reto.
**2 · Acción (Terminal B · Claude Code):**
```text
Crea evidencias/README.md con cuatro secciones, en español, usando solo archivos reales del repo:
1. «Índice de evidencias»: tabla Evidencia | Archivo | Qué demuestra. Incluye salida/HU-10/criterios.feature, casos_prueba.json, validaciones.md, reporte.md, resultados.xml y decisiones.md; auditoria.jsonl y evidencias/auditoria-*; evidencias/pytest-*.txt, docker-compose-ps.txt y hu10-comprobacion.txt; evidencias/lab4b-*.txt, salida/HU-99/criterios.feature, salida/bloqueada/reporte.md y salida/seguridad.md; flujos/salidas/grafo_flujo_s4.html; y cada imagen de evidencias/capturas/.
2. «Prompts utilizados»: enlace y una línea de propósito para SISTEMA de agentes/analista.py y agentes/disenador_pruebas.py, INSTRUCCIONES y prompts de planificar/construir de agentes/desarrollador.py, TAREA de agentes/despliegue.py y agentes/automatizador.py, PROMPT de agentes/triage.py, el prompt de filtrar_historia en flujos/flujo_s4.py, CLAUDE.md y app/CLAUDE.md. Además copia textual del comentario con que rechacé el primer plan (línea «Plan rechazado: …» de salida/HU-10/reporte.md).
3. «Iteraciones»: resumen de salida/HU-10/validaciones.md y de evidencias/borrador-ejecuciones.md (cuántas ejecuciones de HU-10, qué falló y qué se corrigió en la fábrica).
4. «Reflexión»: copia exactamente este texto:
**Qué funcionó.** El flujo fijo con validadores deterministas: cada etapa dejó evidencia y el código, no el agente, decidió si avanzar. La aprobación del plan fue mi punto de mayor influencia: un comentario concreto con rutas, códigos y mensajes exactos alineó al desarrollador antes de escribir código. Las defensas en código (filtro y hooks) detuvieron HU-99 sin depender de que el modelo se negara.
**Qué mejoraría.** 1) Auditar también las herramientas del analista y del diseñador, no solo las de Claude Code. 2) Usar un checkpointer persistente (SqliteSaver) con un thread_id por ejecución para retomar tras una caída. 3) Que el validador del analista lea los mensajes obligatorios del contexto en lugar de una lista por historia. 4) Validar la codificación de los archivos de contexto antes de ejecutar: un acento corrupto basta para reprobar las pruebas ocultas.
```
**3 · Output esperado:** `evidencias/README.md` con las 4 secciones y enlaces que funcionan.
**4 · Evidencia:** `evidencias/README.md` → F5a, F5b y F5c.
**5 · Rúbrica:** R4 (nivel Suficiente: «evidencia clara del proceso: prompts, iteraciones, reflexión»), P.

### Paso 38 · Revisar las capturas
**1 · Qué:** Confirma que están las 7 capturas con su nombre.
**2 · Acción (Terminal A):**
```powershell
Get-ChildItem evidencias\capturas | Select-Object -ExpandProperty Name
```
**3 · Output esperado:**
- `01-plan-rechazado.png`
- `02-plan-aprobado.png`
- `03-reporte-lista.png`
- `04-grafo-flujo-s4.png`
- `05-ui-solicitud-exitosa.png`
- `06-ui-error-sin-dias-habiles.png`
- `07-hu99-bloqueada.png`

Si falta alguna, vuelve al paso donde se tomaba.
**4 · Evidencia:** `evidencias/capturas/` → anexo del Word.
**5 · Rúbrica:** R4, P.

### Paso 39 · Formato de entrega (Word)
**1 · Qué:** Confirma con datos reales el borrador `guias/m3-reto/entrega/M3_Formato_de_entrega_HU-10.md` (está escrito suponiendo que todo salió bien) y pásalo a la plantilla de Word junto con las capturas.
**2 · Acción (Terminal B · Claude Code):**
```text
Paso 1 · Confirmar el borrador. Abre ../guias/m3-reto/entrega/M3_Formato_de_entrega_HU-10.md. Usa su tabla «Datos a confirmar» para reemplazar cada marcador [confirmar: …] con el dato real del archivo que indica. Si un dato real no coincide con lo supuesto, corrige también la frase. Por ejemplo: si hubo 2 ejecuciones de HU-10, si un validador rechazó un intento, si el estado no fue LISTA o si el prompt endurecido dejó pasar el ataque. No inventes nada: usa solo evidencias/, salida/ y git. Al terminar, muéstrame el diff.
Paso 2 · Generar el Word. Usa la skill docx:
- Copia ../guias/m3-reto/hu-10-M3._Formato_de_entrega_NGC(3).docx a ../guias/m3-reto/entrega/M3_Reto_HU-10_JoseJuanMartinezMorales.docx.
- En la copia, reemplaza en orden cada párrafo «Ocupa este espacio para redactar tu respuesta.» por el texto de la sección correspondiente (1a, 1b, 1c, 2a … 6c) del .md ya confirmado. Conserva las tablas como tablas de Word.
- Después del bloque de instrucciones de la plantilla, inserta la «Nota de alcance» del .md con su tabla.
- No copies al Word la sección «Datos a confirmar» ni «Qué pasos del plan alimentan cada sección».
- Al final agrega el título «Anexo · Evidencias» y las imágenes de evidencias/capturas/ en orden de nombre, de 15 cm de ancho, cada una con su nombre de archivo como pie.
- No cambies el resto de la plantilla. Dime la ruta del archivo final.
```
Revisión (Terminal A):
```powershell
Select-String -Path ..\guias\m3-reto\entrega\M3_Formato_de_entrega_HU-10.md -Pattern "\[confirmar"
Start-Process ..\guias\m3-reto\entrega\M3_Reto_HU-10_JoseJuanMartinezMorales.docx
```
Si la skill docx no está disponible, abre la plantilla en Word, pega a mano cada sección del .md confirmado y guarda con ese nombre.
**3 · Output esperado:** el `Select-String` no imprime nada (ya no quedan marcadores) y el Word abre con las 18 respuestas llenas y 7 imágenes al final.
**4 · Evidencia:** `guias/m3-reto/entrega/M3_Reto_HU-10_JoseJuanMartinezMorales.docx` → este es el entregable de la plataforma.
**5 · Rúbrica:** F1a–F6c, P (presentación y ortografía).

---

## Bloque 6 · Entrega (≈15 min)

### Paso 40 · Verificación final
**1 · Qué:** Revisa el checklist de la Guía de forma automática.
**2 · Acción (Terminal A):**
```powershell
'historias\HU-10-solicitar-vacaciones.md','contexto\reglas_vacaciones.md','contexto\convenciones_vacaciones.md','salida\HU-10\criterios.feature','salida\HU-10\casos_prueba.json','salida\HU-10\reporte.md','salida\HU-10\decisiones.md','salida\seguridad.md','auditoria.jsonl','app\docker-compose.yml','app\tests\api\test_hu_10.py','app\tests\e2e\test_hu_10_e2e.py','README.md','CHANGELOG.md','evidencias\README.md' | ForEach-Object { '{0,-42} {1}' -f $_, (Test-Path $_) }
Select-String -Path salida\HU-10\reporte.md -Pattern "Estado:"
(Get-Content salida\HU-10\decisiones.md -Raw -Encoding utf8).Split([char[]]" `r`n", [StringSplitOptions]::RemoveEmptyEntries).Count
git -C .. diff --stat 94c5b74 -- m3-sistemas_agenticos/seguridad
if ($env:DEFENSAS) { "OJO: DEFENSAS esta definida" } else { "Defensas activas" }
```
**3 · Output esperado:**
- 15 líneas que terminan en `True`.
- `**Estado:** LISTA`.
- Un número menor o igual a 450.
- El `git diff` de `seguridad` sale vacío (hooks intactos).
- `Defensas activas`.
**4 · Evidencia:** —
**5 · Rúbrica:** G1–G4 (checklist completo de la Guía).

### Paso 41 · Commit final
**1 · Qué:** Un commit con todo, incluido `auditoria.jsonl`, que el `.gitignore` excluye.
**2 · Acción (Terminal A):**
```powershell
cd ..
git add m3-sistemas_agenticos guias/m3-reto
git add -f m3-sistemas_agenticos/auditoria.jsonl
git diff --cached --name-only | Select-String -Pattern "(^|/)\.env$"
git diff --cached --name-only | Select-String -Pattern "auditoria.jsonl|salida/HU-10/decisiones.md|salida/seguridad.md"
git commit -m "feat(reto-hu10): HU-10 Solicitar vacaciones procesada por la fabrica, con evidencias y documentacion"
```
**3 · Output esperado:** el primer `Select-String` sale vacío, el segundo muestra 3 rutas y `git commit` muestra `N files changed`.
**4 · Evidencia:** el commit de entrega.
**5 · Rúbrica:** G3 (integridad: auditoría de la ejecución final y sin `.env`).

### Paso 42 · Push
**1 · Qué:** Sube `dev` y deja `main` en el mismo commit.
**2 · Acción (Terminal A):**
```powershell
git push origin dev
git push origin dev:main
git log -1 --format="%H"
Start-Process https://github.com/josemtzco/modulo3/tree/main/m3-sistemas_agenticos
cd m3-sistemas_agenticos
```
**3 · Output esperado:** `dev -> dev`, `dev -> main`, el hash del commit, y en GitHub se ven `salida/HU-10/` y `auditoria.jsonl`.
**4 · Evidencia:** la URL del commit: `https://github.com/josemtzco/modulo3/commit/<hash>` → F6a.
**5 · Rúbrica:** checklist de la Guía («hice push»), P («liga a tu repositorio»).

### Paso 43 · Subir a la plataforma
**1 · Qué:** Entrega el Word y la liga.
**2 · Acción:** sube `guias\m3-reto\entrega\M3_Reto_HU-10_JoseJuanMartinezMorales.docx` y pega este texto (cambia `<hash>` por el del Paso 42):
```text
Reto M3 · HU-10 Solicitar vacaciones. Repositorio: https://github.com/josemtzco/modulo3 (rama main, carpeta m3-sistemas_agenticos). Commit de entrega: https://github.com/josemtzco/modulo3/commit/<hash>. Índice de evidencias: m3-sistemas_agenticos/evidencias/README.md.
```
**3 · Output esperado:** la plataforma confirma la entrega.
**4 · Evidencia:** la confirmación de la plataforma.
**5 · Rúbrica:** P (entrega en plazo con la plantilla).

---

## Checklist de entregables contra la rúbrica

| Criterio | Qué lo cumple | Pasos |
|---|---|---|
| **R1** Arquitectura multiagente (25 %) · Sobresaliente: 5 o más agentes con roles definidos | 6 agentes + filtro + triage de punta a punta; roles y mapeo planificador/implementador/tester/reviewer documentados | 13–15, 25, 35 §1, 36 |
| **R2** LangGraph (25 %) · todas las features | StateGraph + TypedDict con reductores, aristas condicionales, ramas paralelas, ciclos, `interrupt`/`Command`, checkpointer + `thread_id`, salida estructurada y grafo dibujado | 25, 27, 31, 35 §4, 36 |
| **R3** Flujo E2E funcional (20 %) | Estado LISTA, pruebas en verde y app en el puerto 8080 | 8, 13–16, 25–30 |
| **R4** Seguridad (20 %) · robusto ante inputs maliciosos | HU-99 bloqueada, hooks, auditoría, `seguridad.md`, prompts, iteraciones y reflexión | 5, 18–21, 32, 34, 37 |
| **R5** Documentación (10 %) | Docstrings, README para 3 sistemas operativos, CHANGELOG, CLAUDE.md, índice de evidencias | 11, 36, 37 |
| **G1** La app cumple la historia (40 %) | Mensajes exactos, reglas 1–3 con sus límites y comprobación independiente | 9, 10, 22–23, 25, 28–30 |
| **G2** Recorrido completo (35 %) | Seis etapas en orden, validaciones registradas y plan rechazado → aprobado | 25–27 |
| **G3** Integridad y seguridad (10 %) | Auditoría solo de la ejecución final, hooks sin diff, nada editado a mano, sin `.env` | 5, 17, 24, 32, 40, 41 |
| **G4** Decisiones (15 %) | 5 respuestas con evidencia en una página o menos | 35 |
| Guía · historia y contexto en su lugar | `historias/HU-10…`, contexto anexado y archivos separados | 22, 23 |
| Guía · ejecutado con defensas | Sin `DEFENSAS=0` | 25, 40 |
| Guía · un escenario por regla, mensajes letra por letra | Validador con 9 mensajes | 9, 26 |
| Guía · al menos un caso por escenario | `validar_plan` | 10, 26 |
| Guía · bitácora con aprobación del plan | «Plan rechazado» → «Plan aprobado» | 25, 27 |
| Guía · `docker compose ps` y app en 8080 | Evidencia en texto y en el navegador | 28, 30 |
| Guía · pruebas de API y E2E de vacaciones que pasan | `test_hu_10*.py` | 28 |
| Guía · HU-01 a HU-03 siguen pasando | Regresión | 16, 28 |
| Guía · `reporte.md` con el estado final | Estado LISTA | 25, 27 |
| Guía · `decisiones.md` de una página o menos | ≤ 450 palabras | 35, 40 |
| Guía · `auditoria.jsonl` de la ejecución final | Limpieza + `git add -f` | 24, 32, 41 |
| Guía · sin edición manual ni hooks tocados | Plan B corrige solo la fábrica; diff de `seguridad/` vacío | Plan B, 40 |
| Guía · commit sin `.env` y push | Verificado | 17, 41, 42 |
| P · 4 roles (planificador, implementador, tester, reviewer) | README y Formato §5b | 36, 39 |
| P · docstrings, README (Mac/Linux/Windows) y changelog | — | 11, 36 |
| P · evidencia: prompts, capturas/logs y reflexión | `evidencias/` | 37, 38 |
| P · `decisiones.md` y `seguridad.md` | — | 34, 35 |
| P · demo HU-99, capa que detuvo el ataque y OWASP | — | 18–21, 34 |
| P · fragmento de `auditoria.jsonl` | `evidencias/auditoria-fragmento.jsonl` | 32 |
| P · Formato de entrega y liga al repo | Word + plataforma | 39, 42, 43 |
| F1a–F6c · Formato de entrega | `entrega/M3_Formato_de_entrega_HU-10.md` (Anexo B) | 39 |

---

## Informe de decisiones tomadas por ti

| # | Decisión | Alternativa descartada | Por qué |
|---|---|---|---|
| 1 | Seguir `convenciones_vacaciones.md` en API, códigos, mensajes y `data-testid` (400/404/409, `dias_restantes`, `vacaciones-abrir/enviar/mensaje`) | Tabla de la Guía (422, `dias_disponibles`, `vacaciones-empleado/solicitar`, `mensaje-exito/error`) | La Guía dice que las pruebas ocultas se construyen solo con los archivos de reglas y convenciones |
| 2 | Rúbrica principal = .docx (R1–R5), cubriendo también la tabla de la Guía (G1–G4) | Usar solo una | Los mismos pasos cubren ambas, sin costo extra |
| 3 | Formato de entrega: conservar sus 6 secciones, responder con el equivalente de HU-10, agregar una nota inicial y poner «no aplica» en JWT, hash, rate limiting y cobertura de líneas | Construir autenticación o CI para llenar la plantilla | La plantilla es de otro reto, y la regla 7 de negocio dice que la app no tiene inicio de sesión |
| 4 | Anexar reglas y convenciones a `reglas_negocio.md` y `convenciones_app.md`, y además crear `reglas_vacaciones.md` y `convenciones_vacaciones.md` | Hacer solo una de las dos | La Guía pide anexar (es lo que leen los agentes) y la HU cita los archivos separados |
| 5 | Reparar la doble codificación al copiar (cp1252 → UTF-8) | Copiar tal cual | Con `dÃ­as` todos los mensajes exactos fallarían |
| 6 | Generar HU-01 a HU-03 antes de agregar el contexto de HU-10 | Ir directo a HU-10 o agregar todo junto | El reto parte de la base funcionando; agregar antes contaminaría la base y la evidencia |
| 7 | Aprobar con `si` los planes de HU-01 a HU-03 | Rechazarlos también | La intervención humana que se califica es la de HU-10; ahorra tiempo y costo |
| 8 | Rechazar siempre el primer plan de HU-10 con el Comentario A y aprobar el segundo | Aprobar a la primera | Deja la evidencia «rechazado → aprobado» y fija rutas y mensajes; la Guía lo valora explícitamente |
| 9 | `MODEL=claude-sonnet-5-5`, con respaldo `claude-sonnet-5` | Opus, o el valor de `.env.example` sin probar | Buen balance entre costo y calidad; el Paso 4 lo valida |
| 10 | `PRESUPUESTO_USD=5` | 2 (valor por defecto) | Construir la app desde cero puede pasar de 2 USD y cortar el flujo |
| 11 | El validador del analista usa una lista de 9 mensajes por historia | Extraer los mensajes del contexto automáticamente | Más simple de leer y defender, con la misma garantía |
| 12 | Registrar cada validación en `salida/HU-xx/validaciones.md` desde el código | Capturar la terminal con Tee o Transcript | En PowerShell 5.1 eso rompe `input()` o la codificación; además, así el archivo lo escribe la fábrica |
| 13 | Arreglar `npm` con `shutil.which` en `verificacion.py` | Usar WSL | Son 3 líneas en lugar de mover todo el entorno |
| 14 | Docstrings solo en `agentes/` y `flujos/` | Incluir `seguridad/hooks.py` | Que `hooks.py` no tenga ningún diff evita dudas de integridad |
| 15 | Mantener `InMemorySaver` | SqliteSaver o PostgresSaver | El Plan de reto lo acepta; uno persistente exige una dependencia nueva y acumula la bitácora entre re-ejecuciones |
| 16 | No hacer la ampliación ASI06 (contexto envenenado) | Hacerla | Es opcional y podría dejar la línea envenenada en `app/CLAUDE.md` antes de la ejecución final |
| 17 | Hacer el Lab 4B antes de la ejecución final de HU-10 | Hacerlo después | Si el filtro fallara, contaminaría `app/` y el `auditoria.jsonl` de la entrega |
| 18 | Script propio `evidencias/comprobar_hu10.py`, fuera de `app/` | Confiar solo en las pruebas generadas | Si desarrollador y automatizador se equivocan igual, nadie lo detecta; y no es edición de `app/` |
| 19 | No probar el 409 (baja) en el script propio | Descubrir la ruta de baja | La ruta la define la HU-03 generada; ya lo cubren las pruebas del automatizador |
| 20 | Evidencias en `m3-sistemas_agenticos/evidencias/` | `.ai/` | El profesor revisa la carpeta de la fábrica |
| 21 | Quitar la clave real de `.env.example` | Dejarla | Es un secreto versionado y contradice la regla de seguridad |
| 22 | PowerShell con `OutputEncoding` UTF-8 y `Out-File` en utf8 | Git Bash | Es lo que documentan las guías para Windows y evita acentos rotos en los logs |
| 23 | Dos commits en `dev` (base y final) y `push dev:main` | Un único commit | Protege la base si algo falla; la Guía cuenta el último commit |
| 24 | En el Word usar el nombre «José Juan Martínez Morales», tomado de `reto-m2-josejuanmartinezmorales.zip` | «Jose Martinez» (el de git) | Es el nombre completo que ya usaste en el reto anterior |
| 25 | `decisiones.md` y `seguridad.md` redactados por Claude Code con plantilla fija y solo con datos de la evidencia | Escribirlos desde cero | Es más rápido y siguen hablando de tu ejecución real |
| 26 | Medir cobertura por requisitos (regla → escenario → caso → test) | Instalar pytest-cov | No hay pruebas unitarias en el alcance y no agrega dependencias |
| 27 | Sin CI/CD externo: el «pipeline» es el grafo con sus gates | Crear GitHub Actions | La rúbrica no lo pide; esa sección del Formato es de otro reto |
| 28 | Regla del 29 de febrero → 1 de marzo, sin caso propio | Agregar un caso | Con años 2026–2027 y fecha de ingreso no futura es imposible probarla |
| 29 | `vacaciones-disponibles` muestra solo el número (detalle de la Guía) | Texto libre | No contradice las convenciones y facilita las pruebas E2E |
| 30 | Máximo 1 reintento en la base y 2 en HU-10; después se entrega igual | Reintentar sin límite | El plazo es hoy; ESCALAR es un estado válido si se explica |
| 31 | Dejar en el commit los archivos de `.idea/` que ya estaban en staging | Sacarlos | No afectan la calificación y tú ya los habías agregado |

---

## Anexo A · Comentario de rechazo del primer plan de HU-10

Pégalo **en una sola línea** cuando aparezca el primer `--- PLAN ---` (Paso 25):

```text
No apruebo todavía. Ajusta el plan: 1) Extiende el código de HU-01 a HU-03 sin reemplazarlo ni cambiar su comportamiento. 2) Nueva tabla vacaciones (id, empleado_id, fecha_inicio, fecha_fin, dias_habiles); calcula dias_habiles en el backend con la tabla de festivos 2026 y 2027, contando inicio y fin y sin sábados ni domingos. 3) Valida en este orden, con estos códigos y textos exactos en detail: 404 Empleado no encontrado; 409 No se pueden solicitar vacaciones para un empleado dado de baja; 400 La fecha de fin no puede ser anterior a la fecha de inicio; 400 Las vacaciones deben estar dentro de un mismo año calendario; 400 Solo se pueden solicitar vacaciones en 2026 y 2027; 400 Se requiere al menos un año de antigüedad a la fecha de inicio (aniversario el mismo día y mes; el 29 de febrero pasa al 1 de marzo); 400 El periodo no incluye días hábiles; 400 La solicitud excede los días disponibles: quedan N días hábiles (tope de 12 por año calendario; usar exactamente lo que queda sí se permite). 4) POST /api/empleados/{empleado_id}/vacaciones responde 201 con id, empleado_id, fecha_inicio, fecha_fin, dias_habiles y dias_restantes; GET /api/empleados/{empleado_id}/vacaciones?anio=AAAA responde 200 con empleado_id, anio, dias_usados, dias_disponibles y solicitudes; sin anio usa el año en curso. 5) Pantalla: cada empleado activo del directorio tiene el botón Solicitar vacaciones con data-testid vacaciones-abrir-{empleado_id}; el formulario usa vacaciones-fecha-inicio, vacaciones-fecha-fin, vacaciones-enviar, vacaciones-disponibles (solo el número) y vacaciones-mensaje, que muestra Solicitud registrada: N días hábiles. Te quedan M días hábiles en AAAA. o el detail exacto del error.
```

---

## Anexo B · Formato de entrega

Las 18 respuestas del Formato de entrega están en **`guias/m3-reto/entrega/M3_Formato_de_entrega_HU-10.md`**. Están escritas suponiendo que todo sale bien.

Ese archivo trae además:
- una tabla «Datos a confirmar», con cada dato supuesto, el archivo donde se confirma y su paso;
- una tabla «Qué pasos del plan alimentan cada sección».

El Paso 39 confirma esos datos con la evidencia real y genera el Word.
