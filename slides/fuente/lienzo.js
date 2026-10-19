/* Láminas del módulo: cada una se dibujó en un lienzo de 1920 × 1080 px. Aquí se convierten sus
   conectores e iconos a SVG y el lienzo se escala para que quepa entre la banda superior y el pie. */
(() => {
  const NS = "http://www.w3.org/2000/svg";
  const ICONOS = {
    Check: '<path d="M20 6 9 17l-5-5"/>',
    CheckCircle: '<circle cx="12" cy="12" r="10"/><path d="m9 12 2 2 4-4"/>',
    Code: '<path d="m16 18 6-6-6-6"/><path d="m8 6-6 6 6 6"/>',
    Search: '<circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/>',
    Settings: '<circle cx="12" cy="12" r="3.5"/><path d="M12 2v3M12 19v3M4.9 4.9l2.1 2.1M17 17l2.1 2.1M2 12h3M19 12h3M4.9 19.1 7 17M17 7l2.1-2.1"/>',
    Warning: '<path d="M10.3 3.9 1.8 18a2 2 0 0 0 1.7 3h17a2 2 0 0 0 1.7-3L13.7 3.9a2 2 0 0 0-3.4 0z"/><path d="M12 9v4M12 17h.01"/>',
    Database: '<ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M3 5v14c0 1.7 4 3 9 3s9-1.3 9-3V5"/><path d="M3 12c0 1.7 4 3 9 3s9-1.3 9-3"/>',
    Globe: '<circle cx="12" cy="12" r="10"/><path d="M2 12h20"/><path d="M12 2a15 15 0 0 1 0 20a15 15 0 0 1 0-20"/>',
    PaperPlane: '<path d="m22 2-7 20-4-9-9-4z"/><path d="M22 2 11 13"/>'
  };

  // <x-icon>: iconos de línea en SVG
  document.querySelectorAll("x-icon").forEach(el => {
    const svg = document.createElementNS(NS, "svg");
    svg.setAttribute("viewBox", "0 0 24 24");
    svg.setAttribute("fill", "none");
    svg.setAttribute("stroke-width", "2");
    svg.setAttribute("stroke-linecap", "round");
    svg.setAttribute("stroke-linejoin", "round");
    svg.setAttribute("aria-hidden", "true");
    svg.style.cssText = el.style.cssText + ";flex-shrink:0";
    svg.style.stroke = el.style.color || "currentColor";
    svg.innerHTML = ICONOS[el.getAttribute("name")] || "";
    el.replaceWith(svg);
  });

  // <x-shape>: flechas y rombos como SVG que llenan su caja
  document.querySelectorAll("x-shape").forEach(el => {
    const tipo = el.getAttribute("kind"), est = el.style;
    const relleno = est.backgroundColor || "#4A5061";
    const svg = document.createElementNS(NS, "svg");
    svg.setAttribute("viewBox", "0 0 100 100");
    svg.setAttribute("preserveAspectRatio", "none");
    svg.style.cssText = el.style.cssText + ";background:none;border:none;flex-shrink:0";
    const formas = {
      "arrow-right": "0,30 60,30 60,0 100,50 60,100 60,70 0,70",
      "diamond": "50,2 98,50 50,98 2,50"
    };
    svg.innerHTML = `<polygon points="${formas[tipo] || formas.diamond}" style="fill:${relleno};stroke:${est.borderColor || "none"}" stroke-width="3" vector-effect="non-scaling-stroke"/>`;
    el.replaceWith(svg);
  });

  // <x-connector>: líneas con punta, en coordenadas de la diapositiva
  let n = 0;
  document.querySelectorAll(".lienzo").forEach(seccion => {
    const conectores = seccion.querySelectorAll("x-connector");
    if (!conectores.length) return;
    const svg = document.createElementNS(NS, "svg");
    svg.setAttribute("width", "1920"); svg.setAttribute("height", "1080");
    svg.style.cssText = "position:absolute;left:0;top:0;pointer-events:none;overflow:visible";
    let defs = "", trazos = "";
    conectores.forEach(c => {
      const [x1, y1, x2, y2] = ["x1", "y1", "x2", "y2"].map(a => parseFloat(c.getAttribute(a)));
      const color = c.style.color || "#4A5061";
      const ancho = parseFloat(c.style.borderWidth) || 2;
      const guiones = c.style.borderStyle === "dashed" ? `stroke-dasharray="${ancho * 4} ${ancho * 3}"` : "";
      const ruta = c.getAttribute("route") || "straight", punta = c.getAttribute("head") || "end";
      let d = `M${x1} ${y1} L${x2} ${y2}`;
      if (ruta === "hv") d = `M${x1} ${y1} H${x2} V${y2}`;
      if (ruta === "vh") d = `M${x1} ${y1} V${y2} H${x2}`;
      if (ruta === "elbow") {
        d = Math.abs(x2 - x1) >= Math.abs(y2 - y1)
          ? `M${x1} ${y1} H${(x1 + x2) / 2} V${y2} H${x2}`
          : `M${x1} ${y1} V${(y1 + y2) / 2} H${x2} V${y2}`;
      }
      const id = "punta" + (n++);
      defs += `<marker id="${id}" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="${4.5}" markerHeight="${4.5}" orient="auto-start-reverse"><path d="M0 0L10 5L0 10z" style="fill:${color}"/></marker>`;
      const fin = punta === "end" || punta === "both" ? `marker-end="url(#${id})"` : "";
      const inicio = punta === "both" ? `marker-start="url(#${id})"` : "";
      trazos += `<path d="${d}" fill="none" style="stroke:${color}" stroke-width="${ancho}" stroke-linecap="round" stroke-linejoin="round" ${guiones} ${fin} ${inicio}/>`;
      c.remove();
    });
    svg.innerHTML = `<defs>${defs}</defs>${trazos}`;
    seccion.appendChild(svg);
  });


  function ajustar() {
    const s = Math.min(innerWidth / 1920, innerHeight / 1080) * 0.9;
    document.querySelectorAll('.lienzo').forEach(l => {
      l.style.transform = 'scale(' + s + ')';
      l.style.left = ((innerWidth - 1920 * s) / 2) + 'px';
      l.style.top = (innerHeight * 0.075) + 'px';
    });
  }
  ajustar();
  addEventListener('resize', ajustar);
  addEventListener('beforeprint', ajustar);
})();
