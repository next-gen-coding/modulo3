"""Topología: Traspasos (handoffs). No hay supervisor: el agente activo pasa el control con una herramienta.

Lo que distingue a la topología en el código:
  - cada agente tiene herramientas `transferir_a_<agente>`; llamarlas ES decidir quién sigue,
  - el nodo traduce esa llamada en `Command(goto=...)`,
  - todos comparten UNA conversación (`mensajes`), que viaja con el control.

Uso:  python -m ejemplos.s3_topologias.traspasos
En tu fábrica:  analista → diseñador → desarrollador podrían ser traspasos; usamos el grafo para fijar el orden.
"""
from typing import Annotated, Literal, TypedDict

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_core.tools import tool
from langgraph.graph import START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.types import Command

from ejemplos.comun import EMPLEADOS, modelo, paso, titulo

MAX_TRASPASOS = 4


@tool
def transferir_a_altas(motivo: str) -> str:
    """Pasa la conversación al agente de altas y bajas de empleados. Ejemplo: motivo='quiere registrar a alguien'."""
    return motivo


@tool
def transferir_a_directorio(motivo: str) -> str:
    """Pasa la conversación al agente que consulta el directorio de empleados. Ejemplo: motivo='busca a una persona'."""
    return motivo


@tool
def transferir_a_recepcion(motivo: str) -> str:
    """Regresa la conversación a recepción cuando el tema no es tuyo. Ejemplo: motivo='pregunta por otro tema'."""
    return motivo


AGENTES = {
    "recepcion": ("Eres recepción de RR. HH. No resuelves nada: transfiere al agente correcto.",
                  [transferir_a_altas, transferir_a_directorio]),
    "altas": ("Atiendes altas y bajas. Explica qué datos se necesitan para registrar (reglas: correo "
              "@empresa.com, departamento válido, fecha no futura). Si piden otra cosa, transfiere.",
              [transferir_a_directorio, transferir_a_recepcion]),
    "directorio": (f"Consultas el directorio. Datos: {EMPLEADOS}. Responde la consulta; si piden otra "
                   "cosa, transfiere.", [transferir_a_altas, transferir_a_recepcion]),
}


class Estado(TypedDict, total=False):
    mensajes: Annotated[list, add_messages]   # ← una sola conversación para todos
    traspasos: int


def agente(nombre: str):
    sistema, herramientas = AGENTES[nombre]
    destinos = Literal["recepcion", "altas", "directorio", "__end__"]

    def nodo(s: Estado) -> Command[destinos]:
        resp: AIMessage = modelo().bind_tools(herramientas).invoke([SystemMessage(sistema), *s["mensajes"]])
        if resp.tool_calls and s.get("traspasos", 0) < MAX_TRASPASOS:        # ← el traspaso
            llamada = resp.tool_calls[0]
            destino = llamada["name"].removeprefix("transferir_a_")
            paso(nombre, f"traspasa a {destino}: {llamada['args'].get('motivo', '')}")
            # La nota del traspaso entra a la conversación compartida; va como turno de usuario
            # para que la conversación nunca termine en un mensaje del asistente.
            nota = HumanMessage(f"[Traspaso: {nombre} pasa la conversación a {destino}. "
                                f"Motivo: {llamada['args'].get('motivo', '')}]")
            return Command(goto=destino, update={"mensajes": [nota], "traspasos": s.get("traspasos", 0) + 1})
        paso(nombre, resp.text)
        return Command(goto="__end__", update={"mensajes": [AIMessage(resp.text)]})  # responde y termina
    return nodo


grafo = StateGraph(Estado)
for nombre in AGENTES:
    grafo.add_node(nombre, agente(nombre))
grafo.add_edge(START, "recepcion")
app = grafo.compile()

if __name__ == "__main__":
    for pregunta in ["Quiero dar de alta a una nueva analista en Finanzas, ¿qué necesito?",
                     "¿Quién es el empleado más antiguo de Tecnología que sigue activo?"]:
        titulo(f"Traspasos · «{pregunta}»")
        app.invoke({"mensajes": [HumanMessage(pregunta)]})
