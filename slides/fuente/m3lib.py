"""Piezas para escribir los decks del Módulo 3 con el sistema «Tec Editorial» (tec-inspira.css + deck.js).

Cada función devuelve el HTML de una <section class="slide"> con su badge INSPIRA, su timebox y sus notas.
Los diagramas usan las piezas del sistema (.flow, .fbox, .farrow, .cycle, .layers…) más unas pocas
clases propias del módulo (ESTILO_MODULO), escritas solo con variables de color para que funcionen
en modo oscuro.
"""
import html
import re

PROGRAMA = "Next-Gen Coding: Desarrollo de Software con IA Generativa (Virtual)"
MODULO = "Módulo 3 · Construcción de Sistemas Agénticos"

ESTILO_MODULO = """
/* ── Piezas propias del Módulo 3 (solo variables del sistema: funcionan en modo oscuro) ── */
.fbox.persona { border-top-color: var(--introduce); }
.fbox.persona .tag { color: var(--introduce); }
.fbox.gate { border-top-color: var(--integra); }
.fbox.gate .tag { color: var(--integra); }
.fbox.claude { border-top-color: var(--reta); }
.fbox.claude .tag { color: var(--reta); }
.fbox.punteada { border-style: dashed; border-top-style: solid; }
.fbox.centro { background: var(--tec-tint); }
.fbox b { font-weight: 700; }
.diag { margin: .9rem 0 1rem; }
.diag .fbox { font-size: 1.12rem; padding: .9rem 1.2rem; }
.fbox .tag { display: block; }
table + p, pre + p { margin-top: .9rem; }
.cmd { display: inline-block; }
.pie { margin-top: .8rem; }
.pie p { font-size: 1.05rem; max-width: none; }
/* Árbol: raíz, rama horizontal y N hijos */
.arbol { display: flex; flex-direction: column; }
.arbol .raiz { display: flex; justify-content: center; }
.arbol .raiz > .fbox { min-width: 30%; }
.arbol .baja { text-align: center; color: var(--tec); font-size: 1.2rem; line-height: 1.25; }
.arbol .rama { border-top: 1.5px solid var(--tec); margin: 0 calc(50% / var(--n)); height: 0; }
.arbol .hijos { display: grid; grid-template-columns: repeat(var(--n), 1fr); gap: .9rem; }
.arbol .hijo { display: flex; flex-direction: column; }
/* Ramas: entrada → decisión → varias salidas apiladas */
.ramas { display: grid; grid-template-columns: 1fr auto 1.15fr auto 1.4fr auto 1fr; gap: .7rem; align-items: center; }
.ramas.sin-cierre { grid-template-columns: 1fr auto 1.15fr auto 1.6fr; }
.pila { display: flex; flex-direction: column; gap: .6rem; }
.ramas .pila .fila > .fbox { flex: 1; }
/* Vuelta: el regreso de un ciclo */
.vuelta { border: 1.5px solid var(--introduce); border-top: none; height: 1rem; margin: .1rem 9% 0; }
.vuelta-txt { text-align: center; color: var(--introduce); font-size: 1rem; margin-top: .35rem; max-width: none; }
/* Rejilla 3×3 (red, pizarra) */
.rejilla { display: grid; grid-template-columns: 1fr 3.2rem 1fr 3.2rem 1fr; gap: .45rem; align-items: center; }
.rejilla .farrow { font-size: 1.4rem; }
/* Traza de ejemplo */
.traza { background: var(--paper-2); border-left: 3px solid var(--tec); padding: 1rem 1.3rem; }
.traza p { font-family: var(--mono); font-size: .9rem; line-height: 1.5; max-width: none; margin: .22rem 0; font-weight: 500; }
.traza .et { font-weight: 700; }
.et-p { color: var(--introduce); } .et-a { color: var(--tec); } .et-o { color: var(--practica); }
.et-x { color: var(--reta); } .et-r { color: var(--ink); } .et-g { color: var(--ink-2); }
/* Idea del patrón: alternativas y definición */
.alt { margin: 0 0 .7rem; }
.alt li { font-size: 1.05rem; line-height: 1.45; }
.def { margin-top: .4rem; }
.def p { font-size: 1.12rem; line-height: 1.5; }
/* Código: líneas que distinguen al patrón */
pre .hl { background: var(--tec-tint); }
.cmd { font-family: var(--mono); font-size: .92rem; color: var(--tec-deep); }
"""


def esc(t: str) -> str:
    return html.escape(t, quote=False)


def seccion(badge: str, tb: str, cuerpo: str, notas: str, clases: str = "", attrs: str = "") -> str:
    nombre = {"introduce": "Introduce", "nutre": "Nutre", "significa": "Significa", "practica": "Practica",
              "integra": "Integra", "reta": "Reta", "acompana": "Acompaña"}[badge]
    cl = f"slide {clases}".strip()
    return (f'<section class="{cl}"{attrs}>\n  <div class="badge {badge}">{nombre}</div>\n'
            f'  <div class="timebox">{tb}</div>\n{cuerpo}\n  <div class="notes">{notas}</div>\n</section>\n')


def portada(sesion: str, clase: int, promesa: str, notas: str) -> str:
    cuerpo = (f'  <p class="eyebrow">Certificado</p>\n  <h1 class="programa">{PROGRAMA}</h1>\n'
              f'  <h2 class="sesion">{sesion}</h2>\n  <div class="kicker">{MODULO}</div>\n'
              f'  <p class="big muted">Clase {clase} · Sesión de 2 h 30 min · Nivel profesional</p>\n'
              f'  <p class="muted">{promesa}</p>')
    return seccion("introduce", "0:00 · Apertura", cuerpo, notas, "cover hero")


def apertura(badge: str, tb: str, kicker: str, titulo: str, sub: str, notas: str) -> str:
    return seccion(badge, tb, f'  <div class="kicker">{kicker}</div>\n  <h1>{titulo}</h1>\n'
                              f'  <p class="big muted">{sub}</p>', notas, "cover")


def contenido(badge: str, tb: str, titulo: str, cuerpo: str, notas: str, attrs: str = "") -> str:
    return seccion(badge, tb, f"  <h2>{titulo}</h2>\n{cuerpo}", notas, attrs=attrs)


def ul(items: list[str]) -> str:
    return "  <ul>\n" + "".join(f"    <li>{i}</li>\n" for i in items) + "  </ul>"


def ol(items: list[str]) -> str:
    return "  <ol>\n" + "".join(f"    <li>{i}</li>\n" for i in items) + "  </ol>"


def panel(t: str) -> str:
    return f'  <div class="panel"><p>{t}</p></div>'


def muted(t: str, extra: str = "") -> str:
    return f'  <p class="muted{(" " + extra) if extra else ""}">{t}</p>'


def tarjetas(items: list[tuple[str, str]]) -> str:
    cols = "cols3" if len(items) == 3 else "cols"
    return f'  <div class="{cols}">\n' + "".join(
        f'    <div class="card"><h3>{h}</h3><p>{p}</p></div>\n' for h, p in items) + "  </div>"


def tabla(cab: list[str], filas: list[list[str]]) -> str:
    t = "  <table>\n    <tr>" + "".join(f"<th>{c}</th>" for c in cab) + "</tr>\n"
    for f in filas:
        t += "    <tr>" + "".join(f"<td>{c}</td>" for c in f) + "</tr>\n"
    return t + "  </table>"


def significa(tb: str, pregunta: str, consigna: str, notas: str) -> str:
    cuerpo = (f'  <div class="panel q">\n    <p><strong>Pregunta poderosa:</strong> {pregunta}</p>\n  </div>\n'
              f'  <p class="muted">{consigna}</p>')
    return contenido("significa", tb, "Aterricemos", cuerpo,
                     "AULA VIRTUAL: respuesta al chat; si hay tiempo, salas de 3. No respondas tú primero: deja el silencio. "
                     + notas)


def descanso(tb: str, minutos: int, vuelve: str) -> str:
    cuerpo = (f'  <div class="countdown">{minutos}:00</div>\n'
              f'  <p class="muted" style="text-align:center; max-width:none">{vuelve}</p>')
    return seccion("acompana", tb, f'  <h2 style="text-align:center">DESCANSO</h2>\n{cuerpo}',
                   "Quédate en la sala los primeros 2 minutos: ahí llegan las dudas 1:1.",
                   attrs=f' data-timer="{minutos}"')


# ── Código ───────────────────────────────────────────────────────────
KW = r"\b(def|return|for|in|if|else|elif|not|and|or|import|from|class|raise|with|as|lambda|while|None|True|False|async|await|try|except)\b"


def _colorear(linea: str) -> str:
    comillas, corte = None, len(linea)
    for i, ch in enumerate(linea):
        if ch in "\"'" and comillas in (None, ch):
            comillas = None if comillas else ch
        elif ch == "#" and not comillas:
            corte = i
            break
    codigo, comentario = linea[:corte], linea[corte:]
    partes = re.split(r'("[^"]*"|\'[^\']*\')', codigo)
    patron = re.compile(KW + r"|(?<![\w.])([A-Za-z_]\w*)(?=\()")

    def pinta(m: re.Match) -> str:
        if m.group(1):
            return f'<span class="kw">{m.group(1)}</span>'
        return f'<span class="fn">{m.group(2)}</span>'

    out = []
    for i, p in enumerate(partes):
        if i % 2:
            out.append(f'<span class="str">{esc(p)}</span>')
        else:   # se colorea por tramos para no tocar el HTML ya insertado
            pos, trozos = 0, []
            for m in patron.finditer(p):
                trozos.append(esc(p[pos:m.start()]) + pinta(m))
                pos = m.end()
            trozos.append(esc(p[pos:]))
            out.append("".join(trozos))
    if comentario:
        out.append(f'<span class="com">{esc(comentario)}</span>')
    return "".join(out)


def codigo(fuente: str) -> str:
    """Las líneas que empiezan con '!' se resaltan: son las que distinguen al patrón."""
    lineas = []
    for l in fuente.strip("\n").splitlines():
        marcada = l.startswith("!")
        l = l[1:] if marcada else l
        c = _colorear(l)
        lineas.append(f'<span class="hl">{c}</span>' if marcada else c)
    return "<pre>" + "\n".join(lineas) + "</pre>"


# ── Diagramas ────────────────────────────────────────────────────────
def caja(t: str, sub: str = "", tag: str = "", tipo: str = "", step: int | None = None) -> str:
    s = f' data-step="{step}"' if step else ""
    tg = f'<span class="tag">{tag}</span>' if tag else ""
    sb = f"<small>{sub}</small>" if sub else ""
    return f'<div class="fbox {tipo}"{s}>{tg}{t}{sb}</div>'


def flecha(t: str = "→", step: int | None = None) -> str:
    s = f' data-step="{step}"' if step else ""
    return f'<span class="farrow"{s}>{t}</span>'


def flujo(*piezas: str) -> str:
    return '  <div class="flow diag">' + "".join(piezas) + "</div>"


def traza(lineas: list[tuple[str, str, str]], pasos: bool = True) -> str:
    """lineas: (tipo, etiqueta, texto). tipo: p pensamiento · a acción · o observación · x falla · r respuesta · g contexto."""
    out = []
    for k, (tipo, et, tx) in enumerate(lineas):
        st = f' data-step="{k}"' if pasos and k else ""
        out.append(f'<p{st}><span class="et et-{tipo}">{et}</span> {tx}</p>')
    return '<div class="traza">' + "".join(out) + "</div>"


def idea(tb: str, titulo: str, alternativas: list[tuple[str, str]], patron: tuple[str, str],
         lineas: list[tuple[str, str, str]], fuente_txt: str, notas: str) -> str:
    alt = "<ul class=\"alt\">" + "".join(f"<li><strong>{a}:</strong> {b}</li>" for a, b in alternativas) + "</ul>"
    cuerpo = (f'  <div class="cols">\n    <div><h3>Sin el patrón</h3>{alt}'
              f'<div class="panel def"><p><strong>{patron[0]}:</strong> {patron[1]}</p></div></div>\n'
              f'    <div><h3>Un ejemplo</h3>{traza(lineas)}</div>\n  </div>\n'
              f'  <p class="muted pie-fuente" style="font-size:.9rem; margin-top:.9rem">{fuente_txt}</p>')
    pasos = len(lineas) - 1
    return contenido("nutre", tb, titulo, cuerpo,
                     notas + f" Paso a paso: cada → muestra una línea más de la traza ({pasos} pasos).")


def pila(*cajas: str, step: int | None = None) -> str:
    s = f' data-step="{step}"' if step else ""
    return f'<div class="pila"{s}>' + "".join(cajas) + "</div>"


def arbol(raiz: str, hijos: list[str], sube: bool = False, step: int | None = None) -> str:
    """Una raíz con N hijos unidos por una rama. sube=True dibuja flechas de ida y vuelta (↕)."""
    s = f' data-step="{step}"' if step else ""
    f = "↕" if sube else "↓"
    hj = "".join(f'<div class="hijo"><div class="baja">{f}</div>{h}</div>' for h in hijos)
    return (f'<div class="arbol"{s} style="--n:{len(hijos)}"><div class="raiz">{raiz}</div><div class="baja">{f}</div>'
            f'<div class="rama"></div><div class="hijos">{hj}</div></div>')


def ramas(entrada: str, decision: str, salidas: list[str], step: int | None = None) -> str:
    """Entrada → decisión → varias salidas apiladas (enrutamiento, humano en el flujo, triage)."""
    pl = "".join(f'<div class="fila" style="display:flex; align-items:center; gap:.6rem">{flecha()}{x}</div>' for x in salidas)
    s = f' data-step="{step}"' if step else ""
    return (f'  <div class="ramas sin-cierre diag">{entrada}{flecha()}{decision}<span></span>'
            f'<div class="pila"{s}>{pl}</div></div>')


def rejilla(celdas: list[str]) -> str:
    """Rejilla 5×3: cajas en columnas impares y flechas en las pares."""
    return '  <div class="rejilla diag">' + "".join(c if c else "<span></span>" for c in celdas) + "</div>"


# ════════════════════════════════════════════════════════════════════
# Versión 2: solo el estilo Tec Editorial y la separación por sesiones.
# El badge lleva la etiqueta de la slide (no el momento INSPIRA) y la
# esquina derecha, la sesión. No hay límites de palabras ni de tiempo.
# ════════════════════════════════════════════════════════════════════
import json as _json
from pathlib import Path as _Path

DATOS = _json.loads((_Path(__file__).parent / "datos.json").read_text(encoding="utf-8"))
DATOS["codigo"]["c-react"]["codigo"] = DATOS["codigo"]["c-react"]["codigo"].replace(
    "return resp.content[0].text", 'return "".join(b.text for b in resp.content if b.type == "text")')
DATOS["codigo"]["c-plan"]["codigo"] = DATOS["codigo"]["c-plan"]["codigo"].replace(
    "return Plan.model_validate(resp.content[0].input)",
    'return Plan.model_validate(next(b.input for b in resp.content if b.type == "tool_use"))')

ESTILO_V2 = """
.dos { display: grid; grid-template-columns: 1.45fr 1fr; gap: 2.8rem; align-items: center; }
.dos-codigo { display: grid; grid-template-columns: 1.8fr 1fr; gap: 2.2rem; align-items: start; }
.lado { display: flex; flex-direction: column; gap: 1.05rem; }
.lado h3 { margin-bottom: .3rem; }
.lado p { font-size: 1.08rem; line-height: 1.5; max-width: none; }
.lado .panel { margin: 0; }
.lado .cmd { font-size: .85rem; display: block; background: var(--paper-3); border: 1px solid var(--rule-2); padding: .5rem .7rem; }
.pie-slide { font-size: .92rem; margin-top: 1.3rem; max-width: none; }
.ideas .card { margin-bottom: .8rem; }
.ideas .card p, .ideas .panel p { font-size: 1.05rem; line-height: 1.5; }
.ideas .panel { margin: 0; }
.traza p { font-size: .95rem; }
.nota-idea { font-size: 1rem; margin-top: .9rem; max-width: none; }
.stats { display: flex; gap: 3rem; margin-top: 1.6rem; }
.stat b { display: block; font-family: var(--serif); font-size: 2.6rem; color: var(--tec); line-height: 1.1; }
.stat span { font-family: var(--mono); font-size: .8rem; letter-spacing: .14em; text-transform: uppercase; color: var(--ink-2); }
.obj5 { display: grid; grid-template-columns: repeat(5, 1fr); gap: 1rem; }
.obj5 .card { display: flex; flex-direction: column; gap: .4rem; }
.obj5 .num { font-family: var(--serif); font-size: 2rem; color: var(--tec); font-weight: 600; }
.obj5 p { font-size: 1rem; line-height: 1.45; }
.obj5 small { font-family: var(--mono); font-size: .72rem; letter-spacing: .1em; text-transform: uppercase; color: var(--ink-2); }
.card ul li, .card ol li { font-size: 1rem; line-height: 1.45; margin: .35rem 0; }
.huge-sola { max-width: 26ch; }
"""


def slide(tipo: str, etiqueta: str, sesion: str, cuerpo: str, notas: str, clases: str = "", attrs: str = "") -> str:
    cl = f"slide {clases}".strip()
    return (f'<section class="{cl}"{attrs}>\n  <div class="badge {tipo}">{etiqueta}</div>\n'
            f'  <div class="timebox">{sesion}</div>\n{cuerpo}\n  <div class="notes">{notas}</div>\n</section>\n')


def con_titulo(tipo, etiqueta, sesion, titulo, cuerpo, notas, pie=""):
    p = f'\n  <p class="muted pie-slide">{pie}</p>' if pie else ""
    return slide(tipo, etiqueta, sesion, f"  <h2>{titulo}</h2>\n{cuerpo}{p}", notas)


def portada_v2(sesion: str, clase: int, promesa: str, notas: str) -> str:
    cuerpo = (f'  <p class="eyebrow">Certificado</p>\n  <h1 class="programa">{PROGRAMA}</h1>\n'
              f'  <h2 class="sesion">{sesion}</h2>\n  <div class="kicker">{MODULO}</div>\n'
              f'  <p class="big muted">Sesión {clase} de 4 · 2 h 30 min</p>\n  <p class="muted">{promesa}</p>')
    return slide("introduce", "Tecnológico de Monterrey", f"Sesión {clase}", cuerpo, notas, "cover hero")


def apertura_v2(sesion: str, numero: str, titulo: str, sub: str, lab: str, notas: str) -> str:
    return slide("introduce", f"Sesión {numero}", sesion,
                 f'  <div class="kicker">Sesión {numero} · 150 min</div>\n  <h1>{titulo}</h1>\n'
                 f'  <p class="big muted">{sub}</p>\n  <p class="muted">{lab}</p>', notas, "cover")


def _bloque(t: str, p: str) -> str:
    return f"<div><h3>{t}</h3><p>{p}</p></div>"


def patron_v2(pid: str, sesion: str, diagrama: str, tipo: str = "nutre") -> str:
    d = DATOS["patrones"][pid]
    if "bloques" in d:
        bl = d["bloques"]
        lado = "".join(_bloque(t, p) for t, p in bl[:-1]) + f'<div class="panel"><h3>{bl[-1][0]}</h3><p>{bl[-1][1]}</p></div>'
    else:
        seg = "Ventaja y riesgo" if d["topologia"] else "Úsalo cuando"
        lado = (_bloque("Cómo funciona", d["como"]) + _bloque(seg, d["segundo"]) +
                f'<div class="panel"><h3>En tu fábrica</h3><p>{d["fabrica"]}</p></div>')
    cuerpo = f'  <div class="dos">\n    <div>{diagrama}</div>\n    <div class="lado">{lado}</div>\n  </div>'
    return con_titulo(tipo, d["ceja"], sesion, d["titulo"], cuerpo, d["notas"], d["pie"])


def codigo_v2(cid: str, sesion: str) -> str:
    d = DATOS["codigo"][cid]
    cmds = "".join(f'<span class="cmd">{esc(c)}</span>' for c in d["comando"].split("<br>"))
    lado = (_bloque("Lo que lo distingue", d["distingue"]) + _bloque("Compáralo con", d["compara"]) +
            f"<div><h3>Ejecútalo</h3>{cmds}</div>" +
            f'<div class="panel"><h3>En tu fábrica</h3><p>{d["fabrica"]}</p></div>')
    cuerpo = f'  <div class="dos-codigo">\n    <div>{codigo(d["codigo"])}</div>\n    <div class="lado">{lado}</div>\n  </div>'
    return con_titulo("nutre", d["ceja"], sesion, d["titulo"], cuerpo, d["notas"],
                      f'Fragmento simplificado de {d["archivo"]} · las líneas resaltadas son el patrón')


_ET = {"p": "p", "a": "a", "o": "o", "x": "x", "r": "r", "g": "g"}


def idea_v2(iid: str, sesion: str) -> str:
    d = DATOS["ideas"][iid]
    (t1, x1), (t2, x2), (t3, x3) = d["tarjetas"]
    izq = (f'<div class="card"><h3>{t1}</h3><p>{x1}</p></div><div class="card"><h3>{t2}</h3><p>{x2}</p></div>'
           f'<div class="panel"><h3>{t3}</h3><p>{x3}</p></div>')
    lineas = []
    for k, (tipo, et, tx) in enumerate(d["traza"]):
        st = f' data-step="{k}"' if k else ""
        if tipo == "g":
            lineas.append(f'<p{st}><span class="et et-g">{et}</span>{esc(tx)}</p>')
        else:
            sep = "" if tx.startswith("→") else " ·"
            lineas.append(f'<p{st}><span class="et et-{_ET[tipo]}">{et}{sep}</span> {esc(tx)}</p>')
    der = f'<h3>Un ejemplo</h3><div class="traza">{"".join(lineas)}</div><p class="muted nota-idea">{d["nota"]}</p>'
    cuerpo = f'  <div class="cols ideas">\n    <div>{izq}</div>\n    <div>{der}</div>\n  </div>'
    return con_titulo("nutre", d["ceja"], sesion, d["titulo"], cuerpo,
                      d["notas"] + f" Paso a paso: cada → muestra una línea más de la traza.", d["pie"])
