"""Topología: Red (swarm). Cualquier agente puede pasarle el trabajo a cualquier otro.

Lo que distingue a la topología en el código: TODOS los nodos devuelven
`Command[Literal[<todos los demás>]]` y no hay ninguna arista fija salvo la de entrada.
El flujo emerge de las decisiones de los agentes; por eso el tope de turnos es obligatorio.
Compáralo con supervisor.py: allí solo el supervisor decide; aquí decide cada uno.

Uso:  python -m ejemplos.s3_topologias.red
En tu fábrica:  no la usamos: con pasos conocidos, un grafo fijo es más predecible y más barato.
"""
from typing import Literal, TypedDict

from langgraph.graph import START, StateGraph
from langgraph.types import Command
from pydantic import BaseModel

from ejemplos.comun import historia, modelo, paso, titulo, guardar_grafo

MAX_TURNOS = 6
ROLES = {
    "analista": "aclaras la historia y escribes criterios de aceptación",
    "tester": "buscas huecos en los criterios y propones casos de prueba",
    "desarrollador": "propones cómo implementarlo (endpoint y modelo de datos)",
    "revisor": "revisas todo el trabajo y decides si está listo",
}
Destino = Literal["analista", "tester", "desarrollador", "revisor", "__end__"]


class Turno(BaseModel):
    aporte: str                                                             # máximo 4 líneas
    siguiente: Literal["analista", "tester", "desarrollador", "revisor", "FIN"]
    motivo: str


class Estado(TypedDict, total=False):
    historia: str
    notas: list[str]
    turnos: int

#Como en los ejemplos anteriores el nombre del nodo al que puede irse
def par(nombre: str):
    def nodo(s: Estado) -> Command[Destino]:
        turnos = s.get("turnos", 0) + 1
        #Aporta y decide a quien enviarlo de todos los pares
        t = modelo().with_structured_output(Turno).invoke(
            f"Eres el {nombre}: {ROLES[nombre]}. Equipo: {list(ROLES)}.\nHistoria:\n{s['historia']}\n\n"
            f"Notas del equipo hasta ahora:\n" + "\n".join(s.get("notas", [])) +
            "\n\nAporta algo nuevo (máximo 4 líneas) y elige a quién pasar el trabajo, o FIN si está listo.")
        paso(f"{nombre} · turno {turnos}", f"{t.aporte}  → {t.siguiente} ({t.motivo})", 220)
        #Asigna fin, o es el que sigue, o los turnos ya fueron topados
        fin = t.siguiente == "FIN" or turnos >= MAX_TURNOS                   # ← tope obligatorio
        return Command(goto="__end__" if fin else t.siguiente,               # ← cualquiera → cualquiera
                       update={"notas": s.get("notas", []) + [f"{nombre}: {t.aporte}"], "turnos": turnos})
    return nodo


grafo = StateGraph(Estado)
for nombre in ROLES:
    grafo.add_node(nombre, par(nombre))
grafo.add_edge(START, "analista")   # la única arista fija
app = grafo.compile()

if __name__ == "__main__":
    import sys
    
    titulo("Red · el grafo")
    guardar_grafo(app, "red", abrir="--abrir" in sys.argv, xray=True)   # xray: dibuja cada equipo por dentro
    if "--grafo" in sys.argv:          # solo el dibujo, sin llamar al modelo
            sys.exit()
    
    titulo("Red")
    final = app.invoke({"historia": historia("HU-03")})
    print(f"\nTurnos usados: {final['turnos']} de {MAX_TURNOS}")
