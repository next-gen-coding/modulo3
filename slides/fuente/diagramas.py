"""Diagramas de cada patrón con las piezas del sistema Tec Editorial (cajas con filete, flechas, ciclos, árboles)."""
from m3lib import arbol, caja, flecha, flujo, pila, ramas, rejilla


def ciclo(nodos: list[tuple[str, str]], vuelta: str, margen_der: str = "9%") -> str:
    partes = []
    for k, (t, s) in enumerate(nodos):
        if k:
            partes.append(flecha())
        partes.append(f'<div class="cnode">{t}<br><small class="muted">{s}</small></div>')
    return (f'<div class="cycle diag">{"".join(partes)}</div>'
            f'<div class="vuelta" style="margin-right:{margin_der_ok(margen_der)}"></div><p class="vuelta-txt">↑ {vuelta}</p>')


def margin_der_ok(m: str) -> str:
    return m


def vuelta(texto: str, step: int | None = None) -> str:
    s = f' data-step="{step}"' if step else ""
    return f'<div{s}><div class="vuelta"></div><p class="vuelta-txt">{texto}</p></div>'


def fase(etiqueta: str, *piezas: str) -> str:
    return f'<h3 style="margin-top:.6rem">{etiqueta}</h3>' + flujo(*piezas)


D = {}

D["p-react"] = (ciclo([("Razonar", "¿qué hago?"), ("Actuar", "usa una herramienta"), ("Observar", "lee el resultado")],
                      "otra vuelta con lo observado") +
                flujo(caja("Ya puedo responder", tipo="gate"), flecha(), caja("Respuesta", tipo="centro")) +
                '<p class="muted" style="text-align:center; max-width:none; font-size:1rem">Cada vuelta es una llamada al modelo</p>')

D["p-plan"] = (fase("Fase 1 · planificar", caja("Tarea"), flecha(), caja("Planificador", "un modelo"), flecha(),
                    caja("Plan", "lista de pasos", tipo="centro"), flecha(), caja("Persona", "aprueba", tipo="persona", step=1)) +
               fase("Fase 2 · ejecutar", caja("Paso 1", step=2), flecha(step=2), caja("Paso 2", step=2), flecha(step=2),
                    caja("Paso 3", step=2), flecha(step=2), caja("Resultado", tipo="centro", step=2)) +
               vuelta("si un paso falla, se vuelve a planificar", 3))

D["p-reflexion"] = ciclo([("Generar", "el borrador"), ("Criticar", "contra criterios"), ("Corregir", "con la crítica")],
                         "la crítica entra al siguiente intento · máximo 3 · si se agota, decide una persona")

D["p-salidas"] = (flujo(caja("Modelo", "propone"), flecha(), caja("Contrato", "Pydantic", tipo="centro"), flecha(),
                        caja("1 · Esquema", "tipos y campos", tipo="gate", step=1)) +
                  flujo(flecha("→", step=2), caja("2 · Reglas", "de negocio", tipo="gate", step=2), flecha(step=3),
                        caja("3 · Pruebas", "ejecutables", tipo="gate", step=3), flecha(step=3), caja("Siguiente agente", tipo="centro", step=3)) +
                  vuelta("falla: el problema regresa al modelo · máximo 2 intentos · después decide una persona", 4))

D["p-encadenamiento"] = (flujo(caja("Historia"), flecha(), caja("Analista", "criterios"), flecha(), caja("validar", tipo="gate", step=1)) +
                         flujo(flecha(step=2), caja("Diseñador", "casos", step=2), flecha(step=2), caja("validar", tipo="gate", step=2),
                               flecha(step=3), caja("Desarrollador", "código", step=3)) +
                         vuelta("si una compuerta falla, no avanza: regresa al mismo paso con el error", 4) +
                         '<p class="muted" style="text-align:center; max-width:none; font-size:1rem">Cada paso es pequeño, comprobable y fácil de depurar</p>')

D["p-enrutamiento"] = ramas(caja("Historia", "HU-xx"), caja("Clasificador", "¿de qué tipo es?", tipo="centro"),
                            [caja("Diseñar casos", "historia clara"), caja("Pedir aclaración", "historia ambigua", tipo="persona"),
                             caja("Bloquear", "historia sospechosa", tipo="punteada")], step=1) + \
    '<p class="muted" style="text-align:center; max-width:none; font-size:1rem">Solo se ejecuta una rama</p>'

D["p-paralelizacion"] = (flujo(caja("Verificar", "la app compila"), flecha(),
                               pila(caja("Despliegue", "agente 4 · Docker", tipo="claude"), caja("Automatizador", "agente 5 · Playwright", tipo="claude"), step=1),
                               flecha(step=2), caja("Listo", "unión", tipo="centro", step=2)) +
                         '<p class="muted" style="text-align:center; max-width:none; font-size:1rem">al mismo tiempo · '
                         '<span class="cmd">add_edge(["desplegar", "automatizar"], "listo")</span></p>')

D["p-orquestador"] = (arbol(caja("Orquestador", "divide la tarea", tipo="centro"),
                            [caja("Trabajador", "backend"), caja("Trabajador", "frontend"), caja("… N", "los que hagan falta", tipo="punteada")], step=1) +
                      '<div class="arbol" data-step="2"><div class="baja">↓</div><div class="raiz">' +
                      caja("Síntesis", "une los resultados", tipo="centro") + "</div></div>" +
                      '<p class="muted" style="text-align:center; max-width:none; font-size:1rem">El orquestador decide en el momento cuántos y cuáles</p>')

D["p-evaluador"] = (ciclo([("Generador", "desarrollador"), ("Evaluador", "pytest · npm build"), ("Aprobado", "sigue el flujo")],
                          "falla: el error vuelve como contexto", "42%") +
                    '<p class="muted" style="text-align:center; max-width:none; font-size:1rem">Máximo 2 intentos; después decide una persona. '
                    'El juez es independiente: otro agente o una herramienta.</p>')

D["p-humano"] = ramas(caja("Agente", "propone acciones"), caja("Código", "clasifica el riesgo", tipo="centro"),
                      [caja("Se ejecuta solo", "bajo riesgo · supervisa"), caja("interrupt: aprueba", "irreversible · decide", tipo="persona"),
                       caja("Escalar a persona", "no se puede clasificar", tipo="punteada")], step=1) + \
    '<p class="muted" style="text-align:center; max-width:none; font-size:1rem">La persona ve qué se hará, sobre qué y con qué evidencia</p>'

D["t-supervisor"] = (arbol(caja("Supervisor", "decide quién sigue", tipo="centro"), [caja("Analista"), caja("Tester"), caja("Desarrollador")], sube=True) +
                     '<p class="muted" style="text-align:center; max-width:none; font-size:1rem">Los agentes no hablan entre sí: todo pasa por el supervisor</p>')

D["t-jerarquica"] = (arbol(caja("Director", tipo="centro"),
                           [arbol(caja("Calidad", "líder"), [caja("Analista"), caja("Tester")]),
                            arbol(caja("Desarrollo", "líder"), [caja("Backend"), caja("Frontend")])]) +
                     '<p class="muted" style="text-align:center; max-width:none; font-size:1rem">Cada nivel solo ve lo suyo</p>')

D["t-traspasos"] = ('<div class="panel" style="text-align:center"><p style="max-width:none">Una sola conversación: quien la tiene, responde</p></div>' +
                    flujo(caja("Analista", "terminó"), flecha("→ pasa →"), caja("Diseñador", "tiene el control", tipo="centro"),
                          flecha("→ pasará →"), caja("Desarrollador", "en espera", tipo="punteada")) +
                    '<p class="muted" style="text-align:center; max-width:none; font-size:1rem"><span class="cmd">transferir_a(agente, motivo)</span> · '
                    'sin supervisor: el control viaja con la conversación</p>')

D["t-red"] = (rejilla([caja("Analista"), flecha("↔"), caja("Tester"), "", "",
                       flecha("↕"), '<span class="farrow" style="font-size:1rem">todos con todos</span>', flecha("↕"), "", "",
                       caja("Desarrollador"), flecha("↔"), caja("Revisor"), "", ""]) +
              '<p class="muted" style="text-align:center; max-width:none; font-size:1rem">4 agentes = 6 canales · 10 agentes = 45 canales</p>')

D["t-pizarra"] = ('<div class="arbol diag" style="--n:4"><div class="hijos">' +
                  "".join(caja(x) for x in ("Analista", "Diseñador", "Desarrollador", "Automatizador")) +
                  '</div><div class="hijos">' + '<div class="baja">↕</div>' * 4 + '</div><div class="raiz" style="display:block">' +
                  caja("Pizarra", "criterios · casos · plan · errores", tipo="centro") + "</div></div>" +
                  '<p class="muted" style="text-align:center; max-width:none; font-size:1rem">Los agentes no se hablan: leen y escriben en la pizarra</p>')

D["p-mcp"] = ('<div class="ramas sin-cierre diag">' +
              pila(caja("Claude Code", "claude mcp add"), caja("mcp_cliente.py", "tu agente", tipo="centro"), caja("Otro agente", "cualquier cliente", tipo="punteada")) +
              flecha("↔") + caja("Servidor MCP", "directorio-empleados", "stdio", tipo="claude") + "<span></span>" +
              pila(caja("Datos", "empleados"), caja("1 · list_tools()", "descubre"), caja("2 · call_tool()", "actúa")) + "</div>" +
              '<p class="muted" style="text-align:center; max-width:none; font-size:1rem">Una herramienta, muchos agentes: nadie importa el código del otro</p>')
