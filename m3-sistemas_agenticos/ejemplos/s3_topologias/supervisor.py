"""Topología: Supervisor. Un agente central decide quién trabaja; todos le reportan a él.

Lo que distingue a la topología en el código:
  - el supervisor devuelve `Command(goto=...)`: él elige al siguiente agente en cada vuelta,
  - cada especialista tiene una sola arista: de regreso al supervisor (`add_edge(agente, "supervisor")`).
Los especialistas nunca se hablan entre sí.

Uso:  python -m ejemplos.s3_topologias.supervisor
En tu fábrica:  flujos/flujo_s4.py es un supervisor determinista (escrito en código);
                el ejercicio con el Agent SDK usa un supervisor que razona.
"""
from typing import Literal, TypedDict

from langgraph.graph import START, StateGraph
from langgraph.types import Command
from pydantic import BaseModel

from ejemplos.comun import historia, modelo, paso, titulo

MAX_VUELTAS = 6
AGENTES = {
    "analista": "Escribe 3 criterios de aceptación breves en Gherkin para la historia.",
    "tester": "Escribe un caso de prueba por criterio (id, pasos, resultado esperado).",
    "desarrollador": "Propón el endpoint FastAPI y el modelo de datos, en pseudocódigo de 10 líneas.",
}


class Decision(BaseModel):
    siguiente: Literal["analista", "tester", "desarrollador", "FIN"]
    motivo: str


class Estado(TypedDict, total=False):
    historia: str
    trabajo: dict[str, str]   # lo que entregó cada especialista
    vueltas: int


def supervisor(s: Estado) -> Command[Literal["analista", "tester", "desarrollador", "__end__"]]:
    hecho = s.get("trabajo", {})
    if s.get("vueltas", 0) >= MAX_VUELTAS:
        return Command(goto="__end__")
    d = modelo().with_structured_output(Decision).invoke(
        f"Eres el supervisor de un equipo: {list(AGENTES)}.\nHistoria:\n{s['historia']}\n\n"
        f"Ya entregaron: {list(hecho) or 'nadie'}.\nDecide quién sigue (cada uno trabaja una vez, "
        "en un orden que tenga sentido) o FIN si ya está todo.")
    paso("supervisor", f"→ {d.siguiente} · {d.motivo}")
    return Command(goto="__end__" if d.siguiente == "FIN" else d.siguiente,   # ← el supervisor enruta
                   update={"vueltas": s.get("vueltas", 0) + 1})


def especialista(nombre: str):
    def nodo(s: Estado) -> Estado:
        previo = "\n\n".join(f"## {k}\n{v}" for k, v in s.get("trabajo", {}).items())
        texto = modelo(800).invoke(f"{AGENTES[nombre]}\n\nHistoria:\n{s['historia']}\n\n{previo}").text
        paso(nombre, texto, 160)
        return {"trabajo": {**s.get("trabajo", {}), nombre: texto}}
    return nodo


grafo = StateGraph(Estado)
grafo.add_node("supervisor", supervisor)
for nombre in AGENTES:
    grafo.add_node(nombre, especialista(nombre))
    grafo.add_edge(nombre, "supervisor")          # ← la única salida de un especialista
grafo.add_edge(START, "supervisor")
app = grafo.compile()

if __name__ == "__main__":
    titulo("Supervisor")
    app.invoke({"historia": historia("HU-01")})
