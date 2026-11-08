/*
 * Interacción de la interfaz (sin algoritmos numéricos).
 */
(function () {
  "use strict";

  document.addEventListener("DOMContentLoaded", () => {
    // Fórmulas con KaTeX
    if (window.renderMathInElement) {
      renderMathInElement(document.body, {
        delimiters: [
          { left: "$$", right: "$$", display: true },
          { left: "\\(", right: "\\)", display: false },
        ],
        throwOnError: false,
      });
    }

    // Recordar la pestaña activa de cada módulo
    const clave = "pestana:" + window.location.pathname;
    try {
      const guardada = localStorage.getItem(clave);
      if (guardada && window.bootstrap) {
        const boton = document.querySelector(`[data-bs-target="${guardada}"]`);
        if (boton) bootstrap.Tab.getOrCreateInstance(boton).show();
      }
    } catch (e) { /* almacenamiento no disponible */ }
    document.querySelectorAll('[data-bs-toggle="tab"]').forEach((b) => {
      b.addEventListener("shown.bs.tab", (ev) => {
        try { localStorage.setItem(clave, ev.target.dataset.bsTarget); } catch (e) { /* nada */ }
      });
    });

    iniciarPresentaciones();

    // Botón "restablecer" que vuelve a los valores por defecto
    document.querySelectorAll("[data-restablecer]").forEach((b) => {
      b.addEventListener("click", () => { window.location = window.location.pathname; });
    });
  });

  /* ------------------------- Modo presentación ------------------------- */
  function iniciarPresentaciones() {
    const presentaciones = document.querySelectorAll(".presentacion");
    if (!presentaciones.length || !window.bootstrap) return;

    presentaciones.forEach((sec) => {
      const carrusel = sec.querySelector(".carousel");
      const items = carrusel.querySelectorAll(".carousel-item");
      const puntos = sec.querySelector("[data-puntos]");
      const contador = sec.querySelector("[data-contador]");
      const progreso = sec.querySelector("[data-progreso]");
      const control = bootstrap.Carousel.getOrCreateInstance(carrusel, { interval: false, wrap: false, keyboard: false });

      items.forEach((_, i) => {
        const b = document.createElement("button");
        b.type = "button";
        b.title = `Diapositiva ${i + 1}`;
        b.addEventListener("click", () => control.to(i));
        puntos.appendChild(b);
      });

      const actualizar = () => {
        const i = Array.from(items).findIndex((it) => it.classList.contains("active"));
        contador.textContent = `${i + 1} / ${items.length}`;
        progreso.style.width = `${((i + 1) / items.length) * 100}%`;
        puntos.querySelectorAll("button").forEach((b, j) => b.classList.toggle("activo", j === i));
      };
      carrusel.addEventListener("slid.bs.carousel", () => {
        actualizar();
        const i = Array.from(items).findIndex((it) => it.classList.contains("active"));
        history.replaceState(null, "", `#diapositiva-${i + 1}`);
      });
      // Abrir directamente una diapositiva: .../integracion/#diapositiva-5
      const m = /^#diapositiva-(\d+)$/.exec(window.location.hash);
      if (m) {
        const destino = Math.min(Math.max(parseInt(m[1], 10), 1), items.length) - 1;
        items.forEach((it, j) => it.classList.toggle("active", j === destino));
        // Dibuja las gráficas de la diapositiva que acaba de hacerse visible
        document.dispatchEvent(new Event("slid.bs.carousel"));
      }
      actualizar();

      // Navegación con teclado (también funciona con presentadores/clickers: PageUp/PageDown)
      document.addEventListener("keydown", (ev) => {
        const tag = (ev.target.tagName || "").toLowerCase();
        if (tag === "input" || tag === "select" || tag === "textarea" || ev.target.isContentEditable) return;
        if (presentaciones.length > 1 && !sec.contains(document.activeElement) && document.fullscreenElement !== sec) return;
        if (["ArrowRight", "PageDown"].includes(ev.key)) { ev.preventDefault(); control.next(); }
        else if (["ArrowLeft", "PageUp"].includes(ev.key)) { ev.preventDefault(); control.prev(); }
        else if (ev.key === "Home") control.to(0);
        else if (ev.key === "End") control.to(items.length - 1);
        else if (ev.key.toLowerCase() === "f") alternarPantallaCompleta(sec);
      });
    });

    document.querySelectorAll("[data-pantalla-completa]").forEach((b) => {
      b.addEventListener("click", () => alternarPantallaCompleta(document.querySelector(b.dataset.pantallaCompleta)));
    });

    // Nombre del expositor editable y recordado en este navegador
    document.querySelectorAll("[data-guardar]").forEach((el) => {
      const clave = "expositor:" + el.dataset.guardar;
      try { const v = localStorage.getItem(clave); if (v) el.textContent = v; } catch (e) { /* nada */ }
      el.addEventListener("input", () => { try { localStorage.setItem(clave, el.textContent.trim()); } catch (e) { /* nada */ } });
      el.addEventListener("keydown", (ev) => { if (ev.key === "Enter") { ev.preventDefault(); el.blur(); } });
    });
  }

  function alternarPantallaCompleta(elemento) {
    if (!elemento) return;
    if (document.fullscreenElement) document.exitFullscreen();
    else if (elemento.requestFullscreen) elemento.requestFullscreen();
    elemento.focus();
  }
})();
