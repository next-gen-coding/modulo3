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

from ejemplos.comun import historia, modelo, paso, titulo, guardar_grafo

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
    #SI LAS VUELTAS ALCANZARON EL MAXIMO TERMINA
    if s.get("vueltas", 0) >= MAX_VUELTAS:
        return Command(goto="__end__")
    d = modelo().with_structured_output(Decision).invoke(
        #El MODELO DECIDE A QUIEN LE ASIGNA EL TRABAJO
        f"Eres el supervisor de un equipo: {list(AGENTES)}.\nHistoria:\n{s['historia']}\n\n"
        f"Ya entregaron: {list(hecho) or 'nadie'}.\nDecide quién sigue (cada uno trabaja una vez, "
        "en un orden que tenga sentido) o FIN si ya está todo.")
    paso("supervisor", f"→ {d.siguiente} · {d.motivo}")
    return Command(goto="__end__" if d.siguiente == "FIN" else d.siguiente,   # ← el supervisor enruta
                   update={"vueltas": s.get("vueltas", 0) + 1})


#En este caso, loc que recibe es el nombre del nodo ! 
#Lo que hace es crear una función que escribe un nodo que regresa
#El nombre puede ser analista, tester o desarrollador
def especialista(nombre: str):
    #Este es el nodo que se crea de forma dinámica. El crea el nodo, pero no lo ejecuta 
    #Quien lo ejecuta? El supervisor a través de un Command
    def nodo(s: Estado) -> Estado:
        previo = "\n\n".join(f"## {k}\n{v}" for k, v in s.get("trabajo", {}).items())
        texto = modelo(800).invoke(f"{AGENTES[nombre]}\n\nHistoria:\n{s['historia']}\n\n{previo}").text
        paso(nombre, texto, 160)
        return {"trabajo": {**s.get("trabajo", {}), nombre: texto}}
    return nodo

#NOTA EN VES DE ESCROBIR TRES VECES LO MISMO 
#SE CODIFICA EL ESPECIALISTA 
"""
def analista(s: Estado) -> Estado:
    previo = ...
    texto = modelo(800).invoke(f"{AGENTES['analista']}\n\nHistoria: ...").text
    return {"trabajo": {**s.get("trabajo", {}), "analista": texto}}

def tester(s: Estado) -> Estado:
    # lo mismo, cambiando 'analista' por 'tester'

def desarrollador(s: Estado) -> Estado:
    # lo mismo otra vez
"""

#NOTA

grafo = StateGraph(Estado)
grafo.add_node("supervisor", supervisor)
for nombre in AGENTES:
    grafo.add_node(nombre, especialista(nombre))
    #El especialista no puede terminar siempre regresa a su supervisor
    grafo.add_edge(nombre, "supervisor")          # ← la única salida de un especialista
grafo.add_edge(START, "supervisor")
app = grafo.compile()

if __name__ == "__main__":
    import sys
    #Guarda el grafo 
    titulo("Supervisor · el grafo")
    guardar_grafo(app, "supervisor", abrir="--abrir" in sys.argv)
    if "--grafo" in sys.argv:          # solo el dibujo, sin llamar al modelo
        sys.exit()

    #Flujo Supervisor
    titulo("Supervisor")
    app.invoke({"historia": historia("HU-01")})
