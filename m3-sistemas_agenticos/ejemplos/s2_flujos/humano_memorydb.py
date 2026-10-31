"""El humano en el flujo: el agente propone, el código clasifica el riesgo y una persona aprueba lo irreversible.

Lo que distingue al patrón en el código:
  - `interrupt(...)` pausa el grafo y le muestra a la persona EXACTAMENTE qué se va a hacer,
  - un checkpointer (`SqliteSaver`) guarda el estado en un archivo SQLite mientras la persona decide,
  - `Command(resume=...)` reanuda el flujo con su respuesta, en el mismo `thread_id`.
Tres niveles de autonomía en un mismo flujo: lo de bajo riesgo se ejecuta solo, lo irreversible
espera aprobación, y lo que el código no puede clasificar se escala a una persona.

Uso:  python -m ejemplos.s2_flujos.humano_sqlite
Requiere:  uv pip install langgraph-checkpoint-sqlite
El estado de cada thread_id queda en ejemplos/salidas/humano.sqlite.
En tu fábrica:  flujos/flujo_s2.py → aprobar_plan y pedir_aclaracion

Instrucciones para postgress: 
Installar:
langgraph-checkpoint-postgres
psycopg[binary]

Antes de correrlo:
  1. Postgres:  docker run -d --name hitl-postgres -e POSTGRES_PASSWORD=clase -p 5432:5432 postgres:16
  2. En .env:   POSTGRES_URI=postgresql://postgres:clase@localhost:5432/postgres?sslmode=disable
  3. Paquetes:  pip install langgraph-checkpoint-postgres "psycopg[binary]"
 
Uso:  python -m ejemplos.s2_flujos.humano_postgres "Dar de baja a Ana López" sol-1
      python -m ejemplos.s2_flujos.humano_postgres --continuar sol-1     (retoma una solicitud en pausa)
      python -m ejemplos.s2_flujos.humano_postgres --grafo               (solo guarda el grafo)
Para ver lo guardado:
      docker exec -it hitl-postgres psql -U postgres -c "select thread_id, checkpoint_id from checkpoints;"
"""
import os
import sys
from typing import Literal, TypedDict
import sqlite3


from dotenv import load_dotenv
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, interrupt
from pydantic import BaseModel
from psycopg import Connection

from ejemplos.comun import EMPLEADOS, RAIZ, paso, titulo, modelo, guardar_grafo

load_dotenv()

class Accion(BaseModel):
    tipo: Literal["cambiar_puesto", "dar_de_baja", "otra"]
    numero_empleado: str
    detalle: str


class Acciones(BaseModel):
    acciones: list[Accion]


class Estado(TypedDict, total=False):
    solicitud: str
    automaticas: list[dict]
    con_aprobacion: list[dict]
    bitacora: list[str]


def interpretar(s: Estado) -> Estado:
    """El agente propone acciones estructuradas; todavía no ejecuta nada."""
    a = modelo().with_structured_output(Acciones).invoke(
        f"Directorio: {EMPLEADOS}\n\nConvierte esta solicitud de RR. HH. en acciones:\n{s['solicitud']}")
    # El CÓDIGO decide el riesgo, no el modelo: dar de baja no se deshace fácilmente
    auto = [x.model_dump() for x in a.acciones if x.tipo == "cambiar_puesto"]
    riesgo = [x.model_dump() for x in a.acciones if x.tipo != "cambiar_puesto"]
    paso("agente propone", f"{len(auto)} automáticas · {len(riesgo)} requieren a una persona")
    return {"automaticas": auto, "con_aprobacion": riesgo, "bitacora": []}


def ejecutar_automaticas(s: Estado) -> Estado:
    log = [f"AUTO · {x['tipo']} {x['numero_empleado']}: {x['detalle']}" for x in s["automaticas"]]
    for linea in log:
        paso("ejecuta sin pedir permiso", linea)
    return {"bitacora": s["bitacora"] + log}


def aprobar(s: Estado) -> Estado:
    log = list(s["bitacora"])
    for x in s["con_aprobacion"]:
        empleado = next((e for e in EMPLEADOS if e["numero"] == x["numero_empleado"]), None)
        decision = interrupt({                                   # ← pausa: la persona ve qué y a quién
            "accion": x["tipo"], "empleado": empleado or "NO ENCONTRADO", "detalle": x["detalle"],
            "pregunta": "¿Apruebas? (si / no)"})
        estado = "APROBADA" if str(decision).strip().lower() == "si" else "RECHAZADA"
        log.append(f"{estado} por una persona · {x['tipo']} {x['numero_empleado']}: {x['detalle']}")
    return {"bitacora": log}


def hay_riesgo(s: Estado) -> Literal["aprobar", "__end__"]:
    return "aprobar" if s["con_aprobacion"] else END


grafo = StateGraph(Estado)
grafo.add_node("interpretar", interpretar)
grafo.add_node("ejecutar_automaticas", ejecutar_automaticas)
grafo.add_node("aprobar", aprobar)
grafo.add_edge(START, "interpretar")
grafo.add_edge("interpretar", "ejecutar_automaticas")
grafo.add_conditional_edges("ejecutar_automaticas", hay_riesgo)
grafo.add_edge("aprobar", END)
(RAIZ / "ejemplos" / "salidas").mkdir(parents=True, exist_ok=True)
#SQL Lite
#conexion = sqlite3.connect(RAIZ / "ejemplos" / "salidas" / "humano.sqlite", check_same_thread=False)
"""
Postgres DB
"""
conexion = Connection.connect(os.environ["POSTGRES_URI"], autocommit=True, prepare_threshold=0)
checkpointer = PostgresSaver(conexion)
checkpointer.setup()
app = grafo.compile(checkpointer=checkpointer)
"""
SQLITE
"""
#app = grafo.compile(checkpointer=SqliteSaver(conexion))   # ← ahora cada thread_id se guarda en SQLite
app = grafo.compile(checkpointer=checkpointer)
if __name__ == "__main__":
     #Dibujar el grafo
    import sys
    titulo("Human in the Loop (HITL) · el grafo")
    guardar_grafo(app, "HITL", abrir="--abrir" in sys.argv)
    if "--grafo" in sys.argv:          # solo el dibujo, sin llamar al modelo
        sys.exit()
       
    
    titulo("El humano en el flujo")
    config = {"configurable": {"thread_id": "solicitud-1"}}
    resultado = app.invoke({"solicitud": "Jorge Díaz (EMP-0004) pasa a ser Líder técnico. "
                                         "Además, da de baja a Luis Pérez (EMP-0002) a partir de hoy."}, config)
    while "__interrupt__" in resultado:                              # el flujo está en pausa
        pregunta = resultado["__interrupt__"][0].value
        print(f"\n⏸  {pregunta['accion']} · {pregunta['empleado']}\n   {pregunta['detalle']}")
        respuesta = input(f"   {pregunta['pregunta']} ")
        resultado = app.invoke(Command(resume=respuesta), config)    # ← se reanuda donde quedó
    print("\nBitácora:", *resultado["bitacora"], sep="\n  ")