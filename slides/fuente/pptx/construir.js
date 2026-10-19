// Construye un .pptx editable a partir de diapositivas.json (formas, textos, líneas e iconos con posición).
const fs = require("fs");
const pptxgen = require("pptxgenjs");
const { applyTheme } = require(process.env.SKILL + "/scripts/apply_theme.js");

const [, , entrada, salida, titulo] = process.argv;
const slides = JSON.parse(fs.readFileSync(entrada, "utf8"));
const ANCHO = slides[0].ancho || 1920;        // ancho en px de la ventana en que se midió
const IN = (px) => px * 13.333 / ANCHO;      // la diapositiva mide 13.333 in de ancho
const PT = (px) => px * 960 / ANCHO;         // y 960 pt

function color(c) {
  if (!c) return null;
  const s = c.match(/color\(srgb ([\d.]+) ([\d.]+) ([\d.]+)(?: \/ ([\d.]+))?\)/);   // color-mix() calculado
  if (s) c = `rgba(${s[1] * 255}, ${s[2] * 255}, ${s[3] * 255}, ${s[4] === undefined ? 1 : s[4]})`;
  const m = c.match(/rgba?\(([\d.]+),\s*([\d.]+),\s*([\d.]+)(?:,\s*([\d.]+))?\)/);
  if (!m) return null;
  const hex = [m[1], m[2], m[3]].map((v) => Math.round(+v).toString(16).padStart(2, "0")).join("").toUpperCase();
  const alpha = m[4] === undefined ? 1 : +m[4];
  return { hex, transparency: Math.round((1 - alpha) * 100) };
}

function fuente(family) {        // las fuentes de medición tienen las métricas de estas
  const primera = family.split(",")[0].replace(/["']/g, "").trim();
  if (/Mono|monospace/i.test(primera)) return "Courier New";
  if (/Serif|Charter|Georgia|^serif$/.test(primera)) return "Georgia";   // medido con DejaVu Serif Condensed, de ancho parecido
  return "Arial";
}

const THEME = {          // Tec Editorial: papel, tinta, azul Tec y los colores de los momentos INSPIRA
  name: "Tec Editorial · INSPIRA", headFontFace: "Georgia", bodyFontFace: "Arial",
  colors: { dk1: "16181D", lt1: "EDE8DC", dk2: "585E6F", lt2: "E3DCCB", accent1: "0033A0", accent2: "AC321E",
            accent3: "6B3FA0", accent4: "1B6A43", accent5: "7C560C", accent6: "0E6871", hlink: "0033A0", folHlink: "984514" },
};

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE";
pres.title = titulo;
pres.author = "Tecnológico de Monterrey · Next-Gen Coding";
pres.theme = { headFontFace: THEME.headFontFace, bodyFontFace: THEME.bodyFontFace };

for (const d of slides) {
  const s = pres.addSlide();
  d.id = "s" + (slides.indexOf(d) + 1);
  if (d.bgimg) s.background = { data: "image/jpeg;base64," + d.bgimg };
  else { const bg = color(d.bg); if (bg) s.background = { color: bg.hex }; }
  let n = 0;
  for (const it of d.items) {
    n++;
    if (it.t === "shape") {
      if (it.w < 0.5 || it.h < 0.5) continue;
      const f = color(it.fill);
      const opts = { x: IN(it.x), y: IN(it.y), w: IN(it.w), h: IN(it.h), objectName: `${d.id}-forma-${n}` };
      if (f && f.transparency < 100) opts.fill = { color: f.hex, transparency: f.transparency || undefined };
      else opts.fill = { type: "none" };
      if (it.line) {
        const l = color(it.line.c);
        opts.line = { color: l.hex, width: PT(it.line.w), dashType: it.line.dash ? "dash" : "solid" };
      } else opts.line = { type: "none" };
      let tipo = pres.ShapeType.rect;
      const minLado = Math.min(it.w, it.h);
      if (it.radius >= minLado / 2 - 1 && Math.abs(it.w - it.h) < 2) tipo = pres.ShapeType.ellipse;
      else if (it.radius > 0) { tipo = pres.ShapeType.roundRect; opts.rectRadius = IN(Math.min(it.radius, minLado / 2)); }
      s.addShape(tipo, opts);
    } else if (it.t === "line") {
      const c = color(it.color) || { hex: "4A5061" };
      for (let i = 0; i < it.pts.length - 1; i++) {
        const [x1, y1] = it.pts[i], [x2, y2] = it.pts[i + 1];
        if (x1 === x2 && y1 === y2) continue;
        const ultimo = i === it.pts.length - 2, primero = i === 0;
        s.addShape(pres.ShapeType.line, {
          x: IN(Math.min(x1, x2)), y: IN(Math.min(y1, y2)), w: IN(Math.abs(x2 - x1)), h: IN(Math.abs(y2 - y1)),
          flipH: x2 < x1, flipV: y2 < y1, objectName: `${d.id}-linea-${n}-${i}`,
          line: { color: c.hex, width: PT(it.w), dashType: it.dash ? "dash" : "solid",
                  endArrowType: it.end && ultimo ? "triangle" : undefined,
                  beginArrowType: it.start && primero ? "triangle" : undefined },
        });
      }
    } else if (it.t === "img") {
      s.addImage({ data: "image/png;base64," + it.png, x: IN(it.x), y: IN(it.y), w: IN(it.w), h: IN(it.h), objectName: `${d.id}-logo-${n}` });
    } else if (it.t === "image") {
      s.addImage({ data: "image/png;base64," + it.png, x: IN(it.x), y: IN(it.y), w: IN(it.w), h: IN(it.h), objectName: `${d.id}-icono-${n}` });
    } else if (it.t === "text") {
      const partes = [];
      for (const r of it.runs) {
        if (r.br) { if (partes.length) partes[partes.length - 1].options.breakLine = true; continue; }
        const c = color(r.color);
        const o = { color: c.hex, bold: r.weight >= 600, italic: r.italic, fontFace: fuente(r.family), fontSize: PT(r.size) };
        if (r.ls) o.charSpacing = PT(r.ls);
        if (r.bg) { const h = color(r.bg); if (h) o.highlight = h.hex; }
        if (it.pre) {   // en código, cada salto es un párrafo y los espacios iniciales no se colapsan
          r.text.split("\n").forEach((linea, k, todas) => {
            partes.push({ text: linea.replace(/ /g, "\u00a0"), options: { ...o, breakLine: k < todas.length - 1 } });
          });
          continue;
        }
        partes.push({ text: r.text, options: o });
      }
      if (!partes.length) continue;
      const alinea = { start: "left", left: "left", center: "center", right: "right", end: "right", justify: "left" }[it.align] || "left";
      // Holgura: Arial y Consolas no miden igual que las fuentes web; el cuadro crece hacia donde no altera la alineación
      let x = it.x, w = it.w;
      if (!it.pre) {
        const extra = Math.max(it.w * 0.06, 8);
        if (alinea === "left") w += extra;
        else if (alinea === "center") { x -= extra / 2; w += extra; }
        else { x -= extra; w += extra; }
      }
      const tamano = partes[0].options.fontSize;
      // Una sola línea medida en el navegador: no se deja partir, por si la fuente sustituta es más ancha
      const primera = it.runs.find(r => !r.br);
      const unaLinea = !it.runs.some(r => r.br) && it.h < primera.size * it.lh * 1.5;
      s.addText(partes, {
        x: IN(x), y: IN(it.y), w: IN(Math.max(w, 4)), h: IN(Math.max(it.h, 4)), margin: 0, align: alinea, valign: "top",
        lineSpacing: PT(partes.length ? it.runs.find(r => !r.br).size * it.lh : 24), paraSpaceBefore: 0, paraSpaceAfter: 0,
        wrap: !it.pre && !unaLinea, fit: "none", isTextBox: true, objectName: `${d.id}-texto-${n}`,
      });
    }
  }
  if (d.notes) s.addNotes(d.notes);
}

pres.writeFile({ fileName: salida }).then(async () => {
  await applyTheme(salida, THEME);
  console.log("escrito", salida, slides.length, "diapositivas");
});
