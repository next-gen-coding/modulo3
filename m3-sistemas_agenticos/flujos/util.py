import os
import html
import os
import webbrowser

from langgraph.graph import StateGraph
from pathlib import Path
RAIZ = Path(__file__).resolve().parent.parent


def dibuja_grafo(app, nombre: str) -> Path:
    """Guarda el grafo de LangGraph como página HTML (Mermaid) en flujos/salidas/grafo_<nombre>.html.

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
    carpeta = RAIZ / "flujos" / "salidas"
    carpeta.mkdir(exist_ok=True)
    ruta = carpeta / f"grafo_{nombre}.html"
    ruta.write_text(pagina, encoding="utf-8")
    return ruta    
