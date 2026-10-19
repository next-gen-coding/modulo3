"""Patrón ReAct: razonar → actuar (herramienta) → observar → repetir hasta poder responder.

Lo que distingue a ReAct en el código: un bucle `for` que sigue mientras el modelo pida
herramientas (stop_reason == "tool_use"). El modelo decide cuántas vueltas dar; nosotros ponemos el tope.

Uso:  python -m ejemplos.s1_razonamiento.react
En tu fábrica:  agentes/base.py → ejecutar_agente()
"""
import json
import os

from anthropic import Anthropic

from ejemplos.comun import EMPLEADOS, paso, titulo


# --- Herramientas: funciones normales + un esquema que el modelo puede leer ---
def buscar_empleados(departamento: str) -> str:
    encontrados = [e for e in EMPLEADOS if e["departamento"] == departamento]
    return json.dumps(encontrados, ensure_ascii=False) if encontrados else "Sin empleados en ese departamento"


HERRAMIENTAS = {"buscar_empleados": buscar_empleados}
ESQUEMAS = [{
    "name": "buscar_empleados",
    "description": "Devuelve los empleados de un departamento con su estado y fecha de ingreso. "
                   "Ejemplo: departamento='Tecnología'.",
    "input_schema": {"type": "object", "properties": {"departamento": {"type": "string"}},
                     "required": ["departamento"]},
}]

#----Muestra el patrón ReAct: razonar → actuar → observar → repetir hasta poder responder.
def react(pregunta: str, max_pasos: int = 5) -> str:
    cliente = Anthropic()
    #El mensaje inicial solo tiene la pregunta
    mensajes = [{"role": "user", "content": pregunta}]
    #Cada llamada es una vuelta del ciclo: el modelo razona, actúa y observa. 
    #vuelta[0] razona la pregunta, actua con la herramienta y observa el resultado.
    #vuelta[1] con la información observada realiza el análisis
    for n in range(max_pasos):  
        #Llamada al LLM, cada ciclo es una llamada
        # Le da las herramientas a utilizar, el LLM decide que y cuando usarlas                                 
        resp = cliente.messages.create(model=os.environ["MODEL"], max_tokens=1000,
                                      #ESQUEMAS, que herramientas puede usar el LLM
                                      #Y que hacen y que devuelven, el LLM decide que herramienta usar y cuando
                                       tools=ESQUEMAS, messages=mensajes)
        mensajes.append({"role": "assistant", "content": resp.content})
        for b in resp.content:
            if b.type == "text" and b.text.strip():
                paso(f"razona · vuelta {n}", b.text)
        # Si el modelo no necesita más herramientas para responder, ya puede responder
        #"tool_use" significa que necesita una herramienta, así que el bucle sigue.
        #Cualquier otro valor, normalmente "end_turn", 
        # significa que ya tiene la respuesta. Se juntan sus bloques de texto y se devuelven.
        if resp.stop_reason != "tool_use":                       # ya puede responder
            return "".join(b.text for b in resp.content if b.type == "text")
        resultados = []
        #el ciclo for es por que puede necesitar varias herrrmientas
        for b in resp.content:
            #Se recorren los bloques y, por cada tool_use, se busca la función en el registro y 
            # se llama con los argumentos que eligió el modelo. **b.input convierte {"departamento": "Tecnología"} 
            # en buscar_empleados(departamento="Tecnología").        
            if b.type == "tool_use":
                paso("actúa", f"{b.name}({b.input})")
                try:
                    observacion, error = HERRAMIENTAS[b.name](**b.input), False   # ACTUAR
                except Exception as e:                            # el error también es una observación
                    observacion, error = f"Error: {e}", True
                paso("observa", observacion)                      # OBSERVAR
                resultados.append({"type": "tool_result", "tool_use_id": b.id,
                                   "content": observacion, "is_error": error})
        mensajes.append({"role": "user", "content": resultados})  # la observación vuelve al modelo
    raise RuntimeError(f"Se alcanzó el límite de {max_pasos} pasos")


if __name__ == "__main__":
    titulo("ReAct")
    print(react("¿Cuántos empleados ACTIVOS hay en Tecnología y quién de ellos es el más antiguo?"))
