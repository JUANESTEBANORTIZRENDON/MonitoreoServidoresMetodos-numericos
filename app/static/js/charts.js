/*
 * Renderizado de gráficas. Los datos YA vienen calculados desde el backend
 * (Flask + metodos_numericos); aquí solo se traducen a la configuración de Chart.js.
 */
(function () {
  "use strict";

  function convertirSerie(s, tipoGrafica) {
    const color = s.color || "#0d3b66";
    const ds = {
      label: s.nombre,
      data: s.datos,
      borderColor: color,
      backgroundColor: Array.isArray(color) ? color : color,
      borderWidth: s.grosor || 2,
      pointRadius: s.radio !== undefined ? s.radio : (tipoGrafica === "line" && s.datos.length > 60 ? 0 : 3),
      pointHoverRadius: (s.radio || 3) + 2,
      spanGaps: false,
      tension: 0,
    };
    if (s.discontinua) ds.borderDash = [6, 4];
    if (s.estilo) ds.pointStyle = s.estilo;
    if (s.relleno) { ds.fill = true; ds.backgroundColor = "rgba(13,59,102,0.12)"; }
    if (s.eje === "y2") ds.yAxisID = "y2";
    if (tipoGrafica === "scatter") ds.showLine = !!s.linea;
    return ds;
  }

  function crearConfig(g) {
    const datasets = g.series.map((s) => convertirSerie(s, g.tipo));
    if (g.lineas_umbral && g.labels) {
      const colores = ["#f4a259", "#e76f51"];
      g.lineas_umbral.forEach((u, i) => {
        datasets.push({
          label: `Umbral ${u} °C`, data: g.labels.map(() => u), borderColor: colores[i % 2],
          borderDash: [4, 4], borderWidth: 1.5, pointRadius: 0, yAxisID: "y",
        });
      });
    }
    const escalas = {
      x: {
        type: g.tipo === "scatter" ? "linear" : "category",
        title: { display: true, text: g.x_titulo },
        ticks: { maxTicksLimit: 12, autoSkip: true },
      },
      y: {
        type: g.log ? "logarithmic" : "linear",
        title: { display: true, text: g.y_titulo },
        beginAtZero: g.tipo === "bar" && g.cero !== false,
      },
    };
    if (g.y2_titulo) {
      escalas.y2 = { position: "right", title: { display: true, text: g.y2_titulo },
                     grid: { drawOnChartArea: false } };
    }
    return {
      type: g.tipo,
      data: { labels: g.labels, datasets: datasets },
      options: {
        responsive: true, maintainAspectRatio: false, animation: false,
        interaction: { mode: g.tipo === "scatter" ? "nearest" : "index", intersect: false },
        plugins: {
          title: { display: true, text: g.titulo, color: "#0d3b66", font: { size: 14, weight: "600" } },
          legend: { display: g.tipo !== "bar" || g.series.length > 1, position: "bottom" },
          tooltip: {
            callbacks: {
              label: (ctx) => {
                const v = ctx.parsed.y;
                if (v === null || v === undefined) return `${ctx.dataset.label}: sin dato`;
                const x = g.tipo === "scatter" ? `x = ${ctx.parsed.x.toFixed(5)}, ` : "";
                return `${ctx.dataset.label}: ${x}${Number(v).toFixed(5)}`;
              },
            },
          },
        },
        scales: escalas,
      },
    };
  }

  function renderizar() {
    if (typeof Chart === "undefined") return;
    document.querySelectorAll("script[data-grafica-para]").forEach((nodo) => {
      const canvas = document.getElementById(nodo.dataset.graficaPara);
      if (!canvas || canvas.dataset.renderizado) return;
      // Las gráficas en diapositivas o pestañas ocultas se dibujan al hacerse visibles
      if (canvas.offsetParent === null) return;
      try {
        const g = JSON.parse(nodo.textContent);
        new Chart(canvas, crearConfig(g));
        canvas.dataset.renderizado = "1";
      } catch (e) {
        console.error("No se pudo dibujar la gráfica", e);
      }
    });
  }

  document.addEventListener("DOMContentLoaded", renderizar);
  // Las gráficas dentro de pestañas ocultas se dibujan cuando se muestran
  ["shown.bs.tab", "slid.bs.carousel", "fullscreenchange"].forEach((evento) => {
    document.addEventListener(evento, () => {
      renderizar();
      window.dispatchEvent(new Event("resize"));
    });
  });
})();
