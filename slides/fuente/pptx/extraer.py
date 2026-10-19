"""Extrae cada slide de un deck Tec Editorial (tec-inspira.css + deck.js) como formas, textos e imágenes con su posición.

Uso: python3 extraer.py deck.html salida.json
"""
import asyncio
import base64
import json
import sys
from pathlib import Path
from urllib.parse import unquote, urlparse

from playwright.async_api import async_playwright

HTML = Path(sys.argv[1]).resolve()
# A 2134 × 1200 las láminas de 1920 × 1080 quedan a escala 1 (se escalan al 90 %), así los tamaños medidos son los reales
ANCHO, ALTO = 2134, 1200
SALIDA = Path(sys.argv[2])
# Fuentes de medición con las mismas métricas que las del PPTX (Arial, Courier New) y una serif más ancha que Georgia
MEDIDA = (":root{--serif:'DejaVu Serif Condensed','DejaVu Serif',serif !important;--sans:'Liberation Sans',Arial,sans-serif !important;"
          "--mono:'Liberation Mono',monospace !important} *{transition:none!important;animation:none!important;font-stretch:condensed} #pasos{display:none!important}")
FONDO = ".slide.active > *{visibility:hidden!important} #deck-chrome,#progress{visibility:hidden!important}"

JS = r"""
(idx) => {
  const secs = [...document.querySelectorAll('.slide')];
  secs.forEach((s, k) => s.classList.toggle('active', k === idx));
  const sec = secs[idx];
  const hero = sec.classList.contains('hero');
  document.body.classList.toggle('hero-activo', hero);
  const logo = document.querySelector('#deck-chrome img');
  if (logo) logo.src = hero ? logo.getAttribute('data-blanco') : logo.getAttribute('data-azul');
  const cont = document.getElementById('counter'); if (cont) cont.textContent = (idx + 1) + ' / ' + secs.length;
  const prog = document.getElementById('progress'); if (prog) prog.style.width = ((idx + 1) / secs.length * 100) + '%';
  sec.querySelectorAll('[data-step],[data-mark]').forEach(e => e.classList.add('on'));
  for (let q = 1; q <= 12; q++) sec.classList.add('p' + q);
  // Materializa ::before y ::after como elementos reales para poder medirlos y dibujarlos
  function materializar(root) {
    for (const el of [root, ...root.querySelectorAll('*')]) {
      if (el.hasAttribute('data-pseudo') || el.hasAttribute('data-ph')) continue;
      for (const ps of ['::before', '::after']) {
        const cs = getComputedStyle(el, ps);
        const c = cs.content;
        if (!c || c === 'none' || c === 'normal' || cs.display === 'none') continue;
        const sp = document.createElement('span');
        sp.setAttribute('data-pseudo', ps);
        for (let k = 0; k < cs.length; k++) sp.style.setProperty(cs[k], cs.getPropertyValue(cs[k]));
        let txt = '';
        if (/^".*"$/.test(c)) { try { txt = JSON.parse(c); } catch (e) { txt = ''; } }
        else if (c.startsWith('counter(')) {
          const ol = el.parentElement;
          const base = parseInt((getComputedStyle(ol).counterReset.match(/-?\d+/) || ['0'])[0], 10) || 0;
          const n = [...ol.children].filter(x => x.tagName === 'LI').indexOf(el) + 1 + base;
          txt = String(n).padStart(2, '0');
        }
        sp.textContent = txt;
        sp.style.setProperty('content', 'normal');
        if (ps === '::before') el.insertBefore(sp, el.firstChild); else el.appendChild(sp);
      }
      el.setAttribute('data-ph', '1');
    }
  }
  materializar(sec); materializar(document.getElementById('deck-chrome'));
  // Contenido mixto (texto suelto junto a hijos de bloque, como «Historia<small>…</small>»):
  // cada tramo de texto en línea se envuelve en un <span> en línea, sin alterar la composición.
  for (const el of [sec, ...sec.querySelectorAll('*')]) {
    if (el.hasAttribute('data-pseudo') || el.tagName === 'PRE' || el.closest('pre')) continue;
    const nodos = [...el.childNodes];
    const bloque = n => n.nodeType === 1 && (n.hasAttribute('data-pseudo') || getComputedStyle(n).display !== 'inline');
    if (!nodos.some(bloque)) continue;
    if (!nodos.some(n => n.nodeType === 3 && n.textContent.trim())) continue;
    let tramo = [];
    const cerrar = () => {
      if (tramo.some(n => n.textContent.trim())) {
        const sp = document.createElement('span'); sp.setAttribute('data-tramo', '1');
        el.insertBefore(sp, tramo[0]); tramo.forEach(n => sp.appendChild(n));
      }
      tramo = [];
    };
    for (const n of nodos) { if (bloque(n)) cerrar(); else tramo.push(n); }
    cerrar();
  }
  if (!document.getElementById('sin-pseudos')) {
    const st = document.createElement('style'); st.id = 'sin-pseudos';
    st.textContent = '[data-ph]::before,[data-ph]::after{content:none!important;display:none!important}';
    document.head.appendChild(st);
  }
  const B = sec.getBoundingClientRect();
  const R = el => { const r = el.getBoundingClientRect(); return {x: r.left - B.left, y: r.top - B.top, w: r.width, h: r.height}; };
  const visible = c => c && c !== 'transparent' && !/rgba\(.*,\s*0\)$/.test(c);
  const INLINE = new Set(['SPAN','B','STRONG','I','EM','CODE','BR','A','SMALL','SUP','SUB','U','MARK']);
  const items = [];
  let iconos = 0;

  function runs(el, pre) {
    const out = [];
    (function walk(n) {
      for (const c of n.childNodes) {
        if (c.nodeType === 1 && c.hasAttribute('data-pseudo')) continue;
        if (c.nodeType === 3) {
          let t = c.textContent;
          if (!pre) t = t.replace(/[ \n\r\t]+/g, ' ');
          if (!t) continue;
          const cs = getComputedStyle(c.parentElement);
          if (cs.textTransform === 'uppercase') t = t.toUpperCase();
          out.push({text: t, color: cs.color, weight: parseInt(cs.fontWeight), italic: cs.fontStyle === 'italic',
                    family: cs.fontFamily, size: parseFloat(cs.fontSize),
                    ls: cs.letterSpacing === 'normal' ? 0 : parseFloat(cs.letterSpacing),
                    bg: visible(cs.backgroundColor) && c.parentElement !== el ? cs.backgroundColor : null});
        } else if (c.nodeType === 1) {
          if (c.tagName === 'BR') out.push({br: true});
          else walk(c);
        }
      }
    })(el);
    if (!pre && out.length) {   // recorta espacios al inicio y al final del bloque
      const f = out.find(r => !r.br); if (f) f.text = f.text.replace(/^ /, '');
      const l = [...out].reverse().find(r => !r.br); if (l) l.text = l.text.replace(/ $/, '');
    }
    return out.filter(r => r.br || r.text);
  }

  const reales = el => [...el.childNodes].filter(n => !(n.nodeType === 1 && n.hasAttribute('data-pseudo')));
  function esBloqueTexto(el) {
    let texto = false;
    for (const c of reales(el)) {
      if (c.nodeType === 3 && c.textContent.trim()) texto = true;
      if (c.nodeType === 1) {
        if (!INLINE.has(c.tagName) || getComputedStyle(c).display !== 'inline') return false;
        if (c.textContent.trim()) texto = true;
      }
    }
    return texto;
  }

  function forma(el, cs, r) {
    const lados = ['Top','Right','Bottom','Left'].map(s => ({w: parseFloat(cs['border'+s+'Width']) || 0,
      c: cs['border'+s+'Color'], st: cs['border'+s+'Style']}));
    const fondo = visible(cs.backgroundColor) ? cs.backgroundColor : null;
    const conBorde = lados.filter(l => l.w > 0 && l.st !== 'none' && visible(l.c));
    if (!fondo && !conBorde.length) return;
    const radio = parseFloat(cs.borderTopLeftRadius) || 0;
    const iguales = conBorde.length === 4 && conBorde.every(l => l.w === conBorde[0].w && l.c === conBorde[0].c);
    items.push({t: 'shape', ...r, fill: fondo, radius: radio,
                line: iguales ? {w: conBorde[0].w, c: conBorde[0].c, dash: conBorde[0].st === 'dashed'} : null});
    if (!iguales) {
      const [T, Rt, Bt, L] = lados;
      if (T.w && T.st !== 'none' && visible(T.c)) items.push({t: 'shape', x: r.x, y: r.y, w: r.w, h: T.w, fill: T.c, radius: 0});
      if (Bt.w && Bt.st !== 'none' && visible(Bt.c)) items.push({t: 'shape', x: r.x, y: r.y + r.h - Bt.w, w: r.w, h: Bt.w, fill: Bt.c, radius: 0});
      if (L.w && L.st !== 'none' && visible(L.c)) items.push({t: 'shape', x: r.x, y: r.y, w: L.w, h: r.h, fill: L.c, radius: 0});
      if (Rt.w && Rt.st !== 'none' && visible(Rt.c)) items.push({t: 'shape', x: r.x + r.w - Rt.w, y: r.y, w: Rt.w, h: r.h, fill: Rt.c, radius: 0});
    }
  }

  function conectores(svg) {
    const rs = svg.getBoundingClientRect(), esc = rs.width / 1920, ox = rs.left - B.left, oy = rs.top - B.top;
    for (const p of svg.querySelectorAll('path')) {
      if (p.closest('marker')) continue;
      const d = p.getAttribute('d'); const pts = []; let x = 0, y = 0;
      const tok = d.match(/[MLHV]|-?[\d.]+/g); let i = 0;
      while (i < tok.length) {
        const c = tok[i++];
        if (c === 'M' || c === 'L') { x = +tok[i++]; y = +tok[i++]; }
        else if (c === 'H') x = +tok[i++];
        else if (c === 'V') y = +tok[i++];
        pts.push([x, y]);
      }
      for (const q of pts) { q[0] = ox + q[0] * esc; q[1] = oy + q[1] * esc; }
      items.push({t: 'line', pts, color: getComputedStyle(p).stroke, w: parseFloat(p.getAttribute('stroke-width')) * esc,
                  dash: !!p.getAttribute('stroke-dasharray'), end: !!p.getAttribute('marker-end'), start: !!p.getAttribute('marker-start')});
    }
  }

  function pseudo(c) {
    const cs = getComputedStyle(c); const r = R(c);
    if (r.w === 0 && r.h === 0) return;
    forma(c, cs, r);
    if (c.textContent.trim()) items.push({t: 'text', x: r.x, y: r.y, w: r.w, h: r.h, align: cs.textAlign,
      lh: cs.lineHeight === 'normal' ? 1.2 : parseFloat(cs.lineHeight) / parseFloat(cs.fontSize), pre: false, runs: runs(c, false)});
  }
  function walk(el) {
    for (const c of el.children) {
      if (c.tagName === 'ASIDE' || c.classList.contains('notes') || c.id === 'pasos') continue;
      const cs = getComputedStyle(c);
      if (cs.display === 'none' || cs.visibility === 'hidden' || parseFloat(cs.opacity) === 0) continue;
      if (c.hasAttribute('data-pseudo')) { pseudo(c); continue; }
      if (c.tagName === 'IMG') { items.push({t: 'img', src: c.currentSrc || c.src, ...R(c)}); continue; }
      if (c.tagName.toLowerCase() === 'svg') {
        if (c.querySelector('marker') || c.getAttribute('width') === '1920') conectores(c);
        else { c.setAttribute('data-icono', String(iconos)); items.push({t: 'image', id: iconos++, ...R(c)}); }
        continue;
      }
      const r = R(c);
      if (r.w === 0 && r.h === 0) continue;
      forma(c, cs, r);
      if (esBloqueTexto(c)) {
        const pl = parseFloat(cs.paddingLeft) + parseFloat(cs.borderLeftWidth), pr = parseFloat(cs.paddingRight) + parseFloat(cs.borderRightWidth);
        const pt = parseFloat(cs.paddingTop) + parseFloat(cs.borderTopWidth), pb = parseFloat(cs.paddingBottom) + parseFloat(cs.borderBottomWidth);
        const pre = cs.whiteSpace.startsWith('pre') || getComputedStyle(c.parentElement).whiteSpace.startsWith('pre');
        const lh = cs.lineHeight === 'normal' ? 1.2 : parseFloat(cs.lineHeight) / parseFloat(cs.fontSize);
        for (const p of c.querySelectorAll(':scope > [data-pseudo]')) pseudo(p);
        let x = r.x + pl, y = r.y + pt, w = r.w - pl - pr, h = r.h - pt - pb;
        const rs = reales(c).filter(n => n.nodeType !== 3 || n.textContent.trim());
        if (rs.length && !pre) {     // la caja real del texto (después de viñetas, filetes o puntos)
          const rg = document.createRange(); rg.setStartBefore(rs[0]); rg.setEndAfter(rs[rs.length - 1]);
          const q = rg.getBoundingClientRect();
          if (q.width > 0) {
            y = q.top - B.top; h = q.height;
            if (cs.textAlign === 'start' || cs.textAlign === 'left') { const fin = x + w; x = Math.min(q.left - B.left, fin - 4); w = fin - x; }
          }
        }
        items.push({t: 'text', x, y, w, h, align: cs.textAlign, lh, pre, runs: runs(c, pre)});
        for (const p of c.querySelectorAll(':scope > [data-pseudo]')) {}
        continue;
      }
      walk(c);
    }
  }
  walk(sec);
  const chrome = document.getElementById('deck-chrome'); if (chrome) walk(chrome);
  if (prog) forma(prog, getComputedStyle(prog), R(prog));
  const notas = sec.querySelector('.notes');
  const bgSec = getComputedStyle(sec).backgroundColor;
  return {bg: visible(bgSec) ? bgSec : getComputedStyle(document.body).backgroundColor, hero,
          notes: notas ? notas.textContent.trim().replace(/\s+/g, ' ') : '', items, iconos};
}
"""


def leer_imagen(src: str, ancho: float) -> str:
    """El logotipo se reduce a 3 veces su tamaño en pantalla: se repite en cada slide y así el PPTX pesa poco."""
    import io
    from PIL import Image
    datos = base64.b64decode(src.split(",", 1)[1]) if src.startswith("data:") else Path(unquote(urlparse(src).path)).read_bytes()
    im = Image.open(io.BytesIO(datos))
    w = max(1, int(ancho * 3))
    if im.width > w:
        im = im.resize((w, round(im.height * w / im.width)), Image.LANCZOS)
    out = io.BytesIO(); im.save(out, "PNG", optimize=True)
    return base64.b64encode(out.getvalue()).decode()


async def main() -> None:
    async with async_playwright() as p:
        b = await p.chromium.launch()
        pg = await b.new_page(viewport={"width": ANCHO, "height": ALTO})
        await pg.goto(HTML.as_uri())
        await pg.wait_for_timeout(800)
        await pg.add_style_tag(content=MEDIDA)
        await pg.evaluate("document.fonts.ready")
        n = await pg.evaluate("document.querySelectorAll('.slide').length")
        diapositivas = []
        for i in range(n):
            d = await pg.evaluate(JS, i)
            d["ancho"] = ANCHO
            for it in d["items"]:
                if it["t"] == "image":       # iconos y formas en SVG: se toman como imagen
                    png = await pg.locator(f".slide.active svg[data-icono='{it['id']}']").screenshot(scale="device")
                    it["png"] = base64.b64encode(png).decode()
                if it["t"] == "img":
                    it["png"] = leer_imagen(it.pop("src"), it["w"])
            if d["hero"]:     # el degradado de la portada va como imagen de fondo
                h = await pg.add_style_tag(content=FONDO)
                d["bgimg"] = base64.b64encode(await pg.screenshot(type="jpeg", quality=88)).decode()
                await h.evaluate("e => e.remove()")
            diapositivas.append(d)
        await b.close()
    SALIDA.write_text(json.dumps(diapositivas, ensure_ascii=False), encoding="utf-8")
    print(n, "slides extraídas de", HTML.name)


asyncio.run(main())
