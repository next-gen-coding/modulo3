"""MCP · cliente: el bucle ReAct de react.py, pero las herramientas llegan de un servidor MCP.

Este archivo es un agente ReAct cuyas herramientas no están escritas en su código: 
las descubre de un servidor MCP (mcp_directorio.py) y, cuando el modelo pide una, se la pasa al servidor para que la ejecute

Lo que distingue a MCP en el código: el agente no tiene ni un esquema escrito a mano.
  1. Arranca el servidor y abre una sesión            → stdio_client(...) y ClientSession(...)
  2. Descubre las herramientas                         → await sesion.list_tools()
  3. Las traduce al formato de la API de Claude        → name, description, input_schema
  4. Cuando el modelo pide una, se la pasa al servidor → await sesion.call_tool(nombre, argumentos)
El bucle (razonar → actuar → observar) es idéntico al de react.py: MCP cambia DE DÓNDE salen las
herramientas, no cómo razona el agente.

Uso:  python -m ejemplos.s3_topologias.mcp_cliente
En tu fábrica:  Claude Code hace estos cuatro pasos por ti cuando registras un servidor con `claude mcp add`.
"""
import asyncio
import os
import sys

from anthropic import AsyncAnthropic
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from ejemplos.comun import RAIZ, paso, titulo

# Cómo arrancar el servidor: el mismo comando que se registra en Claude Code
#sys.executable es el mismo Python que estás usando, el de tu .venv.
#cwd=str(RAIZ) lo arranca desde la raíz del repo, para que encuentre ejemplos.comun.
SERVIDOR = StdioServerParameters(command=sys.executable,
                                 args=["-m", "ejemplos.s3_topologias.mcp_directorio"], cwd=str(RAIZ))


"""
    Hablar con el servidor y con la API de Claude implica esperar respuestas. async/await es la forma de Python de esperar sin bloquear todo el programa. 
    Para entender el código basta leer await X como «haz X y espera su respuesta». 
    Al final, asyncio.run(...) es lo que echa a andar la función asíncrona.
    """
async def react_con_mcp(pregunta: str, max_pasos: int = 5) -> str:
    """
     stdio_client arranca el servidor como un proceso aparte y te da dos «tubos»: uno para leer lo que dice y otro para escribirle.
    ClientSession pone encima el protocolo MCP, para que no tengas que armar los mensajes a mano.
    Los async with garantizan que, al terminar (o si algo falla), la sesión se cierra y el servidor se apaga solo.
    """
    async with stdio_client(SERVIDOR) as (lectura, escritura):
        async with ClientSession(lectura, escritura) as sesion:
            await sesion.initialize()                                      # 1. saludo del protocolo
            """
            El cliente pregunta «¿qué herramientas tienes?», y el servidor responde con sus fichas: buscar_empleados y consultar_empleado,
            cada una con su nombre, su descripción (el docstring) y su esquema de argumentos (los tipos). 
            Las fichas que armó @servidor.tool() del otro lado.
            """
            lista = await sesion.list_tools()                              # 2. DESCUBRIR
            """
            Traduce cada ficha de MCP al formato que pide la API de Claude. Es casi uno a uno: inputSchema se llama input_schema. 
            El resultado es exactamente la lista que en react.py se escribía a mano. Aquí nadie la escribió: llegó del servidor.
            """
            esquemas = [{"name": h.name, "description": h.description or "",
                         "input_schema": h.inputSchema} for h in lista.tools]   # 3. TRADUCIR
            paso("descubre", ", ".join(h.name for h in lista.tools))
            
            cliente = AsyncAnthropic()
            mensajes = [{"role": "user", "content": pregunta}]
            for n in range(max_pasos):                                     # el mismo bucle de react.py
                resp = await cliente.messages.create(model=os.environ["MODEL"], max_tokens=1000,
                                                     tools=esquemas, messages=mensajes)
                mensajes.append({"role": "assistant", "content": resp.content})
                for b in resp.content:
                    if b.type == "text" and b.text.strip():
                        paso(f"razona · vuelta {n}", b.text)
                if resp.stop_reason != "tool_use":
                    return "".join(b.text for b in resp.content if b.type == "text")
                resultados = []
                for b in resp.content:
                    if b.type == "tool_use":
                        paso("actúa (vía MCP)", f"{b.name}({b.input})")
                        r = await sesion.call_tool(b.name, b.input)       # 4. EJECUTA EL SERVIDOR
                        observacion = "".join(c.text for c in r.content if c.type == "text")
                        paso("observa", observacion)
                        resultados.append({"type": "tool_result", "tool_use_id": b.id,
                                           "content": observacion, "is_error": r.isError})
                mensajes.append({"role": "user", "content": resultados})
            raise RuntimeError(f"Se alcanzó el límite de {max_pasos} pasos")


if __name__ == "__main__":
    titulo("MCP · el agente descubre sus herramientas")
    print(asyncio.run(react_con_mcp(
        "¿Quién es el empleado activo más antiguo de Tecnología? Y ¿existe el EMP-0099?")))
