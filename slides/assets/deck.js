/* ============================================================
   TEC EDITORIAL · Motor de navegación de decks INSPIRA
   ------------------------------------------------------------
   Inyecta el cromo (barra de progreso, logotipo, folio) para que
   los decks no tengan que declararlo en su markup.

   Teclas:  → / espacio / PageDown  avanzar (primero los pasos de animación)
            ← / PageUp              retroceder (paso a paso)
            ↓ / ↑                   saltar a la slide siguiente / anterior
            A                       reproducir la animación sola, en bucle
            Home / End              primera / última
            N                       notas del orador
            D                       modo oscuro
            F                       pantalla completa

   Ratón:   doble clic              avanzar
            (el clic simple no avanza, para poder seleccionar texto en clase)

   Etiqueta del deck: <body data-deck="Módulo 1 · Clase 2 — …">
   Ruta del logotipo: <body data-logo="assets/logo-tec.png">
   ============================================================ */
(function () {
  'use strict';

  var LOGO_DEFAULT = 'assets/logo-tec.png';
  var LOGO_BLANCO = 'assets/logo-tec-blanco.png';

  function build() {
    var slides = [].slice.call(document.querySelectorAll('.slide'));
    if (!slides.length) return;

    // --- Cromo ---
    if (!document.getElementById('progress')) {
      var p = document.createElement('div');
      p.id = 'progress';
      document.body.appendChild(p);
    }

    var chrome = document.getElementById('deck-chrome');
    if (!chrome) {
      chrome = document.createElement('div');
      chrome.id = 'deck-chrome';

      var brand = document.createElement('div');
      brand.className = 'brand';

      var logoSrc = document.body.getAttribute('data-logo') || LOGO_DEFAULT;
      if (logoSrc) {
        var img = document.createElement('img');
        img.src = logoSrc;
        img.alt = 'Tecnológico de Monterrey';
        img.setAttribute('data-azul', logoSrc);
        img.setAttribute('data-blanco', document.body.getAttribute('data-logo-blanco') || LOGO_BLANCO);
        // Si el logotipo no carga, se retira en silencio: el deck sigue usable.
        img.onerror = function () { img.remove(); };
        brand.appendChild(img);
      }

      var label = document.body.getAttribute('data-deck');
      if (label) {
        var span = document.createElement('span');
        span.className = 'deck-label';
        span.textContent = label;
        brand.appendChild(span);
      }

      chrome.appendChild(brand);

      var counter = document.getElementById('counter');
      if (!counter) {
        counter = document.createElement('div');
        counter.id = 'counter';
      }
      chrome.appendChild(counter);
      document.body.appendChild(chrome);
    }

    var progress = document.getElementById('progress');
    var counterEl = document.getElementById('counter');
    var i = 0;

    // --- Pasos de animación dentro de una slide ---
    // [data-step="n"]  aparece al llegar al paso n (oculto antes).
    // [data-mark="n"]  siempre visible; recibe .on desde el paso n.
    // Ambos reciben .actual exactamente en su paso.
    // La slide recibe las clases p1…pN acumuladas y el atributo data-paso,
    // y emite el evento 'paso' ({paso, total}) para animaciones con JS.
    // data-steps="N" (en la slide o en un hijo) fija el total cuando la
    // animación es solo JS.
    var s = 0;
    var pasosEl = document.createElement('span');
    pasosEl.id = 'pasos';
    if (counterEl) counterEl.parentNode.insertBefore(pasosEl, counterEl);

    function totalPasos(slide) {
      var t = parseInt(slide.getAttribute('data-steps') || '0', 10) || 0;
      var decl = slide.querySelectorAll('[data-steps]');
      for (var d = 0; d < decl.length; d++) t = Math.max(t, parseInt(decl[d].getAttribute('data-steps'), 10) || 0);
      var els = slide.querySelectorAll('[data-step],[data-mark]');
      for (var k = 0; k < els.length; k++) {
        var v = parseInt(els[k].getAttribute('data-step') || els[k].getAttribute('data-mark'), 10);
        if (v > t) t = v;
      }
      return t;
    }

    function aplicarPaso(slide, paso) {
      var total = totalPasos(slide);
      paso = Math.max(0, Math.min(total, paso));
      var els = slide.querySelectorAll('[data-step],[data-mark]');
      for (var k = 0; k < els.length; k++) {
        var v = parseInt(els[k].getAttribute('data-step') || els[k].getAttribute('data-mark'), 10);
        els[k].classList.toggle('on', paso >= v);
        els[k].classList.toggle('actual', paso === v);
      }
      for (var q = 1; q <= Math.max(total, 12); q++) slide.classList.toggle('p' + q, q <= paso);
      slide.setAttribute('data-paso', paso);
      var ev;
      try { ev = new CustomEvent('paso', { detail: { paso: paso, total: total } }); }
      catch (e) { ev = document.createEvent('CustomEvent'); ev.initCustomEvent('paso', false, false, { paso: paso, total: total }); }
      slide.dispatchEvent(ev);
      return paso;
    }

    function pintarPasos() {
      var total = totalPasos(slides[i]);
      if (!total) { pasosEl.innerHTML = ''; return; }
      var h = '';
      for (var k = 1; k <= total; k++) h += '<i class="' + (k <= s ? 'lleno' : '') + '"></i>';
      pasosEl.innerHTML = (auto ? '<b>▶ auto</b>' : '') + h;
    }

    function show(n, alFinal) {
      i = Math.max(0, Math.min(slides.length - 1, n));
      for (var k = 0; k < slides.length; k++) {
        slides[k].classList.toggle('active', k === i);
      }
      if (progress) progress.style.width = ((i + 1) / slides.length * 100) + '%';
      if (counterEl) counterEl.textContent = (i + 1) + ' / ' + slides.length;

      // Portada de marca: fondo oscuro → logotipo y cromo en blanco
      var esHero = slides[i].classList.contains('hero');
      document.body.classList.toggle('hero-activo', esHero);
      var logo = document.querySelector('#deck-chrome img');
      if (logo) {
        var quiere = esHero ? logo.getAttribute('data-blanco') : logo.getAttribute('data-azul');
        if (quiere && logo.getAttribute('src') !== quiere) logo.setAttribute('src', quiere);
      }

      if (history.replaceState) history.replaceState(null, '', '#' + (i + 1));
      else location.hash = i + 1;
      startTimer(slides[i]);
      s = aplicarPaso(slides[i], alFinal ? totalPasos(slides[i]) : 0);
      pintarPasos();
    }

    // Avanzar/retroceder: primero los pasos de la slide, luego la slide.
    function siguiente() {
      if (s < totalPasos(slides[i])) { s = aplicarPaso(slides[i], s + 1); pintarPasos(); }
      else show(i + 1);
    }
    function anterior() {
      if (s > 0) { s = aplicarPaso(slides[i], s - 1); pintarPasos(); }
      else show(i - 1, true);
    }

    // --- Reproducción automática (tecla A) ---
    // Recorre los pasos de la slide actual y vuelve a empezar en bucle.
    // Nunca cambia de slide por sí sola. Se detiene al navegar a mano.
    var auto = null;
    var AUTO_MS = parseInt(document.body.getAttribute('data-auto-ms') || '2200', 10);
    function pararAuto() { if (auto) { clearInterval(auto); auto = null; pintarPasos(); } }
    function alternarAuto() {
      if (auto) { pararAuto(); return; }
      if (!totalPasos(slides[i])) return;
      if (s >= totalPasos(slides[i])) s = aplicarPaso(slides[i], 0);
      auto = setInterval(function () {
        var t = totalPasos(slides[i]);
        s = aplicarPaso(slides[i], s >= t ? 0 : s + 1);
        pintarPasos();
      }, AUTO_MS);
      pintarPasos();
    }

    // Al imprimir, cada slide sale en su estado final.
    window.addEventListener('beforeprint', function () {
      pararAuto();
      document.body.classList.add('imprimiendo');
      slides.forEach(function (sl) { aplicarPaso(sl, totalPasos(sl)); });
    });
    window.addEventListener('afterprint', function () {
      document.body.classList.remove('imprimiendo');
      slides.forEach(function (sl, k) { if (k !== i) aplicarPaso(sl, 0); });
      s = aplicarPaso(slides[i], s);
    });

    // --- Cuenta regresiva de descanso ---
    // El atributo data-timer (en minutos) puede ir en la <section class="slide">
    // o en el propio <div class="countdown">.
    var tick = null;
    function startTimer(slide) {
      if (tick) { clearInterval(tick); tick = null; }
      var el = slide.querySelector('.countdown');
      if (!el) return;
      var mins = slide.getAttribute('data-timer') || el.getAttribute('data-timer');
      if (!mins) return;
      var total = parseFloat(mins) * 60;
      var end = Date.now() + total * 1000;
      function paint() {
        var left = Math.max(0, Math.round((end - Date.now()) / 1000));
        var m = Math.floor(left / 60), s = left % 60;
        el.textContent = m + ':' + (s < 10 ? '0' : '') + s;
        if (left <= 0 && tick) { clearInterval(tick); tick = null; }
      }
      paint();
      tick = setInterval(paint, 1000);
    }

    // --- Modo oscuro (tecla D), recordado entre sesiones si el navegador lo permite ---
    function alternarOscuro(forzar) {
      var activo = typeof forzar === 'boolean'
        ? forzar
        : !document.body.classList.contains('oscuro');
      document.body.classList.toggle('oscuro', activo);
      try { localStorage.setItem('tec-deck-oscuro', activo ? '1' : '0'); } catch (e) { /* file:// sin storage */ }
    }
    try {
      if (localStorage.getItem('tec-deck-oscuro') === '1') alternarOscuro(true);
    } catch (e) { /* sin storage: arranca en claro */ }

    // --- Teclado ---
    document.addEventListener('keydown', function (e) {
      if (e.metaKey || e.ctrlKey || e.altKey) return;
      // Controles interactivos dentro de una slide (p.ej. un slider) conservan sus teclas.
      if (e.target && e.target.closest && e.target.closest('input, select, textarea, [contenteditable]')) return;
      var k = e.key;
      if (k === 'ArrowRight' || k === ' ' || k === 'PageDown') { e.preventDefault(); pararAuto(); siguiente(); }
      else if (k === 'ArrowLeft' || k === 'PageUp') { e.preventDefault(); pararAuto(); anterior(); }
      else if (k === 'ArrowDown') { e.preventDefault(); pararAuto(); show(i + 1); }
      else if (k === 'ArrowUp') { e.preventDefault(); pararAuto(); show(i - 1); }
      else if (k === 'Home') { e.preventDefault(); pararAuto(); show(0); }
      else if (k === 'End') { e.preventDefault(); pararAuto(); show(slides.length - 1); }
      else if (k === 'a' || k === 'A') { alternarAuto(); }
      else if (k === 'n' || k === 'N') { document.body.classList.toggle('show-notes'); }
      else if (k === 'd' || k === 'D') { alternarOscuro(); }
      else if (k === 'f' || k === 'F') {
        if (document.fullscreenElement) document.exitFullscreen();
        else if (document.documentElement.requestFullscreen) document.documentElement.requestFullscreen();
      }
    });

    // --- Doble clic para avanzar ---
    // El clic simple NO avanza: al seleccionar texto con el ratón para señalar
    // algo en clase, el navegador dispara un 'click' al soltar y la diapositiva
    // se iba sola. Con doble clic el gesto es deliberado y la selección libre.
    document.addEventListener('dblclick', function (e) {
      if (e.target.closest('a, .notes, #deck-chrome')) return;
      // El doble clic selecciona una palabra como efecto secundario: se limpia
      // para no arrastrar un resalte accidental a la diapositiva siguiente.
      var sel = window.getSelection && window.getSelection();
      if (sel && sel.removeAllRanges) sel.removeAllRanges();
      pararAuto();
      siguiente();
    });

    var start = parseInt((location.hash || '').slice(1), 10);
    show(isNaN(start) ? 0 : start - 1);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', build);
  } else {
    build();
  }
})();
