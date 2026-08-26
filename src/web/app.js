const NIVELES = ["Beginner", "Intermediate", "Advanced", "Unspecified"];
const CATEGORIAS = [
  "business english", "comprehension", "culture & tips", "english resource",
  "expressions", "grammar", "ielts", "pronunciation", "slang",
  "speaking", "vocabulary", "writing",
];

const estado = { pagina: 1, limite: 20, filtros: { nivel: "", categoria: "", texto: "", estado: "" } };
const charts = {};
let rolActual = "usuario";

function esc(s) {
  const div = document.createElement("div");
  div.textContent = s ?? "";
  return div.innerHTML;
}

async function fetchJSON(url, opts) {
  const resp = await fetch(url, opts);
  if (!resp.ok) {
    const data = await resp.json().catch(() => ({}));
    throw new Error(data.detail || "Error del servidor");
  }
  return resp.json();
}

function fmtNota(n) { return n == null ? "—" : Number(n).toFixed(2); }

// ---------- Pestañas ----------
document.querySelectorAll(".tab").forEach((btn) => {
  btn.addEventListener("click", () => {
    document.querySelectorAll(".tab").forEach((b) => b.classList.remove("active"));
    document.querySelectorAll(".panel").forEach((p) => p.classList.remove("active"));
    btn.classList.add("active");
    document.getElementById(btn.dataset.tab).classList.add("active");
  });
});

// ---------- Resumen ----------
async function cargarResumen() {
  const el = document.getElementById("cards");
  const insEl = document.getElementById("insights");
  try {
    const [r, rch, ins] = await Promise.all([
      fetchJSON("/api/resumen"),
      fetchJSON("/api/racha"),
      fetchJSON("/api/insights"),
    ]);
    const cards = [
      { clase: "acento", etiqueta: "Videos totales", valor: r.total },
      { clase: "ok", etiqueta: "Vistos", valor: r.vistos },
      { clase: "warn", etiqueta: "Pendientes", valor: r.pendientes },
      { clase: "acento", etiqueta: "% Completado", valor: r.porcentaje + "%" },
      { clase: "ok", etiqueta: "Racha (días)", valor: rch.actual },
      { clase: "", etiqueta: "Promedio general", valor: r.promedio == null ? "—" : Number(r.promedio).toFixed(2) },
    ];
    el.innerHTML = cards.map((c) => `
      <div class="card ${c.clase}">
        <div class="valor">${esc(c.valor)}</div>
        <div class="etiqueta">${esc(c.etiqueta)}</div>
      </div>`).join("");

    insEl.innerHTML = ins.length
      ? `<div class="insights-box">${ins.map((i) => `<p>💡 ${esc(i)}</p>`).join("")}</div>`
      : "";
  } catch (e) {
    el.innerHTML = `<div class="mensaje error">${esc(e.message)}</div>`;
  }
}

// ---------- Gráficos ----------
const centroTexto = {
  id: "centroTexto",
  afterDatasetsDraw(chart) {
    const { ctx } = chart;
    const meta = chart.getDatasetMeta(0);
    if (!meta.data.length) return;
    const { x, y } = meta.data[0];
    const texto = chart.config.options.plugins.centroTexto;
    if (!texto) return;
    ctx.save();
    ctx.textAlign = "center";
    ctx.textBaseline = "middle";
    ctx.font = "bold 34px Segoe UI, sans-serif";
    ctx.fillStyle = "#e2e8f0";
    ctx.fillText(texto.linea1, x, y - 10);
    ctx.font = "14px Segoe UI, sans-serif";
    ctx.fillStyle = "#94a3b8";
    ctx.fillText(texto.linea2, x, y + 20);
    ctx.restore();
  },
};

function crearOActualizar(id, config) {
  if (charts[id]) charts[id].destroy();
  const ctx = document.getElementById(id).getContext("2d");
  charts[id] = new Chart(ctx, config);
}

async function cargarGraficos() {
  try {
    const [r, stats] = await Promise.all([
      fetchJSON("/api/resumen"),
      fetchJSON("/api/quiz-stats"),
    ]);
    crearOActualizar("chartGlobal", {
      type: "doughnut",
      data: {
        labels: ["Vistos", "Pendientes"],
        datasets: [{
          data: [r.vistos, r.pendientes],
          backgroundColor: ["#22c55e", "#334155"],
          borderColor: "#0f172a",
          borderWidth: 2,
        }],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        cutout: "65%",
        plugins: {
          legend: { position: "bottom", labels: { color: "#e2e8f0", padding: 16, font: { size: 13 } } },
          centroTexto: { linea1: r.porcentaje + "%", linea2: "completado" },
        },
      },
      plugins: [centroTexto],
    });

    const evo = stats.evolucion;
    const evolLabels = evo.map((d) => d.fecha);
    const evolData = evo.map((d) => d.promedio);
    const evolCantidad = evo.map((d) => d.cantidad);
    crearOActualizar("chartEvolucion", {
      type: "line",
      data: {
        labels: evolLabels,
        datasets: [{
          label: "Promedio",
          data: evolData,
          borderColor: "#38bdf8",
          backgroundColor: "rgba(56,189,248,0.15)",
          fill: true,
          tension: 0.3,
          pointRadius: 5,
          pointBackgroundColor: "#38bdf8",
        }, {
          label: "Quizzes",
          data: evolCantidad,
          borderColor: "#22c55e",
          backgroundColor: "rgba(34,197,94,0.15)",
          fill: false,
          tension: 0.3,
          pointRadius: 4,
          pointBackgroundColor: "#22c55e",
          yAxisID: "y1",
        }],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          x: { ticks: { color: "#94a3b8" }, grid: { color: "#1e293b" } },
          y: { min: 0, max: 10, ticks: { color: "#94a3b8" }, grid: { color: "#1e293b" }, title: { display: true, text: "Promedio", color: "#94a3b8" } },
          y1: { position: "right", min: 0, ticks: { color: "#94a3b8", stepSize: 1 }, grid: { drawOnChartArea: false }, title: { display: true, text: "Quizzes", color: "#94a3b8" } },
        },
        plugins: {
          legend: { labels: { color: "#e2e8f0" } },
          tooltip: {
            callbacks: {
              afterBody: (items) => {
                const idx = items[0].dataIndex;
                return `Quizzes: ${evolCantidad[idx]}`;
              },
            },
          },
        },
      },
    });

    const dist = stats.distribucion;
    const distColores = ["#ef4444", "#f59e0b", "#eab308", "#22c55e", "#38bdf8"];
    crearOActualizar("chartDistribucion", {
      type: "bar",
      data: {
        labels: dist.map((d) => d.rango),
        datasets: [{
          label: "Quizzes",
          data: dist.map((d) => d.cantidad),
          backgroundColor: distColores,
          borderColor: distColores.map((c) => c),
          borderWidth: 1,
          borderRadius: 6,
        }],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          x: { ticks: { color: "#94a3b8" }, grid: { color: "#1e293b" } },
          y: { beginAtZero: true, ticks: { color: "#94a3b8", stepSize: 1 }, grid: { color: "#1e293b" } },
        },
        plugins: {
          legend: { display: false },
        },
      },
    });
  } catch (e) {
    console.error(e);
  }
}

// ---------- Videos ----------
function poblarFiltros() {
  document.getElementById("fNivel").innerHTML =
    `<option value="">Todos los niveles</option>` +
    NIVELES.map((n) => `<option value="${n}">${n}</option>`).join("");
  document.getElementById("fCategoria").innerHTML =
    `<option value="">Todas las categorías</option>` +
    CATEGORIAS.map((c) => `<option value="${c}">${c}</option>`).join("");
}

async function cargarVideos(resetearPagina = false) {
  if (resetearPagina) estado.pagina = 1;
  const f = estado.filtros;
  const params = new URLSearchParams({ limite: estado.limite, offset: (estado.pagina - 1) * estado.limite });
  if (f.nivel) params.set("nivel", f.nivel);
  if (f.categoria) params.set("categoria", f.categoria);
  if (f.texto) params.set("texto", f.texto);
  if (f.estado) params.set("estado", f.estado);

  const tbody = document.querySelector("#tablaVideos tbody");
  try {
    const data = await fetchJSON("/api/videos?" + params);
    tbody.innerHTML = data.resultados.length
      ? data.resultados.map(filaVideo).join("")
      : `<tr><td colspan="7" class="mensaje">Sin resultados.</td></tr>`;
    const totalPag = Math.max(1, Math.ceil(data.total / estado.limite));
    document.getElementById("pagInfo").textContent = `Página ${estado.pagina} de ${totalPag} · ${data.total} resultados`;
    document.getElementById("btnPrev").disabled = estado.pagina <= 1;
    document.getElementById("btnNext").disabled = estado.pagina >= totalPag;
  } catch (e) {
    tbody.innerHTML = `<tr><td colspan="7" class="mensaje error">${esc(e.message)}</td></tr>`;
  }
}

function filaVideo(v) {
  const tag = v.completado
    ? `<span class="tag visto">✓ Visto</span>`
    : `<span class="tag pendiente">Pendiente</span>`;
  const btn = v.completado
    ? `<button class="btn-mini" data-accion="desmarcar" data-id="${v.id}">Desmarcar</button>`
    : `<button class="btn-mini visto" data-accion="marcar" data-id="${v.id}">Marcar visto</button>`;
  const titulo = v.url
    ? `<a href="${esc(v.url)}" target="_blank" rel="noopener">${esc(v.titulo)}</a>`
    : esc(v.titulo);
  return `
    <tr>
      <td>${v.id}</td>
      <td class="titulo">${titulo}</td>
      <td>${esc(v.nivel)}</td>
      <td>${esc(v.categorias || "—")}</td>
      <td>${tag}</td>
      <td>${fmtNota(v.nota_quiz)} <span class="texto-suave">(${v.intentos})</span></td>
      <td class="acciones">
        ${btn}
        <input type="number" class="nota-input" min="0" max="10" step="0.5" placeholder="Nota">
        <button class="btn-mini${v.intentos > 0 ? ' quiz-hecho' : ''}" data-accion="nota" data-id="${v.id}">Guardar</button>
      </td>
    </tr>`;
}

document.querySelector("#tablaVideos tbody").addEventListener("click", async (e) => {
  const boton = e.target.closest("button[data-accion]");
  if (!boton) return;
  const id = boton.dataset.id;
  const accion = boton.dataset.accion;
  const cuerpo = { method: "POST", headers: { "Content-Type": "application/json" } };
  try {
    if (accion === "marcar") await fetchJSON(`/api/videos/${id}/visto`, { ...cuerpo, body: JSON.stringify({ completado: true }) });
    if (accion === "desmarcar") await fetchJSON(`/api/videos/${id}/visto`, { ...cuerpo, body: JSON.stringify({ completado: false }) });
    if (accion === "nota") {
      const input = boton.closest(".acciones").querySelector(".nota-input");
      const valor = parseFloat(input.value.replace(",", "."));
      if (isNaN(valor) || valor < 0 || valor > 10) { alert("Nota inválida (0-10)."); return; }
      await fetchJSON(`/api/videos/${id}/nota`, { ...cuerpo, body: JSON.stringify({ nota: valor }) });
      input.value = "";
    }
    await Promise.all([cargarVideos(), cargarResumen(), cargarGraficos()]);
  } catch (err) {
    alert(err.message);
  }
});

document.getElementById("btnBuscar").addEventListener("click", buscarConFiltros);
document.getElementById("btnReset").addEventListener("click", () => {
  document.getElementById("fNivel").value = "";
  document.getElementById("fCategoria").value = "";
  document.getElementById("fTexto").value = "";
  document.getElementById("fEstado").value = "";
  estado.filtros = { nivel: "", categoria: "", texto: "", estado: "" };
  cargarVideos(true);
});

function buscarConFiltros() {
  estado.filtros = {
    nivel: document.getElementById("fNivel").value,
    categoria: document.getElementById("fCategoria").value,
    texto: document.getElementById("fTexto").value.trim(),
    estado: document.getElementById("fEstado").value,
  };
  cargarVideos(true);
}

document.getElementById("fTexto").addEventListener("keydown", (e) => {
  if (e.key === "Enter") buscarConFiltros();
});

document.getElementById("btnPrev").addEventListener("click", () => {
  if (estado.pagina > 1) { estado.pagina--; cargarVideos(); }
});
document.getElementById("btnNext").addEventListener("click", () => {
  if (!document.getElementById("btnNext").disabled) {
    estado.pagina++;
    cargarVideos();
  }
});

// ---------- Recomendaciones ----------
async function cargarRecomendaciones() {
  const el = document.getElementById("recomLista");
  try {
    const data = await fetchJSON("/api/recomendaciones");
    if (!data.length) { el.innerHTML = `<div class="mensaje">Sin datos.</div>`; return; }
    el.innerHTML = data.map((g) => {
      const sub = g.promedio == null ? "aún sin quizzes" : `promedio ${Number(g.promedio).toFixed(2)}`;
      const items = g.pendientes.length
        ? g.pendientes.map((v) => `
          <div class="recom-video">
            <a href="${esc(v.url)}" target="_blank" rel="noopener">${esc(v.titulo)} <span class="tag">${esc(v.nivel)}</span></a>
            <button class="btn-mini visto" data-accion="recom-marcar" data-id="${v.id}">Marcar visto</button>
          </div>`).join("")
        : `<div class="mensaje">Todos vistos. ¡Bien! 🎉</div>`;
      return `
        <div class="recom-item">
          <h3>💡 ${esc(g.categoria)}</h3>
          <div class="sub">${esc(sub)}</div>
          ${items}
        </div>`;
    }).join("");
  } catch (e) {
    el.innerHTML = `<div class="mensaje error">${esc(e.message)}</div>`;
  }
}

document.getElementById("recomLista").addEventListener("click", async (e) => {
  const boton = e.target.closest("button[data-accion='recom-marcar']");
  if (!boton) return;
  try {
    await fetchJSON(`/api/videos/${boton.dataset.id}/visto`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ completado: true }),
    });
    await Promise.all([cargarRecomendaciones(), cargarResumen(), cargarGraficos()]);
  } catch (err) {
    alert(err.message);
  }
});

// ---------- Reset progreso ----------
document.getElementById("btnResetProgreso").addEventListener("click", async () => {
  if (!confirm("¿Estás seguro? Se borrarán todos los videos marcados y las notas de quiz.")) return;
  try {
    await fetchJSON("/api/reset-progreso", { method: "POST" });
    await Promise.all([cargarResumen(), cargarGraficos(), cargarVideos(), cargarRecomendaciones()]);
  } catch (err) {
    alert(err.message);
  }
});

// ---------- Logout ----------
document.getElementById("btnLogout").addEventListener("click", async () => {
  await fetch("/logout", { method: "POST" });
  window.location.href = "/login";
});

// ---------- Usuarios ----------
async function cargarUsuarios() {
  const el = document.getElementById("listaUsuarios");
  try {
    const usuarios = await fetchJSON("/api/usuarios");
    if (!usuarios.length) { el.innerHTML = `<div class="mensaje">Sin usuarios.</div>`; return; }
    el.innerHTML = `<div class="tabla-wrap"><table class="tabla-usuarios">
      <thead><tr><th>Usuario</th>${rolActual === "admin" ? "<th>Acciones</th>" : ""}</tr></thead>
      <tbody>${usuarios.map((u) => `
        <tr>
          <td>${esc(u.username)}</td>
          ${rolActual === "admin" && u.username !== "admin"
            ? `<td><button class="btn-mini btn-eliminar" data-id="${u.id}">Eliminar</button></td>`
            : rolActual === "admin" ? `<td><span class="texto-suave">—</span></td>` : ""}
        </tr>`).join("")}
      </tbody></table></div>`;
  } catch (e) {
    el.innerHTML = `<div class="mensaje error">${esc(e.message)}</div>`;
  }
}

document.getElementById("listaUsuarios").addEventListener("click", async (e) => {
  const btn = e.target.closest(".btn-eliminar");
  if (!btn) return;
  if (!confirm("¿Eliminar este usuario?")) return;
  try {
    await fetchJSON(`/api/usuarios/${btn.dataset.id}`, { method: "DELETE" });
    cargarUsuarios();
  } catch (err) {
    alert(err.message);
  }
});

// ---------- Inicio ----------
async function init() {
  try {
    const data = await fetchJSON("/api/rol");
    rolActual = data.rol || "usuario";
  } catch {
    rolActual = "usuario";
  }

  poblarFiltros();
  cargarResumen();
  cargarGraficos();
  cargarVideos();
  cargarRecomendaciones();

  if (rolActual === "admin") {
    cargarUsuarios();
  } else {
    document.querySelector('[data-tab="usuarios"]').style.display = "none";
  }
}
init();
