# Ejemplos de patrones para clase

Diecisiete programas cortos: uno por patrón, más dos para los conceptos de salidas estructuradas y del humano en el flujo, y una pareja servidor-cliente para MCP. Todos trabajan sobre el mismo dominio (empleados de la empresa) y las mismas historias, para que lo único que cambie de un archivo a otro sea **la estructura**. Cada archivo empieza con un comentario que dice qué línea distingue al patrón y dónde aparece en tu fábrica.

Se ejecutan con Claude real (usan `ANTHROPIC_API_KEY` y `MODEL` de tu `.env`), siempre desde la raíz del repo:

```bash
python -m ejemplos.s1_razonamiento.react
python -m ejemplos.s2_flujos.enrutamiento
python -m ejemplos.s3_topologias.supervisor
```

Cada ejecución hace entre 1 y 10 llamadas cortas al modelo; ejecutar todos cuesta del orden de centavos de dólar.

## Sesión 1 · Patrones de razonamiento (Python y `anthropic`, sin frameworks)

| Archivo | Patrón | Lo que lo distingue en el código | En tu fábrica |
| --- | --- | --- | --- |
| `s1_razonamiento/react.py` | ReAct | `for` que sigue mientras `stop_reason == "tool_use"`; la observación vuelve como `tool_result` | `agentes/base.py` → `ejecutar_agente()` |
| `s1_razonamiento/plan_ejecucion.py` | Plan-and-Execute | Dos fases: `planificar()` devuelve un `Plan` (Pydantic), una persona aprueba, `ejecutar()` lo recorre | `agentes/desarrollador.py` → `planificar()` y `construir()` |
| `s1_razonamiento/salidas_estructuradas.py` | Salidas estructuradas y validación | Un contrato Pydantic, la herramienta forzada con `tool_choice` y dos niveles de validación en código (esquema y reglas); si no se puede corregir, decide una persona | `agentes/disenador_pruebas.py` → `PlanPruebas` y `validar_plan()` |
| `s1_razonamiento/reflexion.py` | Reflexión | `for intento`: el revisor (código) devuelve problemas y se agregan al prompt | `agentes/analista.py` → `validar_gherkin()` |

## Sesión 2 · Patrones de flujo (LangGraph)

| Archivo | Patrón | Lo que lo distingue en el código | En tu fábrica |
| --- | --- | --- | --- |
| `s2_flujos/encadenamiento.py` | Encadenamiento | Solo `add_edge` en línea recta y una compuerta con `add_conditional_edges` | `flujos/flujo_s2.py`: analizar → diseñar → planificar → construir |
| `s2_flujos/enrutamiento.py` | Enrutamiento | `add_conditional_edges(nodo, función, {valor: destino})`; clasificador con `Literal` | `despues_de_analizar()`; `filtrar_historia` en `flujo_s4.py` |
| `s2_flujos/paralelizacion.py` | Paralelización | Dos aristas desde el mismo nodo, unión con `add_edge([a, b], "unir")` y un reductor | `flujos/flujo_s3.py`: desplegar ∥ automatizar |
| `s2_flujos/orquestador.py` | Orquestador y trabajadores | `Send("trabajador", datos)` en una lista: el número de trabajadores lo decide el modelo | `agentes/triage.py`; subagentes de Claude Code |
| `s2_flujos/humano.py` | El humano en el flujo | `interrupt()` muestra qué se hará, `InMemorySaver` guarda el estado y `Command(resume=…)` reanuda; el código decide qué requiere aprobación | `flujo_s2.py` → `aprobar_plan` y `pedir_aclaracion` |
| `s2_flujos/evaluador.py` | Evaluador-optimizador | Un ciclo evaluar → generar con tope; el juez es pytest en un subproceso | `construir` → `verificar` → `construir` |

## Sesión 3 · Topologías multi-agente (LangGraph)

| Archivo | Topología | Lo que la distingue en el código | En tu fábrica |
| --- | --- | --- | --- |
| `s3_topologias/supervisor.py` | Supervisor | El supervisor devuelve `Command(goto=…)`; cada especialista solo tiene `add_edge(agente, "supervisor")` | `flujo_s4.py` (supervisor en código); equipo con el Agent SDK |
| `s3_topologias/jerarquica.py` | Jerárquica | Un grafo compilado como nodo de otro: `add_node("calidad", equipo_calidad)` | Tu flujo delega en Claude Code, que tiene sus subagentes |
| `s3_topologias/traspasos.py` | Traspasos | Herramientas `transferir_a_*`; el nodo las traduce en `Command(goto=…)`; una sola conversación | Alternativa al grafo para analista → diseñador → desarrollador |
| `s3_topologias/red.py` | Red | Todos los nodos devuelven `Command[Literal[todos]]`; ninguna arista fija; tope de turnos | No se usa: muestra por qué |
| `s3_topologias/pizarra.py` | Pizarra | Tabla `REQUIERE → ESCRIBE` y un controlador en código que elige quién puede trabajar | El estado de LangGraph y la carpeta `salida/HU-xx/` |

### MCP · conectar agentes con herramientas

MCP (Model Context Protocol) no es una topología: es el **cable** entre un agente y sus herramientas. El servidor publica herramientas; cualquier agente que hable MCP las descubre y las usa sin importar su código. El paquete `mcp` ya viene instalado con `claude-agent-sdk`.

| Archivo | Papel | Lo que lo distingue en el código | En tu fábrica |
| --- | --- | --- | --- |
| `s3_topologias/mcp_directorio.py` | Servidor | `@servidor.tool()` sobre funciones con tipos y docstring; FastMCP genera el esquema y lo sirve por stdio | Datos de la empresa para los agentes 3, 4 y 5 sin tocar su código |
| `s3_topologias/mcp_cliente.py` | Cliente | El bucle de `react.py` con `list_tools()` para descubrir y `call_tool()` para actuar; ningún esquema escrito a mano | Lo que Claude Code hace por ti con `claude mcp add` |

Para verlo con Claude Code, con el `.venv` activado y desde la raíz:

```bash
claude mcp add directorio -- python -m ejemplos.s3_topologias.mcp_directorio
claude mcp list          # directorio … ✔ Connected
claude                   # pregunta: «¿quién es el empleado activo más antiguo de Tecnología?»
claude mcp remove directorio
```

El registro queda en tu configuración local (alcance `local`), no en el repo: así los agentes de la fábrica no lo cargan por accidente.

## Ideas para la clase

- **Compara de dos en dos.** `paralelizacion.py` contra `orquestador.py` (ramas fijas contra `Send`); `supervisor.py` contra `red.py` (quién decide el siguiente paso); `reflexion.py` contra `evaluador.py` (quién juzga); `react.py` contra `mcp_cliente.py` (de dónde salen las herramientas).
- **Dibuja el grafo** de cualquier ejemplo de LangGraph y pégalo en un visor de Mermaid:
  ```bash
  python -c "from ejemplos.s2_flujos.enrutamiento import app; print(app.get_graph().draw_mermaid())"
  ```
- **Rómpelo a propósito.** Quita el reductor en `paralelizacion.py` y lee el error; pon `MAX_TURNOS = 30` en `red.py` y mira el costo.
- **Ancla al lab.** Después de cada ejemplo, abre el archivo de la columna «En tu fábrica» y busca la misma línea.
