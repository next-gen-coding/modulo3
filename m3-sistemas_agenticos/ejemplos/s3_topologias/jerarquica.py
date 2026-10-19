"""Topología: Jerárquica. Supervisores de supervisores: cada equipo es un grafo completo.

Lo que distingue a la topología en el código: un grafo COMPILADO se agrega como nodo de otro grafo
(`director.add_node("calidad", equipo_calidad)`). El director solo ve el resumen de cada equipo,
no los mensajes internos: así cada nivel mantiene su contexto pequeño.

Uso:  python -m ejemplos.s3_topologias.jerarquica
En tu fábrica:  tu flujo delega en Claude Code, y Claude Code puede lanzar sus propios subagentes.
"""
from typing import Literal, TypedDict

from langgraph.graph import END, START, StateGraph
from langgraph.types import Command
from pydantic import BaseModel

from ejemplos.comun import historia, modelo, paso, titulo


class Estado(TypedDict, total=False):
    historia: str
    detalle: str          # trabajo interno de un equipo
    informes: dict[str, str]


def miembro(nombre: str, tarea: str):
    def nodo(s: Estado) -> Estado:
        texto = modelo(600).invoke(f"{tarea}\n\nHistoria:\n{s['historia']}\n\n{s.get('detalle', '')}").text
        paso(f"  {nombre}", texto, 120)
        return {"detalle": s.get("detalle", "") + f"\n## {nombre}\n{texto}"}
    return nodo


def jefe(equipo: str):
    """Cada líder resume para el director: lo que sube de nivel es corto."""
    def nodo(s: Estado) -> Estado:
        resumen = modelo(300).invoke(f"Resume en 3 viñetas para el director:\n{s['detalle']}").text
        paso(f" líder de {equipo}", resumen, 160)
        return {"informes": {**s.get("informes", {}), equipo: resumen}, "detalle": ""}
    return nodo


def equipo(nombre: str, miembros: list[tuple[str, str]]):
    """Un equipo es un grafo completo: miembros en cadena y su líder al final."""
    g = StateGraph(Estado)
    anterior = START
    for m, tarea in miembros:
        g.add_node(m, miembro(m, tarea))
        g.add_edge(anterior, m)
        anterior = m
    g.add_node("lider", jefe(nombre))
    g.add_edge(anterior, "lider")
    g.add_edge("lider", END)
    return g.compile()


equipo_calidad = equipo("calidad", [("analista", "Escribe 3 criterios Gherkin breves."),
                                    ("tester", "Escribe un caso de prueba por criterio.")])
equipo_desarrollo = equipo("desarrollo", [("backend", "Propón el endpoint FastAPI en 8 líneas."),
                                          ("frontend", "Propón el formulario React en 8 líneas.")])


class Orden(BaseModel):
    siguiente: Literal["calidad", "desarrollo", "FIN"]


def director(s: Estado) -> Command[Literal["calidad", "desarrollo", "__end__"]]:
    informes = s.get("informes", {})
    if len(informes) == 2:
        return Command(goto="__end__")
    o = modelo().with_structured_output(Orden).invoke(
        f"Diriges los equipos 'calidad' y 'desarrollo'. Ya informaron: {list(informes) or 'ninguno'}. "
        "¿Qué equipo trabaja ahora? (calidad define qué se espera antes de que desarrollo construya)")
    paso("director", f"→ equipo {o.siguiente}")
    return Command(goto="__end__" if o.siguiente == "FIN" else o.siguiente)


grafo = StateGraph(Estado)
grafo.add_node("director", director)
grafo.add_node("calidad", equipo_calidad)          # ← un grafo dentro de otro grafo
grafo.add_node("desarrollo", equipo_desarrollo)
grafo.add_edge(START, "director")
grafo.add_edge("calidad", "director")
grafo.add_edge("desarrollo", "director")
app = grafo.compile()

if __name__ == "__main__":
    titulo("Jerárquica")
    final = app.invoke({"historia": historia("HU-01")})
    for equipo_, informe in final["informes"].items():
        print(f"\nInforme de {equipo_}:\n{informe}")
