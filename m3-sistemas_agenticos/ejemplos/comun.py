"""Piezas compartidas por los ejemplos: el modelo, unos datos de empleados y utilidades de impresión.

Los ejemplos son demostraciones para clase: cada uno muestra UN patrón en pocas líneas,
siempre sobre el mismo dominio, para que lo único que cambie entre archivos sea la estructura.
"""
import os
import html
import os
import webbrowser

from pathlib import Path

from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic

load_dotenv()
RAIZ = Path(__file__).resolve().parent.parent

# Un directorio pequeño, en memoria, para que los ejemplos no dependan de la app generada
EMPLEADOS = [
    {"numero": "EMP-0001", "nombre": "Ana López", "departamento": "Tecnología", "fecha_ingreso": "2019-03-04", "estado": "activo"},
    {"numero": "EMP-0002", "nombre": "Luis Pérez", "departamento": "Ventas", "fecha_ingreso": "2021-07-19", "estado": "activo"},
    {"numero": "EMP-0003", "nombre": "Marta Ruiz", "departamento": "Tecnología", "fecha_ingreso": "2016-11-02", "estado": "baja"},
    {"numero": "EMP-0004", "nombre": "Jorge Díaz", "departamento": "Tecnología", "fecha_ingreso": "2022-01-10", "estado": "activo"},
    {"numero": "EMP-0005", "nombre": "Sofía Gómez", "departamento": "Finanzas", "fecha_ingreso": "2020-05-25", "estado": "activo"},
]


def modelo(max_tokens: int = 1500) -> ChatAnthropic:
    """El modelo de los ejemplos con LangGraph. Se lee de MODEL en .env, como en la fábrica."""
    return ChatAnthropic(model=os.environ["MODEL"], max_tokens=max_tokens)


def historia(nombre: str) -> str:
    """Texto de una historia de usuario de historias/, por ejemplo historia('HU-01')."""
    return next((RAIZ / "historias").glob(f"{nombre}-*.md")).read_text(encoding="utf-8")


def reglas() -> str:
    return (RAIZ / "contexto" / "reglas_negocio.md").read_text(encoding="utf-8")


def titulo(texto: str) -> None:
    print(f"\n\033[1;33m── {texto} ──\033[0m")


def paso(quien: str, texto: str, limite: int = 300) -> None:
    """Imprime lo que hizo un nodo o agente, recortado para que se lea en pantalla."""
    texto = " ".join(str(texto).split())
    print(f"\033[1;36m[{quien}]\033[0m {texto[:limite]}{'…' if len(texto) > limite else ''}")

def guardar_grafo(app, nombre: str, abrir: bool = False) -> Path:
    """Guarda el grafo de LangGraph como página HTML (Mermaid) en ejemplos/salidas/grafo_<nombre>.html.

    Las aristas sólidas son add_edge; las punteadas, add_conditional_edges.
    Con abrir=True además lo muestra en el navegador.
    """
    texto = app.get_graph().draw_mermaid()
    pagina = f"""<!doctype html><meta charset="utf-8"><title>Grafo · {nombre}</title>
    <body style="font-family:sans-serif;display:flex;justify-content:center;padding:2rem">
    <pre class="mermaid">{html.escape(texto)}</pre>
    <script type="module">
    import mermaid from "https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs";
    mermaid.initialize({{ startOnLoad: true }});
    </script>"""
    carpeta = RAIZ / "ejemplos" / "salidas"
    carpeta.mkdir(exist_ok=True)
    ruta = carpeta / f"grafo_{nombre}.html"
    ruta.write_text(pagina, encoding="utf-8")
    paso("grafo", f"guardado en {ruta.relative_to(RAIZ)}")
    if abrir:
        webbrowser.open(ruta.as_uri())
    return ruta    

def guardar_grafo(app, nombre: str, abrir: bool = False, xray: bool = False) -> Path:
    """Guarda el grafo de LangGraph como página HTML (Mermaid) en ejemplos/salidas/grafo_<nombre>.html.

    Las aristas sólidas son add_edge; las punteadas, add_conditional_edges.
    Con abrir=True además lo muestra en el navegador.
    Con xray=True dibuja por dentro los subgrafos (los equipos de la topología jerárquica).
    """
    texto = app.get_graph(xray=xray).draw_mermaid()
    pagina = f"""<!doctype html><meta charset="utf-8"><title>Grafo · {nombre}</title>
<body style="font-family:sans-serif;display:flex;justify-content:center;padding:2rem">
<pre class="mermaid">{html.escape(texto)}</pre>
<script type="module">
  import mermaid from "https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs";
  mermaid.initialize({{ startOnLoad: true }});
</script>"""
    carpeta = RAIZ / "ejemplos" / "salidas"
    carpeta.mkdir(exist_ok=True)
    ruta = carpeta / f"grafo_{nombre}.html"
    ruta.write_text(pagina, encoding="utf-8")
    paso("grafo", f"guardado en {ruta.relative_to(RAIZ)}")
    if abrir:
        webbrowser.open(ruta.as_uri())
    return ruta

