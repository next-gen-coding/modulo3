"""MCP · servidor: publica las herramientas del directorio de empleados para CUALQUIER agente.

Lo que distingue a MCP en el código: la herramienta ya no vive dentro del agente. Aquí solo hay
funciones con anotaciones de tipo y un docstring; FastMCP genera el esquema a partir de ellos y
las sirve por stdio. Quien se conecta (Claude Code, mcp_cliente.py u otro agente) las DESCUBRE
con list_tools() y las usa con call_tool(); no importa este archivo ni sabe cómo están hechas.

Compáralo con react.py: es la misma buscar_empleados, pero allí el esquema JSON se escribía a mano
y solo ese agente podía usarla.

Uso con Claude Code (desde la raíz del repo):
    claude mcp add directorio -- python -m ejemplos.s3_topologias.mcp_directorio
    claude mcp list            # debe decir: directorio … ✔ Connected
Uso con nuestro propio agente:
    python -m ejemplos.s3_topologias.mcp_cliente
Este archivo no se ejecuta solo: lo arranca el cliente y le habla por la entrada y salida estándar.
Por eso nunca usa print(): cualquier texto en stdout rompería el protocolo.

En tu fábrica: hoy los agentes 3, 4 y 5 usan las herramientas integradas de Claude Code;
un servidor como este les daría acceso a datos de la empresa sin tocar su código.
"""
import json

from mcp.server.fastmcp import FastMCP

from ejemplos.comun import EMPLEADOS

servidor = FastMCP("directorio-empleados", log_level="WARNING")   # sin ruido en la terminal


@servidor.tool()
def buscar_empleados(departamento: str) -> str:
    """Devuelve los empleados de un departamento con su estado y fecha de ingreso.
    Ejemplo: departamento='Tecnología'."""
    encontrados = [e for e in EMPLEADOS if e["departamento"] == departamento]
    return json.dumps(encontrados, ensure_ascii=False) if encontrados else "Sin empleados en ese departamento"


@servidor.tool()
def consultar_empleado(numero: str) -> str:
    """Devuelve los datos de un empleado por su número. Ejemplo: numero='EMP-0003'.
    Si no existe, responde con un error que el agente puede leer."""
    for e in EMPLEADOS:
        if e["numero"] == numero:
            return json.dumps(e, ensure_ascii=False)
    raise ValueError(f"No existe el empleado {numero}")   # MCP lo devuelve como error, no se silencia


# Solo lectura a propósito: un servidor MCP es código de terceros dentro del contexto del agente
# (riesgo de cadena de suministro, ASI04). Publica lo mínimo y sin permisos de escritura.

if __name__ == "__main__":
    servidor.run()   # transporte stdio por defecto
