"""Sesión 1 · Agente 1, analista: historia de usuario -> criterios de aceptación en Gherkin.

Uso:  python -m agentes.analista historias/HU-01-registrar-empleado.md
"""
import re
import sys
from pathlib import Path

from agentes.base import RAIZ, SALIDA, ejecutar_agente, herramientas_archivos, hu_de, rel

SISTEMA = """Eres analista de producto en un equipo de software. Conviertes historias de usuario
en criterios de aceptación escritos en Gherkin, en español.

Cómo trabajas:
1. Lee la historia y el archivo contexto/reglas_negocio.md.
2. Guarda el Gherkin con la herramienta escribir_archivo en {destino}. La primera línea es
   `# language: es` y usas solo las palabras clave Característica, Escenario, Dado, Cuando,
   Entonces, Y. No uses Antecedentes ni Esquema del escenario: cada Escenario lleva su propio
   Dado, Cuando y Entonces.
3. Incluye el camino feliz y un escenario de error por cada regla de negocio que aplique a ESTA historia.
4. Cada escenario se puede verificar desde la pantalla o la API: datos concretos, nada de «funciona bien».
5. No inventes reglas. Si falta información, agrégala al final como comentarios bajo `# Preguntas abiertas`.
6. Responde al final con una sola línea: cuántos escenarios escribiste."""


def escenarios(gherkin: str) -> list[str]:
    return re.findall(r"^\s*Escenario:\s*(.+?)\s*$", gherkin, flags=re.MULTILINE)


def preguntas_abiertas(gherkin: str) -> list[str]:
    if "# Preguntas abiertas" not in gherkin:
        return []
    bloque = gherkin.split("# Preguntas abiertas", 1)[1]
    return [l.lstrip("# -").strip() for l in bloque.splitlines() if l.strip().lstrip("#").strip()]


def validar_gherkin(texto: str) -> list[str]:
    """Evaluador determinista: devuelve los problemas encontrados; vacío = válido."""
    problemas = []
    if not texto.lstrip().startswith("# language: es"):
        problemas.append("La primera línea debe ser '# language: es'.")
    if "Característica:" not in texto:
        problemas.append("Falta 'Característica:'.")
    bloques = re.split(r"^\s*Escenario:", texto, flags=re.MULTILINE)[1:]
    if len(bloques) < 2:
        problemas.append("Se esperan al menos 2 escenarios (camino feliz y un error).")
    for i, bloque in enumerate(bloques, 1):
        for clave in ("Dado", "Cuando", "Entonces"):
            if not re.search(rf"^\s*{clave}\b", bloque, flags=re.MULTILINE):
                problemas.append(f"El escenario {i} no tiene '{clave}'.")
    return problemas


def generar_criterios(historia: Path, max_intentos: int = 2) -> Path:
    carpeta = SALIDA / hu_de(historia)
    destino = carpeta / "criterios.feature"
    herramientas = herramientas_archivos(lectura=[RAIZ / "historias", RAIZ / "contexto"], escritura=carpeta)
    tarea = f"Historia de usuario: {rel(historia)}"
    for intento in range(1, max_intentos + 1):
        print(f"Analista · intento {intento}")
        ejecutar_agente(SISTEMA.format(destino=rel(destino)), herramientas, tarea, nombre="analista")
        problemas = validar_gherkin(destino.read_text(encoding="utf-8")) if destino.exists() \
            else [f"No se escribió {rel(destino)}."]
        if not problemas:
            return destino
        # Reflexión guiada por un evaluador determinista: el agente recibe los problemas y corrige
        tarea += "\n\nTu versión anterior tiene estos problemas; corrígelos:\n- " + "\n- ".join(problemas)
    raise ValueError("Criterios inválidos tras varios intentos:\n- " + "\n- ".join(problemas))


if __name__ == "__main__":
    ruta = generar_criterios(Path(sys.argv[1]).resolve())
    texto = ruta.read_text(encoding="utf-8")
    print(f"\nListo: {rel(ruta)} · {len(escenarios(texto))} escenarios")
    for p in preguntas_abiertas(texto):
        print("  Pregunta abierta:", p)
