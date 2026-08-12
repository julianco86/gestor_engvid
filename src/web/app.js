const NIVELES = ["Beginner", "Intermediate", "Advanced", "Unspecified"];
const CATEGORIAS = [
  "business english", "comprehension", "culture & tips", "english resource",
  "expressions", "grammar", "ielts", "pronunciation", "slang",
  "speaking", "vocabulary", "writing",
];

const estado = { pagina: 1, limite: 20, filtros: { nivel: "", categoria: "", texto: "", estado: "" } };
const charts = {};

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
  try {
    const r = await fetchJSON("/api/resumen");
    const cards = [
      { clase: "acento", etiqueta: "Videos totales", valor: r.total },
      { clase: "ok", etiqueta: "Vistos", valor: r.vistos },
      { clase: "warn", etiqueta: "Pendientes", valor: r.pendientes },
      { clase: "acento", etiqueta: "% Completado", valor: r.porcentaje + "%" },
      { clase: "", etiqueta: "Quizzes", valor: r.quizzes },
      { clase: "", etiqueta: "Promedio general", valor: r.promedio == null ? "—" : r.promedio },
    ];
    el.innerHTML = cards.map((c) => `
      <div class="card ${c.clase}">
        <div class="valor">${esc(c.valor)}</div>
        <div class="etiqueta">${esc(c.etiqueta)}</div>
      </div>`).join("");
  } catch (e) {
    el.innerHTML = `<div class="mensaje error">${esc(e.message)}</div>`;
  }
}

// ---------- Gráficos ----------
const COLORES = ["#38bdf8", "#a78bfa", "#34d399", "#fbbf24", "#f472b6", "#60a5fa", "#fb923c", "#22d3ee", "#a3e635", "#e879f9", "#4ade80", "#facc15"];

function crearOActualizar(id, config) {
  if (charts[id]) charts[id].destroy();
  const ctx = document.getElementById(id).getContext("2d");
  charts[id] = new Chart(ctx, config);
}

async function cargarGraficos() {
  try {
    const [nivel, cats] = await Promise.all([
      fetchJSON("/api/por-nivel"),
      fetchJSON("/api/por-categoria"),
    ]);

    crearOActualizar("chartNivel", {
      type: "bar",
      data: {
        labels: nivel.map((n) => n.nivel),
        datasets: [{
          label: "% Completado",
          data: nivel.map((n) => n.porcentaje),
          backgroundColor: "#38bdf8",
        }],
      },
      options: { responsive: true, scales: { y: { beginAtZero: true, max: 100 } } },
    });

    crearOActualizar("chartCategoria", {
      type: "bar",
      data: {
        labels: cats.map((c) => c.categoria),
        datasets: [
          { label: "Videos", data: cats.map((c) => c.videos), backgroundColor: COLORES },
          { label: "% Completado", data: cats.map((c) => c.porcentaje), backgroundColor: "#1e293b", borderColor: "#38bdf8", borderWidth: 1 },
        ],
      },
      options: { responsive: true, scales: { y: { beginAtZero: true, max: 100 } } },
    });

    crearOActualizar("chartPromedio", {
      type: "bar",
      data: {
        labels: cats.map((c) => c.categoria),
        datasets: [{
          label: "Promedio de notas",
          data: cats.map((c) => c.promedio == null ? null : c.promedio),
          backgroundColor: "#a78bfa",
        }],
      },
      options: { responsive: true, scales: { y: { beginAtZero: true, max: 10 } } },
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
  return `
    <tr>
      <td>${v.id}</td>
      <td class="titulo">${esc(v.titulo)}</td>
      <td>${esc(v.nivel)}</td>
      <td>${esc(v.categorias || "—")}</td>
      <td>${tag}</td>
      <td>${fmtNota(v.nota_quiz)} <span class="texto-suave">(${v.intentos})</span></td>
      <td class="acciones">
        ${btn}
        <input type="number" class="nota-input" min="0" max="10" step="0.5" placeholder="Nota">
        <button class="btn-mini" data-accion="nota" data-id="${v.id}">Guardar</button>
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
    }
    await Promise.all([cargarVideos(), cargarResumen()]);
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
  estado.pagina++;
  cargarVideos();
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
    await Promise.all([cargarRecomendaciones(), cargarResumen()]);
  } catch (err) {
    alert(err.message);
  }
});

// ---------- Inicio ----------
poblarFiltros();
cargarResumen();
cargarGraficos();
cargarVideos();
cargarRecomendaciones();
