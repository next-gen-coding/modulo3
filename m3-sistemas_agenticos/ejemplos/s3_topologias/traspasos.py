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

from ejemplos.comun import EMPLEADOS, modelo, paso, titulo, guardar_grafo

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

     
def agente(nombre: str): #nombre: recepcion, alta , directorio
    """
    Ejemplo, si llega a la recepción:
    sistema      = "Eres recepción de RR. HH. No resuelves nada: transfiere al agente correcto."
    herramientas = [transferir_a_altas, transferir_a_directorio]
    """   
    #Que agente te está atendiendo y cuales son las herramientas para utilizar (a donde envio mi respuesta)
    sistema, herramientas = AGENTES[nombre]
    #Son las opciones para el cliente: o me atiende recepción, altas o directorio
    destinos = Literal["recepcion", "altas", "directorio", "__end__"]
    def nodo(s: Estado) -> Command[destinos]:
        # 1. Le das al agente su formulario y le muestras toda la conversación
        # Cada herramienta dada en bind_tools es una casilla, para que sea solo esa! 
        resp: AIMessage = modelo().bind_tools(herramientas).invoke([SystemMessage(sistema), *s["mensajes"]])
         # 2. ¿Llenó el formulario? (y no se ha rebotado demasiadas veces)
        if resp.tool_calls and s.get("traspasos", 0) < MAX_TRASPASOS:        # ← el traspaso
           # 3. tomas el formulario 
            llamada = resp.tool_calls[0]
            # 4. lees la casilla, ejemplo: "altas"
            destino = llamada["name"].removeprefix("transferir_a_")
            paso(nombre, f"traspasa a {destino}: {llamada['args'].get('motivo', '')}")
            # 5. engrapas una nota al expediente
            nota = HumanMessage(f"[Traspaso: {nombre} pasa la conversación a {destino}. "
                                f"Motivo: {llamada['args'].get('motivo', '')}]")
            # 6. lo llevas con el destino que le corresponde, ejemplo: "altas"
            return Command(goto=destino, update={"mensajes": [nota], "traspasos": s.get("traspasos", 0) + 1})
        paso(nombre, resp.text)
        # 7. No llenó el formulario: contestó él mismo, y se acabó. Es decir llegó al agente destino
        return Command(goto="__end__", update={"mensajes": [AIMessage(resp.text)]})  # responde y termina
    return nodo


grafo = StateGraph(Estado)
for nombre in AGENTES:
    grafo.add_node(nombre, agente(nombre))
grafo.add_edge(START, "recepcion")
app = grafo.compile()

if __name__ == "__main__":
    import sys

    titulo("Traspasos · el grafo")
    guardar_grafo(app, "traspasos", abrir="--abrir" in sys.argv, xray=True)   # xray: dibuja cada equipo por dentro
    if "--grafo" in sys.argv:          # solo el dibujo, sin llamar al modelo
        sys.exit()


    for pregunta in ["Quiero dar de alta a Ana López como analista en Finanzas, ¿qué necesito?",
                     "¿Quién es el empleado más antiguo de Tecnología que sigue activo?"]:
        titulo(f"Traspasos · «{pregunta}»")
        app.invoke({"mensajes": [HumanMessage(pregunta)]})
