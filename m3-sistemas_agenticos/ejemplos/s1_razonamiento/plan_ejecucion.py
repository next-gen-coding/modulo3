"""Patrón Plan-and-Execute: primero un plan completo y revisable; después se ejecuta paso a paso.

Lo que distingue al patrón en el código: DOS fases separadas. La primera devuelve una estructura
(Plan, con Pydantic) que una persona puede aprobar; la segunda recorre esa lista con un `for`.
Compáralo con react.py: allí el modelo decide el siguiente paso en cada vuelta; aquí lo decidió antes.

Uso:  python -m ejemplos.s1_razonamiento.plan_ejecucion
En tu fábrica:  agentes/desarrollador.py → planificar() y construir(); flujos/flujo_s2.py → aprobar_plan
"""
import os

from anthropic import Anthropic
#Pydantic es una libreria de estructuras de datos que contienen:
# Una estructura de datos: un modelo. Un esquema es decir, reglas de seguridad para tus datos y parsing. 
# Tú le describes cómo deben verse (qué campos, de qué tipo, con qué reglas) 
# y él revisa cada dato que entra: si cumple, lo deja pasar ya ordenado; si no, lo detiene y te dice exactamente qué está mal.
from pydantic import BaseModel
from ejemplos.comun import historia, paso, titulo


class Plan(BaseModel):
    pasos: list[str]  # cada paso es una instrucción concreta y ejecutable


def planificar(tarea: str) -> Plan:
    """Fase 1. Forzamos la herramienta 'plan' para obtener una salida estructurada y validable."""
    #Aquí la herramienta plan no existe como función: nunca se ejecuta nada. Es un truco para obtener una salida estructurada:
    #input_schema se le pasa como el esquema del Pydantic Plan. Así el modelo sabe que debe mandar {"pasos": [...]}.
    #tool_choice lo obliga a usar esa herramienta, en vez de responder con texto libre.    
    resp = Anthropic().messages.create(
        model=os.environ["MODEL"], max_tokens=1000,
        tools=[{"name": "plan", "description": "Registra el plan de trabajo, de 3 a 5 pasos.",
                "input_schema": Plan.model_json_schema()}],
        tool_choice={"type": "tool", "name": "plan"},
        messages=[{"role": "user", "content": f"Haz un plan breve para: {tarea}"}])
    # Por cada bloque b de resp.content, si es de tipo tool_use, dame su input. 
    # Discrimamos entre tool_use y text porque el modelo puede mandar varios bloques, 
    # por ejemplo uno de razonamiento interno (thinking) y otro de texto. Solo nos interesa el de tool_use.
    return Plan.model_validate(next(b.input for b in resp.content if b.type == "tool_use"))


def ejecutar(tarea: str, plan: Plan) -> str:
    """Fase 2. Cada paso recibe lo que produjeron los anteriores."""
    cliente, avance = Anthropic(), ""
    for i, instruccion in enumerate(plan.pasos, 1):
        resp = cliente.messages.create(
            model=os.environ["MODEL"], max_tokens=2000,
            messages=[{"role": "user", "content":
                       f"Tarea general: {tarea}\nAvance hasta ahora:\n{avance or '(nada)'}\n\n"
                       f"Haz SOLO este paso y responde en pocas líneas: {instruccion}"}])
        # La respuesta puede traer varios bloques (por ejemplo, uno de razonamiento interno, «thinking»);
        # nos quedamos solo con los de texto en lugar de suponer que el primero lo es.
        resultado = "".join(b.text for b in resp.content if b.type == "text")
        paso(f"ejecuta {i}/{len(plan.pasos)}", resultado)
        avance += f"\n## Paso {i}: {instruccion}\n{resultado}"
    return avance


if __name__ == "__main__":
    tarea = "Definir qué construir para esta historia (modelo de datos, endpoint y pantalla):\n" + historia("HU-01")
    titulo("Fase 1 · Planificar")
    plan = planificar(tarea)
    for i, p in enumerate(plan.pasos, 1):
        print(f"  {i}. {p}")
    if input("\n¿Aprobar el plan? (si/no) ").strip().lower() != "si":   # punto de control humano
        raise SystemExit("Plan rechazado: no se gastó nada en ejecutarlo.")
    titulo("Fase 2 · Ejecutar")
    ejecutar(tarea, plan)
