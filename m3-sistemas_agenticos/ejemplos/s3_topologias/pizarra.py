"""Topología: Pizarra (blackboard). Los agentes no se hablan: leen y escriben en un estado compartido.

Lo que distingue a la topología en el código:
  - cada agente declara QUÉ necesita leer y QUÉ campo escribe (REQUIERE / ESCRIBE),
  - un controlador en código mira la pizarra y activa al primer agente que ya puede trabajar,
  - nadie llama a nadie: agregar un agente nuevo es agregar una línea a la tabla.

Uso:  python -m ejemplos.s3_topologias.pizarra
En tu fábrica:  el estado de LangGraph es tu pizarra, y la carpeta salida/HU-xx/ es una pizarra en disco.
"""
from typing import TypedDict

from langgraph.graph import END, START, StateGraph

from ejemplos.comun import historia, modelo, paso, titulo


class Pizarra(TypedDict, total=False):
    historia: str
    criterios: str
    casos: str
    endpoint: str
    pantalla: str


# agente: (lo que necesita leer, el campo que escribe, su tarea) — el orden NO importa
AGENTES = {
    "pantalla": (["criterios", "endpoint"], "pantalla", "Describe el formulario React en 6 líneas."),
    "disenador": (["criterios"], "casos", "Escribe un caso de prueba por criterio."),
    "analista": (["historia"], "criterios", "Escribe 3 criterios Gherkin breves."),
    "backend": (["criterios"], "endpoint", "Propón el endpoint FastAPI en 6 líneas."),
}


def listo_para(p: Pizarra) -> list[str]:
    """Agentes cuyos insumos ya están en la pizarra y cuyo campo sigue vacío."""
    return [a for a, (lee, escribe, _) in AGENTES.items() if all(p.get(c) for c in lee) and not p.get(escribe)]


def controlador(p: Pizarra) -> Pizarra:
    paso("pizarra", f"tiene {[c for c in Pizarra.__annotations__ if p.get(c)]} · pueden trabajar: {listo_para(p)}")
    return {}


def elegir(p: Pizarra) -> str:
    candidatos = listo_para(p)
    return candidatos[0] if candidatos else END        # ← el controlador decide mirando la pizarra


def agente(nombre: str):
    lee, escribe, tarea = AGENTES[nombre]

    def nodo(p: Pizarra) -> Pizarra:
        insumos = "\n\n".join(f"## {c}\n{p[c]}" for c in lee)
        texto = modelo(600).invoke(f"{tarea}\n\n{insumos}").text
        paso(f"{nombre} escribe '{escribe}'", texto, 140)
        return {escribe: texto}                         # ← solo escribe SU campo
    return nodo


grafo = StateGraph(Pizarra)
grafo.add_node("controlador", controlador)
for nombre in AGENTES:
    grafo.add_node(nombre, agente(nombre))
    grafo.add_edge(nombre, "controlador")               # todos regresan a la pizarra
grafo.add_edge(START, "controlador")
grafo.add_conditional_edges("controlador", elegir, [*AGENTES, END])
app = grafo.compile()

if __name__ == "__main__":
    titulo("Pizarra")
    app.invoke({"historia": historia("HU-01")})
