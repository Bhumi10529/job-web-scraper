document.addEventListener("DOMContentLoaded", () => {

  /* Loading spinner on any search form */
  document.querySelectorAll("form").forEach(form => {
    const btn = form.querySelector("#searchBtn");
    if (!btn) return;
    form.addEventListener("submit", () => {
      btn.querySelector(".btn-text")?.classList.add("hidden");
      btn.querySelector(".btn-loading")?.classList.remove("hidden");
      btn.disabled = true;
    });
  });

  /* ── Card filter logic ─────────────────────────────── */
  const cards   = Array.from(document.querySelectorAll(".job-card"));
  const countEl = document.getElementById("visibleCount");
  const noRes   = document.getElementById("noResults");
  const search  = document.getElementById("cardSearch");

  if (!cards.length) return;

  /* Populate sidebar counts */
  const counts = {};
  cards.forEach(c => {
    [c.dataset.type, c.dataset.mode, c.dataset.source].forEach(v => {
      if (v) counts[v] = (counts[v] || 0) + 1;
    });
  });
  Object.entries(counts).forEach(([k, v]) => {
    const el = document.getElementById("c-" + k);
    if (el) el.textContent = v;
  });

  function getChecked() {
    const f = { type: [], mode: [], source: [] };
    document.querySelectorAll(".fcb").forEach(cb => {
      if (cb.checked) f[cb.dataset.key].push(cb.dataset.val);
    });
    return f;
  }

  function run() {
    const f = getChecked();
    const q = search ? search.value.toLowerCase().trim() : "";
    let vis = 0;
    cards.forEach(c => {
      const ok =
        (!f.type.length   || f.type.includes(c.dataset.type))   &&
        (!f.mode.length   || f.mode.includes(c.dataset.mode))   &&
        (!f.source.length || f.source.includes(c.dataset.source)) &&
        (!q || c.dataset.title.includes(q) || c.dataset.company.includes(q));
      c.classList.toggle("card-hidden", !ok);
      if (ok) vis++;
    });
    if (countEl) countEl.textContent = `${vis} job${vis !== 1 ? "s" : ""} found`;
    if (noRes)   noRes.classList.toggle("hidden", vis > 0);
  }

  document.querySelectorAll(".fcb").forEach(cb => cb.addEventListener("change", run));
  if (search) search.addEventListener("input", run);

  function resetAll() {
    document.querySelectorAll(".fcb").forEach(cb => cb.checked = true);
    if (search) search.value = "";
    run();
  }

  document.getElementById("clearAll")?.addEventListener("click", resetAll);
  document.getElementById("resetFilters")?.addEventListener("click", resetAll);

  run(); // initial

  /* ── Mobile sidebar ────────────────────────────────── */
  const sidebar = document.getElementById("filterSidebar");
  const mobBtn  = document.getElementById("mobFilterBtn");
  const overlay = document.getElementById("mobOverlay");

  if (mobBtn && sidebar && overlay) {
    mobBtn.addEventListener("click", () => {
      sidebar.classList.add("open");
      overlay.classList.remove("hidden");
    });
    overlay.addEventListener("click", () => {
      sidebar.classList.remove("open");
      overlay.classList.add("hidden");
    });
  }

  /* ── Navbar scroll shadow ──────────────────────────── */
  const nav = document.querySelector(".navbar");
  if (nav) {
    window.addEventListener("scroll", () => {
      nav.style.boxShadow = window.scrollY > 4
        ? "0 2px 12px rgba(0,0,0,.08)" : "0 1px 0 #e5e3f0";
    }, { passive: true });
  }

});
