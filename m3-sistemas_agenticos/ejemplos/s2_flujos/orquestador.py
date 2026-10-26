"""Patrón de flujo: Orquestador y trabajadores. Un modelo decide en el momento cuántas subtareas hay.

Lo que distingue al patrón en el código: `Send`. El orquestador devuelve una LISTA de
Send("trabajador", datos), una por subtarea; LangGraph lanza tantos trabajadores como elementos tenga.
Compáralo con paralelizacion.py: allí las ramas están escritas en el grafo; aquí no se conocen de antemano.

Uso:  python -m ejemplos.s2_flujos.orquestador
En tu fábrica:  agentes/triage.py decide a quién mandar cada falla; Claude Code lanza subagentes (Task)
"""
import operator
from typing import Annotated, TypedDict

from langgraph.graph import END, START, StateGraph
from langgraph.types import Send
from pydantic import BaseModel

from ejemplos.comun import historia, modelo, paso, titulo, guardar_grafo

#Subtareas: el contrato con el orquestador
#Es una clase Pydantic con un solo campo: una lista de textos, donde cada texto es una subtarea. 
# Por ejemplo:
class Subtareas(BaseModel):
    subtareas: list[str]  # entre 2 y 5, cada una independiente de las demás (que se define en el prompt)
    #  subtareas: list[str] = Field(min_length=2, max_length=5) # Si el numero de subtareas fuera explicito

#El "Expediente" del grafo.
class Estado(TypedDict, total=False):
    historia: str
    subtareas: list[str]
    resultados: Annotated[list[str], operator.add]
    sintesis: str

#El orquestador es salidas estructuradas que producen una lista de encargos. 
# Su prompt carga con dos responsabilidades críticas: 
# limitar cuántas subtareas hay y garantizar que sean independientes. 
# El orquestador decide, pero no reparte.
def orquestador(s: Estado) -> Estado:
    #Salida estructurada: Subtareas, que es un Pydantic con un solo campo: una lista de subtareas.
    plan = modelo().with_structured_output(Subtareas).invoke(
        "Divide la implementación de esta historia en 2 a 5 subtareas independientes " #independientes => que se hagan en paralelo
        "(por ejemplo: modelo de datos, endpoint, pantalla, pruebas). Decide tú cuántas:\n" + s["historia"]) #El modelo decide cuantas subtareas. 
    paso("orquestador", f"decidió {len(plan.subtareas)} subtareas: {plan.subtareas}")
    return {"subtareas": plan.subtareas} #El orquestrador devuelva las subtareas, pero no las manda


def repartir(s: Estado) -> list[Send]:
    #Lo que hace Send, es enviar cada subtarea a un trabajador, que se ejecuta en paralelo.
    return [Send("trabajador", {"historia": s["historia"], "subtarea": t}) for t in s["subtareas"]]  # ← el patrón

#Importante observación: el trabajor NO recibe todo el "expediente" sino un "sobre" de lo que le toca hacer
def trabajador(datos: dict) -> Estado:
    texto = modelo(600).invoke(f"Historia:\n{datos['historia']}\n\nResuelve SOLO esta subtarea, "
                               f"en 5 líneas como máximo: {datos['subtarea']}").text
    paso(f"trabajador · {datos['subtarea'][:40]}", texto, 160)
    return {"resultados": [f"### {datos['subtarea']}\n{texto}"]} #regresa una hoja de resultados para integrar al "expediente" de resultados final. 


def sintetizar(s: Estado) -> Estado:
    #Integra los resultados de todos los trabajadores
    #Importante notar coherente: Los trabajadores trabajaron aislados,si hay inconsistencias
    #El modelo debe detectar y reconciliar esas inconsistencias.
    texto = modelo().invoke("Une estos resultados en un plan de implementación coherente y breve:\n\n"
                            + "\n\n".join(s["resultados"])).text
    paso("síntesis", texto, 600)
    return {"sintesis": texto}


grafo = StateGraph(Estado)
grafo.add_node("orquestador", orquestador)
grafo.add_node("trabajador", trabajador)
grafo.add_node("sintetizar", sintetizar)


grafo.add_edge(START, "orquestador")
#Cuando termine el nodo orquestador, llama a la función repartir para saber qué sigue. 
# Lo que siga solo puede ser el nodo trabajador
#Es decir, origen,funcion condicionante, destino
grafo.add_conditional_edges("orquestador", repartir, ["trabajador"])
grafo.add_edge("trabajador", "sintetizar")   # sintetizar espera a todos los trabajadores lanzados
grafo.add_edge("sintetizar", END)
app = grafo.compile()

if __name__ == "__main__":
    import sys
    titulo("Orquestador y trabajadores · el grafo")
    guardar_grafo(app, "orquestador", abrir="--abrir" in sys.argv)
    if "--grafo" in sys.argv:          # solo el dibujo, sin llamar al modelo
        sys.exit()
        
    titulo("Orquestador y trabajadores")
    app.invoke({"historia": historia("HU-03")})
