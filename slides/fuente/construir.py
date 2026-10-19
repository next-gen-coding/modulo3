"""Decks del Módulo 3 con el estilo «Tec Editorial», uno por sesión.

El contenido es el de la presentación completa (las mismas láminas, diagramas, código y notas); aquí solo
se le aplica el estilo del sistema (papel, tinta, azul Tec, serif en títulos, filetes en lugar de cajas
redondeadas, badge INSPIRA, marca de tiempo, logotipo y pie) y se reparte en cuatro sesiones con una
lámina de apertura por bloque.

Uso:  python3 fuente/construir.py RUTA_A_LAS_LAMINAS_ORIGINALES
"""
import base64
import re
import sys
from pathlib import Path

from bs4 import BeautifulSoup, Comment

RAIZ = Path(__file__).resolve().parent.parent
ORIGEN = Path(sys.argv[1]).resolve()
sys.path.insert(0, str(Path(__file__).parent))
from sesiones import SESIONES  # noqa: E402

PROGRAMA = "Next-Gen Coding: Desarrollo de Software con IA Generativa (Virtual)"
MODULO = "Módulo 3 · Construcción de Sistemas Agénticos"
NOMBRE = {"introduce": "Introduce", "nutre": "Nutre", "significa": "Significa", "practica": "Practica",
          "integra": "Integra", "reta": "Reta", "acompana": "Acompaña"}

# ── Paleta: de los colores originales a las variables del sistema (así funciona también en modo oscuro) ──
NARANJA_TINTE = "color-mix(in srgb, var(--reta) 13%, var(--paper))"
FUERA = {
    "#14171F": "var(--ink)", "#1B1F2A": "var(--ink)", "#4A5061": "var(--ink-2)",
    "#F0935A": "var(--reta)", "#E8793A": "var(--reta)", "#A34A17": "var(--reta)", "#B5541C": "var(--reta)",
    "#F7D9C4": NARANJA_TINTE, "#2F5D9E": "var(--tec)", "#DCE6F3": "var(--tec-tint)",
    "#F6F5F0": "var(--paper)", "#FDFCF9": "var(--paper-2)", "#ECEAE2": "var(--paper-2)", "#E6E3D8": "var(--paper-2)",
    "#6B7080": "var(--ink-2)", "#5E6372": "var(--ink-2)", "#B9BDC8": "var(--ink-2)", "#9AA0AE": "var(--ink-2)",
    "#DEDBD0": "var(--rule)", "#C9C5B8": "var(--rule)", "#3A3F4D": "var(--rule)", "#222634": "var(--rule)",
    "#A9D18E": "var(--practica)", "#8DB7F0": "var(--tec)", "#3A2A1F": "var(--tec-tint)",
}
# Dentro de los bloques oscuros (código y trazas) el fondo pasa a papel y el texto a tinta
DENTRO = dict(FUERA, **{
    "#14171F": "var(--paper-3)", "#1B1F2A": "var(--paper-2)",
    "#E6E3D8": "var(--ink)", "#F6F5F0": "var(--ink)", "#FDFCF9": "var(--ink)", "#ECEAE2": "var(--ink)",
    "#F0935A": "var(--introduce)", "#E8793A": "var(--introduce)", "#B5541C": "var(--introduce)",
    "#4A5061": "var(--rule)", "#DEDBD0": "var(--ink-2)", "#C9C5B8": "var(--ink-2)",
})
FUENTES = {"'IBM Plex Sans', Arial, sans-serif": "var(--sans)", "'Space Grotesk', Arial, sans-serif": "var(--serif)",
           "'JetBrains Mono', monospace": "var(--mono)"}


def restilar(estilo: str, oscuro: bool) -> str:
    mapa = DENTRO if oscuro else FUERA
    for viejo, nuevo in FUENTES.items():
        estilo = estilo.replace(viejo, nuevo)
    ceja = "text-transform:uppercase" in estilo and "letter-spacing" in estilo
    if ceja:   # las cejas pasan al estilo de .kicker: mono, azul Tec
        estilo = estilo.replace("#B5541C", "var(--tec)").replace("#A34A17", "var(--tec)")
        estilo = re.sub(r"font-size:\s*24px", "font-size:20px", estilo) + "; font-family:var(--mono)"
        estilo = re.sub(r"(?<![-\w])color:\s*#[0-9A-Fa-f]{6}", "color:var(--tec)", estilo)
    estilo = re.sub(r"#[0-9A-Fa-f]{6}\b", lambda m: mapa.get(m.group(0).upper(), m.group(0)), estilo)
    # Filetes en lugar de cajas redondeadas
    estilo = re.sub(r"border-radius:\s*(?!50%)[\d.]+px", "border-radius:0", estilo)
    estilo = re.sub(r"border:\s*2px solid", "border:1px solid", estilo)
    estilo = re.sub(r"border:\s*2px dashed", "border:1.5px dashed", estilo)
    if oscuro and "background:var(--paper-3)" in estilo:
        estilo += "; border:1px solid var(--rule-2); border-left:3px solid var(--rule)"
    return estilo


def es_oscuro(el) -> bool:
    for a in [el, *el.parents]:
        st = a.get("style", "") if hasattr(a, "get") else ""
        if re.search(r"background:\s*#14171F", st or "", re.I):
            return True
    return False


def lamina_original(id_: str, badge: str, tb: str) -> str:
    sopa = BeautifulSoup((ORIGEN / f"{id_}.html").read_text(encoding="utf-8"), "html.parser")
    sec = sopa.find("section")
    for com in sec.find_all(string=lambda x: isinstance(x, Comment)):
        com.extract()                       # los comentarios de coordenadas no se muestran
    aside = sec.find("aside")
    notas = aside.get_text(" ", strip=True) if aside else ""
    if aside:
        aside.decompose()
    fondo = re.search(r"background:\s*(#[0-9A-Fa-f]{6})", sec.get("style", ""))
    seccion_oscura = bool(fondo) and fondo.group(1).upper() in {"#14171F", "#1B1F2A", "#B5541C", "#2F5D9E", "#A34A17"}
    for el in sec.find_all(True):          # primero se decide qué está dentro de un bloque oscuro
        el["data-o"] = "1" if (seccion_oscura or es_oscuro(el)) else "0"
    for el in sec.find_all(True):
        if el.get("style"):
            el["style"] = restilar(el["style"], el["data-o"] == "1")
        del el["data-o"]
    for h2 in sec.find_all("h2"):          # los títulos en serif ocupan más que en la fuente original: que quepan en una línea
        m = re.search(r"font-size:\s*(\d+)px", h2.get("style", ""))
        if m:
            n = len(h2.get_text().strip())
            nuevo = max(40, min(int(m.group(1)), int(1664 / (n * 0.6))))
            h2["style"] = h2["style"].replace(m.group(0), f"font-size:{nuevo}px")
    estilo = re.sub(r"background:\s*#[0-9A-Fa-f]{6};?\s*", "", sec.get("style", ""))   # el fondo es el papel del sistema
    estilo = re.sub(r"(?<![-\w])color:\s*#[0-9A-Fa-f]{6};?\s*", "", estilo)
    estilo = restilar(estilo, False)
    cuerpo = "".join(str(c) for c in sec.contents)
    return (f'<section class="slide lamina" id="{id_}">\n  <div class="badge {badge}">{NOMBRE[badge]}</div>\n'
            f'  <div class="timebox">{tb}</div>\n  <div class="lienzo" style="{estilo}">{cuerpo}</div>\n'
            f'  <div class="notes">{notas}</div>\n</section>\n')


def portada(n: int, titulo: str, promesa: str, notas: str) -> str:
    return (f'<section class="slide cover hero">\n  <div class="badge introduce">Introduce</div>\n'
            f'  <div class="timebox">0:00 · Apertura</div>\n  <p class="eyebrow">Certificado</p>\n'
            f'  <h1 class="programa">{PROGRAMA}</h1>\n  <h2 class="sesion">{titulo}</h2>\n'
            f'  <div class="kicker">{MODULO}</div>\n  <p class="big muted">Sesión {n} · 2 h 30 min · Nivel profesional</p>\n'
            f'  <p class="muted">{promesa}</p>\n  <div class="notes">{notas}</div>\n</section>\n')


def apertura(badge: str, tb: str, kicker: str, titulo: str, sub: str, notas: str) -> str:
    return (f'<section class="slide cover">\n  <div class="badge {badge}">{NOMBRE[badge]}</div>\n'
            f'  <div class="timebox">{tb}</div>\n  <div class="kicker">{kicker}</div>\n  <h1>{titulo}</h1>\n'
            f'  <p class="big muted">{sub}</p>\n  <div class="notes">{notas}</div>\n</section>\n')


def descanso(tb: str, minutos: int, vuelve: str) -> str:
    return (f'<section class="slide" data-timer="{minutos}">\n  <div class="badge acompana">Acompaña</div>\n'
            f'  <div class="timebox">{tb}</div>\n  <h2 style="text-align:center">DESCANSO</h2>\n'
            f'  <div class="countdown">{minutos}:00</div>\n'
            f'  <p class="muted" style="text-align:center; max-width:none">{vuelve}</p>\n'
            f'  <div class="notes">Quédate en la sala los primeros 2 minutos: ahí llegan las dudas 1:1.</div>\n</section>\n')


ESTILO = (Path(__file__).parent / "lienzo.css").read_text(encoding="utf-8")
SCRIPT = (Path(__file__).parent / "lienzo.js").read_text(encoding="utf-8")

PLANTILLA = """<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{titulo}</title>
<link rel="stylesheet" href="assets/tec-inspira.css">
<style>{estilo}</style>
</head>
<body data-deck="{etiqueta}">

{slides}
<script>{script}</script>
<script src="assets/deck.js"></script>
</body>
</html>
"""


def archivo_unico(pagina: str) -> str:
    a = RAIZ / "assets"
    css = (a / "tec-inspira.css").read_text(encoding="utf-8")
    js = (a / "deck.js").read_text(encoding="utf-8")
    logo = "data:image/png;base64," + base64.b64encode((a / "logo-tec.png").read_bytes()).decode()
    blanco = "data:image/png;base64," + base64.b64encode((a / "logo-tec-blanco.png").read_bytes()).decode()
    pagina = pagina.replace('<link rel="stylesheet" href="assets/tec-inspira.css">', f"<style>{css}</style>")
    pagina = pagina.replace('<script src="assets/deck.js"></script>', f"<script>{js}</script>")
    return pagina.replace("<body data-deck=", f'<body data-logo="{logo}" data-logo-blanco="{blanco}" data-deck=', 1)


def revisar_tiempos(nombre: str, slides: list[str]) -> list[str]:
    avisos, vistos, total = [], [], 0
    for s in slides:
        tb = re.search(r'class="timebox">([^<]+)<', s).group(1)
        if tb not in vistos:
            vistos.append(tb)
    for tb in vistos:
        m = re.match(r"(\d+):(\d+) · (\d+) min", tb)
        if not m:
            continue
        ini = int(m.group(1)) * 60 + int(m.group(2))
        if ini != total:
            avisos.append(f"{nombre}: {tb} empieza en {ini}, se esperaba {total}")
        total = ini + int(m.group(3))
    if total != 150:
        avisos.append(f"{nombre}: suma {total} min")
    return avisos


def main() -> None:
    (RAIZ / "dist").mkdir(exist_ok=True)
    avisos = []
    for ses in SESIONES:
        slides = []
        for e in ses["laminas"]:
            tipo = e[0]
            if tipo == "portada":
                slides.append(portada(ses["n"], ses["titulo"], ses["promesa"], e[1]))
            elif tipo == "apertura":
                slides.append(apertura(*e[1:]))
            elif tipo == "descanso":
                slides.append(descanso(*e[1:]))
            else:   # ("lamina", id, badge, timebox)
                slides.append(lamina_original(*e[1:]))
        avisos += revisar_tiempos(ses["archivo"], slides)
        pagina = PLANTILLA.format(titulo=ses["titulo_html"], estilo=ESTILO, etiqueta=ses["etiqueta"],
                                  slides="\n".join(slides), script=SCRIPT)
        (RAIZ / ses["archivo"]).write_text(pagina, encoding="utf-8")
        (RAIZ / "dist" / ses["archivo"]).write_text(archivo_unico(pagina), encoding="utf-8")
        print(f'{ses["archivo"]}: {len(slides)} láminas')
    print("\n".join(avisos) if avisos else "Tiempos en orden: los bloques se encadenan y suman 150 min por sesión.")


if __name__ == "__main__":
    main()
