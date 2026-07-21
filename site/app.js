/* The Albiceleste Anomaly — chart layer.
   Emphasis form throughout: Argentina = --arg (albiceleste blue), field/context = --de gray.
   Diverging blue<->red only where color means polarity (favorable/unfavorable).
   Every chart: legend, selective direct labels, hover tooltip, table-view twin. */
(function () {
"use strict";
const D = window.WC_DATA;
/* Community tape backend: dedicated Supabase project "albiceleste-tape"
   (isolated — its own database and keys; publishable key is safe to embed).
   Public may INSERT pending submissions and READ approved ones; moderation
   happens in the Supabase dashboard (set status to 'approved'). */
const SUPA_URL = "https://rjqwbwujolwzqvjwfeyj.supabase.co";
const SUPA_KEY = "sb_publishable_ACwUPxssuLlpH9cHi5ESnQ_zR_lz7tB";
const SUPA_HEADERS = { apikey: SUPA_KEY, Authorization: "Bearer " + SUPA_KEY, "Content-Type": "application/json" };
const $ = (s) => document.querySelector(s);
const css = (v) => getComputedStyle(document.documentElement).getPropertyValue(v).trim();
const NS = "http://www.w3.org/2000/svg";

/* ---------- theme ---------- */
const btn = $("#themeBtn");
btn.addEventListener("click", () => {
  const r = document.documentElement;
  const dark = (r.dataset.theme || (matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light")) === "dark";
  r.dataset.theme = dark ? "light" : "dark";
  render(); // re-render so SVGs pick up new tokens
});

/* ---------- tooltip ---------- */
const tip = $("#tip");
function tipShow(html, ev) {
  tip.innerHTML = html; tip.style.display = "block";
  const pad = 14, w = tip.offsetWidth, h = tip.offsetHeight;
  let x = ev.clientX + pad, y = ev.clientY + pad;
  if (x + w > innerWidth - 8) x = ev.clientX - w - pad;
  if (y + h > innerHeight - 8) y = ev.clientY - h - pad;
  tip.style.left = x + "px"; tip.style.top = y + "px";
}
function tipHide() { tip.style.display = "none"; }
function hover(node, html) {
  node.addEventListener("mousemove", (e) => tipShow(html, e));
  node.addEventListener("mouseleave", tipHide);
}

/* ---------- svg helpers ---------- */
function E(tag, attrs, parent) {
  const n = document.createElementNS(NS, tag);
  for (const k in attrs) n.setAttribute(k, attrs[k]);
  if (parent) parent.appendChild(n);
  return n;
}
function text(parent, x, y, str, opts = {}) {
  const t = E("text", {
    x, y, fill: opts.fill || css("--ink-2"),
    "font-family": "system-ui,-apple-system,'Segoe UI',sans-serif",
    "font-size": opts.size || 11.5,
    "font-weight": opts.weight || 400,
    "text-anchor": opts.anchor || "start",
    "dominant-baseline": opts.baseline || "auto",
  }, parent);
  t.textContent = str;
  return t;
}

/* ---------- card scaffold: header + legend + chart/table toggle ---------- */
function card(sel, title, sub, legendKeys, drawChart, tableSpec) {
  const host = $(sel); host.innerHTML = "";
  const head = document.createElement("div"); head.className = "card-head";
  const tl = document.createElement("div");
  tl.innerHTML = `<div class="card-title">${title}</div><div class="card-sub">${sub}</div>`;
  head.appendChild(tl);
  const right = document.createElement("div");
  right.style.cssText = "display:flex;gap:16px;align-items:center;flex-wrap:wrap";
  if (legendKeys && legendKeys.length >= 2) {
    const lg = document.createElement("div"); lg.className = "legend";
    for (const k of legendKeys)
      lg.innerHTML += `<span class="key"><span class="swatch" style="background:${k.color}"></span>${k.label}</span>`;
    right.appendChild(lg);
  }
  const tg = document.createElement("div"); tg.className = "toggle";
  if (tableSpec) {
    tg.innerHTML = `<button aria-pressed="true">Chart</button><button aria-pressed="false">Table</button>`;
    right.appendChild(tg);
  }
  head.appendChild(right);
  host.appendChild(head);
  const plot = document.createElement("div"); plot.className = "plot"; host.appendChild(plot);
  const tbl = document.createElement("div"); tbl.style.display = "none"; host.appendChild(tbl);
  if (tableSpec) {
    const [bc, bt] = tg.querySelectorAll("button");
    bc.onclick = () => { bc.setAttribute("aria-pressed", "true"); bt.setAttribute("aria-pressed", "false"); plot.style.display = ""; tbl.style.display = "none"; };
    bt.onclick = () => { bt.setAttribute("aria-pressed", "true"); bc.setAttribute("aria-pressed", "false"); plot.style.display = "none"; tbl.style.display = ""; };
    tbl.innerHTML = `<div class="scrolltable">${tableHTML(tableSpec.cols, tableSpec.rows, tableSpec.argKey)}</div>`;
  }
  drawChart(plot);
}
/* All data fields originate from scraped web content — escape EVERYTHING that
   reaches innerHTML; formatters receive pre-escaped values. */
function esc(v) {
  return String(v ?? "—").replace(/[&<>"']/g, (c) =>
    ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
}
function tableHTML(cols, rows, argKey) {
  let h = `<table class="dv"><thead><tr>${cols.map(c => `<th>${esc(c.h)}</th>`).join("")}</tr></thead><tbody>`;
  for (const r of rows) {
    const isArg = argKey && String(r[argKey]).includes("Argentina");
    h += `<tr${isArg ? ' class="arg"' : ""}>${cols.map(c => `<td>${c.f ? c.f(esc(r[c.k]), r) : esc(r[c.k])}</td>`).join("")}</tr>`;
  }
  return h + "</tbody></table>";
}
const r2 = (x, d = 2) => x == null || isNaN(x) ? "—" : (+x).toFixed(d);
/* word-safe clipping: never cuts mid-word, always signals with an ellipsis */
function clip(s, n) {
  s = String(s ?? "");
  if (s.length <= n) return s;
  const cut = s.slice(0, n - 1);
  const sp = cut.lastIndexOf(" ");
  return (sp > n * 0.5 ? cut.slice(0, sp) : cut) + "…";
}

/* card with mode buttons (chart redraws per mode) + optional table twin */
function modeCard(sel, title, sub, legendKeys, modes, drawFn, tableSpec) {
  const host = $(sel); host.innerHTML = "";
  let mode = modes[0].id;
  const head = document.createElement("div"); head.className = "card-head";
  head.innerHTML = `<div><div class="card-title">${title}</div><div class="card-sub">${sub}</div></div>`;
  const right = document.createElement("div");
  right.style.cssText = "display:flex;gap:14px;align-items:center;flex-wrap:wrap";
  if (legendKeys) {
    const lg = document.createElement("div"); lg.className = "legend";
    for (const k of legendKeys)
      lg.innerHTML += `<span class="key"><span class="swatch" style="background:${k.color}"></span>${k.label}</span>`;
    right.appendChild(lg);
  }
  const mt = document.createElement("div"); mt.className = "toggle";
  mt.innerHTML = modes.map((m, i) => `<button data-m="${m.id}" aria-pressed="${i === 0}">${m.label}</button>`).join("");
  right.appendChild(mt);
  const vt = document.createElement("div"); vt.className = "toggle";
  vt.innerHTML = `<button aria-pressed="true">Chart</button><button aria-pressed="false">Table</button>`;
  if (tableSpec) right.appendChild(vt);
  head.appendChild(right); host.appendChild(head);
  const plot = document.createElement("div"); plot.className = "plot"; host.appendChild(plot);
  const tbl = document.createElement("div"); tbl.style.display = "none"; host.appendChild(tbl);
  if (tableSpec) tbl.innerHTML = tableHTML(tableSpec.cols, tableSpec.rows, tableSpec.argKey);
  const redraw = () => { plot.innerHTML = ""; drawFn(plot, mode); };
  mt.querySelectorAll("button").forEach(b => b.onclick = () => {
    mode = b.dataset.m;
    mt.querySelectorAll("button").forEach(x => x.setAttribute("aria-pressed", String(x === b)));
    redraw();
  });
  if (tableSpec) {
    const [bc, bt] = vt.querySelectorAll("button");
    bc.onclick = () => { bc.setAttribute("aria-pressed", "true"); bt.setAttribute("aria-pressed", "false"); plot.style.display = ""; tbl.style.display = "none"; };
    bt.onclick = () => { bt.setAttribute("aria-pressed", "true"); bc.setAttribute("aria-pressed", "false"); plot.style.display = "none"; tbl.style.display = ""; };
  }
  redraw();
}

/* ---------- data assembly ---------- */
// penalties awarded per tournament: archival 1930-2010 (auto-grows) + FBref PKatt 2014+
function pensByTournament() {
  const rows = (D.pens_awarded_by_tournament || []).map(r => ({
    year: r.year, argFor: r.arg_for, argAg: r.arg_against, argM: r.arg_matches,
    fieldRate: r.field_rate_per_team_match, src: "archival",
  }));
  for (const yr of [2014, 2018, 2022, 2026]) {
    const s = D.squad_discipline.filter(r => r.tournament_year === yr);
    if (!s.length) continue;
    const a = s.find(r => r.team === "Argentina");
    const tot = s.reduce((z, r) => z + (r.penalty_kicks_attempted || 0), 0);
    const tm = s.reduce((z, r) => z + r.matches_played, 0);
    rows.push({
      year: yr, argFor: a.penalty_kicks_attempted, argM: a.matches_played,
      argAg: yr === 2026 ? 0 : (a.penalties_conceded ?? null),
      fieldRate: +( (tot - a.penalty_kicks_attempted) / (tm - a.matches_played) ).toFixed(4),
      src: "fbref",
    });
  }
  return rows.filter(r => r.argM > 0).sort((a, b) => a.year - b.year);
}

/* ---------- masthead meta + KPI tiles ---------- */
(function meta() {
  const pooled = D.pens_awarded_tests || [];
  const nInc = (D.pens_incidents || []).length;
  $("#mastmeta").innerHTML =
    `<span><a href="https://github.com/VeritasSimplexAI/albiceleste-anomaly" target="_blank" rel="noopener" style="color:var(--arg);text-decoration:none;border-bottom:1px solid color-mix(in srgb, var(--arg) 40%, transparent)"><b>Open source</b> — all data &amp; code on GitHub</a></span>` +
    `<span><b>${D.team_tournament.length.toLocaleString()}</b> team-tournament records, 1930–2022</span>` +
    `<span><b>102</b> matches of 2026 compiled</span>` +
    `<span><b>${nInc}</b> penalties individually source-verified</span>` +
    `<span><b>86</b> directional VAR overturns, 2018–2026</span>`;
})();
(function kpis() {
  const k = $("#kpis");
  const t = (cls, lbl, val, sub) =>
    `<div class="tile ${cls}"><div class="lbl">${lbl}</div><div class="val">${val}</div><div class="sub">${sub}</div></div>`;
  k.innerHTML =
    t("hero", "Penalty awards vs field, since 2022", "5.0×", "8 in 14 matches · ≈ 1 in 2,200 by chance") +
    t("", "Same team, 1930–2018", "1.0×", "92 years bang average — the control") +
    t("", "VAR overturns, since 2018", "8–1", "for Argentina · 5–0 in 2026 (≈ 1 in 100)") +
    t("hero", "Same team, Copa América", "1.1×", "CONMEBOL's own cup — the edge follows the tournament, not the team") +
    t("", "2022 title run vs its rating", "−0.72", "the only champion since 1990 to win BELOW its Elo") +
    t("", "Marciniak × Argentina", "4", "the only 4-match referee pairing in 96 years — incl. the 2022 final");
})();

/* ---------- global numeric-aware table sorting (all .dv tables except #cmpTable) ---------- */
document.addEventListener("click", (e) => {
  const th = e.target.closest("table.dv th");
  if (!th || th.closest("#cmpTable")) return;
  const table = th.closest("table");
  const idx = [...th.parentNode.children].indexOf(th);
  const dir = th.dataset.dir === "asc" ? -1 : 1;
  table.querySelectorAll("th").forEach(h => { delete h.dataset.dir; h.querySelector(".sortarr")?.remove(); });
  th.dataset.dir = dir === 1 ? "asc" : "desc";
  th.insertAdjacentHTML("beforeend", ` <span class="sortarr">${dir === 1 ? "▲" : "▼"}</span>`);
  const body = table.tBodies[0];
  const rows = [...body.rows];
  const val = (r) => r.cells[idx]?.textContent.trim() ?? "";
  const num = (s) => { const n = parseFloat(s.replace(/[+%×,]/g, "").replace("—", "")); return isNaN(n) ? null : n; };
  rows.sort((a, b) => {
    const av = val(a), bv = val(b), an = num(av), bn = num(bv);
    return dir * (an !== null && bn !== null ? an - bn : av.localeCompare(bv));
  });
  rows.forEach(r => body.appendChild(r));
});

/* ---------- filterable data browser card ---------- */
function browserCard(sel, title, sub, cols, rows, filters, chartDraw) {
  const host = $(sel); if (!host) return;
  host.innerHTML = `<div class="card-head"><div><div class="card-title">${title}</div>
    <div class="card-sub">${sub}</div></div>${chartDraw ? '<div class="toggle" id="bvt"><button aria-pressed="false">Chart</button><button aria-pressed="true">Data</button></div>' : ""}</div>
    ${chartDraw ? '<div class="plot bchart" style="display:none"></div>' : ""}
    <div class="filters"></div><div class="scrolltable"><div class="bwrap"></div></div>`;
  if (chartDraw) {
    const cplot = host.querySelector(".bchart"), ftr = () => host.querySelector(".filters"),
          scr = () => host.querySelector(".scrolltable");
    const [bc, bd] = host.querySelectorAll("#bvt button");
    bc.onclick = () => { bc.setAttribute("aria-pressed", "true"); bd.setAttribute("aria-pressed", "false");
      cplot.style.display = ""; ftr().style.display = "none"; scr().style.display = "none";
      if (!cplot.hasChildNodes()) chartDraw(cplot); };
    bd.onclick = () => { bd.setAttribute("aria-pressed", "true"); bc.setAttribute("aria-pressed", "false");
      cplot.style.display = "none"; ftr().style.display = ""; scr().style.display = ""; };
  }
  const fdiv = host.querySelector(".filters");
  const state = {};
  for (const f of filters) {
    const id = `f_${Math.random().toString(36).slice(2, 8)}`;
    if (f.type === "select") {
      const opts = ["(all)", ...f.options].map(o => `<option>${esc(o)}</option>`).join("");
      fdiv.insertAdjacentHTML("beforeend", `<label>${esc(f.label)}</label><select id="${id}">${opts}</select>`);
    } else {
      fdiv.insertAdjacentHTML("beforeend", `<label>${esc(f.label)}</label><input id="${id}" type="text" placeholder="type to filter…">`);
    }
    state[f.key] = { el: null, id, f };
  }
  fdiv.insertAdjacentHTML("beforeend", `<span class="rescount"></span>`);
  const wrap = host.querySelector(".bwrap"), count = host.querySelector(".rescount");
  const redraw = () => {
    let out = rows;
    for (const k in state) {
      const { el, f } = state[k];
      const v = el.value.trim();
      if (!v || v === "(all)") continue;
      out = out.filter(r => f.type === "select"
        ? String(r[k]) === v
        : String(r[k] ?? "").toLowerCase().includes(v.toLowerCase()) ||
          (f.also || []).some(k2 => String(r[k2] ?? "").toLowerCase().includes(v.toLowerCase())));
    }
    wrap.innerHTML = tableHTML(cols, out);
    count.textContent = `${out.length} of ${rows.length} rows`;
  };
  for (const k in state) {
    state[k].el = host.querySelector(`#${state[k].id}`);
    state[k].el.addEventListener(state[k].f.type === "select" ? "change" : "input", redraw);
  }
  redraw();
}

/* ================= Prologue: the record ================= */
function drawRecord(plot) {
  const d = D.argentina_record || [];
  const W = Math.max(700, plot.clientWidth || 920), H = 300, L = 110, R = 30, T = 40, B = 46;
  const iw = W - L - R, ih = H - T - B;
  const x = (i) => L + (i + 0.5) * (iw / d.length);
  const y = (v) => T + ih - ((v - 1) / 5) * ih;
  const svg = E("svg", { width: W, height: H, viewBox: `0 0 ${W} ${H}` }, null);
  // FIFA-president era bands (drawn first, behind everything)
  const ERAS = [["Rimet+", 1930, 1958], ["Rous", 1962, 1974], ["Havelange", 1978, 1998],
                ["Blatter", 2002, 2014], ["Infantino", 2018, 2026]];
  const idxOf = (yr) => d.findIndex(r => r.year === yr);
  const step = iw / d.length;
  ERAS.forEach((e, k) => {
    const i0 = idxOf(e[1]), i1 = idxOf(e[2]);
    if (i0 < 0 || i1 < 0) return;
    const x0 = L + i0 * step, x1 = L + (i1 + 1) * step;
    if (k % 2 === 0) E("rect", { x: x0, y: T - 30, width: x1 - x0, height: ih + 30, fill: css("--ink"), opacity: 0.035 }, svg);
    text(svg, (x0 + x1) / 2, T - 28, e[0], { anchor: "middle", size: 9.5, fill: css("--muted") });
  });
  const LBL = { 1: "Group stage", 2: "Round of 16", 3: "Quarter-finals", 4: "Semi-finals", 5: "Final", 6: "CHAMPIONS" };
  for (let v = 1; v <= 6; v++) {
    E("line", { x1: L, x2: W - R, y1: y(v), y2: y(v), stroke: css("--grid") }, svg);
    text(svg, L - 8, y(v) + 3, LBL[v], { anchor: "end", size: 10.5, fill: v === 6 ? css("--ink-2") : css("--muted"), weight: v === 6 ? 650 : 400 });
  }
  E("path", { d: d.map((r, i) => `${i ? "L" : "M"} ${x(i)} ${y(r.ord)}`).join(" "),
    fill: "none", stroke: css("--arg"), "stroke-width": 2, "stroke-linejoin": "round", opacity: 0.55 }, svg);
  d.forEach((r, i) => {
    const champ = r.ord === 6;
    const dot = E("circle", { cx: x(i), cy: y(r.ord), r: champ ? 7 : 5, fill: css("--arg"),
      stroke: css("--surface"), "stroke-width": 2 }, svg);
    hover(dot, `<b>${r.year} — ${esc(r.label)}</b><br>${r.wins}W ${r.draws}D ${r.losses}L · ${r.gf}–${r.ga} goals`);
    if (champ) text(svg, x(i), y(r.ord) - 12, "★", { anchor: "middle", size: 13, fill: css("--ink") });
    if (i % 2 === 0 || champ || r.year === 2026)
      text(svg, x(i), H - 26, String(r.year), { anchor: "middle", size: 10, fill: champ ? css("--ink") : css("--muted"), weight: champ ? 650 : 400 });
  });
  text(svg, L, H - 6, "How far Argentina went at every World Cup entered (missed 1938–1954 qualifying/withdrawals and 1970) · ★ = title", { size: 10.5, fill: css("--muted") });
  plot.appendChild(svg);
}

/* ================= Exhibit A: diverging penalty chart (against ← | → for) ================= */
function drawPensDiverging(plot) {
  const rows = pensByTournament();
  const W = Math.max(700, plot.clientWidth || 920), rowH = 27, T = 26, B = 40;
  const H = T + rows.length * rowH + B;
  const C = W * 0.5, span = W * 0.42, maxV = 0.8;
  const xr = (v) => C + (v / maxV) * span * 0.95;   // for → right
  const xl = (v) => C - (v / maxV) * span * 0.95;   // against → left
  const svg = E("svg", { width: W, height: H, viewBox: `0 0 ${W} ${H}` }, null);
  E("line", { x1: C, x2: C, y1: T - 8, y2: H - B + 6, stroke: css("--axis"), "stroke-width": 1.5 }, svg);
  text(svg, C + 8, T - 12, "penalties FOR per match →", { size: 10.5, weight: 650, fill: css("--pos") });
  text(svg, C - 8, T - 12, "← penalties AGAINST per match", { size: 10.5, weight: 650, fill: css("--neg"), anchor: "end" });
  rows.forEach((r, i) => {
    const yc = T + i * rowH + rowH / 2;
    const forV = r.argFor / r.argM;
    // field-rate reference ticks (same both sides by symmetry)
    for (const fx of [xr(r.fieldRate), xl(r.fieldRate)])
      E("line", { x1: fx, x2: fx, y1: yc - 8, y2: yc + 8, stroke: css("--axis"), "stroke-width": 1.5 }, svg);
    // FOR bar (blue, right)
    const bf = E("rect", { x: C + 1, y: yc - 8, width: Math.max(xr(forV) - C - 1, 1), height: 16, rx: 3,
      fill: css("--arg"), opacity: r.year >= 2022 ? 1 : 0.75 }, svg);
    hover(bf, `<b>${r.year}</b> — ${r.argFor} awarded FOR in ${r.argM} matches (${r2(forV)}/match)<br>field rate ${r2(r.fieldRate, 3)} (the tick)`);
    if (forV > 0.02) text(svg, xr(forV) + 5, yc + 4, `${r.argFor}`, { size: 10.5, fill: r.year >= 2022 ? css("--ink") : css("--muted"), weight: r.year >= 2022 ? 700 : 400 });
    // AGAINST bar (red, left) — 2014 unknown
    if (r.argAg == null) {
      text(svg, C - 8, yc + 4, "?", { anchor: "end", size: 11, fill: css("--muted") });
    } else {
      const agV = r.argAg / r.argM;
      const ba = E("rect", { x: xl(agV), y: yc - 8, width: Math.max(C - 1 - xl(agV), 1), height: 16, rx: 3,
        fill: css("--neg"), opacity: 0.75 }, svg);
      hover(ba, `<b>${r.year}</b> — ${r.argAg} awarded AGAINST in ${r.argM} matches (${r2(agV)}/match)<br>field rate ${r2(r.fieldRate, 3)} (the tick)`);
      if (agV > 0.02) text(svg, xl(agV) - 5, yc + 4, `${r.argAg}`, { anchor: "end", size: 10.5, fill: css("--muted") });
    }
    text(svg, 8, yc + 4, String(r.year), { size: 11, weight: r.year >= 2022 ? 700 : 400, fill: r.year >= 2022 ? css("--ink") : css("--ink-2") });
  });
  text(svg, 8, H - 10, clip("Each row is a tournament · bars = Argentina's awarded penalties per match · ticks = the going rate that year · 2014 'against' unpublished", Math.floor((W - 16) / 5.8)), { size: 10.5, fill: css("--muted") });
  plot.appendChild(svg);
}

/* ================= Exhibit A: penalties chart (modes: for / against / net) ================= */
function drawPens(plot, mode = "for") {
  const rows = pensByTournament();
  const val = (r) => {
    if (mode === "for") return r.argFor / r.argM;
    if (mode === "against") return r.argAg == null ? null : r.argAg / r.argM;
    return r.argAg == null ? null : (r.argFor - r.argAg) / r.argM;
  };
  const fieldVal = (r) => mode === "net" ? 0 : r.fieldRate;
  const W = Math.max(700, plot.clientWidth || 920), H = 300, L = 46, R = 30, T = 18, B = 46;
  const iw = W - L - R, ih = H - T - B;
  const vals = rows.map(val).filter(v => v != null);
  const maxY = Math.max(0.3, ...vals, ...rows.map(fieldVal)) * 1.15;
  const minY = Math.min(0, ...vals) * 1.3;
  const y = (v) => T + ih - ((v - minY) / (maxY - minY)) * ih;
  const bw = Math.max(8, Math.min(24, iw / rows.length / 2 - 5));
  const svg = E("svg", { width: W, height: H, viewBox: `0 0 ${W} ${H}` }, null);
  for (const g of [-0.2, 0, 0.2, 0.4, 0.6]) {
    if (g > maxY || g < minY) continue;
    E("line", { x1: L, x2: W - R, y1: y(g), y2: y(g), stroke: g === 0 ? css("--axis") : css("--grid") }, svg);
    text(svg, L - 6, y(g) + 3, g.toFixed(1), { anchor: "end", fill: css("--muted"), size: 10.5 });
  }
  rows.forEach((r, i) => {
    const cx = L + (i + 0.5) * (iw / rows.length);
    const aRate = val(r);
    if (aRate == null) {
      text(svg, cx - bw / 2, y(0) - 6, "?", { anchor: "middle", size: 11, fill: css("--muted") });
    } else {
      const bars = [{ x: cx - bw - 1, v: aRate, c: css("--arg"), lab: "Argentina" }];
      if (mode !== "net") bars.push({ x: cx + 1, v: fieldVal(r), c: css("--de"), lab: "Field" });
      for (const b of bars) {
        const y0 = y(Math.max(0, b.v)), hgt = Math.abs(y(b.v) - y(0));
        const bar = b.v >= 0
          ? E("path", { d: roundTop(b.x, y0, bw, Math.max(hgt, 1), 4), fill: b.c }, svg)
          : E("rect", { x: b.x, y: y(0), width: bw, height: Math.max(hgt, 1), rx: 3, fill: b.c }, svg);
        hover(bar, `<b>${r.year}</b> — ${b.lab}<br>` + (b.lab === "Argentina"
          ? `${r.argFor} awarded for${r.argAg == null ? " (against: no data 2014)" : `, ${r.argAg} against`} in ${r.argM} matches`
          : `${r2(b.v, 3)} per team-match`) +
          `<br><span style="opacity:.7">${r.src === "fbref" ? "FBref squad data" : "archival per-incident compilation"}</span>`);
      }
      if (r.year >= 2022 && mode === "for")
        text(svg, cx, y(aRate) - 6, `${r.argFor} in ${r.argM}`, { anchor: "middle", weight: 650, size: 11, fill: css("--ink") });
    }
    if ([1930, 1950, 1966, 1982, 1998, 2014, 2026].includes(r.year))
      text(svg, cx, H - 26, String(r.year), { anchor: "middle", fill: css("--muted"), size: 10.5 });
  });
  const i22 = rows.findIndex(r => r.year === 2022);
  if (i22 > 0) {
    const dx = L + i22 * (iw / rows.length) + 2;
    E("line", { x1: dx, x2: dx, y1: T, y2: y(minY < 0 ? minY : 0), stroke: css("--axis") }, svg);
    text(svg, dx - 6, T + 10, "the apex era →", { size: 11, weight: 650, fill: css("--ink"), anchor: "end" });
  }
  const CAP = { for: "Penalties awarded TO Argentina per match vs field. Awarded = referee's decision, scored or not.",
                against: "Penalties awarded AGAINST Argentina per match vs field (2014 per-team data unpublished — shown as ?).",
                net: "Net penalty decisions per match (for − against). Zero line = neutral treatment." };
  text(svg, L, H - 8, CAP[mode], { size: 10.5, fill: css("--muted") });
  plot.appendChild(svg);
}
function roundTop(x, ytop, w, h, r) {
  if (h <= 0.5) return `M ${x} ${ytop} h ${w} v 0 h ${-w} Z`;
  r = Math.min(r, w / 2, h);
  return `M ${x} ${ytop + h} V ${ytop + r} Q ${x} ${ytop} ${x + r} ${ytop} H ${x + w - r} Q ${x + w} ${ytop} ${x + w} ${ytop + r} V ${ytop + h} Z`;
}

/* ---------- generic chart builders (chart twin for every table) ---------- */
function hbarChart(plot, items, opts = {}) {
  const W = Math.max(380, plot.clientWidth || 700), rowH = 30, R = 70, T = 8;
  const maxLabel = Math.max(...items.map(i => String(i.label).length));
  const L = Math.min(Math.max(opts.labelW || 150, maxLabel * 6.6 + 16), W * 0.5);
  const labelBudget = Math.floor((L - 14) / 6.4);
  const H = T + items.length * rowH + 40;
  const vals = items.map(i => i.value);
  const lo = Math.min(0, ...vals), hi = Math.max(...vals, opts.parity ?? 0) * 1.12 || 1;
  const fmtF = opts.fmt || (v => v);
  // negative-value labels sit LEFT of the bar tip; reserve a margin so they never reach the names
  const negPad = vals.some(v => v < 0)
    ? Math.max(...items.filter(i => i.value < 0).map(i => String(fmtF(i.value)).length)) * 6.4 + 14 : 0;
  const x = (v) => (L + negPad) + ((v - lo) / (hi - lo)) * (W - L - negPad - R);
  const svg = E("svg", { width: W, height: H, viewBox: `0 0 ${W} ${H}` }, null);
  E("line", { x1: x(0), x2: x(0), y1: T, y2: H - 32, stroke: css("--axis"), "stroke-width": 1.2 }, svg);
  if (opts.parity != null) {
    E("line", { x1: x(opts.parity), x2: x(opts.parity), y1: T, y2: H - 32, stroke: css("--axis"), "stroke-dasharray": "" }, svg);
    text(svg, x(opts.parity), T - 1, opts.parityLabel || "parity", { anchor: "middle", size: 9.5, fill: css("--muted") });
  }
  items.forEach((it, i) => {
    const yc = T + i * rowH + rowH / 2;
    const x0 = Math.min(x(0), x(it.value)), w = Math.abs(x(it.value) - x(0));
    const col = it.hl ? css("--arg") : (it.value < 0 && opts.diverge ? css("--neg") : css("--de"));
    const bar = E("rect", { x: x0, y: yc - 8, width: Math.max(w, 1.5), height: 16, rx: 3,
      fill: col, opacity: it.hl ? 1 : 0.6 }, svg);
    hover(bar, it.tip || `<b>${esc(it.label)}</b><br>${it.value}`);
    text(svg, L - 8, yc + 4, clip(it.label, labelBudget), { anchor: "end", size: 11.5, weight: it.hl ? 700 : 400, fill: it.hl ? css("--ink") : css("--ink-2") });
    text(svg, it.value >= 0 ? x(it.value) + 6 : x(it.value) - 6, yc + 4,
      fmtF(it.value), { anchor: it.value >= 0 ? "start" : "end", size: 11, fill: it.hl ? css("--ink") : css("--muted"), weight: it.hl ? 650 : 400 });
  });
  if (opts.note) text(svg, 8, H - 8, clip(opts.note, Math.floor((W - 16) / 5.8)), { size: 10.5, fill: css("--muted") });
  plot.appendChild(svg);
}
function yearStackChart(plot, rows, opts) {
  // rows: raw records; opts: {yearKey, catOf(row)->id, cats:[{id,label,color}], note}
  const counts = {};
  for (const r of rows) {
    const y = r[opts.yearKey], c = opts.catOf(r);
    if (c == null) continue;
    (counts[y] = counts[y] || {})[c] = (counts[y][c] || 0) + 1;
  }
  const years = Object.keys(counts).sort();
  const W = Math.max(380, plot.clientWidth || 700), H = 240, L = 40, R = 14, T = 14, B = 60;
  const iw = W - L - R, ih = H - T - B;
  const maxY = Math.max(...years.map(y => Object.values(counts[y]).reduce((a, b) => a + b, 0)));
  const yscale = (v) => T + ih - (v / (maxY * 1.1)) * ih;
  const svg = E("svg", { width: W, height: H, viewBox: `0 0 ${W} ${H}` }, null);
  E("line", { x1: L, x2: W - R, y1: yscale(0), y2: yscale(0), stroke: css("--axis") }, svg);
  const bw = Math.min(30, iw / years.length - 8);
  years.forEach((yr, i) => {
    const cx = L + (i + 0.5) * (iw / years.length);
    let acc = 0;
    for (const cat of opts.cats) {
      const n = counts[yr][cat.id] || 0;
      if (!n) continue;
      const y1 = yscale(acc + n), y0 = yscale(acc);
      const seg = E("rect", { x: cx - bw / 2, y: y1, width: bw, height: Math.max(y0 - y1 - 2, 1), rx: 2, fill: cat.color, opacity: 0.85 }, svg);
      hover(seg, `<b>${yr}</b> — ${esc(cat.label)}: ${n}`);
      acc += n;
    }
    text(svg, cx, H - B + 16, String(yr), { anchor: "middle", size: 10, fill: css("--muted") });
  });
  // legend inline at bottom
  let lx = L;
  for (const cat of opts.cats) {
    E("rect", { x: lx, y: H - 26, width: 10, height: 10, rx: 2, fill: cat.color }, svg);
    const t = text(svg, lx + 14, H - 17, cat.label, { size: 10.5, fill: css("--ink-2") });
    lx += 24 + cat.label.length * 6.2;
  }
  if (opts.note) text(svg, L, H - 4, clip(opts.note, Math.floor((W - L - 8) / 5.6)), { size: 10, fill: css("--muted") });
  plot.appendChild(svg);
}
function dumbbellChart(plot, rows, opts) {
  // rows: [{label, a, b}] · opts: {la, lb, fmt, note, max}
  const W = Math.max(380, plot.clientWidth || 440), rowH = 30, R = 30, T = 26;
  const L = Math.min(Math.max(140, Math.max(...rows.map(r => String(r.label).length)) * 6.6 + 14), W * 0.45);
  const dlBudget = Math.floor((L - 12) / 6.4);
  const H = T + rows.length * rowH + 40;
  const maxV = opts.max || Math.max(...rows.flatMap(r => [r.a, r.b])) * 1.15;
  const x = (v) => L + (v / maxV) * (W - L - R);
  const svg = E("svg", { width: W, height: H, viewBox: `0 0 ${W} ${H}` }, null);
  text(svg, L, T - 12, `● ${opts.la}`, { size: 10.5, fill: css("--arg"), weight: 650 });
  text(svg, L + 90, T - 12, `● ${opts.lb}`, { size: 10.5, fill: css("--muted") });
  rows.forEach((r, i) => {
    const yc = T + i * rowH + rowH / 2;
    E("line", { x1: x(Math.min(r.a, r.b)), x2: x(Math.max(r.a, r.b)), y1: yc, y2: yc, stroke: css("--grid"), "stroke-width": 2 }, svg);
    const db = E("circle", { cx: x(r.b), cy: yc, r: 5.5, fill: css("--de"), stroke: css("--surface"), "stroke-width": 2 }, svg);
    hover(db, `<b>${esc(r.label)}</b> — ${opts.lb}: ${r.b}`);
    const da = E("circle", { cx: x(r.a), cy: yc, r: 6.5, fill: css("--arg"), stroke: css("--surface"), "stroke-width": 2 }, svg);
    hover(da, `<b>${esc(r.label)}</b> — ${opts.la}: ${r.a}`);
    text(svg, 8, yc + 4, clip(r.label, dlBudget), { size: 11.5 });
  });
  E("line", { x1: L, x2: W - R, y1: H - 32, y2: H - 32, stroke: css("--axis") }, svg);
  if (opts.note) text(svg, 8, H - 8, clip(opts.note, Math.floor((W - 16) / 5.8)), { size: 10.5, fill: css("--muted") });
  plot.appendChild(svg);
}

/* ================= Exhibit A table: era tests ================= */
function penEraTable() {
  const rows = (D.pens_awarded_tests || []).map(r => ({ ...r }));
  return {
    cols: [
      { h: "Era", k: "era" }, { h: "Direction", k: "metric", f: v => v === "awarded_for" ? "Awarded FOR Argentina" : "Awarded AGAINST" },
      { h: "Argentina", k: "arg", f: (v, r) => `${v} in ${r.arg_matches}` },
      { h: "Rate/match", k: "arg_rate", f: v => r2(v, 3) }, { h: "Field", k: "field_rate", f: v => r2(v, 3) },
      { h: "Ratio", k: "ratio", f: v => `<b>${r2(v, 2)}×</b>` }, { h: "p", k: "p", f: v => r2(v, 4) },
    ],
    rows, argKey: null,
  };
}

/* ================= Exhibit B: VAR leaderboard ================= */
function drawVar(plot) {
  const lb = D.var_leaderboard.filter(r => r.m >= 7).sort((a, b) => b.net_pm - a.net_pm).slice(0, 10);
  const W = 920, rowH = 34, L = 190, R = 90, T = 8;
  const H = T + lb.length * rowH + 30;
  const maxV = Math.max(...lb.map(r => r.net_pm)) * 1.1;
  const x = (v) => L + (v / maxV) * (W - L - R);
  const svg = E("svg", { width: W, height: H, viewBox: `0 0 ${W} ${H}` }, null);
  E("line", { x1: L, x2: L, y1: T, y2: H - 26, stroke: css("--axis") }, svg);
  lb.forEach((r, i) => {
    const yc = T + i * rowH + rowH / 2;
    const isArg = r.team === "Argentina";
    const bh = 18;
    const bar = E("path", { d: `M ${L} ${yc - bh / 2} H ${x(r.net_pm) - 4} Q ${x(r.net_pm)} ${yc - bh / 2} ${x(r.net_pm)} ${yc - bh / 2 + 4} V ${yc + bh / 2 - 4} Q ${x(r.net_pm)} ${yc + bh / 2} ${x(r.net_pm) - 4} ${yc + bh / 2} H ${L} Z`,
      fill: isArg ? css("--arg") : css("--de"), opacity: isArg ? 1 : 0.55 }, svg);
    hover(bar, `<b>${esc(r.team)}</b><br>+${r.fav} overturns for, −${r.ag} against<br>${r.m} matches → net ${r2(r.net_pm, 3)}/match`);
    text(svg, L - 8, yc + 4, r.team, { anchor: "end", weight: isArg ? 700 : 400, fill: isArg ? css("--ink") : css("--ink-2"), size: 12.5 });
    text(svg, x(r.net_pm) + 8, yc + 4, `+${r.fav} / −${r.ag} in ${r.m}`, { size: 11, fill: isArg ? css("--ink") : css("--muted"), weight: isArg ? 650 : 400 });
  });
  text(svg, L, H - 8, "Net VAR overturns per match (favorable − unfavorable), 2018–2026 pooled · teams with ≥7 VAR-era matches", { size: 10.5, fill: css("--muted") });
  plot.appendChild(svg);
}

/* ================= Exhibit C: cards timeline (modes: opp / own / diff) ================= */
function drawCards(plot, mode = "opp") {
  const tt = D.team_tournament.filter(r => r.year >= 1970);
  const years = [...new Set(tt.map(r => r.year))].sort();
  const pts = [];
  for (const yr of years) {
    const g = tt.filter(r => r.year === yr);
    const a = g.find(r => r.team_name === "Argentina");
    if (!a) { continue; }
    const totY = g.reduce((z, r) => z + r.yellows_received, 0);
    const totM = g.reduce((z, r) => z + r.matches, 0);
    const fld = totY / totM;
    pts.push({
      year: yr, argM: a.matches,
      arg: mode === "opp" ? a.yellows_drawn / a.matches
        : mode === "own" ? a.yellows_received / a.matches
        : (a.yellows_drawn - a.yellows_received) / a.matches,
      field: mode === "diff" ? 0 : fld,
    });
  }
  const g26 = { opp: D.argentina_2026.find(r => r.metric === "yellows_drawn"),
                own: D.argentina_2026.find(r => r.metric === "yellows_received") };
  pts.push({ year: 2026, argM: 7,
             arg: mode === "opp" ? g26.opp.arg_rate : mode === "own" ? g26.own.arg_rate
               : g26.opp.arg_rate - g26.own.arg_rate,
             field: mode === "diff" ? 0 : g26.opp.field_rate });
  const W = Math.max(700, plot.clientWidth || 920), H = 290, L = 44, R = 60, T = 16, B = 40;
  const iw = W - L - R, ih = H - T - B;
  const x = (yr) => L + ((yr - 1970) / (2026 - 1970)) * iw;
  const minY = mode === "diff" ? -2 : 0, maxY = 4;
  const y = (v) => T + ih - ((v - minY) / (maxY - minY)) * ih;
  const svg = E("svg", { width: W, height: H, viewBox: `0 0 ${W} ${H}` }, null);
  for (let g = minY; g <= maxY; g++) {
    E("line", { x1: L, x2: W - R, y1: y(g), y2: y(g), stroke: g === 0 ? css("--axis") : css("--grid") }, svg);
    text(svg, L - 6, y(g) + 3, String(g), { anchor: "end", size: 10.5, fill: css("--muted") });
  }
  // diff mode: shaded band = middle half of ALL teams' differentials that year (1970-2022; per-match 2026 data exists only for ARG)
  if (mode === "diff") {
    const band = [];
    for (const yr of years) {
      const g = tt.filter(r => r.year === yr).map(r => (r.yellows_drawn - r.yellows_received) / r.matches).sort((a, b) => a - b);
      if (g.length < 8) continue;
      band.push({ yr, lo: g[Math.floor(g.length * 0.25)], hi: g[Math.floor(g.length * 0.75)] });
    }
    if (band.length) {
      const dTop = band.map((b, i) => `${i ? "L" : "M"} ${x(b.yr)} ${y(b.hi)}`).join(" ");
      const dBot = band.slice().reverse().map(b => `L ${x(b.yr)} ${y(b.lo)}`).join(" ");
      E("path", { d: dTop + " " + dBot + " Z", fill: css("--de"), opacity: 0.13 }, svg);
      text(svg, x(band[band.length - 1].yr) + 6, y(band[band.length - 1].hi) - 2, "middle half of all teams", { size: 9.5, fill: css("--muted") });
    }
  }
  const TIPLBL = { opp: "Opponents of Argentina", own: "Argentina's players", diff: "Card differential (opp − own)" };
  const line = (key, color, wd) => {
    const p = pts.filter(q => q[key] != null);
    E("path", { d: p.map((q, i) => `${i ? "L" : "M"} ${x(q.year)} ${y(q[key])}`).join(" "),
      fill: "none", stroke: color, "stroke-width": wd, "stroke-linejoin": "round", "stroke-linecap": "round" }, svg);
    for (const q of p) {
      const dot = E("circle", { cx: x(q.year), cy: y(q[key]), r: key === "arg" ? 4.5 : 3.5, fill: color, stroke: css("--surface"), "stroke-width": 2 }, svg);
      hover(dot, `<b>${q.year}</b><br>${key === "arg" ? `${TIPLBL[mode]}: ${r2(q.arg)} /match (${q.argM} matches)` : `Tournament average: ${r2(q.field)} yellows per team-match`}`);
    }
  };
  if (mode !== "diff") line("field", css("--de"), 2);
  line("arg", css("--arg"), 2);
  if (mode === "opp") {
    const p22 = pts.find(q => q.year === 2022);
    text(svg, x(2022), y(p22.arg) - 12, "3.7 a match — a 1-in-2,500 fluke", { anchor: "middle", weight: 700, size: 11.5, fill: css("--ink") });
  }
  for (const yr of [1970, 1982, 1994, 2006, 2018, 2026])
    text(svg, x(yr), H - 22, String(yr), { anchor: "middle", size: 10.5, fill: css("--muted") });
  const CAP = { opp: "Yellow cards shown to Argentina's opponents per match · gray = tournament average per team-match · cards begin 1970",
                own: "Yellow cards shown to Argentina's own players per match · gray = tournament average — note 2022 was high for BOTH sides",
                diff: "Card differential per match (opponents' yellows − Argentina's yellows) · above zero = net card advantage" };
  text(svg, L, H - 6, CAP[mode], { size: 10.5, fill: css("--muted") });
  plot.appendChild(svg);
}

/* ================= Exhibit D: leniency dumbbells + nulls table ================= */
function leniencyRows() {
  return [2018, 2022, 2026].map(yr => {
    const s = D.squad_discipline.filter(r => r.tournament_year === yr && r.fouls_committed != null && r.yellow_cards > 0)
      .map(r => ({ team: r.team, fpy: r.fouls_committed / r.yellow_cards }));
    const a = s.find(r => r.team === "Argentina");
    const med = s.map(r => r.fpy).sort((p, q) => p - q)[Math.floor(s.length / 2)];
    const rank = s.filter(r => r.fpy > a.fpy).length + 1;
    return { yr, arg: a.fpy, med, rank, n: s.length };
  });
}
function drawLeniency(plot) {
  const rows = leniencyRows();
  const W = 440, H = 220, L = 60, R = 30, T = 14, B = 44, iw = W - L - R;
  const maxV = 12, x = (v) => L + (v / maxV) * iw;
  const svg = E("svg", { width: W, height: H, viewBox: `0 0 ${W} ${H}` }, null);
  rows.forEach((r, i) => {
    const yc = T + 26 + i * 52;
    E("line", { x1: x(Math.min(r.arg, r.med)), x2: x(Math.max(r.arg, r.med)), y1: yc, y2: yc, stroke: css("--grid"), "stroke-width": 2 }, svg);
    const dm = E("circle", { cx: x(r.med), cy: yc, r: 6, fill: css("--de"), stroke: css("--surface"), "stroke-width": 2 }, svg);
    hover(dm, `<b>${r.yr}</b> field median: ${r2(r.med)} fouls per yellow`);
    const da = E("circle", { cx: x(r.arg), cy: yc, r: 7, fill: css("--arg"), stroke: css("--surface"), "stroke-width": 2 }, svg);
    hover(da, `<b>${r.yr}</b> Argentina: ${r2(r.arg)} fouls per yellow<br>rank ${r.rank}/${r.n} most leniently treated`);
    text(svg, 8, yc + 4, String(r.yr), { weight: 650, size: 12 });
    text(svg, x(r.arg) + (r.arg >= r.med ? 12 : -12), yc + 4, `${r2(r.arg, 1)} (rank ${r.rank}/${r.n})`,
      { anchor: r.arg >= r.med ? "start" : "end", size: 11, fill: css("--ink") });
  });
  E("line", { x1: L, x2: W - R, y1: H - B + 4, y2: H - B + 4, stroke: css("--axis") }, svg);
  for (const g of [0, 4, 8, 12]) text(svg, x(g), H - B + 18, String(g), { anchor: "middle", size: 10.5, fill: css("--muted") });
  text(svg, 8, H - 6, "Fouls allowed per yellow card received — higher = treated more leniently", { size: 10.5, fill: css("--muted") });
  plot.appendChild(svg);
}
function nullsTable() {
  const rows = D.argentina_2026.filter(r => ["yellows_received", "fouls_committed", "fouls_drawn", "yellows_drawn"].includes(r.metric));
  return {
    cols: [
      { h: "2026 metric", k: "metric", f: v => ({ yellows_received: "Yellows received /match", yellows_drawn: "Opponents' yellows /match", fouls_committed: "Fouls committed /match", fouls_drawn: "Fouls drawn /match" }[v]) },
      { h: "Argentina", k: "arg_rate", f: v => r2(v) }, { h: "Field", k: "field_rate", f: v => r2(v) },
      { h: "Ratio", k: "rate_ratio", f: v => `${r2(v)}×` }, { h: "p", k: "p_value", f: v => r2(v, 2) },
    ], rows, argKey: null,
  };
}

/* ================= Exhibit E: cohort table ================= */
function cohortTable() {
  const rows = D.cohort_2022.sort((a, b) => b.pens_for_pm - a.pens_for_pm);
  return {
    cols: [
      { h: "2022 deep-run team", k: "team_name" }, { h: "Matches", k: "matches" },
      { h: "Card differential /match", k: "card_net_pm", f: v => (v > 0 ? "+" : "") + r2(v) },
      { h: "Penalties scored /match", k: "pens_for_pm", f: (v, r) => r.team_name === "Argentina" ? `<b>${r2(v)}</b> (5 awarded)` : r2(v) },
      { h: "Net pens /match", k: "pen_net_pm", f: v => (v > 0 ? "+" : "") + r2(v) },
    ], rows, argKey: "team_name",
  };
}

/* ================= Exhibit B table: VAR incidents ================= */
function varIncidentTable() {
  const label = { penalty_awarded: "Penalty awarded", penalty_rescinded: "Penalty rescinded", goal_disallowed: "Goal disallowed", goal_awarded: "Goal awarded", red_card_issued: "Red card issued", red_card_rescinded: "Red card rescinded", other: "Other" };
  const rows = D.var_incidents_argentina.map(r => ({ ...r }));
  return {
    cols: [
      { h: "Year", k: "tournament_year" }, { h: "Match", k: "home_team", f: (v, r) => `${esc(r.home_team)} v ${esc(r.away_team)}` },
      { h: "Decision", k: "decision_type", f: v => label[v] || v },
      { h: "Went to", k: "beneficiary_team", f: v => v === "Argentina" ? `<span class="hl">Argentina ✓</span>` : (v || "—") },
      { h: "What happened", k: "description", f: (v, r) => `<span style="color:var(--muted)">${esc(clip(r.description || "", 130))}</span>` },
    ], rows, argKey: "beneficiary_team",
  };
}

/* ================= Exhibit E: cohort strip plot + receipts ================= */
function drawCohortStrip(plot) {
  const data = D.cohort_post22 || [];
  const lanes = [{ yr: 2022, fieldRate: 0.149 }, { yr: 2026, fieldRate: 0.091 }];
  const W = Math.max(700, plot.clientWidth || 920), H = 230, L = 64, R = 40, T = 26;
  const laneH = 74, maxX = 0.8;
  const x = (v) => L + (v / maxX) * (W - L - R);
  const svg = E("svg", { width: W, height: H, viewBox: `0 0 ${W} ${H}` }, null);
  for (const g of [0, 0.2, 0.4, 0.6, 0.8]) {
    E("line", { x1: x(g), x2: x(g), y1: T, y2: T + lanes.length * laneH, stroke: css("--grid") }, svg);
    text(svg, x(g), T + lanes.length * laneH + 16, g.toFixed(1), { anchor: "middle", size: 10.5, fill: css("--muted") });
  }
  lanes.forEach((ln, li) => {
    const yc = T + li * laneH + laneH / 2;
    text(svg, 8, yc + 4, String(ln.yr), { weight: 700, size: 13 });
    E("line", { x1: x(ln.fieldRate), x2: x(ln.fieldRate), y1: yc - 22, y2: yc + 22, stroke: css("--axis"), "stroke-width": 1.5 }, svg);
    text(svg, x(ln.fieldRate), yc - 27, "field avg", { anchor: "middle", size: 9.5, fill: css("--muted") });
    const rows = data.filter(r => r.tournament_year === ln.yr);
    // spread overlapping dots vertically within the lane
    const seen = {};
    for (const r of rows.sort((a, b) => a.pens_pm - b.pens_pm)) {
      const bucket = Math.round(r.pens_pm * 25);
      seen[bucket] = (seen[bucket] || 0);
      const dy = (seen[bucket] % 2 ? -1 : 1) * Math.ceil(seen[bucket] / 2) * 13;
      seen[bucket]++;
      const isArg = r.team === "Argentina";
      const dot = E("circle", { cx: x(r.pens_pm), cy: yc + dy, r: isArg ? 8 : 5.5,
        fill: isArg ? css("--arg") : css("--de"), opacity: isArg ? 1 : 0.6,
        stroke: css("--surface"), "stroke-width": 2 }, svg);
      hover(dot, `<b>${esc(r.team)} ${ln.yr}</b><br>${r.penalty_kicks_attempted} penalties awarded in ${r.matches_played} matches (${r2(r.pens_pm)}/match)`);
      if (isArg)
        text(svg, x(r.pens_pm), yc + dy - 13, `Argentina — ${r.penalty_kicks_attempted} in ${r.matches_played}`, { anchor: "middle", weight: 700, size: 11.5, fill: css("--ink") });
    }
  });
  text(svg, L, H - 2, "Penalties awarded per match, teams with 5+ matches · dot spread is only to avoid overlap", { size: 10.5, fill: css("--muted") });
  plot.appendChild(svg);
}
function receiptsTable() {
  const lbl = v => v ? `<span style="color:var(--ink)">${esc(v)}</span>` : `<span style="color:var(--muted)">—</span>`;
  return {
    cols: [
      { h: "Date", k: "date" }, { h: "Stage", k: "stage", f: v => esc(String(v).replace("stage", "").trim() || "Group") },
      { h: "Opponent", k: "opponent" }, { h: "Score", k: "score" },
      { h: "Pens for", k: "pens_for", f: (v, r) => v ? `<b>${v}</b>${r.pens_note ? `<br><span style="color:var(--muted);font-size:11px">${esc(r.pens_note)}</span>` : ""}` : "—" },
      { h: "Pens against", k: "pens_against", f: v => v || "—" },
      { h: "Opp. reds", k: "opp_reds", f: v => v || "—" },
      { h: "VAR for Argentina", k: "var_for", f: lbl },
      { h: "VAR against", k: "var_against", f: lbl },
    ],
    rows: D.argentina_receipts || [],
  };
}

/* ================= Exhibit F: crew growth (stacked by confederation) ================= */
function drawCrew(plot) {
  const g = D.crew_growth || [];
  const byConf = {};
  for (const r of (D.crew_by_conf || []))
    (byConf[r.tournament_year] = byConf[r.tournament_year] || {})[r.confederation] = r.n;
  const CONFS = [["UEFA", css("--s1")], ["CONMEBOL", css("--s5")], ["CONCACAF", css("--s4")],
                 ["AFC", css("--s6")], ["CAF", css("--s7")], ["OFC", css("--de")]];
  const W = Math.max(380, plot.clientWidth || 440), H = 262, L = 44, R = 16, T = 16, B = 66;
  const iw = W - L - R, ih = H - T - B;
  const maxY = 180, y = (v) => T + ih - (v / maxY) * ih;
  const svg = E("svg", { width: W, height: H, viewBox: `0 0 ${W} ${H}` }, null);
  for (const gv of [0, 60, 120, 180]) {
    E("line", { x1: L, x2: W - R, y1: y(gv), y2: y(gv), stroke: gv === 0 ? css("--axis") : css("--grid") }, svg);
    text(svg, L - 6, y(gv) + 3, String(gv), { anchor: "end", size: 10.5, fill: css("--muted") });
  }
  const bw = Math.min(24, iw / g.length - 5);
  g.forEach((r, i) => {
    const cx = L + (i + 0.5) * (iw / g.length);
    const confs = byConf[r.tournament_year] || {};
    let acc = 0;
    for (const [cf, col] of CONFS) {
      const n = confs[cf] || 0;
      if (!n) continue;
      const seg = E("rect", { x: cx - bw / 2, y: y(acc + n), width: bw, height: Math.max(y(acc) - y(acc + n) - 1.5, 1), rx: 2, fill: col, opacity: 0.88 }, svg);
      hover(seg, `<b>${r.tournament_year}</b> — ${cf}: ${n} officials<br>total ${r.appointed_officials} · crew ${r.avg_match_crew}/match`);
      acc += n;
    }
    if ((i % 4 === 0 && i < g.length - 2) || i === g.length - 1)
      text(svg, cx, H - 48, String(r.tournament_year), { anchor: "middle", size: 10.5, fill: css("--muted") });
    if ([1990, 2018, 2026].includes(r.tournament_year))
      text(svg, cx, y(r.appointed_officials) - 6, String(r.appointed_officials), { anchor: "middle", size: 11, weight: 650, fill: css("--ink") });
  });
  let lx = L;
  for (const [cf, col] of CONFS) {
    E("rect", { x: lx, y: H - 34, width: 10, height: 10, rx: 2, fill: col }, svg);
    text(svg, lx + 13, H - 25, cf, { size: 9.5, fill: css("--ink-2") });
    lx += 24 + cf.length * 6;
  }
  text(svg, 8, H - 8, clip("Appointed officials by confederation · crew 3 → 4 → 8 per match (VAR era)", Math.floor((W - 16) / 5.8)), { size: 10.5, fill: css("--muted") });
  plot.appendChild(svg);
}
function confMixTable() {
  const rows = (D.referee_conf_mix || []).sort((a, b) => b.argentina - a.argentina);
  return {
    cols: [
      { h: "Referee's confederation", k: "confederation" },
      { h: "Share of Argentina matches", k: "argentina", f: v => `${(v * 100).toFixed(1)}%` },
      { h: "Share of all matches", k: "all_matches", f: v => `${(v * 100).toFixed(1)}%` },
    ], rows,
  };
}
function repeatsTable() {
  const rows = (D.referee_repeats || []).sort((a, b) => b.n - a.n || b.n_tournaments - a.n_tournaments);
  return {
    cols: [
      { h: "Team", k: "team" }, { h: "Referee", k: "referee" },
      { h: "Matches", k: "n", f: (v, r) => r.team === "Argentina" && r.n >= 4 ? `<b>${v} — most in dataset</b>` : v },
      { h: "Tournaments", k: "years" },
    ], rows, argKey: "team",
  };
}

/* ---------- render all ---------- */
function render() {
  if (D.argentina_record) {
    card("#chart-record", "Nineteen World Cups, three stars, one pending",
      "Hover any tournament for the full record",
      null, drawRecord, { cols: [{ h: "Year", k: "year" }, { h: "Finish", k: "label" }, { h: "P", k: "matches" }, { h: "W–D–L", k: "wins", f: (v, r) => `${r.wins}–${r.draws}–${r.losses}` }, { h: "Goals", k: "gf", f: (v, r) => `${r.gf}–${r.ga}` }], rows: D.argentina_record });
    browserCard("#table-matches", "Every Argentina World Cup match, 1930–2026",
      "95 matches · filter, sort any column by clicking its header, scroll for all",
      [{ h: "Date", k: "date" }, { h: "Year", k: "year" }, { h: "Stage", k: "stage" }, { h: "Opponent", k: "opponent" },
       { h: "Score", k: "score", f: (v, r) => r.et ? `${v} <span style="color:var(--muted);font-size:11px">aet</span>` : v },
       { h: "Shootout", k: "pens", f: v => v || "—" },
       { h: "Result", k: "result", f: v => `<b style="color:${v === "W" ? "var(--pos)" : v === "L" ? "var(--neg)" : "var(--muted)"}">${v}</b>` }],
      D.argentina_all_matches,
      [{ key: "year", label: "Tournament", type: "select", options: [...new Set(D.argentina_all_matches.map(r => r.year))] },
       { key: "result", label: "Result", type: "select", options: ["W", "D", "L"] },
       { key: "opponent", label: "Opponent", type: "text" }],
      (plot) => yearStackChart(plot, D.argentina_all_matches, {
        yearKey: "year", catOf: r => r.result,
        cats: [{ id: "W", label: "Won", color: css("--arg") }, { id: "D", label: "Drew", color: css("--de") }, { id: "L", label: "Lost", color: css("--neg") }],
        note: "Matches per tournament by result" }));
  }
  card("#chart-pens", "Penalty decisions by tournament: against ← | → for",
    "Every tournament one row · 205 penalties source-verified 1930–2010 + FBref 2014–2026 · ticks mark the going rate",
    [{ color: css("--arg"), label: "Awarded FOR Argentina" }, { color: css("--neg"), label: "Awarded AGAINST" }],
    drawPensDiverging, penEraTableWrap());
  browserCard("#table-pen-browser", "The penalty ledger, raw — all 205 compiled penalties 1930–2010",
    "Every in-game penalty individually source-verified (2014+ lives in FBref squad tables) · filter and sort",
    [{ h: "Year", k: "tournament_year" }, { h: "Date", k: "match_date" }, { h: "Stage", k: "stage" },
     { h: "Awarded to", k: "team_awarded", f: (v, r) => r.team_awarded === "Argentina" ? `<b>${v}</b>` : v },
     { h: "Against", k: "opponent" }, { h: "Taker", k: "taker" },
     { h: "Converted", k: "converted", f: v => v === "yes" ? "yes" : `<span style="color:var(--neg)">no</span>` }],
    D.pens_incidents,
    [{ key: "tournament_year", label: "Tournament", type: "select", options: [...new Set(D.pens_incidents.map(r => r.tournament_year))].sort() },
     { key: "team_awarded", label: "Team", type: "text", also: ["opponent"] },
     { key: "converted", label: "Converted", type: "select", options: ["yes", "no"] }],
    (plot) => yearStackChart(plot, D.pens_incidents, {
      yearKey: "tournament_year", catOf: r => r.converted === "yes" ? "sc" : "miss",
      cats: [{ id: "sc", label: "Scored", color: css("--arg") }, { id: "miss", label: "Missed/saved", color: css("--de") }],
      note: "All compiled penalties per tournament, 1930–2010" }));
  card("#table-pen-eras", "Era by era: how big, how unlikely", "Ratio = times the going rate · p = chance it's luck (small = suspicious) · sources in Method",
    null, (plot) => hbarChart(plot,
      (D.pens_awarded_tests || []).map(r => ({
        label: `${r.era} · ${r.metric === "awarded_for" ? "for" : "against"}`,
        value: r.ratio, hl: r.metric === "awarded_for" && r.ratio > 2,
        tip: `<b>${esc(r.era)}</b> awarded ${r.metric === "awarded_for" ? "FOR" : "AGAINST"}<br>${r.arg} in ${r.arg_matches} matches · ratio ${r.ratio}× · p=${r.p}` })),
      { parity: 1, fmt: v => v + "×", diverge: false, note: "Rate ratio vs field · 1× = treated like everyone else" }),
    { cols: penEraTable().cols, rows: penEraTable().rows });
  varLedgerCard("#chart-var");
  card("#table-var-incidents", "Every VAR intervention in an Argentina match, 2018–2026", "8 favorable · 1 against · source-linked in the data files",
    null, (plot) => yearStackChart(plot, D.var_incidents_argentina, {
      yearKey: "tournament_year",
      catOf: r => r.beneficiary_team === "Argentina" ? "for" : "against",
      cats: [{ id: "for", label: "Favorable to Argentina", color: css("--arg") }, { id: "against", label: "Against", color: css("--neg") }],
      note: "Directional VAR overturns in Argentina matches, by tournament" }),
    (() => { const s = varIncidentTable(); return { cols: s.cols, rows: s.rows, argKey: s.argKey }; })());
  browserCard("#table-var-browser", "The full VAR ledger — all 86 directional overturns, 2018–2026",
    "Every team, every overturn · filter by team, tournament, or decision type · all formerly-ambiguous feed entries resolved as confirmed-call checks (see data notes)",
    [{ h: "Year", k: "tournament_year" }, { h: "Date", k: "match_date" },
     { h: "Match", k: "home_team", f: (v, r) => `${esc(r.home_team)} v ${esc(r.away_team)}` },
     { h: "Decision", k: "decision_type", f: v => String(v).replace(/_/g, " ") },
     { h: "Went to", k: "beneficiary_team", f: (v, r) => r.beneficiary_team === "Argentina" ? `<b>${v}</b>` : v },
     { h: "Against", k: "against_team" }],
    D.var_incidents_all,
    [{ key: "tournament_year", label: "Tournament", type: "select", options: [...new Set(D.var_incidents_all.map(r => r.tournament_year))].sort() },
     { key: "beneficiary_team", label: "Team", type: "text", also: ["against_team", "home_team", "away_team"] },
     { key: "decision_type", label: "Decision", type: "select", options: [...new Set(D.var_incidents_all.map(r => r.decision_type))].sort() }],
    (plot) => yearStackChart(plot, D.var_incidents_all, {
      yearKey: "tournament_year",
      catOf: r => /goal/.test(r.decision_type) ? "goal" : /penalty/.test(r.decision_type) ? "pen" : /red|card/.test(r.decision_type) ? "card" : "other",
      cats: [{ id: "goal", label: "Goal decisions", color: css("--arg") }, { id: "pen", label: "Penalties", color: css("--neg") },
             { id: "card", label: "Cards", color: css("--de") }, { id: "other", label: "Other", color: css("--axis") }],
      note: "Directional VAR overturns per tournament by decision type" }));
  cardsHistoryCard("#table-cards-browser");
  modeCard("#chart-cards", "Yellow cards in Argentina matches, 1970–2026",
    "The 2022 spike is the one result that survives testing every team, metric and era since 1970",
    [{ color: css("--arg"), label: "Argentina metric" }, { color: css("--de"), label: "Tournament average" }],
    [{ id: "opp", label: "Opponents' cards" }, { id: "own", label: "Argentina's cards" }, { id: "diff", label: "Differential" }],
    drawCards, { cols: [{ h: "Year", k: "year" }, { h: "Opp. yellows/match", k: "arg", f: v => r2(v) }, { h: "Tournament avg", k: "field", f: v => r2(v) }], rows: cardTableRows(), argKey: null });
  card("#chart-leniency", "Card leniency: fouls per yellow", "Argentina vs field median — note 2018 and 2022 ran AGAINST them",
    [{ color: css("--arg"), label: "Argentina" }, { color: css("--de"), label: "Field median" }],
    drawLeniency,
    { cols: [{ h: "Year", k: "yr" }, { h: "Argentina fouls/yellow", k: "arg", f: v => r2(v) }, { h: "Field median", k: "med", f: v => r2(v) }, { h: "Leniency rank", k: "rank", f: (v, r) => `${v}/${r.n}` }],
      rows: leniencyRows() });
  card("#table-nulls", "2026 routine decisions: no signal", "Cards and fouls at field rate — the honest nulls",
    null, (plot) => hbarChart(plot,
      nullsTable().rows.map(r => ({
        label: { yellows_received: "Yellows received", yellows_drawn: "Opp. yellows", fouls_committed: "Fouls committed", fouls_drawn: "Fouls drawn" }[r.metric],
        value: r.rate_ratio,
        tip: `<b>${r.metric.replace(/_/g, " ")}</b><br>ARG ${r2(r.arg_rate)} vs field ${r2(r.field_rate)} · p=${r2(r.p_value, 2)}` })),
      { parity: 1, fmt: v => v + "×", note: "2026 routine metrics vs field · all hug the 1× parity line" }),
    (() => { const s = nullsTable(); return { cols: s.cols, rows: s.rows }; })());
  if (D.cohort_post22) {
    card("#chart-cohort", "Penalties awarded per match — every deep-run team, 2022 and 2026",
      "Each dot is a team with 5+ matches; the tick is the whole-tournament average",
      [{ color: css("--arg"), label: "Argentina" }, { color: css("--de"), label: "Other deep-run teams" }],
      drawCohortStrip, { cols: [{ h: "Year", k: "tournament_year" }, { h: "Team", k: "team" }, { h: "Matches", k: "matches_played" }, { h: "Pens awarded", k: "penalty_kicks_attempted" }, { h: "Per match", k: "pens_pm", f: v => r2(v) }], rows: (D.cohort_post22 || []).slice().sort((a, b) => b.pens_pm - a.pens_pm), argKey: "team" });
    card("#table-receipts", "The receipts — all 14 post-2022 matches, decision by decision",
      "Penalties from verified per-match data; VAR events from the incident compilation; 2022 'pens for' are scored penalties (see note on Poland row)",
      null, (plot) => hbarChart(plot,
        (D.argentina_receipts || []).map(r => {
          const fav = r.pens_for + r.opp_reds + (r.var_for ? r.var_for.split(",").length : 0);
          const ag = r.pens_against + r.own_reds + (r.var_against ? r.var_against.split(",").length : 0);
          return { label: `${r.date.slice(2, 10)} ${r.opponent}`, value: fav - ag, hl: fav - ag >= 2,
                   tip: `<b>${esc(r.opponent)} (${esc(r.score)})</b><br>favorable events: ${fav} · against: ${ag}` };
        }),
        { diverge: true, fmt: v => (v > 0 ? "+" : "") + v, labelW: 190, note: "Net high-discretion decisions per match (pens + reds + VAR events, for − against)" }),
      (() => { const s = receiptsTable(); return { cols: s.cols, rows: s.rows }; })());
  }
  card("#table-cohort", "Same cohort, cards view (2022)", "Card differentials: Argentina NOT unique — England and Portugal ran higher. It's the penalties that separate.",
    null, (plot) => hbarChart(plot,
      cohortTable().rows.map(r => ({ label: r.team_name, value: r.card_net_pm, hl: r.team_name === "Argentina",
        tip: `<b>${esc(r.team_name)}</b> 2022 · card diff ${r.card_net_pm > 0 ? "+" : ""}${r2(r.card_net_pm)}/match · pens scored ${r2(r.pens_for_pm)}/match` })),
      { diverge: true, fmt: v => (v > 0 ? "+" : "") + r2(v), note: "Card differential per match, 2022 deep-run teams — Argentina 3rd, not unique" }),
    (() => { const s = cohortTable(); return { cols: s.cols, rows: s.rows, argKey: s.argKey }; })());
  if (D.crew_growth) {
    card("#chart-crew", "The officiating machine grows", "Appointed officials per tournament, 1930–2026",
      null, drawCrew, { cols: [{ h: "Year", k: "tournament_year" }, { h: "Officials", k: "appointed_officials" }, { h: "Avg crew/match", k: "avg_match_crew" }], rows: D.crew_growth });
    card("#table-confmix", "Who referees the CONMEBOL nations?",
      "Share of matches taken by EUROPEAN referees since 1990 · same neutrality rules for everyone — yet Argentina leads the continent",
      null, (plot) => hbarChart(plot,
        (D.conmebol_ref_mix || []).filter(r => r.era === "since 1990" && !r.team.startsWith("—"))
          .sort((a, b) => b.uefa - a.uefa)
          .map(r => ({ label: r.team, value: r.uefa, hl: r.team === "Argentina",
            tip: `<b>${esc(r.team)}</b> since 1990 (${r.matches} matches)<br>UEFA ${r.uefa}% · CONCACAF ${r.concacaf}% · AFC ${r.afc}% · CAF ${r.caf}% · CONMEBOL ${r.conmebol}%` }))
          .concat([{ label: "field average", value: 42.5, hl: false, tip: "<b>All matches since 1990</b><br>UEFA referees take 42.5%" }]),
        { fmt: v => v + "%", note: "UEFA share of each team's referees, 1990–2026 · Brazil went just as deep with 19 points fewer European refs" }),
      { cols: [{ h: "Era", k: "era" }, { h: "Team", k: "team" }, { h: "Matches", k: "matches" },
               { h: "UEFA %", k: "uefa" }, { h: "CONMEBOL %", k: "conmebol" }, { h: "CONCACAF %", k: "concacaf" },
               { h: "AFC %", k: "afc" }, { h: "CAF %", k: "caf" }], rows: D.conmebol_ref_mix || [] });
    card("#table-repeats", "Every referee–team pairing with 3+ matches, 1930–2026", "One pairing in 96 years reaches four — Marciniak with Argentina, spanning the 2022 final and the 2026 opener",
      null, (plot) => hbarChart(plot,
        repeatsTable().rows.slice(0, 14).map(r => ({ label: `${r.referee} · ${r.team}`, value: r.n, hl: r.team === "Argentina",
          tip: `<b>${esc(r.referee)}</b> × ${esc(r.team)}<br>${r.n} matches (${esc(r.years)})` })),
        { labelW: 230, note: "Matches per referee–team pairing · blue = Argentina pairings" }),
      (() => { const s = repeatsTable(); return { cols: s.cols, rows: s.rows, argKey: s.argKey }; })());
    if (D.argentina_official_comparison) officialComparisonCard("#table-official-records");
  }
  if (D.draw_group_summary) {
    card("#chart-groupdraw", "Argentina's group difficulty, every tournament since 1930",
      "Percentile vs all teams' groups that year — below the median almost every time, long before 2022 · Table shows all three metrics vs fellow top seeds",
      null, drawGroupPctl, (() => { const s = drawSummaryTable(); return { cols: s.cols, rows: s.rows }; })());
    card("#chart-kopaths", "The 2026 knockout roads",
      "Softest on every metric: Elo, FIFA rank, and top seeds faced",
      [{ color: css("--arg"), label: "Argentina" }, { color: css("--de"), label: "Other quarterfinalists" }],
      drawKoPaths, { cols: [{ h: "Year", k: "year" }, { h: "Team", k: "team" }, { h: "Path Elo", k: "path_elo" }, { h: "Path FIFA", k: "path_fifa" }, { h: "Top seeds faced", k: "pot1_opps" }, { h: "Route", k: "route" }], rows: D.draw_ko_paths });
    if (D.hypo_arg_ranks) {
      card("#chart-hypopaths", "The road as projected AT THE DRAW — before any results",
        "Argentina's projected run-to-final difficulty, ranked among that tournament's top eight seeds · 1 = hardest draw · weighted = opponents counted by their Elo chance of showing up",
        [{ color: css("--arg"), label: "Weighted projection" }, { color: css("--de"), label: "Unweighted" }],
        (plot) => {
          const d = D.hypo_arg_ranks;
          const W = Math.max(700, plot.clientWidth || 900), H = 260, L = 96, R = 24, T = 18, B = 44;
          const iw = W - L - R, ih = H - T - B;
          const x = (yr) => L + ((yr - 1986) / (2026 - 1986)) * iw;
          const y = (rank) => T + ((rank - 1) / 8) * ih; // rank 1 (hardest) at TOP
          const svg = E("svg", { width: W, height: H, viewBox: `0 0 ${W} ${H}` }, null);
          for (const g of [1, 3, 5, 7, 9]) {
            E("line", { x1: L, x2: W - R, y1: y(g), y2: y(g), stroke: css("--grid") }, svg);
            text(svg, L - 6, y(g) + 3, g === 1 ? "1 hardest" : g === 9 ? "9 easiest" : String(g), { anchor: "end", size: 10, fill: css("--muted") });
          }
          for (const [key, col, wd] of [["unw", css("--de"), 2], ["wt", css("--arg"), 2.5]]) {
            const pts = d.map(r => ({ yr: r.year, rank: +r[key].split("/")[0], of: +r[key].split("/")[1] }));
            E("path", { d: pts.map((p, i) => `${i ? "L" : "M"} ${x(p.yr)} ${y(p.rank)}`).join(" "), fill: "none", stroke: col, "stroke-width": wd, "stroke-linejoin": "round", opacity: key === "unw" ? 0.6 : 1 }, svg);
            for (const p of pts) {
              const dot = E("circle", { cx: x(p.yr), cy: y(p.rank), r: key === "wt" ? 5 : 3.5, fill: col, stroke: css("--surface"), "stroke-width": 2 }, svg);
              hover(dot, `<b>${p.yr}</b> — projected ${p.rank} of ${p.of} among seeds (${key === "wt" ? "weighted" : "unweighted"})<br>1 = hardest projected road`);
            }
          }
          for (const r of d.filter(q => [1994, 2018, 2022, 2026].includes(q.year)))
            text(svg, x(r.year), y(+r.wt.split("/")[0]) + (+r.wt.split("/")[0] > 4 ? 18 : -10), String(r.year), { anchor: "middle", size: 10.5, weight: 700, fill: css("--ink") });
          for (const yr of [1986, 1998, 2010, 2022])
            text(svg, x(yr), H - 26, String(yr), { anchor: "middle", size: 10, fill: css("--muted") });
          text(svg, L, H - 8, clip("Bracket + Elo projection at the draw · 2022 and 2026 sat near the bottom (easy); 1994 and 2018 at the top (hard)", Math.floor((W - L) / 5.8)), { size: 10.5, fill: css("--muted") });
          plot.appendChild(svg);
        },
        { cols: [{ h: "Year", k: "year" }, { h: "Unweighted rank", k: "unw" }, { h: "Weighted rank", k: "wt" }], rows: D.hypo_arg_ranks });
    }
  }
  if (D.copa_control) {
    card("#chart-copa", "Penalty-award rate vs field — Argentina by competition and edition",
      "Ratio of Argentina's awarded-penalty rate to the field's · 1.0 = treated like everyone else",
      [{ color: css("--de"), label: "Copa América (CONMEBOL)" }, { color: css("--arg"), label: "World Cup (FIFA)" }],
      (plot) => {
        const d = D.copa_control;
        const W = Math.max(700, plot.clientWidth || 920), H = 280, L = 46, R = 20, T = 18, B = 46;
        const iw = W - L - R, ih = H - T - B, maxY = 5.5;
        const y = (v) => T + ih - (v / maxY) * ih;
        const svg = E("svg", { width: W, height: H, viewBox: `0 0 ${W} ${H}` }, null);
        for (const g of [0, 1, 2, 3, 4, 5]) {
          E("line", { x1: L, x2: W - R, y1: y(g), y2: y(g), stroke: g === 1 ? css("--axis") : css("--grid"), "stroke-width": g === 1 ? 1.5 : 1 }, svg);
          text(svg, L - 6, y(g) + 3, g + "×", { anchor: "end", size: 10.5, fill: g === 1 ? css("--ink-2") : css("--muted") });
        }
        text(svg, W - R, y(1) - 5, "parity", { anchor: "end", size: 10, fill: css("--muted") });
        const bw = Math.min(40, iw / d.length - 14);
        d.forEach((r, i) => {
          const cx = L + (i + 0.5) * (iw / d.length);
          const isWC = r.comp === "World Cup";
          const bar = E("path", { d: roundTop(cx - bw / 2, y(r.ratio), bw, Math.max(y(0) - y(r.ratio), 1), 4), fill: isWC ? css("--arg") : css("--de"), opacity: isWC ? 1 : 0.6 }, svg);
          hover(bar, `<b>${esc(r.comp)} ${r.year}</b><br>${r.arg} penalties awarded in ${r.matches} matches<br>${r.ratio}× the field rate`);
          text(svg, cx, H - 26, `'${String(r.year).slice(2)}`, { anchor: "middle", size: 10.5, fill: css("--muted") });
          if (isWC) text(svg, cx, y(r.ratio) - 6, `${r.ratio}×`, { anchor: "middle", weight: 700, size: 11.5, fill: css("--ink") });
        });
        text(svg, L, H - 8, "Copa editions with published penalty data (2015–2024) + World Cups 2022–2026 · same team, two organizers", { size: 10.5, fill: css("--muted") });
        plot.appendChild(svg);
      },
      { cols: [{ h: "Competition", k: "comp" }, { h: "Year", k: "year" }, { h: "Pens awarded", k: "arg", f: (v, r) => `${v} in ${r.matches}` }, { h: "Ratio vs field", k: "ratio", f: v => `${v}×` }], rows: D.copa_control });
    card("#table-copa-recent", "Argentina's recent Copa América record", "16 titles all-time (the record) · the 1993–2021 drought ended in the same window the World Cup anomaly began",
      null, (plot) => hbarChart(plot,
        (D.copa_recent || []).map(r => {
          const FIN = { "Champions": 5, "Runners-up": 4, "Third place": 3, "Semi-finals": 3, "Quarter-finals": 2, "Group stage": 1 };
          const v = FIN[r.finish] ?? (/champ/i.test(String(r.finish)) ? 5 : /runner/i.test(String(r.finish)) ? 4 : /third|semi/i.test(String(r.finish)) ? 3 : 2);
          return { label: `${r.year} (${r.host})`, value: v, hl: v === 5,
                   tip: `<b>Copa ${r.year}</b> — ${esc(r.finish)}<br>${r.wins}W ${r.draws}D ${r.losses}L` };
        }),
        { labelW: 160, fmt: v => ({ 5: "★ Champions", 4: "Final", 3: "Semis/3rd", 2: "QF", 1: "Groups" }[v] || v), note: "Finish per edition · titles in blue" }),
      { cols: [
          { h: "Edition", k: "year" }, { h: "Host", k: "host" },
          { h: "Finish", k: "finish", f: v => /^Champ/i.test(String(v)) ? `<b>${v} ★</b>` : v },
          { h: "P", k: "matches" }, { h: "W–D–L", k: "wins", f: (v, r) => `${r.wins}–${r.draws}–${r.losses}` },
        ], rows: D.copa_recent });
  }
  (function tapeSubmitCard() {
    const host = $("#tape-submit"); if (!host) return;
    const matches = (D.argentina_all_matches || []).filter(m => m.year >= 2022)
      .map(m => `${m.year} · ${m.stage} · vs ${m.opponent} (${m.date})`)
      .concat(["2026 · Final · vs Spain (2026-07-19)"]);
    host.innerHTML = `<div class="card-head"><div>
        <div class="card-title">Seen something we missed? Add a moment — 2022 &amp; 2026 matches</div>
        <div class="card-sub">Suggest a contested call from any Argentina match in Qatar 2022 or 2026 — a video link, or a timestamp and what happened. Every submission is verified against footage and press before publication; verified moments join the index above, credited as community-sourced.</div></div></div>
      <div class="filters" style="align-items:flex-start;flex-direction:column;gap:8px;max-width:640px">
        <div style="display:flex;gap:10px;flex-wrap:wrap;width:100%">
          <select id="tsMatch" style="flex:2;min-width:250px">${matches.map(m => `<option>${esc(m)}</option>`).join("")}</select>
          <input id="tsMinute" type="text" placeholder="minute (e.g. 58')" style="width:110px">
          <select id="tsDir" style="width:170px"><option>favored Argentina</option><option>against Argentina</option><option>not sure</option></select>
        </div>
        <textarea id="tsDesc" rows="3" placeholder="What happened? (the more specific, the faster it verifies)" style="width:100%;background:var(--surface);color:var(--ink);border:1px solid var(--axis);border-radius:6px;padding:8px;font-family:var(--sans);font-size:12.5px"></textarea>
        <input id="tsVideo" type="url" placeholder="video link (optional — official uploads only, please)" style="width:100%">
        <input id="tsWeb" type="text" name="website" tabindex="-1" autocomplete="off" style="position:absolute;left:-9999px;height:0;width:0;opacity:0" aria-hidden="true">
        <div style="display:flex;gap:12px;align-items:center">
          <button id="tsSend" class="toggle" style="font-family:var(--sans);font-size:13px;font-weight:650;background:var(--ink);color:var(--paper);border:none;border-radius:6px;padding:8px 18px;cursor:pointer">Submit for review</button>
          <span id="tsNote" class="rescount"></span>
        </div>
      </div>`;
    $("#tsSend").onclick = async () => {
      const payload = {
        match: $("#tsMatch").value, minute: $("#tsMinute").value.trim() || null,
        direction: $("#tsDir").value, description: $("#tsDesc").value.trim() || null,
        video: $("#tsVideo").value.trim() || null,
      };
      if (!payload.description && !payload.video) { $("#tsNote").textContent = "add a description or a video link first"; return; }
      if ($("#tsWeb") && $("#tsWeb").value) { $("#tsNote").textContent = "received — thank you."; return; } // honeypot: bots fill hidden fields
      $("#tsSend").disabled = true;
      try {
        const r = await fetch(SUPA_URL + "/rest/v1/tape_submissions", {
          method: "POST", headers: { ...SUPA_HEADERS, Prefer: "return=minimal" },
          body: JSON.stringify(payload),
        });
        if (r.ok) {
          $("#tsNote").textContent = "received — thank you. It joins the index above once verified.";
          $("#tsDesc").value = ""; $("#tsVideo").value = ""; $("#tsMinute").value = "";
        } else {
          $("#tsNote").textContent = "submission failed (" + r.status + ") — please try again";
        }
      } catch (e) { $("#tsNote").textContent = "network error — please try again"; }
      $("#tsSend").disabled = false;
    };
    // pull verified community moments into the tape (approved rows only are visible to this key)
    fetch(SUPA_URL + "/rest/v1/tape_submissions?status=eq.approved&select=match,minute,direction,description,video&order=created_at.asc",
      { headers: SUPA_HEADERS })
      .then(r => r.ok ? r.json() : [])
      .then(rows => {
        if (!rows.length) return;
        const extra = rows.map(r => ({
          year: +(String(r.match).slice(0, 4)) || 2026,
          opponent: (String(r.match).match(/vs ([^(]+)/) || [, "?"])[1].trim(),
          minute: r.minute || "", incident: "Community-verified moment",
          direction: r.direction === "favored Argentina" ? "favored_argentina"
            : r.direction === "against Argentina" ? "against_argentina" : "disputed",
          description: r.description || "", press_url: "", video_url: r.video || "",
          video_source: r.video ? "community link" : "",
        }));
        window.__tapeCommunity = extra;
        if (typeof window.__rebuildTape === "function") window.__rebuildTape();
      })
      .catch(() => {});
  })();
  (function verdictCard() {
    const V = {
      BIAS: ["POINTS TO BIAS", "var(--neg)", "color-mix(in srgb, var(--neg) 14%, transparent)"],
      MIXED: ["MIXED", "#a07400", "color-mix(in srgb, var(--s4) 22%, transparent)"],
      CLEAN: ["NO EVIDENCE", "var(--ink-2)", "color-mix(in srgb, var(--de) 18%, transparent)"],
      CTX: ["CONTEXT", "var(--muted)", "color-mix(in srgb, var(--de) 10%, transparent)"],
    };
    const rows = [
      { ex: "A · Penalties", q: "Awards for and against, 1930–2026", f: "92 years bang average, then 5× the field across 2022+2026 (≈1 in 2,200). Led both tournaments. Survives every stress test.", v: "BIAS" },
      { ex: "B · VAR", q: "Every overturn since video review began", f: "8–1 in Argentina's favor; 5–0 in 2026 (≈1 in 100). The one fully-recorded decision class — and it leans one way.", v: "BIAS" },
      { ex: "C · Cards", q: "Yellows and reds, both directions, 1970–2026", f: "One genuine 2022 anomaly (opponents' yellows, the only survivor of testing everything) — but two-sided, gone by 2026, and Argentina were carded HARSHLY per foul in 2018–22.", v: "MIXED" },
      { ex: "D · The officials", q: "Who gets appointed, and how they behave", f: "Marciniak×4 is unique in 96 years (~1-in-10 odds); UEFA refs take 74% of their matches — most in CONMEBOL, 19 points above Brazil. But four forensic tests find no referee whose BEHAVIOR favors them.", v: "MIXED" },
      { ex: "E · The draw", q: "Groups and knockout roads, projected and realized", f: "Groups soft forever — no 2022 change. But both post-2022 brackets projected easy at the draw, and the realized 2026 road is the softest any contender has walked.", v: "MIXED" },
      { ex: "F · The presidents", q: "Eras of FIFA leadership overlaid on the record", f: "Infantino era: best win rate ever, penalty balance 5× any previous reign. Correlation, not causation — flagged because of the era's off-pitch backdrop.", v: "CTX" },
      { ex: "G · The tape", q: "26 contested calls with footage", f: "17 favored Argentina, 6 against, 3 disputed. Vivid, sourced — but curated by history, not a statistic.", v: "CTX" },
      { ex: "H · Copa control", q: "Same team under a different organizer", f: "Penalty rate bang normal in five straight Copas, including both recent title runs. The anomaly follows the organizer, not the team. The cleanest single test in the file.", v: "BIAS" },
      { ex: "I · The whistle", q: "828 players, every tackle, foul-by-foul events", f: "No swallowed-whistle signature anywhere: same players get MORE fouls called at World Cups than at the Copa; rope-before-booking is a coin flip. Fourth straight all-clear on routine officiating.", v: "CLEAN" },
    ];
    const chip = v => `<span style="font-family:var(--sans);font-size:11px;font-weight:700;letter-spacing:.07em;padding:3px 8px;border-radius:4px;background:${V[v][2]};color:${V[v][1]};white-space:nowrap">${V[v][0]}</span>`;
    card("#table-verdict", "Nine exhibits, nine rulings", "POINTS TO BIAS = an anomaly that survived every control · MIXED = real pattern, innocent explanations still live · NO EVIDENCE = tested and clean",
      null,
      (plot) => {
        plot.innerHTML = `<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:12px;margin-top:14px">` +
          rows.map(r => `<div style="border:1px solid var(--grid);border-radius:10px;padding:13px 15px">
            <div style="display:flex;justify-content:space-between;gap:8px;align-items:baseline">
              <span style="font-family:var(--sans);font-weight:700;font-size:13.5px">${r.ex}</span>${chip(r.v)}</div>
            <div style="font-family:var(--sans);font-size:12.5px;color:var(--muted);margin-top:7px">${r.f}</div></div>`).join("") + `</div>`;
      },
      { cols: [{ h: "Exhibit", k: "ex" }, { h: "What it tested", k: "q" }, { h: "Finding", k: "f" }, { h: "Ruling", k: "v", f: v => chip(v) }], rows });
  })();
  if (D.var_confirmed) {
    browserCard("#table-var-confirmed", "The checks that stood — every recorded confirmed VAR review",
      "74 reviews where the on-field call was checked and upheld · a LOWER BOUND, biased toward heavily-covered matches (see note below) · 'favoured' = the team the standing decision helped",
      [{ h: "Year", k: "tournament_year" }, { h: "Date", k: "match_date" },
       { h: "Match", k: "home_team", f: (v, r) => `${esc(r.home_team)} v ${esc(r.away_team)}` },
       { h: "Min", k: "minute", f: v => v ?? "—" },
       { h: "What was checked", k: "review_subject", f: v => `<span style="color:var(--muted)">${esc(clip(v || "", 90))}</span>` },
       { h: "Stood as", k: "standing_decision", f: v => esc(clip(v || "", 40)) },
       { h: "Favoured", k: "favoured_team", f: v => v ? (v === "Argentina" ? `<b>${esc(v)}</b>` : esc(v)) : `<span style="color:var(--muted)">unknown</span>` }],
      D.var_confirmed,
      [{ key: "tournament_year", label: "Tournament", type: "select", options: [...new Set(D.var_confirmed.map(r => r.tournament_year))].sort() },
       { key: "favoured_team", label: "Team", type: "text", also: ["home_team", "away_team"] }],
      (plot) => yearStackChart(plot, D.var_confirmed, {
        yearKey: "tournament_year",
        catOf: r => r.favoured_team ? "known" : "unknown",
        cats: [{ id: "known", label: "Beneficiary identified", color: css("--arg") }, { id: "unknown", label: "Subject never reported", color: css("--de") }],
        note: "Recorded confirmed reviews per tournament — the visible tip of an unlogged iceberg" }));
  }
  if (D.whistle_team) {
    modeCard("#chart-whistle", "Argentina's whistle treatment vs the field, six tournaments",
      "Ratio to field rate · 1.0 = treated like everyone else · exposure = tackles won",
      [{ color: css("--arg"), label: "World Cup" }, { color: css("--de"), label: "Copa América" }],
      [{ id: "fpt", label: "Fouls per tackle" }, { id: "cpf", label: "Cards per foul" }],
      (plot, mode) => {
        const d = D.whistle_team;
        const W = Math.max(700, plot.clientWidth || 920), H = 260, L = 46, R = 20, T = 18, B = 46;
        const iw = W - L - R, ih = H - T - B, maxY = 1.8;
        const y = (v) => T + ih - (v / maxY) * ih;
        const svg = E("svg", { width: W, height: H, viewBox: `0 0 ${W} ${H}` }, null);
        for (const g of [0, 0.5, 1, 1.5]) {
          E("line", { x1: L, x2: W - R, y1: y(g), y2: y(g), stroke: g === 1 ? css("--axis") : css("--grid"), "stroke-width": g === 1 ? 1.5 : 1 }, svg);
          text(svg, L - 6, y(g) + 3, g.toFixed(1) + "×", { anchor: "end", size: 10.5, fill: css("--muted") });
        }
        text(svg, W - R, y(1) - 5, "parity", { anchor: "end", size: 10, fill: css("--muted") });
        const bw = Math.min(44, iw / d.length - 16);
        d.forEach((r, i) => {
          const v = mode === "fpt" ? r.fpt_ratio : r.cpf_ratio;
          const p = mode === "fpt" ? r.p_fpt : r.p_cpf;
          const cx = L + (i + 0.5) * (iw / d.length);
          const isWC = r.comp === "WC";
          const bar = E("path", { d: roundTop(cx - bw / 2, y(v), bw, Math.max(y(0) - y(v), 1), 4), fill: isWC ? css("--arg") : css("--de"), opacity: isWC ? 1 : 0.6 }, svg);
          hover(bar, `<b>${r.comp === "WC" ? "World Cup" : "Copa América"} ${r.year}</b><br>` +
            (mode === "fpt" ? `fouls per tackle-won: ARG ${r.arg_fpt} vs field ${r.field_fpt}` : `cards per foul: ARG ${r.arg_cpf} vs field ${r.field_cpf}`) +
            `<br>ratio ${v}× · p=${p}`);
          text(svg, cx, H - 26, `${r.comp} '${String(r.year).slice(2)}`, { anchor: "middle", size: 10.5, fill: css("--muted") });
          if (p < 0.05) text(svg, cx, y(v) - 6, `${v}× p=${p}`, { anchor: "middle", size: 10.5, weight: 700, fill: css("--ink") });
        });
        text(svg, L, H - 8, mode === "fpt"
          ? "Below 1.0 = fewer fouls called per tackle than the field (the whistle-swallowing signature). It never appears significantly at a World Cup."
          : "Below 1.0 = fewer cards per foul. Argentina ran HARSHER than field 2018–2022; mildest in 2026 (n.s.).", { size: 10.5, fill: css("--muted") });
        plot.appendChild(svg);
      },
      { cols: [{ h: "Comp", k: "comp" }, { h: "Year", k: "year" }, { h: "ARG fouls/tackle", k: "arg_fpt" }, { h: "Field", k: "field_fpt" }, { h: "Ratio", k: "fpt_ratio", f: v => `${v}×` }, { h: "p", k: "p_fpt" }, { h: "ARG cards/foul", k: "arg_cpf" }, { h: "Field", k: "field_cpf" }, { h: "Ratio", k: "cpf_ratio", f: v => `${v}×` }, { h: "p", k: "p_cpf" }], rows: D.whistle_team });
    card("#table-whistle-pairs", "Same twelve players, two organizers (2021–2026)",
      "Aggregate: 1.15 fouls per tackle at World Cups vs 0.94 at the Copa — the same players get MORE whistles against them at FIFA events, the opposite of the swallowed-whistle signature.",
      null, (plot) => dumbbellChart(plot,
        D.whistle_pairs.filter(r => r.is_arg === true || r.is_arg === "True")
          .map(r => ({ label: r.player, a: r.wc_fpt, b: r.cp_fpt })),
        { la: "World Cup", lb: "Copa América", note: "Fouls per tackle won · right = more whistles" }),
      { cols: [
          { h: "Player", k: "player" },
          { h: "WC tackles won", k: "wc_tklw" }, { h: "WC fouls/tackle", k: "wc_fpt" },
          { h: "Copa tackles won", k: "cp_tklw" }, { h: "Copa fouls/tackle", k: "cp_fpt" },
        ], rows: D.whistle_pairs.filter(r => r.is_arg === true || r.is_arg === "True") });
    card("#table-whistle-context", "Reading the ratios", "Defenders tackle cleanest (their craft); forwards foul tactically but rarely get carded. Player comparisons must respect position — the browser below filters by it.",
      null, (plot) => hbarChart(plot,
        [{ label: "Defenders", value: 0.71 }, { label: "Midfielders", value: 1.00 }, { label: "Forwards", value: 1.05 }]
          .map(r => ({ ...r, tip: `<b>${r.label}</b>: median ${r.value} fouls per tackle won` })),
        { fmt: v => r2(v), note: "Median fouls per tackle by position (828 players)" }),
      { cols: [{ h: "Position", k: "pos" }, { h: "Median fouls/tackle", k: "fpt" }, { h: "Median cards/foul", k: "cpf" }],
        rows: [{ pos: "Defenders", fpt: 0.71, cpf: 0.11 }, { pos: "Midfielders", fpt: 1.00, cpf: 0.08 }, { pos: "Forwards", fpt: 1.05, cpf: 0.00 }] });
    browserCard("#table-whistle-players", "The player browser — 828 players, six tournaments",
      "Minimum 180 minutes and 3 tackles won · fpt = fouls per tackle won, cpf = cards per foul · click headers to sort",
      [{ h: "Player", k: "player", f: (v, r) => r.team === "Argentina" ? `<b>${v}</b>` : v },
       { h: "Team", k: "team" }, { h: "Comp", k: "competition" }, { h: "Year", k: "year" },
       { h: "Pos", k: "pos" }, { h: "Min", k: "minutes" }, { h: "Tkl won", k: "tackles_won" },
       { h: "Fouls", k: "fouls_committed" }, { h: "Cards", k: "cards" },
       { h: "Fouls/tackle", k: "fpt" }, { h: "Cards/foul", k: "cpf", f: v => v ?? "—" }],
      D.whistle_players,
      [{ key: "competition", label: "Competition", type: "select", options: [...new Set(D.whistle_players.map(r => r.competition))] },
       { key: "year", label: "Year", type: "select", options: [...new Set(D.whistle_players.map(r => r.year))].sort() },
       { key: "pos", label: "Position", type: "select", options: ["DF", "MF", "FW", "GK"] },
       { key: "team", label: "Team / player", type: "text", also: ["player"] }],
      (plot) => hbarChart(plot,
        D.whistle_players.filter(r => r.tackles_won >= 12).sort((a, b) => a.fpt - b.fpt).slice(0, 16)
          .map(r => ({ label: `${r.player} '${String(r.year).slice(2)}`, value: r.fpt, hl: r.team === "Argentina",
            tip: `<b>${esc(r.player)}</b> (${esc(r.team)}, ${esc(r.competition)} ${r.year})<br>${r.tackles_won} tackles won, ${r.fouls_committed} fouls → ${r.fpt} fouls/tackle` })),
        { labelW: 210, fmt: v => r2(v), note: "Cleanest high-volume tacklers (≥12 tackles won): fewest fouls called per tackle · blue = Argentina" }));
  }
  if (D.whistle_rope) {
    card("#chart-rope", "The rope: fouls a player commits before his first yellow",
      "Event-by-event data (StatsBomb), every foul in order, 2018 + 2022 · Argentina 2022: 0.88 fouls of rope vs field 0.75 — 9th of 32, a coin-flip (p=0.34) · 2018 flips the other way · no 2026 event data exists publicly",
      null, (plot) => hbarChart(plot,
        D.whistle_rope.filter(r => r.year === 2022).sort((a, b) => b.mean_fouls_before_first_yellow - a.mean_fouls_before_first_yellow).slice(0, 16)
          .map(r => ({ label: r.team, value: r.mean_fouls_before_first_yellow, hl: r.team === "Argentina",
            tip: `<b>${esc(r.team)} 2022</b><br>${r.mean_fouls_before_first_yellow} fouls before first yellow (avg over ${r.booked_player_matches} booked player-matches)<br>${r2(r.fouls_per_booking, 1)} fouls per booking` })),
        { fmt: v => r2(v), note: "2022, top 16 of 32 teams by rope · most rope went to the Netherlands — and the single longest rope of all was Dumfries, against Argentina" }),
      { cols: [{ h: "Year", k: "year" }, { h: "Team", k: "team" }, { h: "Fouls", k: "fouls_total" }, { h: "Booked player-matches", k: "booked_player_matches" }, { h: "Mean fouls before 1st yellow", k: "mean_fouls_before_first_yellow" }, { h: "Fouls per booking", k: "fouls_per_booking" }], rows: D.whistle_rope });
  }
  if (D.contested_calls) {
    const DIR = { favored_argentina: ["Favored ARG", "var(--pos)"], against_argentina: ["Against ARG", "var(--neg)"], disputed: ["Disputed", "var(--muted)"] };
    const link = (url, label) => url ? `<a href="${esc(url)}" target="_blank" rel="noopener" style="color:var(--arg);text-decoration:none;border-bottom:1px solid color-mix(in srgb, var(--arg) 40%, transparent)">${label}</a>` : `<span style="color:var(--muted)">—</span>`;
    window.__rebuildTape = () => {
    const allRows = D.contested_calls.concat(window.__tapeCommunity || []);
    browserCard("#table-tape", "The contested-calls index, 1930–2026" + (window.__tapeCommunity ? ` (+${window.__tapeCommunity.length} community-verified)` : ""),
      "26 researched incidents · 18 with verified official video · community-verified moments appended as approved · filter by direction or search any text",
      [{ h: "Year", k: "year" }, { h: "Opponent", k: "opponent" }, { h: "Min", k: "minute" },
       { h: "Incident", k: "incident", f: (v, r) => `<b>${v}</b><br><span style="color:var(--muted);font-size:11.5px">${esc(clip(r.description || "", 110))}</span>` },
       { h: "Direction", k: "direction", f: v => { const d = DIR[String(v).replace(/&.+?;/g, "")] || DIR[v] || ["?", "var(--muted)"]; return `<span style="color:${d[1]};font-weight:650;font-size:12px">${d[0]}</span>`; } },
       { h: "Watch", k: "video_url", f: (v, r) => link(r.video_url, `▶ ${esc(r.video_source || "video")}`) },
       { h: "Press", k: "press_url", f: (v, r) => link(r.press_url, "source") }],
      allRows,
      [{ key: "direction", label: "Direction", type: "select", options: ["favored_argentina", "against_argentina", "disputed"] },
       { key: "incident", label: "Search", type: "text", also: ["opponent", "description"] }],
      (plot) => yearStackChart(plot, allRows, {
        yearKey: "year", catOf: r => r.direction,
        cats: [{ id: "favored_argentina", label: "Favored ARG", color: css("--arg") },
               { id: "against_argentina", label: "Against ARG", color: css("--neg") },
               { id: "disputed", label: "Disputed", color: css("--de") }],
        note: "Contested calls per tournament by direction" }));
    };
    window.__rebuildTape();
  }
  if (D.decision_impact) {
    card("#table-impact", "What the decisions were worth — goals-equivalent swing per match",
      "Conventions: penalty = 0.78 goals (expected value at the whistle) · goal disallowed = 1.00 · opponent red ≈ 0.50. Totals: 2022 +1.84 (the final ran against Argentina, −0.78) · 2026 so far +4.84 — larger than the title run. Two matches flip on decisions alone: Netherlands '22, Egypt '26.",
      null, (plot) => hbarChart(plot,
        D.decision_impact.map(r => ({ label: `${r.date.slice(2, 10)} ${r.opponent}`, value: r.net_swing, hl: !!r.decisive,
          tip: `<b>${esc(r.opponent)} (${esc(r.score)})</b><br>net decision swing ${r.net_swing > 0 ? "+" : ""}${r.net_swing} goals-eq · margin ${r.margin}${r.decisive ? "<br><b>decision-decisive</b>" : ""}` })),
        { diverge: true, fmt: v => (v > 0 ? "+" : "") + v, labelW: 190, note: "Goals-equivalent swing per match · blue = the swing covered the winning margin" }),
      { cols: [
          { h: "Date", k: "date" }, { h: "Opponent", k: "opponent" }, { h: "Score", k: "score" },
          { h: "Net swing (goals-eq)", k: "net_swing", f: v => `<span style="color:${v > 0 ? "var(--pos)" : v < 0 ? "var(--neg)" : "var(--muted)"}">${v > 0 ? "+" : ""}${v}</span>` },
          { h: "Margin", k: "margin", f: v => (v > 0 ? "+" : "") + v },
          { h: "Decision-decisive", k: "decisive", f: v => v ? `<b style="color:var(--neg)">YES</b>` : "—" },
        ], rows: D.decision_impact });
  }
  if (D.president_eras) {
    card("#table-presidents", "Argentina by FIFA presidency", "Era bands are also drawn on the Prologue timeline. *2026 final pending.",
      null, (plot) => hbarChart(plot,
        D.president_eras.map(r => ({ label: r.era, value: r.pens_net_pm, hl: r.era === "Infantino",
          tip: `<b>${esc(r.era)}</b> (${esc(r.span)})<br>${r.record}, ${r.win_pct}% wins<br>pens ${r.pens_for}–${r.pens_against} · net ${r.pens_net_pm > 0 ? "+" : ""}${r.pens_net_pm}/match<br>${esc(r.honors)}` })),
        { diverge: true, fmt: v => (v > 0 ? "+" : "") + v, note: "Net penalty decisions per match by FIFA presidency · hover for full era record" }),
      { cols: [
          { h: "President", k: "era" }, { h: "Reign (WCs)", k: "span" }, { h: "Matches", k: "matches" },
          { h: "W–D–L", k: "record" }, { h: "Win %", k: "win_pct", f: (v, r) => r.era === "Infantino" ? `<b>${v}%</b>` : `${v}%` },
          { h: "Pens for–against", k: "pens_for", f: (v, r) => `${v}–${r.pens_against}` },
          { h: "Net pens /match", k: "pens_net_pm", f: (v, r) => r.era === "Infantino" ? `<b>+${v}</b>` : (v > 0 ? "+" : "") + v },
          { h: "Honors", k: "honors" },
        ], rows: D.president_eras });
  }
  if (D.forensics_champions) {
    card("#table-forensics-verdicts", "Four tests, four verdicts", "Each test attacks the bias thesis from a different angle; full methods in analysis/subreports/",
      null, forensicsVerdicts,
      { cols: [{ h: "Test", k: "test" }, { h: "Question", k: "q" }, { h: "Result", k: "r" }, { h: "Verdict", k: "v", f: v => fChip(v) }], rows: FORENSICS_ROWS });
    if (D.robustness_tests)
      card("#table-robustness", "Stress tests — does the penalty finding survive?",
        "Each row removes a piece of the evidence and re-runs the exact test",
        null, (plot) => hbarChart(plot,
          D.robustness_tests.map(r => ({ label: r.test, value: r.ratio, hl: r.ratio > 2,
            tip: `<b>${esc(r.test)}</b><br>${esc(r.argentina)} · ratio ${r.ratio}× · p=${r.p}<br><span style="opacity:.75">${esc(r.note)}</span>` })),
          { parity: 1, fmt: v => v + "×", labelW: 250, note: "Rate ratio vs field under each stress variant · blue = the signal survives" }),
        { cols: [
            { h: "Variant", k: "test" }, { h: "Argentina", k: "argentina" },
            { h: "Rate", k: "rate" }, { h: "Field", k: "field_rate" },
            { h: "Ratio", k: "ratio", f: v => `<b>${v}×</b>` },
            { h: "p", k: "p" }, { h: "Note", k: "note", f: v => `<span style="color:var(--muted)">${esc(v)}</span>` },
          ], rows: D.robustness_tests });
    card("#chart-champions", "Every champion's title run vs its Elo expectation, 1990–2026",
      "Positive = won more than the ratings predicted. Argentina 2022 is the only negative bar.",
      [{ color: css("--arg"), label: "Argentina" }, { color: css("--de"), label: "Other champions" }],
      drawChampions, { cols: [{ h: "Year", k: "year" }, { h: "Champion", k: "champion" }, { h: "Elo residual", k: "resid" }], rows: D.forensics_champions });
    card("#table-ref-residuals", "Argentina's Elo overperformance per referee (≥2 matches)",
      "Positive = Argentina beat expectations in his matches; p from 10,000 assignment permutations. None survives multiplicity correction.",
      null, (plot) => hbarChart(plot,
        (D.forensics_ref_residuals || []).map(r => ({ label: r.referee, value: r.arg_resid_sum, hl: r.referee === "Szymon Marciniak",
          tip: `<b>${esc(r.referee)}</b> (${r.n_argentina_matches} ARG matches, ${esc(r.years)})<br>Elo residual ${r.arg_resid_sum > 0 ? "+" : ""}${r2(r.arg_resid_sum)} · p(favoritism)=${r2(r.p_perm_onesided_pos, 3)}` })),
        { diverge: true, fmt: v => (v > 0 ? "+" : "") + r2(v), note: "Win rate vs Elo expectation per referee · Marciniak in blue" }),
      (() => { const s = refResidualsTable(); return { cols: s.cols, rows: s.rows }; })());
  }
  $("#foot").innerHTML = `Compiled 2026-07-16 · 2026 final (Argentina v Spain, Jul 19) and third-place match pending · ` +
    `Analysis pipeline, per-incident penalty ledger, VAR compilation and all sources: <b>argentina-worldcup/</b> data &amp; analysis folders · ` +
    `Allegations reported by cited outlets remain allegations; no charges have been filed. · ` +
    `<a href="https://github.com/VeritasSimplexAI/albiceleste-anomaly" target="_blank" rel="noopener" style="color:var(--arg);text-decoration:none;border-bottom:1px solid color-mix(in srgb, var(--arg) 40%, transparent)">Fully open source: every dataset, script and method on GitHub</a>`;
}

/* ================= Exhibit H: the draw ================= */
function drawGroupPctl(plot) {
  const d = D.draw_group_pctl || [];
  const W = Math.max(700, plot.clientWidth || 920), H = 250, L = 46, R = 24, T = 16, B = 44;
  const iw = W - L - R, ih = H - T - B;
  const x = (yr) => L + ((yr - 1930) / (2026 - 1930)) * iw;
  const y = (v) => T + ih - (v / 100) * ih;
  const svg = E("svg", { width: W, height: H, viewBox: `0 0 ${W} ${H}` }, null);
  for (const g of [0, 25, 50, 75, 100]) {
    E("line", { x1: L, x2: W - R, y1: y(g), y2: y(g), stroke: g === 50 ? css("--axis") : css("--grid") }, svg);
    text(svg, L - 6, y(g) + 3, String(g), { anchor: "end", size: 10.5, fill: css("--muted") });
  }
  text(svg, W - R, y(50) - 5, "median difficulty", { anchor: "end", size: 10, fill: css("--muted") });
  E("path", { d: d.map((r, i) => `${i ? "L" : "M"} ${x(r.year)} ${y(r.pctl_vs_all_teams)}`).join(" "),
    fill: "none", stroke: css("--arg"), "stroke-width": 2, "stroke-linejoin": "round" }, svg);
  for (const r of d) {
    const dot = E("circle", { cx: x(r.year), cy: y(r.pctl_vs_all_teams), r: 5, fill: css("--arg"),
      stroke: css("--surface"), "stroke-width": 2 }, svg);
    hover(dot, `<b>${r.year}</b> — group ${esc(r.arg_group)}<br>harder than ${r.pctl_vs_all_teams}% of teams' groups<br>opponents' mean Elo ${r.arg_opp_elo_mean} (tournament mean ${r.tournament_mean})<br>rank among top seeds: ${esc(r.rank_among_seeds)} (1 = hardest)`);
    if ([1994, 2014, 2022].includes(r.year))
      text(svg, x(r.year), y(r.pctl_vs_all_teams) - 12, `${r.pctl_vs_all_teams}%`, { anchor: "middle", size: 10.5, weight: 650, fill: css("--ink") });
  }
  for (const yr of [1930, 1958, 1978, 1998, 2018])
    text(svg, x(yr), H - 26, String(yr), { anchor: "middle", size: 10.5, fill: css("--muted") });
  text(svg, L, H - 6, "Argentina's group difficulty percentile, 1930–2026 (opponents' mean Elo vs every team's group that year) · low = easy group · 1934/38 were pure knockouts", { size: 10.5, fill: css("--muted") });
  plot.appendChild(svg);
}
function drawKoPaths(plot) {
  const d = (D.draw_ko_paths || []).filter(r => r.year === 2026).sort((a, b) => a.path_elo - b.path_elo);
  const W = Math.max(380, plot.clientWidth || 440), rowH = 34, L = 110, R = 60, T = 8;
  const H = T + d.length * rowH + 46;
  const min = 1750, max = 2000;
  const x = (v) => L + ((v - min) / (max - min)) * (W - L - R);
  const svg = E("svg", { width: W, height: H, viewBox: `0 0 ${W} ${H}` }, null);
  d.forEach((r, i) => {
    const yc = T + i * rowH + rowH / 2;
    const isArg = r.team === "Argentina";
    E("rect", { x: L, y: yc - 9, width: Math.max(x(r.path_elo) - L, 1), height: 18, rx: 4,
      fill: isArg ? css("--arg") : css("--de"), opacity: isArg ? 1 : 0.55 }, svg);
    hover(svg.lastChild, `<b>${esc(r.team)} 2026</b><br>path: ${esc(r.route)}<br>mean opponent Elo ${r.path_elo} · mean FIFA rank ${r.path_fifa} · top seeds faced: ${r.pot1_opps}`);
    text(svg, L - 8, yc + 4, r.team, { anchor: "end", size: 12, weight: isArg ? 700 : 400, fill: isArg ? css("--ink") : css("--ink-2") });
    text(svg, x(r.path_elo) + 6, yc + 4, String(Math.round(r.path_elo)), { size: 11, weight: isArg ? 700 : 400, fill: isArg ? css("--ink") : css("--muted") });
  });
  text(svg, 8, H - 24, "Mean KO-opponent Elo · axis starts at 1750", { size: 10.5, fill: css("--muted") });
  text(svg, 8, H - 8, "Hover a bar for the full route", { size: 10.5, fill: css("--muted") });
  plot.appendChild(svg);
}
function drawSummaryTable() {
  return {
    cols: [
      { h: "Year", k: "year" }, { h: "Group", k: "group" },
      { h: "Opp. Elo (mean)", k: "opp_elo_mean" }, { h: "Elo rank*", k: "elo_rank" },
      { h: "Opp. FIFA rank (mean)", k: "opp_fifa_mean", f: v => v ?? "n/a" },
      { h: "FIFA rank*", k: "fifa_rank_rank" },
    ],
    rows: D.draw_group_summary || [],
  };
}

/* ================= Exhibit G: forensics ================= */
const FORENSICS_ROWS = [
    { test: "Within-referee fingerprint", q: "Does any referee's card/penalty behavior change when Argentina plays, vs his own baseline?", r: "No. Pooled favoritism contrast IRR 1.11 (p=0.44); zero referees survive false-discovery correction; Marciniak at his own baseline (0.95×).", v: "NULL" },
    { test: "Assignment Monte Carlo", q: "How improbable is the Marciniak×4 pairing under random assignment? (20,000 sims, workload- and neutrality-preserving)", r: "A 4-match pair somewhere: expected (p≈0.43). Argentina-specifically, spanning 3 tournaments incl. a final: p≈0.06–0.15 — unusual at the 1-in-10 level, post hoc.", v: "MILD" },
    { test: "Elo residuals per referee", q: "Did Argentina beat its Elo expectation under specific referees? (10,000 stratified permutations)", r: "No. Under Marciniak Argentina UNDER-performed (−0.27, p=0.90 in the favoritism direction). No referee survives multiplicity correction.", v: "NULL" },
    { test: "Hierarchical pair model", q: "Across all 1,025 referee×team pairs 1990–2022, is any Argentina pair a card outlier after shrinkage?", r: "No. Pair variance ≈ 0; Lahoz·Argentina (the wild 2022 QF) shrinks to 1.008×; Marciniak·Argentina ranks 1,001/1,025 — neutral.", v: "NULL" },
];
const fChip = v => `<span style="font-family:var(--sans);font-size:11px;font-weight:700;letter-spacing:.08em;padding:3px 8px;border-radius:4px;background:${v === "MILD" ? "color-mix(in srgb, var(--neg) 14%, transparent)" : "color-mix(in srgb, var(--de) 18%, transparent)"};color:${v === "MILD" ? "var(--neg)" : "var(--ink-2)"}">${v === "MILD" ? "1-IN-10 UNUSUAL" : "NO EFFECT FOUND"}</span>`;
function forensicsVerdicts(plot) {
  plot.innerHTML = `<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:14px;margin-top:14px">` +
    FORENSICS_ROWS.map(r => `<div style="border:1px solid var(--grid);border-radius:10px;padding:14px 16px">
      <div style="font-family:var(--sans);font-weight:700;font-size:14px;margin-bottom:6px">${r.test}</div>
      ${fChip(r.v)}<div style="font-family:var(--sans);font-size:12.5px;color:var(--muted);margin-top:8px">${r.q}</div></div>`).join("") + `</div>`;
}
function drawChampions(plot) {
  const data = D.forensics_champions || [];
  const W = Math.max(380, plot.clientWidth || 440), H = 300, R = 60, T = 10;
  const L0 = Math.min(Math.max(150, Math.max(...data.map(r => (`${r.year} ${r.champion}`).length)) * 6.6 + 12), W * 0.5);
  const negPad = data.some(r => r.resid < 0)
    ? Math.max(...data.filter(r => r.resid < 0).map(r => String(r.resid).length)) * 6.4 + 14 : 0;
  const L = L0 + negPad;
  const rowH = (H - T - 30) / data.length;
  const min = -1, max = 3;
  const x = (v) => L + ((v - min) / (max - min)) * (W - L - R);
  const svg = E("svg", { width: W, height: H, viewBox: `0 0 ${W} ${H}` }, null);
  E("line", { x1: x(0), x2: x(0), y1: T, y2: H - 26, stroke: css("--axis"), "stroke-width": 1.5 }, svg);
  data.forEach((r, i) => {
    const yc = T + i * rowH + rowH / 2;
    const isArg = String(r.champion).startsWith("Argentina");
    const x0 = Math.min(x(0), x(r.resid)), w = Math.abs(x(r.resid) - x(0));
    const bar = E("rect", { x: x0, y: yc - 8, width: Math.max(w, 1), height: 16, rx: 3,
      fill: isArg ? css("--arg") : css("--de"), opacity: isArg ? 1 : 0.55 }, svg);
    hover(bar, `<b>${r.year} ${esc(r.champion)}</b><br>title-run Elo overperformance: ${r.resid > 0 ? "+" : ""}${r.resid}<br>(shootouts scored as draws — Elo convention)`);
    text(svg, 8, yc + 4, `${r.year} ${r.champion}`, { size: 11.5, weight: isArg ? 700 : 400, fill: isArg ? css("--ink") : css("--ink-2") });
    text(svg, r.resid >= 0 ? x(r.resid) + 6 : x(r.resid) - 6, yc + 4, (r.resid > 0 ? "+" : "") + r.resid,
      { size: 11, anchor: r.resid >= 0 ? "start" : "end", weight: isArg ? 700 : 400, fill: isArg ? css("--ink") : css("--muted") });
  });
  text(svg, 8, H - 6, clip("Title runs vs Elo expectation · 0 = exactly as predicted", Math.floor((W - 16) / 5.8)), { size: 10.5, fill: css("--muted") });
  plot.appendChild(svg);
}
function refResidualsTable() {
  return {
    cols: [
      { h: "Referee", k: "referee", f: (v, r) => r.referee === "Szymon Marciniak" ? `<b>${v}</b>` : v },
      { h: "ARG matches", k: "n_argentina_matches" },
      { h: "Elo residual", k: "arg_resid_sum", f: v => `<span style="color:${v > 0 ? "var(--pos)" : "var(--neg)"}">${v > 0 ? "+" : ""}${r2(v)}</span>` },
      { h: "p (favoritism)", k: "p_perm_onesided_pos", f: v => r2(v, 3) },
      { h: "Tournaments", k: "years" },
    ],
    rows: (D.forensics_ref_residuals || []),
  };
}

/* ================= Exhibit B: interactive VAR ledger ================= */
function varLedgerCard(sel) {
  const host = $(sel); if (!host) return;
  const state = { years: new Set([2018, 2022, 2026]), teams: null, view: "ledger" };
  const mpByYear = {};
  for (const r of D.squad_discipline) {
    if (![2018, 2022, 2026].includes(r.tournament_year)) continue;
    (mpByYear[r.tournament_year] = mpByYear[r.tournament_year] || {})[r.team] = r.matches_played;
  }
  const allTeams = [...new Set(D.squad_discipline.filter(r => [2018, 2022, 2026].includes(r.tournament_year)).map(r => r.team))].sort();
  host.innerHTML = `<div class="card-head"><div>
      <div class="card-title">The VAR ledger — every team, every overturn, 2018–2026</div>
      <div class="card-sub">Blue right = overturns FOR the team · red left = AGAINST · pick tournaments and teams · 86 real overturns — the 26 once-ambiguous 2026 feed entries were all investigated and every one was a review that CONFIRMED the call (excluded as non-overturns)</div></div>
      <div style="display:flex;gap:12px;flex-wrap:wrap">
        <div class="toggle" id="vlYears">
          <button data-y="2018" aria-pressed="true">2018</button><button data-y="2022" aria-pressed="true">2022</button><button data-y="2026" aria-pressed="true">2026</button>
        </div>
        <div class="toggle" id="vlView">
          <button data-v="ledger" aria-pressed="true">For / Against</button><button data-v="net" aria-pressed="false">Net</button>
        </div>
      </div></div>
    <div class="filters"><label>Teams</label>
      <select id="vlTeams" multiple size="5" style="min-width:180px"><option value="__all" selected>(all teams)</option>${allTeams.map(t => `<option>${esc(t)}</option>`).join("")}</select>
      <span class="rescount" id="vlCount"></span></div>
    <div style="max-height:560px;overflow:auto;margin-top:10px"><div id="vlPlot"></div></div>`;
  const draw = () => {
    const inc = D.var_incidents_all.filter(r => state.years.has(r.tournament_year));
    const rowsMap = {};
    for (const yr of state.years) for (const t in (mpByYear[yr] || {}))
      (rowsMap[t] = rowsMap[t] || { team: t, m: 0, fav: 0, ag: 0 }).m += mpByYear[yr][t];
    for (const r of inc) {
      if (rowsMap[r.beneficiary_team]) rowsMap[r.beneficiary_team].fav++;
      if (rowsMap[r.against_team]) rowsMap[r.against_team].ag++;
    }
    let rows = Object.values(rowsMap);
    if (state.teams) rows = rows.filter(r => state.teams.has(r.team));
    rows.sort((a, b) => (b.fav - b.ag) - (a.fav - a.ag) || b.fav - a.fav);
    $("#vlCount").textContent = `${rows.length} teams · ${inc.length} overturns in view`;
    const plot = $("#vlPlot"); plot.innerHTML = "";
    const W = Math.max(700, plot.clientWidth || 900), rowH = 26, T = 22;
    const H = T + rows.length * rowH + 14;
    const maxC = Math.max(3, ...rows.map(r => Math.max(r.fav, r.ag, Math.abs(r.fav - r.ag))));
    const C = W * 0.5, span = W * 0.38;
    const svg = E("svg", { width: W, height: H, viewBox: `0 0 ${W} ${H}` }, null);
    E("line", { x1: C, x2: C, y1: T - 6, y2: H - 8, stroke: css("--axis"), "stroke-width": 1.5 }, svg);
    text(svg, C + 8, T - 8, state.view === "ledger" ? "for →" : "net →", { size: 10, weight: 650, fill: css("--pos") });
    if (state.view === "ledger") text(svg, C - 8, T - 8, "← against", { size: 10, weight: 650, fill: css("--neg"), anchor: "end" });
    rows.forEach((r, i) => {
      const yc = T + i * rowH + rowH / 2;
      const isArg = r.team === "Argentina";
      const tip = `<b>${esc(r.team)}</b><br>+${r.fav} for, −${r.ag} against in ${r.m} matches<br>net ${r.fav - r.ag >= 0 ? "+" : ""}${r.fav - r.ag} (${r2((r.fav - r.ag) / r.m)}/match)`;
      if (state.view === "ledger") {
        const bf = E("rect", { x: C + 1, y: yc - 8, width: Math.max((r.fav / maxC) * span, r.fav ? 2 : 0.5), height: 16, rx: 3, fill: css("--arg"), opacity: isArg ? 1 : 0.65 }, svg);
        const ba = E("rect", { x: C - 1 - Math.max((r.ag / maxC) * span, r.ag ? 2 : 0.5), y: yc - 8, width: Math.max((r.ag / maxC) * span, r.ag ? 2 : 0.5), height: 16, rx: 3, fill: css("--neg"), opacity: isArg ? 0.95 : 0.55 }, svg);
        hover(bf, tip); hover(ba, tip);
        text(svg, C + 5 + (r.fav / maxC) * span, yc + 4, `+${r.fav}`, { size: 10, fill: isArg ? css("--ink") : css("--muted"), weight: isArg ? 700 : 400 });
        if (r.ag) text(svg, C - 5 - (r.ag / maxC) * span, yc + 4, `−${r.ag}`, { anchor: "end", size: 10, fill: css("--muted") });
      } else {
        const net = r.fav - r.ag;
        const w = (Math.abs(net) / maxC) * span;
        const bar = E("rect", { x: net >= 0 ? C + 1 : C - 1 - w, y: yc - 8, width: Math.max(w, 1), height: 16, rx: 3,
          fill: net >= 0 ? css("--arg") : css("--neg"), opacity: isArg ? 1 : 0.6 }, svg);
        hover(bar, tip);
        text(svg, net >= 0 ? C + 5 + w : C - 5 - w, yc + 4, `${net >= 0 ? "+" : ""}${net}`, { anchor: net >= 0 ? "start" : "end", size: 10, fill: isArg ? css("--ink") : css("--muted"), weight: isArg ? 700 : 400 });
      }
      text(svg, C - span - 12, yc + 4, clip(r.team, Math.max(10, Math.floor((C - span - 18) / 6.2))), { anchor: "end", size: 11, weight: isArg ? 700 : 400, fill: isArg ? css("--ink") : css("--ink-2") });
    });
    plot.appendChild(svg);
  };
  host.querySelectorAll("#vlYears button").forEach(b => b.onclick = () => {
    const y = +b.dataset.y;
    if (state.years.has(y) && state.years.size > 1) { state.years.delete(y); b.setAttribute("aria-pressed", "false"); }
    else { state.years.add(y); b.setAttribute("aria-pressed", "true"); }
    draw();
  });
  host.querySelectorAll("#vlView button").forEach(b => b.onclick = () => {
    state.view = b.dataset.v;
    host.querySelectorAll("#vlView button").forEach(x => x.setAttribute("aria-pressed", String(x === b)));
    draw();
  });
  $("#vlTeams").addEventListener("change", (e) => {
    const sel = [...e.target.selectedOptions].map(o => o.value);
    state.teams = sel.includes("__all") || !sel.length ? null : new Set(sel);
    draw();
  });
  draw();
}

/* ================= Exhibit C: all-team cards history comparer ================= */
function cardsHistoryCard(sel) {
  const host = $(sel); if (!host) return;
  const series = [];
  for (const r of D.team_tournament.filter(r => r.year >= 1970))
    series.push({ year: r.year, team: r.team_name, m: r.matches, y: r.yellows_received, r: r.dismissals_received });
  for (const r of D.squad_discipline.filter(r => r.tournament_year === 2026))
    series.push({ year: 2026, team: r.team, m: r.matches_played, y: r.yellow_cards, r: r.red_cards });
  const teams = [...new Set(series.map(s => s.team))].sort();
  const years = [...new Set(series.map(s => s.year))].sort();
  const state = { sel: ["Argentina", "Brazil"], from: 1970, to: 2026, metric: "y" };
  host.innerHTML = `<div class="card-head"><div>
      <div class="card-title">Card history, team vs team — every side, 1970–2026</div>
      <div class="card-sub">Yellows (or reds) received per match · pick up to 8 teams and a tournament range · gray line = tournament average</div></div>
      <div class="toggle" id="chMetric"><button data-m="y" aria-pressed="true">Yellow cards</button><button data-m="r" aria-pressed="false">Red cards</button></div></div>
    <div class="filters">
      <label>Teams</label><select id="chTeams" multiple size="5" style="min-width:170px">${teams.map(t => `<option${state.sel.includes(t) ? " selected" : ""}>${esc(t)}</option>`).join("")}</select>
      <label>From</label><select id="chFrom">${years.map(y => `<option${y === 1970 ? " selected" : ""}>${y}</option>`).join("")}</select>
      <label>To</label><select id="chTo">${years.map(y => `<option${y === 2026 ? " selected" : ""}>${y}</option>`).join("")}</select>
      <span class="rescount" id="chNote"></span></div>
    <div class="plot" id="chPlot"></div>`;
  const draw = () => {
    const plot = $("#chPlot"); plot.innerHTML = "";
    const picked = state.sel.slice(0, 8);
    $("#chNote").textContent = state.sel.length > 8 ? "showing first 8 selected teams" : "";
    const yrs = years.filter(y => y >= state.from && y <= state.to);
    const W = Math.max(700, plot.clientWidth || 900), H = 320, L = 44, R = 130, T = 16, B = 40;
    const iw = W - L - R, ih = H - T - B;
    const x = (yr) => L + ((yr - yrs[0]) / Math.max(yrs[yrs.length - 1] - yrs[0], 1)) * iw;
    const maxY = state.metric === "y" ? 4 : 0.6;
    const yy = (v) => T + ih - (Math.min(v, maxY) / maxY) * ih;
    const svg = E("svg", { width: W, height: H, viewBox: `0 0 ${W} ${H}` }, null);
    const steps = state.metric === "y" ? [0, 1, 2, 3, 4] : [0, 0.2, 0.4, 0.6];
    for (const g of steps) {
      E("line", { x1: L, x2: W - R, y1: yy(g), y2: yy(g), stroke: g === 0 ? css("--axis") : css("--grid") }, svg);
      text(svg, L - 6, yy(g) + 3, String(g), { anchor: "end", size: 10.5, fill: css("--muted") });
    }
    // field average line
    const fieldPts = yrs.map(yr => {
      const g = series.filter(s => s.year === yr);
      return { yr, v: g.reduce((z, s) => z + s[state.metric], 0) / g.reduce((z, s) => z + s.m, 0) };
    });
    E("path", { d: fieldPts.map((p, i) => `${i ? "L" : "M"} ${x(p.yr)} ${yy(p.v)}`).join(" "), fill: "none", stroke: css("--de"), "stroke-width": 2, opacity: 0.7 }, svg);
    const endLabels = [{ y: yy(fieldPts[fieldPts.length - 1].v), textStr: "avg", col: css("--muted"), w: 400 }];
    picked.forEach((t, ti) => {
      const col = css("--s" + (ti + 1));
      const pts = yrs.map(yr => { const s = series.find(q => q.year === yr && q.team === t); return s ? { yr, v: s[state.metric] / s.m, s } : null; }).filter(Boolean);
      if (!pts.length) return;
      E("path", { d: pts.map((p, i) => `${i ? "L" : "M"} ${x(p.yr)} ${yy(p.v)}`).join(" "), fill: "none", stroke: col, "stroke-width": 2, "stroke-linejoin": "round" }, svg);
      for (const p of pts) {
        const dot = E("circle", { cx: x(p.yr), cy: yy(p.v), r: 4, fill: col, stroke: css("--surface"), "stroke-width": 2 }, svg);
        hover(dot, `<b>${esc(t)} ${p.yr}</b><br>${p.s[state.metric]} ${state.metric === "y" ? "yellows" : "reds"} in ${p.s.m} matches (${r2(p.v)}/match)`);
      }
      endLabels.push({ y: yy(pts[pts.length - 1].v) + 4, textStr: clip(t, 18), col: (col === css("--s4") || col === css("--s3")) ? css("--ink-2") : col, w: 650 });
    });
    // collision-resolve end labels: sort by y, enforce 13px separation
    endLabels.sort((a, b) => a.y - b.y);
    for (let i = 1; i < endLabels.length; i++)
      if (endLabels[i].y - endLabels[i - 1].y < 13) endLabels[i].y = endLabels[i - 1].y + 13;
    for (const l of endLabels)
      text(svg, W - R + 6, Math.min(l.y, H - B), l.textStr, { size: 10.5, weight: l.w, fill: l.col });
    for (const yr of yrs.filter((y, i) => i % 2 === 0 || yrs.length < 10))
      text(svg, x(yr), H - 22, String(yr), { anchor: "middle", size: 10, fill: css("--muted") });
    text(svg, L, H - 6, "Cards received per match · 2026 through the semifinals", { size: 10.5, fill: css("--muted") });
    plot.appendChild(svg);
  };
  $("#chTeams").addEventListener("change", e => { state.sel = [...e.target.selectedOptions].map(o => o.value); draw(); });
  $("#chFrom").addEventListener("change", e => { state.from = +e.target.value; draw(); });
  $("#chTo").addEventListener("change", e => { state.to = +e.target.value; draw(); });
  host.querySelectorAll("#chMetric button").forEach(b => b.onclick = () => {
    state.metric = b.dataset.m;
    host.querySelectorAll("#chMetric button").forEach(x => x.setAttribute("aria-pressed", String(x === b)));
    draw();
  });
  draw();
}

/* ---------- interactive comparison table: scope toggle, sortable, scrollable ---------- */
function officialComparisonCard(sel) {
  const host = $(sel); host.innerHTML = "";
  const state = { scope: "referee", sortKey: "matches", sortDir: -1 };
  const COLS = [
    { h: "Official", k: "official", str: true },
    { h: "Roles", k: "roles", str: true, f: (v) => esc(v).replace(/_/g, " ").replace(/\//g, " · ") },
    { h: "Tournaments", k: "years", str: true },
    { h: "ARG matches", k: "matches" },
    { h: "W–D–L", k: "wins", f: (v, r) => `${r.wins}–${r.draws}–${r.losses}` },
    { h: "ARG win %", k: "win_pct", f: (v, r) => r.losses === 0 && r.matches >= 3 ? `<b>${v}%</b>` : `${v}%` },
    { h: "Expected %", k: "expected_win_pct", f: v => `${v}%`, tip: "opponent-adjusted" },
    { h: "Δ vs expected", k: "delta_vs_expected", f: v => `<span style="color:${v > 0 ? "var(--pos)" : v < 0 ? "var(--neg)" : "var(--muted)"}">${v > 0 ? "+" : ""}${v}</span>` },
    { h: "Other teams' win %", k: "others_win_pct", f: (v, r) => v < 0 ? "n/a" : `${v}% (${r.others_matches}m)` },
  ];
  host.innerHTML = `
    <div class="card-head">
      <div><div class="card-title">Argentina with each official — vs opponent-adjusted expectation and vs other teams</div>
      <div class="card-sub">Baseline 63% wins over all 95 matches 1930–2026 (shootouts as wins). "Expected %" = Argentina's leave-one-out record vs the opponents this official's matches involved.
      "Other teams' win %" = every non-Argentina team-result in this official's matches. Click a column to sort; scroll for the full list.</div></div>
      <div style="display:flex;gap:12px;flex-wrap:wrap">
      <div class="toggle" id="scopeToggle">
        <button data-s="referee" aria-pressed="true">Main referee only</button>
        <button data-s="crew" aria-pressed="false">All crew roles</button>
      </div>
      <div class="toggle" id="cmpView">
        <button data-v="table" aria-pressed="true">Table</button>
        <button data-v="chart" aria-pressed="false">Chart</button>
      </div>
      </div>
    </div>
    <div class="plot" id="cmpChart" style="display:none"></div>
    <div class="scrolltable"><div id="cmpTable"></div></div>`;
  let view = "table";
  const drawChartView = () => {
    const c = $("#cmpChart"); c.innerHTML = "";
    const rows = D.argentina_official_comparison.filter(r => r.scope === state.scope && r.matches >= 2)
      .sort((a, b) => b.delta_vs_expected - a.delta_vs_expected);
    hbarChart(c, rows.map(r => ({ label: r.official, value: r.delta_vs_expected, hl: r.official === "Szymon Marciniak",
      tip: `<b>${esc(r.official)}</b> (${r.matches} ARG matches, ${esc(r.years)})<br>actual ${r.win_pct}% vs expected ${r.expected_win_pct}%` })),
      { diverge: true, fmt: v => (v > 0 ? "+" : "") + v + "pp", labelW: 180,
        note: "Argentina's win% minus opponent-adjusted expectation, officials with ≥2 matches · Marciniak highlighted" });
  };
  const draw = () => {
    let rows = D.argentina_official_comparison.filter(r => r.scope === state.scope);
    const c = COLS.find(c => c.k === state.sortKey);
    rows = rows.slice().sort((a, b) => {
      const av = a[state.sortKey], bv = b[state.sortKey];
      const cmp = c && c.str ? String(av).localeCompare(String(bv)) : (av ?? -1e9) - (bv ?? -1e9);
      return state.sortDir * cmp || b.matches - a.matches;
    });
    let h = `<table class="dv"><thead><tr>` + COLS.map(c =>
      `<th data-k="${c.k}">${esc(c.h)}${c.k === state.sortKey ? ` <span class="arr">${state.sortDir < 0 ? "▼" : "▲"}</span>` : ""}</th>`).join("") + `</tr></thead><tbody>`;
    for (const r of rows) {
      h += "<tr>" + COLS.map(c => `<td>${c.f ? c.f(c.str ? esc(r[c.k]) : r[c.k], r) : esc(r[c.k])}</td>`).join("") + "</tr>";
    }
    $("#cmpTable").innerHTML = h + "</tbody></table>";
    $("#cmpTable").querySelectorAll("th").forEach(th => th.onclick = () => {
      const k = th.dataset.k;
      if (state.sortKey === k) state.sortDir *= -1;
      else { state.sortKey = k; state.sortDir = COLS.find(c => c.k === k).str ? 1 : -1; }
      draw();
    });
  };
  host.querySelectorAll("#scopeToggle button").forEach(b => b.onclick = () => {
    state.scope = b.dataset.s;
    host.querySelectorAll("#scopeToggle button").forEach(x => x.setAttribute("aria-pressed", String(x === b)));
    view === "chart" ? drawChartView() : draw();
  });
  host.querySelectorAll("#cmpView button").forEach(b => b.onclick = () => {
    view = b.dataset.v;
    host.querySelectorAll("#cmpView button").forEach(x => x.setAttribute("aria-pressed", String(x === b)));
    $("#cmpChart").style.display = view === "chart" ? "" : "none";
    host.querySelector(".scrolltable").style.display = view === "chart" ? "none" : "";
    view === "chart" ? drawChartView() : draw();
  });
  draw();
}
function penEraTableWrap() { const s = penEraTable(); return { cols: s.cols, rows: s.rows }; }
function cardTableRows() {
  const tt = D.team_tournament.filter(r => r.year >= 1970 && r.team_name === "Argentina");
  return tt.map(r => {
    const g = D.team_tournament.filter(q => q.year === r.year);
    return { year: r.year, arg: r.yellows_drawn / r.matches, field: g.reduce((z, q) => z + q.yellows_received, 0) / g.reduce((z, q) => z + q.matches, 0) };
  }).concat([{ year: 2026, arg: D.argentina_2026.find(r => r.metric === "yellows_drawn").arg_rate, field: D.argentina_2026.find(r => r.metric === "yellows_drawn").field_rate }]);
}
render();
})();
