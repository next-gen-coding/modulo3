"""Topología: Jerárquica. Supervisores de supervisores: cada equipo es un grafo completo con su propio líder.

Tres niveles, y en los dos de arriba decide un agente:
  - el DIRECTOR (agente) elige qué equipo trabaja,
  - cada LÍDER de equipo (agente) elige qué miembro de su equipo trabaja y cuándo terminó,
  - los MIEMBROS hacen el trabajo y le reportan solo a su líder.
Lo que distingue a la topología en el código: un grafo COMPILADO se agrega como nodo de otro grafo
(`grafo.add_node("calidad", equipo_calidad)`). El director solo ve el resumen de cada equipo,
no el trabajo interno: así cada nivel mantiene su contexto pequeño.

Uso:  python -m ejemplos.s3_topologias.jerarquica                  (guarda el grafo y lo ejecuta)
      python -m ejemplos.s3_topologias.jerarquica --grafo          (solo guarda el grafo, sin llamar al modelo)
      python -m ejemplos.s3_topologias.jerarquica --grafo --abrir  (además lo abre en el navegador)
El grafo queda en ejemplos/salidas/grafo_jerarquica.html, con cada equipo dibujado por dentro.
En tu fábrica:  tu flujo delega en Claude Code, y Claude Code puede lanzar sus propios subagentes.
"""
from typing import Literal, TypedDict

from langgraph.graph import END, START, StateGraph
from langgraph.types import Command
from pydantic import BaseModel

from ejemplos.comun import guardar_grafo, historia, modelo, paso, titulo

MAX_VUELTAS = 4   # límite por equipo: cuántas veces puede decidir su líder


class Estado(TypedDict, total=False):
    historia: str
    detalle: str              # trabajo interno del equipo activo (el director no lo lee)
    vueltas: int              # decisiones del líder del equipo activo
    informes: dict[str, str]  # lo único que sube al director: un resumen por equipo


class Eleccion(BaseModel):
    siguiente: str            # un miembro del equipo, o "FIN"
    motivo: str


# ── Nivel 3 · los miembros: hacen el trabajo y le reportan a su líder ──────────────────────────
#Similar a supervisor, en vez de hacer una función por cada miembro del equipo, crea el nodo y lo regresa
#El lider decide a quien llamar, y que tarea les toca hacer
def miembro(nombre: str, tarea: str):
    def nodo(s: Estado) -> Estado:
        texto = modelo(600).invoke(f"{tarea}\n\nHistoria:\n{s['historia']}\n\n{s.get('detalle', '')}").text
        paso(f"    {nombre}", texto, 120)
        return {"detalle": s.get("detalle", "") + f"\n## {nombre}\n{texto}"}
    return nodo


# ── Nivel 2 · el líder de cada equipo: un agente que decide dentro de su equipo ────────────────
def lider(equipo: str, miembros: dict[str, str]):
    def nodo(s: Estado) -> Command:
        hechos = [m for m in miembros if f"## {m}\n" in s.get("detalle", "")]
        if s.get("vueltas", 0) < MAX_VUELTAS:
            e = modelo().with_structured_output(Eleccion).invoke(
                f"Lideras el equipo de {equipo}: {list(miembros)}.\nHistoria:\n{s['historia']}\n\n"
                f"Ya entregaron: {hechos or 'nadie'}.\nDecide quién sigue (cada uno trabaja una vez, "
                "en un orden que tenga sentido) o FIN si el equipo ya terminó.")
            if e.siguiente in miembros:
                paso(f"  líder de {equipo}", f"→ {e.siguiente} · {e.motivo}")
                return Command(goto=e.siguiente, update={"vueltas": s.get("vueltas", 0) + 1})
        # FIN (o límite alcanzado): el líder resume y le regresa el control al director
        resumen = modelo(300).invoke(f"Resume en 3 viñetas para el director:\n{s.get('detalle', '')}").text
        paso(f"  líder de {equipo}", f"→ informa al director · {resumen}", 160)
        return Command(goto=END, update={"informes": {**s.get("informes", {}), equipo: resumen},
                                         "detalle": "", "vueltas": 0})
    return nodo

#Un equipo en realidad, es un grafo de agentes especializados en un área específica
#El lider NO termina la ejecución del grafo siempre eregresa al lider ! 
def equipo(nombre: str, miembros: dict[str, str]):
    """Un equipo es un grafo completo: un supervisor (el líder) con sus miembros."""
    g = StateGraph(Estado)
    g.add_node("lider", lider(nombre, miembros),
               destinations=(*miembros, END))     # ← a dónde puede mandar el líder (para dibujarlo)
    for m, tarea in miembros.items():
        g.add_node(m, miembro(m, tarea))
        g.add_edge(m, "lider")                     # ← cada miembro le reporta solo a su líder
    g.add_edge(START, "lider")
    return g.compile()

#Subgrafo que representa al equipo de calidad
equipo_calidad = equipo("calidad", {"analista": "Escribe 3 criterios Gherkin breves.",
                                    "tester": "Escribe un caso de prueba por criterio."})
#Subgrafo que representa al equipo de desarrollo
equipo_desarrollo = equipo("desarrollo", {"backend": "Propón el endpoint FastAPI en 8 líneas.",
                                          "frontend": "Propón el formulario React en 8 líneas."})


# ── Nivel 1 · el director: un agente que decide qué equipo trabaja ─────────────────────────────
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
    import sys

    titulo("Jerárquica · el grafo")
    guardar_grafo(app, "jerarquica", abrir="--abrir" in sys.argv, xray=True)   # xray: dibuja cada equipo por dentro
    if "--grafo" in sys.argv:          # solo el dibujo, sin llamar al modelo
        sys.exit()

    titulo("Jerárquica")
    final = app.invoke({"historia": historia("HU-01")})
    for equipo_, informe in final["informes"].items():
        print(f"\nInforme de {equipo_}:\n{informe}")
