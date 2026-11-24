"""
build_interactive_dashboard.py - create a self-contained interactive HTML dashboard.

Usage (from the project root, after prepare_powerbi_data.py):
    python scripts/build_interactive_dashboard.py

Output: dashboard/interactive_dashboard.html
  * opens in any web browser (double-click), works offline - no internet or libraries needed
  * 4 pages (Executive, Product, Customer, Regional) mirroring the Power BI design
  * slicers: date range, category, region, RFM segment, business segment
  * hover tooltips on every chart; click a bar / cell to filter the whole dashboard

All aggregation happens in the browser from the 8,399 order lines embedded in the file,
so every number is computed from the same data as the notebooks, SQL and Power BI model.
"""
import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "dashboard" / "powerbi_data"
OUT = ROOT / "dashboard" / "interactive_dashboard.html"

fact = pd.read_csv(DATA / "fact_sales.csv")
cust = pd.read_csv(DATA / "dim_customer.csv")
prod = pd.read_csv(DATA / "dim_product.csv")
loc = pd.read_csv(DATA / "dim_location.csv")
df = fact.merge(cust, on="customer_key").merge(prod, on="product_key").merge(loc, on="location_key")


def codes(series, order=None):
    """Encode a text column as integer codes + a lookup list (keeps the file small)."""
    cats = order or sorted(series.unique())
    lookup = {v: i for i, v in enumerate(cats)}
    return [lookup[v] for v in series], cats


RFM_ORDER = ["High-Value (Champions)", "Loyal Customers", "Potential Loyalists", "New Customers",
             "Need Attention", "At-Risk Customers", "Hibernating / Lost"]
cols, dicts = {}, {}
cols["ym"], dicts["ym"] = codes(df["order_date"].str[:7])
cols["cat"], dicts["cat"] = codes(df["category"], ["Technology", "Furniture", "Office Supplies"])
cols["sub"], dicts["sub"] = codes(df["sub_category"])
cols["prod"], dicts["prod"] = codes(df["product_name"])
cols["cust"], dicts["cust"] = codes(df["customer_name"])
cols["prov"], dicts["prov"] = codes(df["province"])
cols["reg"], dicts["reg"] = codes(df["region"])
cols["bseg"], dicts["bseg"] = codes(df["business_segment"], ["Corporate", "Home Office", "Consumer", "Small Business"])
cols["rfm"], dicts["rfm"] = codes(df["rfm_segment"], RFM_ORDER)
cols["order"] = df["order_id"].astype(int).tolist()
cols["sales"] = df["sales"].round(2).tolist()
cols["profit"] = df["profit"].round(2).tolist()
cols["qty"] = df["quantity"].astype(int).tolist()
# product -> category / sub-category lookups (for labels and colours)
pmap = df.drop_duplicates("product_name").set_index("product_name")
dicts["prodCat"] = [dicts["cat"].index(pmap.loc[p, "category"]) for p in dicts["prod"]]
dicts["subCat"] = [dicts["cat"].index(df.loc[df["sub_category"] == s, "category"].iloc[0]) for s in dicts["sub"]]
dicts["provReg"] = [dicts["reg"].index(df.loc[df["province"] == p, "region"].iloc[0]) for p in dicts["prov"]]

payload = json.dumps({"cols": cols, "dicts": dicts}, separators=(",", ":"), ensure_ascii=False)

HTML = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Retail Shop Dashboard</title>
<style>
:root{
  --page:#f4f3f0; --panel:#ffffff; --border:#e4e3df; --grid:#ecebe7;
  --text:#0b0b0b; --text2:#52514e; --muted:#8a8984;
  --blue:#2a78d6; --orange:#eb6834; --aqua:#1baf7a; --yellow:#eda100;
  --violet:#6250d6; --red:#e34948; --gray:#9a9994; --blue-l:#9ec5f4;
  --accent-bg:#e8f1fc;
}
@media (prefers-color-scheme: dark){
  :root:not([data-theme="light"]){
    --page:#121211; --panel:#1a1a19; --border:#2f2f2d; --grid:#2a2a28;
    --text:#f0efec; --text2:#c3c2b7; --muted:#8f8e86;
    --blue:#3987e5; --orange:#d95926; --aqua:#199e70; --yellow:#c98500;
    --violet:#9085e9; --red:#e66767; --gray:#7d7c76; --blue-l:#256abf; --accent-bg:#1d2c40;
  }
}
:root[data-theme="dark"]{
  --page:#121211; --panel:#1a1a19; --border:#2f2f2d; --grid:#2a2a28;
  --text:#f0efec; --text2:#c3c2b7; --muted:#8f8e86;
  --blue:#3987e5; --orange:#d95926; --aqua:#199e70; --yellow:#c98500;
  --violet:#9085e9; --red:#e66767; --gray:#7d7c76; --blue-l:#256abf; --accent-bg:#1d2c40;
}
*{box-sizing:border-box}
body{margin:0;background:var(--page);color:var(--text);font:14px/1.4 "Segoe UI",system-ui,-apple-system,Roboto,sans-serif}
header{padding:18px 24px 8px;display:flex;flex-wrap:wrap;align-items:flex-end;gap:8px 24px}
h1{margin:0;font-size:22px}
.sub{color:var(--text2);font-size:13px}
nav{display:flex;gap:4px;padding:0 24px;border-bottom:1px solid var(--border);overflow-x:auto}
nav button{background:none;border:0;border-bottom:3px solid transparent;padding:10px 14px;font:inherit;color:var(--text2);cursor:pointer;white-space:nowrap}
nav button.active{color:var(--text);border-bottom-color:var(--blue);font-weight:600}
.slicers{display:flex;flex-wrap:wrap;gap:10px;padding:14px 24px;align-items:flex-end}
.slicer{display:flex;flex-direction:column;gap:3px;font-size:12px;color:var(--text2)}
.slicer select{font:inherit;font-size:13px;padding:6px 8px;border:1px solid var(--border);border-radius:6px;background:var(--panel);color:var(--text);min-width:140px}
#reset{font:inherit;font-size:13px;padding:6px 12px;border:1px solid var(--border);border-radius:6px;background:var(--panel);color:var(--text);cursor:pointer}
#reset:hover{border-color:var(--blue)}
.chips{padding:0 24px;display:flex;gap:6px;flex-wrap:wrap;min-height:4px}
.chip{background:var(--accent-bg);color:var(--text);border-radius:12px;padding:2px 10px;font-size:12px}
main{padding:10px 24px 28px}
.page{display:none}.page.active{display:block}
.grid{display:grid;gap:14px;grid-template-columns:repeat(12,1fr)}
.card,.panel{background:var(--panel);border:1px solid var(--border);border-radius:10px}
.card{padding:14px 16px;grid-column:span 3}
.card .lab{color:var(--text2);font-size:13px}
.card .val{font-size:28px;font-weight:700;margin-top:4px;font-variant-numeric:tabular-nums}
.card .note{color:var(--text2);font-size:12px;min-height:16px}
.panel{padding:12px 14px 8px;min-width:0}
.panel h3{margin:0 0 2px;font-size:14px}
.panel .hint{color:var(--muted);font-size:11.5px;margin-bottom:4px}
.s4{grid-column:span 4}.s5{grid-column:span 5}.s6{grid-column:span 6}.s7{grid-column:span 7}.s8{grid-column:span 8}.s12{grid-column:span 12}
svg{display:block;max-width:100%;height:auto;overflow:visible}
svg text{fill:var(--text2);font-size:11px}
.axis line,.gridline{stroke:var(--grid)}
.bar{cursor:pointer;transition:opacity .15s}
.bar:hover{opacity:.8}
.dim{opacity:.3}
table{width:100%;border-collapse:collapse;font-size:13px;font-variant-numeric:tabular-nums}
th,td{padding:6px 6px;border-bottom:1px solid var(--grid);text-align:right}
th:first-child,td:first-child{text-align:left}
th{color:var(--text2);font-weight:600;font-size:12px}
.legend{display:flex;flex-wrap:wrap;gap:4px 14px;font-size:12px;color:var(--text2);margin:2px 0 4px}
.legend i{display:inline-block;width:10px;height:10px;border-radius:2px;margin-right:5px;vertical-align:-1px}
#tip{position:fixed;pointer-events:none;background:var(--panel);color:var(--text);border:1px solid var(--border);border-radius:8px;
  padding:8px 10px;font-size:12.5px;box-shadow:0 4px 16px rgba(0,0,0,.12);display:none;z-index:10;max-width:320px}
#tip b{display:block;margin-bottom:2px}
#tip .row{display:flex;justify-content:space-between;gap:16px;color:var(--text2)}
#tip .row span:last-child{color:var(--text);font-variant-numeric:tabular-nums}
footer{padding:0 24px 24px;color:var(--muted);font-size:12px}
@media (max-width:900px){
  .card{grid-column:span 6}
  .s4,.s5,.s6,.s7,.s8{grid-column:span 12}
  header,nav,.slicers,.chips,main,footer{padding-left:16px;padding-right:16px}
}
</style>
</head>
<body>
<header>
  <div>
    <h1>Retail Shop Analysis</h1>
    <div class="sub">Superstore Sales 2009–2012 · interactive dashboard · all values in USD</div>
  </div>
</header>
<nav id="tabs">
  <button data-page="exec" class="active">Executive Overview</button>
  <button data-page="prod">Product Analysis</button>
  <button data-page="cust">Customer Analysis</button>
  <button data-page="reg">Regional Analysis</button>
</nav>
<div class="slicers">
  <label class="slicer">From<select id="f_from"></select></label>
  <label class="slicer">To<select id="f_to"></select></label>
  <label class="slicer">Category<select id="f_cat"></select></label>
  <label class="slicer">Region<select id="f_reg"></select></label>
  <label class="slicer">RFM segment<select id="f_rfm"></select></label>
  <label class="slicer">Business segment<select id="f_bseg"></select></label>
  <button id="reset">Reset filters</button>
</div>
<div class="chips" id="chips"></div>
<main>
  <section class="page active" id="exec">
    <div class="grid">
      <div class="card"><div class="lab">Total Revenue</div><div class="val" id="k_rev"></div><div class="note" id="k_rev_n"></div></div>
      <div class="card"><div class="lab">Total Profit</div><div class="val" id="k_pro"></div><div class="note" id="k_pro_n"></div></div>
      <div class="card"><div class="lab">Total Orders</div><div class="val" id="k_ord"></div><div class="note" id="k_ord_n"></div></div>
      <div class="card"><div class="lab">Average Order Value</div><div class="val" id="k_aov"></div><div class="note" id="k_aov_n"></div></div>
      <div class="panel s8"><h3>Monthly revenue trend</h3><div class="hint">Hover for monthly values</div>
        <div class="legend"><span><i style="background:var(--blue-l)"></i>Monthly revenue</span><span><i style="background:var(--blue)"></i>3-month rolling average</span></div>
        <div id="c_trend"></div></div>
      <div class="panel s4"><h3>Revenue by category</h3><div class="hint">Click a bar to filter</div><div id="c_cat"></div></div>
      <div class="panel s6"><h3>Revenue by year</h3><div id="c_yrev"></div></div>
      <div class="panel s6"><h3>Profit by year</h3><div id="c_ypro"></div></div>
    </div>
  </section>
  <section class="page" id="prod">
    <div class="grid">
      <div class="panel s6"><h3>Top 10 products by revenue</h3><div class="legend" id="lg_cat1"></div><div id="c_top"></div></div>
      <div class="panel s6"><h3>Top 10 loss-making products</h3><div class="hint">Lowest total profit in the current filter</div><div id="c_loss"></div></div>
      <div class="panel s7"><h3>Profit by sub-category</h3><div class="hint">Blue = profit · red = loss · label = margin</div><div id="c_sub"></div></div>
      <div class="panel s5"><h3>Bottom 10 products by revenue</h3><div class="hint">Low-performing products</div><div id="c_low"></div></div>
      <div class="panel s12"><h3>Category profitability</h3><div id="t_cat"></div></div>
    </div>
  </section>
  <section class="page" id="cust">
    <div class="grid">
      <div class="card"><div class="lab">Customers</div><div class="val" id="k_cus"></div><div class="note"></div></div>
      <div class="card"><div class="lab">Repeat Customer Rate</div><div class="val" id="k_rep"></div><div class="note" id="k_rep_n"></div></div>
      <div class="card"><div class="lab">Orders per Customer</div><div class="val" id="k_opc"></div><div class="note"></div></div>
      <div class="card"><div class="lab">Revenue per Customer</div><div class="val" id="k_rpc"></div><div class="note"></div></div>
      <div class="panel s6"><h3>Customers by RFM segment</h3><div class="hint">Click a bar to filter</div><div id="c_rfmc"></div></div>
      <div class="panel s6"><h3>Revenue by RFM segment</h3><div class="hint">Click a bar to filter</div><div id="c_rfmr"></div></div>
      <div class="panel s6"><h3>Top 10 customers</h3><div id="t_cust"></div></div>
      <div class="panel s6"><h3>Revenue by business segment and year</h3><div class="legend" id="lg_bseg"></div><div id="c_bseg"></div></div>
    </div>
  </section>
  <section class="page" id="reg">
    <div class="grid">
      <div class="panel s4"><h3>Revenue by province</h3><div class="hint">Province = sales territory (no store IDs in data)</div><div id="c_prov"></div></div>
      <div class="panel s4"><h3>Profit margin by province</h3><div class="hint">Dashed line = margin of current selection · amber = below 5%</div><div id="c_provm"></div></div>
      <div class="panel s4"><h3>Profit: region × category ($K)</h3><div class="hint">Click a cell to filter by region and category</div><div id="c_heat"></div></div>
    </div>
  </section>
</main>
<footer>Built from dashboard/powerbi_data (same star schema as the Power BI model). Numbers are computed live in your browser from 8,399 order lines.</footer>
<div id="tip"></div>
<script>
const DATA = __DATA__;
const C = DATA.cols, D = DATA.dicts, N = C.sales.length;
const css = n => getComputedStyle(document.documentElement).getPropertyValue(n).trim();
const CAT_COL = () => [css('--blue'), css('--orange'), css('--aqua')];
const BSEG_COL = () => [css('--blue'), css('--orange'), css('--aqua'), css('--violet')];

// ---------- formatting ----------
const money = v => { const s = v < 0 ? '-' : ''; v = Math.abs(v);
  return s + (v >= 1e6 ? '$' + (v/1e6).toFixed(2) + 'M' : v >= 1e4 ? '$' + Math.round(v/1e3) + 'K' : '$' + v.toLocaleString('en-US', {maximumFractionDigits: 0})); };
const moneyFull = v => (v < 0 ? '-$' : '$') + Math.abs(v).toLocaleString('en-US', {maximumFractionDigits: 0});
const pct = v => (isFinite(v) ? v.toFixed(1) : '–') + '%';
const int = v => v.toLocaleString('en-US');
const esc = s => String(s).replace(/[&<>"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
const short = (s, n) => s.length > n ? s.slice(0, n - 1) + '…' : s;
function niceStep(r){ if (!(r > 0)) return 1; const p = Math.pow(10, Math.floor(Math.log10(r))); const f = r / p;
  return (f <= 1 ? 1 : f <= 2 ? 2 : f <= 2.5 ? 2.5 : f <= 5 ? 5 : 10) * p; }
// axis ticks covering [lo, hi] with about 4 intervals
function ticks(lo, hi){ const st = niceStep((hi - lo) / 4 || 1); const a = Math.floor(lo / st) * st, b = Math.ceil(hi / st) * st;
  const out = []; for (let v = a; v <= b + st / 2; v += st) out.push(+v.toFixed(10)); return out; }
const widthOf = (el, min) => Math.max(min || 300, Math.round(el.clientWidth || 520));

// ---------- filters ----------
const F = {from: 0, to: D.ym.length - 1, cat: -1, reg: -1, rfm: -1, bseg: -1};
function fillSelect(id, items, allLabel){
  const el = document.getElementById(id);
  el.innerHTML = (allLabel ? `<option value="-1">${allLabel}</option>` : '') +
    items.map((t, i) => `<option value="${i}">${esc(t)}</option>`).join('');
}
const monthLabel = ym => { const [y, m] = ym.split('-'); return ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'][+m-1] + ' ' + y; };
fillSelect('f_from', D.ym.map(monthLabel)); fillSelect('f_to', D.ym.map(monthLabel));
fillSelect('f_cat', D.cat, 'All'); fillSelect('f_reg', D.reg, 'All');
fillSelect('f_rfm', D.rfm, 'All'); fillSelect('f_bseg', D.bseg, 'All');
const SEL = {from: 'f_from', to: 'f_to', cat: 'f_cat', reg: 'f_reg', rfm: 'f_rfm', bseg: 'f_bseg'};
function syncSelects(){ for (const k in SEL) document.getElementById(SEL[k]).value = F[k]; }
for (const k in SEL) document.getElementById(SEL[k]).addEventListener('change', e => {
  F[k] = +e.target.value;
  if (F.from > F.to) { if (k === 'from') F.to = F.from; else F.from = F.to; }
  render();
});
function setFilter(k, v){ F[k] = F[k] === v ? -1 : v; render(); }   // clicking again clears it
document.getElementById('reset').onclick = () => { Object.assign(F, {from: 0, to: D.ym.length - 1, cat: -1, reg: -1, rfm: -1, bseg: -1}); render(); };

function rows(){
  const out = [];
  for (let i = 0; i < N; i++){
    const y = C.ym[i];
    if (y < F.from || y > F.to) continue;
    if (F.cat >= 0 && C.cat[i] !== F.cat) continue;
    if (F.reg >= 0 && C.reg[i] !== F.reg) continue;
    if (F.rfm >= 0 && C.rfm[i] !== F.rfm) continue;
    if (F.bseg >= 0 && C.bseg[i] !== F.bseg) continue;
    out.push(i);
  }
  return out;
}
function group(idx, keyCol, size){
  const g = Array.from({length: size}, () => ({sales: 0, profit: 0, qty: 0, orders: new Set(), n: 0}));
  for (const i of idx){ const r = g[C[keyCol][i]]; r.sales += C.sales[i]; r.profit += C.profit[i]; r.qty += C.qty[i]; r.orders.add(C.order[i]); r.n++; }
  return g;
}

// ---------- tooltip ----------
const tip = document.getElementById('tip');
function showTip(e, title, rowsKV){
  tip.innerHTML = `<b>${esc(title)}</b>` + rowsKV.map(([k, v]) => `<div class="row"><span>${esc(k)}</span><span>${esc(v)}</span></div>`).join('');
  tip.style.display = 'block'; moveTip(e);
}
function moveTip(e){
  const w = tip.offsetWidth, h = tip.offsetHeight;
  let x = e.clientX + 14, y = e.clientY + 14;
  if (x + w > innerWidth - 8) x = e.clientX - w - 14;
  if (y + h > innerHeight - 8) y = e.clientY - h - 14;
  tip.style.left = x + 'px'; tip.style.top = y + 'px';
}
const hideTip = () => tip.style.display = 'none';
function bindTips(root){
  root.querySelectorAll('[data-tip]').forEach(el => {
    const t = JSON.parse(el.dataset.tip);
    el.addEventListener('mouseenter', e => showTip(e, t[0], t[1]));
    el.addEventListener('mousemove', moveTip);
    el.addEventListener('mouseleave', hideTip);
  });
}
const tipAttr = (title, kv) => `data-tip='${esc(JSON.stringify([title, kv])).replace(/'/g, '&#39;')}'`;

// ---------- chart primitives (plain SVG) ----------
function hbar(el, items, opt){
  // items: {label, value, color, tip:[title,kv], onClick, active}
  const W = widthOf(el), rowH = opt.rowH || 24, padL = Math.min(opt.padL || 150, W * 0.42), padR = 16, H = items.length * rowH + 26;
  const vals = items.map(d => d.value);
  const lo = Math.min(0, ...vals), hi = Math.max(0, ...vals);
  const tk = ticks(lo, hi);
  // extra room for value labels beyond the bar ends
  const span = (tk[tk.length - 1] - tk[0]) || 1, room = opt.valueLabel ? 0.16 * span : 0;
  const xmin = Math.min(tk[0], lo - (lo < 0 ? room : 0)), xmax = Math.max(tk[tk.length - 1], hi + (hi > 0 ? room : 0));
  const sx = v => padL + (v - xmin) / ((xmax - xmin) || 1) * (W - padL - padR);
  let s = `<svg viewBox="0 0 ${W} ${H}" width="${W}" height="${H}" role="img">`;
  for (const v of tk){ const x = sx(v);
    s += `<line class="gridline" x1="${x}" x2="${x}" y1="0" y2="${H - 20}"/><text x="${x}" y="${H - 6}" text-anchor="middle">${opt.axisFmt(v)}</text>`; }
  const anyActive = items.some(d => d.active);
  items.forEach((d, i) => {
    const y = i * rowH + 4, h = rowH - 8, x0 = sx(Math.min(0, d.value)), x1 = sx(Math.max(0, d.value));
    s += `<text x="${padL - 6}" y="${y + h / 2 + 4}" text-anchor="end">${esc(short(d.label, Math.min(opt.labelLen || 24, Math.floor(padL / 6.2))))}</text>`;
    s += `<rect class="bar${anyActive && !d.active ? ' dim' : ''}" x="${x0}" y="${y}" width="${Math.max(1, x1 - x0)}" height="${h}" rx="3" fill="${d.color}" ${tipAttr(d.tip[0], d.tip[1])} data-i="${i}"/>`;
    if (opt.valueLabel) s += `<text x="${d.value >= 0 ? x1 + 4 : x0 - 4}" y="${y + h / 2 + 4}" text-anchor="${d.value >= 0 ? 'start' : 'end'}">${opt.valueLabel(d)}</text>`;
  });
  if (lo < 0) s += `<line x1="${sx(0)}" x2="${sx(0)}" y1="0" y2="${H - 20}" stroke="${css('--text2')}" stroke-width="1"/>`;
  if (opt.refLine != null && isFinite(opt.refLine)) s += `<line x1="${sx(opt.refLine)}" x2="${sx(opt.refLine)}" y1="0" y2="${H - 20}" stroke="${css('--text2')}" stroke-dasharray="4 3"/>`;
  el.innerHTML = s + '</svg>';
  bindTips(el);
  el.querySelectorAll('rect.bar').forEach(r => { const d = items[+r.dataset.i]; if (d.onClick) r.onclick = () => { hideTip(); d.onClick(); }; else r.style.cursor = 'default'; });
}

function vbar(el, items, opt){
  const W = widthOf(el), H = 220, padL = 54, padB = 24, padT = 16;
  const tk = ticks(0, Math.max(...items.map(d => d.value), 1)), max = tk[tk.length - 1];
  const bw = (W - padL) / items.length;
  let s = `<svg viewBox="0 0 ${W} ${H}" width="${W}" height="${H}" role="img">`;
  for (const v of tk){
    const y = H - padB - v / max * (H - padB - padT);
    s += `<line class="gridline" x1="${padL}" x2="${W}" y1="${y}" y2="${y}"/><text x="${padL - 6}" y="${y + 4}" text-anchor="end">${money(v)}</text>`;
  }
  items.forEach((d, i) => {
    const h = Math.max(0, d.value) / max * (H - padB - padT), x = padL + i * bw + bw * 0.2, y = H - padB - h;
    s += `<rect class="bar" style="cursor:default" x="${x}" y="${y}" width="${Math.min(bw * 0.6, 90)}" height="${h}" rx="3" fill="${opt.color}" ${tipAttr(d.label, d.tip)}/>`;
    s += `<text x="${x + bw * 0.3}" y="${H - 6}" text-anchor="middle">${d.label}</text>`;
    s += `<text x="${x + bw * 0.3}" y="${y - 4}" text-anchor="middle">${money(d.value)}</text>`;
  });
  el.innerHTML = s + '</svg>'; bindTips(el);
}

function lines(el, xLabels, series, opt){
  // series: [{name, values, color, width}]; crosshair tooltip over x positions
  const W = widthOf(el), H = opt.H || 260, padL = 58, padB = 26, padT = 10, padR = 28;
  const all = series.flatMap(s => s.values.filter(v => v != null));
  const tk = ticks(0, Math.max(...all, 1)), max = tk[tk.length - 1];
  const n = xLabels.length, sx = i => padL + (n === 1 ? (W - padL - padR) / 2 : i / (n - 1) * (W - padL - padR));
  const sy = v => H - padB - v / max * (H - padB - padT);
  let s = `<svg viewBox="0 0 ${W} ${H}" width="${W}" height="${H}" role="img">`;
  for (const v of tk){ const y = sy(v);
    s += `<line class="gridline" x1="${padL}" x2="${W - padR}" y1="${y}" y2="${y}"/><text x="${padL - 6}" y="${y + 4}" text-anchor="end">${money(v)}</text>`; }
  const step = Math.max(1, Math.ceil(n / Math.max(2, Math.floor((W - padL) / 90))));
  xLabels.forEach((l, i) => { if (i % step === 0 || i === n - 1) s += `<text x="${sx(i)}" y="${H - 6}" text-anchor="middle">${esc(l)}</text>`; });
  series.forEach(se => {
    let d = '', pen = false;
    se.values.forEach((v, i) => { if (v == null) { pen = false; return; } d += (pen ? 'L' : 'M') + sx(i) + ' ' + sy(v); pen = true; });
    s += `<path d="${d}" fill="none" stroke="${se.color}" stroke-width="${se.width || 2}" stroke-linejoin="round"/>`;
    if (opt.markers) se.values.forEach((v, i) => { if (v != null) s += `<circle cx="${sx(i)}" cy="${sy(v)}" r="4" fill="${se.color}" stroke="${css('--panel')}" stroke-width="2"/>`; });
  });
  s += `<line id="xh" x1="0" x2="0" y1="${padT}" y2="${H - padB}" stroke="${css('--text2')}" stroke-dasharray="3 3" visibility="hidden"/>`;
  s += `<rect x="${padL}" y="0" width="${W - padL - padR}" height="${H - padB}" fill="transparent" class="hit"/>`;
  el.innerHTML = s + '</svg>';
  const svg = el.querySelector('svg'), hit = el.querySelector('.hit'), xh = el.querySelector('#xh');
  hit.addEventListener('mousemove', e => {
    const pt = svg.createSVGPoint(); pt.x = e.clientX; pt.y = e.clientY;
    const p = pt.matrixTransform(svg.getScreenCTM().inverse());
    const i = Math.max(0, Math.min(n - 1, Math.round((p.x - padL) / ((W - padL - padR) / Math.max(1, n - 1)))));
    xh.setAttribute('x1', sx(i)); xh.setAttribute('x2', sx(i)); xh.setAttribute('visibility', 'visible');
    showTip(e, xLabels[i], series.map(se => [se.name, se.values[i] == null ? '–' : moneyFull(se.values[i])]));
  });
  hit.addEventListener('mouseleave', () => { hideTip(); xh.setAttribute('visibility', 'hidden'); });
}

function table(el, head, body){
  el.innerHTML = `<table><thead><tr>${head.map(h => `<th>${esc(h)}</th>`).join('')}</tr></thead><tbody>` +
    body.map(r => `<tr>${r.map(c => `<td>${esc(c)}</td>`).join('')}</tr>`).join('') + '</tbody></table>';
}
function legend(el, names, colors){ el.innerHTML = names.map((n, i) => `<span><i style="background:${colors[i]}"></i>${esc(n)}</span>`).join(''); }

// ---------- render ----------
let page = 'exec';
document.querySelectorAll('#tabs button').forEach(b => b.onclick = () => {
  document.querySelectorAll('#tabs button').forEach(x => x.classList.toggle('active', x === b));
  document.querySelectorAll('.page').forEach(p => p.classList.toggle('active', p.id === b.dataset.page));
  page = b.dataset.page; render();
});

function render(){
  syncSelects(); hideTip();
  const chips = [];
  if (F.from > 0 || F.to < D.ym.length - 1) chips.push(`${monthLabel(D.ym[F.from])} – ${monthLabel(D.ym[F.to])}`);
  if (F.cat >= 0) chips.push('Category: ' + D.cat[F.cat]);
  if (F.reg >= 0) chips.push('Region: ' + D.reg[F.reg]);
  if (F.rfm >= 0) chips.push('RFM: ' + D.rfm[F.rfm]);
  if (F.bseg >= 0) chips.push('Segment: ' + D.bseg[F.bseg]);
  document.getElementById('chips').innerHTML = chips.map(c => `<span class="chip">${esc(c)}</span>`).join('');

  const idx = rows();
  let rev = 0, pro = 0; const orders = new Set(), custs = new Set();
  for (const i of idx){ rev += C.sales[i]; pro += C.profit[i]; orders.add(C.order[i]); custs.add(C.cust[i]); }
  const margin = rev ? pro / rev * 100 : NaN;
  const catCol = CAT_COL();
  const $ = id => document.getElementById(id);

  if (page === 'exec'){
    $('k_rev').textContent = money(rev); $('k_rev_n').textContent = `${int(idx.length)} order lines`;
    $('k_pro').textContent = money(pro); $('k_pro_n').textContent = `Margin ${pct(margin)}`;
    $('k_ord').textContent = int(orders.size); $('k_ord_n').textContent = `${int(custs.size)} customers`;
    $('k_aov').textContent = orders.size ? moneyFull(rev / orders.size) : '–'; $('k_aov_n').textContent = 'Revenue ÷ orders';
    const m = group(idx, 'ym', D.ym.length).slice(F.from, F.to + 1).map(r => r.sales);
    const roll = m.map((v, i) => i < 2 ? null : (m[i] + m[i-1] + m[i-2]) / 3);
    lines($('c_trend'), D.ym.slice(F.from, F.to + 1).map(monthLabel),
      [{name: 'Monthly revenue', values: m, color: css('--blue-l'), width: 1.6},
       {name: '3-month rolling avg', values: roll, color: css('--blue'), width: 2.6}], {});
    const g = group(idx, 'cat', D.cat.length);
    hbar($('c_cat'), D.cat.map((c, i) => ({label: c, value: g[i].sales, color: catCol[i], active: F.cat === i,
      tip: [c, [['Revenue', moneyFull(g[i].sales)], ['Profit', moneyFull(g[i].profit)], ['Margin', pct(g[i].profit / g[i].sales * 100)], ['Share of revenue', pct(g[i].sales / rev * 100)]]],
      onClick: () => setFilter('cat', i)})), {padL: 110, rowH: 46, axisFmt: money, valueLabel: d => money(d.value)});
    const years = {}; for (const i of idx){ const y = D.ym[C.ym[i]].slice(0, 4); (years[y] ||= {s: 0, p: 0}); years[y].s += C.sales[i]; years[y].p += C.profit[i]; }
    const ys = Object.keys(years).sort();
    vbar($('c_yrev'), ys.map(y => ({label: y, value: years[y].s, tip: [['Revenue', moneyFull(years[y].s)], ['Margin', pct(years[y].p / years[y].s * 100)]]})), {color: css('--blue')});
    vbar($('c_ypro'), ys.map(y => ({label: y, value: years[y].p, tip: [['Profit', moneyFull(years[y].p)], ['Margin', pct(years[y].p / years[y].s * 100)]]})), {color: css('--aqua')});
  }

  if (page === 'prod'){
    legend($('lg_cat1'), D.cat, catCol);
    const g = group(idx, 'prod', D.prod.length).map((r, i) => ({...r, i})).filter(r => r.n > 0);
    const prodTip = r => [D.prod[r.i], [['Category', D.cat[D.prodCat[r.i]]], ['Revenue', moneyFull(r.sales)], ['Profit', moneyFull(r.profit)], ['Margin', pct(r.profit / r.sales * 100)], ['Units', int(r.qty)], ['Orders', int(r.orders.size)]]];
    const top = [...g].sort((a, b) => b.sales - a.sales).slice(0, 10);
    hbar($('c_top'), top.map(r => ({label: D.prod[r.i], value: r.sales, color: catCol[D.prodCat[r.i]], tip: prodTip(r)})), {padL: 190, labelLen: 30, axisFmt: money});
    const loss = [...g].sort((a, b) => a.profit - b.profit).slice(0, 10).filter(r => r.profit < 0);
    if (loss.length) hbar($('c_loss'), loss.map(r => ({label: D.prod[r.i], value: r.profit, color: css('--red'), tip: prodTip(r)})), {padL: 190, labelLen: 30, axisFmt: money});
    else $('c_loss').innerHTML = '<p class="hint">No loss-making products in this selection.</p>';
    const low = [...g].sort((a, b) => a.sales - b.sales).slice(0, 10);
    hbar($('c_low'), low.map(r => ({label: D.prod[r.i], value: r.sales, color: css('--gray'), tip: prodTip(r)})), {padL: 170, labelLen: 26, axisFmt: v => '$' + Math.round(v).toLocaleString('en-US')});
    const sg = group(idx, 'sub', D.sub.length).map((r, i) => ({...r, i})).filter(r => r.n > 0).sort((a, b) => b.profit - a.profit);
    hbar($('c_sub'), sg.map(r => ({label: D.sub[r.i], value: r.profit, color: r.profit >= 0 ? css('--blue') : css('--red'),
      tip: [D.sub[r.i], [['Category', D.cat[D.subCat[r.i]]], ['Revenue', moneyFull(r.sales)], ['Profit', moneyFull(r.profit)], ['Margin', pct(r.profit / r.sales * 100)]]],
      onClick: () => setFilter('cat', D.subCat[r.i])})), {padL: 190, labelLen: 30, axisFmt: money, valueLabel: d => pct(d.tip[1][3] ? parseFloat(d.tip[1][3][1]) : 0)});
    const cg = group(idx, 'cat', D.cat.length);
    table($('t_cat'), ['Category', 'Revenue', 'Profit', 'Margin', 'Units', 'Orders', 'Share of revenue'],
      D.cat.map((c, i) => [c, moneyFull(cg[i].sales), moneyFull(cg[i].profit), pct(cg[i].profit / cg[i].sales * 100), int(cg[i].qty), int(cg[i].orders.size), pct(cg[i].sales / rev * 100)]));
  }

  if (page === 'cust'){
    const cg = group(idx, 'cust', D.cust.length).map((r, i) => ({...r, i})).filter(r => r.n > 0);
    const rep = cg.filter(r => r.orders.size > 1).length;
    $('k_cus').textContent = int(cg.length);
    $('k_rep').textContent = cg.length ? pct(rep / cg.length * 100) : '–'; $('k_rep_n').textContent = `${int(rep)} repeat buyers in selection`;
    $('k_opc').textContent = cg.length ? (orders.size / cg.length).toFixed(2) : '–';
    $('k_rpc').textContent = cg.length ? moneyFull(rev / cg.length) : '–';
    const segC = D.rfm.map(() => new Set()), segR = D.rfm.map(() => 0), segP = D.rfm.map(() => 0);
    for (const i of idx){ segC[C.rfm[i]].add(C.cust[i]); segR[C.rfm[i]] += C.sales[i]; segP[C.rfm[i]] += C.profit[i]; }
    const segItems = (val, fmt, color) => D.rfm.map((s, k) => ({label: s, value: val(k), color, active: F.rfm === k,
      tip: [s, [['Customers', int(segC[k].size)], ['Revenue', moneyFull(segR[k])], ['Share of revenue', pct(segR[k] / rev * 100)], ['Profit', moneyFull(segP[k])]]],
      onClick: () => setFilter('rfm', k)}));
    hbar($('c_rfmc'), segItems(k => segC[k].size, int, css('--gray')), {padL: 160, axisFmt: v => Math.round(v), valueLabel: d => int(d.value)});
    hbar($('c_rfmr'), segItems(k => segR[k], money, css('--blue')), {padL: 160, axisFmt: money, valueLabel: d => money(d.value)});
    const top = [...cg].sort((a, b) => b.sales - a.sales).slice(0, 10);
    table($('t_cust'), ['Customer', 'Revenue', 'Orders', 'Profit', 'RFM segment'],
      top.map(r => { let seg = ''; for (const i of idx) if (C.cust[i] === r.i){ seg = D.rfm[C.rfm[i]]; break; }
        return [D.cust[r.i], moneyFull(r.sales), int(r.orders.size), moneyFull(r.profit), seg]; }));
    const yrs = [...new Set(idx.map(i => D.ym[C.ym[i]].slice(0, 4)))].sort();
    const bcol = BSEG_COL();
    const series = D.bseg.map((b, k) => ({name: b, color: bcol[k], width: 2.2, values: yrs.map(y => {
      let s = 0; for (const i of idx) if (C.bseg[i] === k && D.ym[C.ym[i]].startsWith(y)) s += C.sales[i]; return s; })}))
      .filter((s, k) => F.bseg < 0 || F.bseg === k);
    legend($('lg_bseg'), series.map(s => s.name), series.map(s => s.color));
    lines($('c_bseg'), yrs, series, {markers: true, H: 280});
  }

  if (page === 'reg'){
    const pg = group(idx, 'prov', D.prov.length).map((r, i) => ({...r, i})).filter(r => r.n > 0);
    const ptip = r => [D.prov[r.i], [['Region', D.reg[D.provReg[r.i]]], ['Revenue', moneyFull(r.sales)], ['Profit', moneyFull(r.profit)], ['Margin', pct(r.profit / r.sales * 100)], ['Orders', int(r.orders.size)]]];
    hbar($('c_prov'), [...pg].sort((a, b) => b.sales - a.sales).map(r => ({label: D.prov[r.i], value: r.sales, color: css('--blue'), tip: ptip(r),
      active: F.reg === D.provReg[r.i], onClick: () => setFilter('reg', D.provReg[r.i])})), {padL: 140, axisFmt: money});
    hbar($('c_provm'), [...pg].sort((a, b) => b.profit / b.sales - a.profit / a.sales).map(r => { const m = r.profit / r.sales * 100;
      return {label: D.prov[r.i], value: m, color: m < 0 ? css('--red') : m < 5 ? css('--yellow') : css('--blue'), tip: ptip(r)}; }),
      {padL: 140, axisFmt: v => v.toFixed(0) + '%', valueLabel: d => pct(d.value), refLine: margin});
    // heatmap region x category (diverging: red = loss, blue = profit)
    const regs = D.reg.map((r, k) => k).filter(k => idx.some(i => C.reg[i] === k));
    const cell = {}; let lim = 1;
    for (const i of idx){ const key = C.reg[i] + '_' + C.cat[i]; cell[key] = (cell[key] || 0) + C.profit[i]; }
    Object.values(cell).forEach(v => lim = Math.max(lim, Math.abs(v)));
    const W = widthOf($('c_heat')), padL = Math.min(140, W * 0.34), cw = (W - padL - 4) / 3, ch = 30, H = regs.length * ch + 26;
    const blend = (v) => { const t = Math.min(1, Math.abs(v) / lim); const a = v >= 0 ? [42,120,214] : [227,73,72];
      return `rgba(${a[0]},${a[1]},${a[2]},${0.12 + 0.78 * t})`; };
    let s = `<svg viewBox="0 0 ${W} ${H}" width="${W}" height="${H}" role="img">`;
    ['Technology','Furniture','Office Supp.'].forEach((c, j) => s += `<text x="${padL + j * cw + cw / 2}" y="${H - 6}" text-anchor="middle">${c}</text>`);
    regs.forEach((k, r) => {
      s += `<text x="${padL - 6}" y="${r * ch + ch / 2 + 4}" text-anchor="end">${esc(short(D.reg[k], 20))}</text>`;
      [0, 1, 2].forEach(j => { const v = cell[k + '_' + j] || 0, strong = Math.abs(v) / lim > 0.55;
        s += `<rect class="bar" data-r="${k}" data-c="${j}" x="${padL + j * cw + 1}" y="${r * ch + 1}" width="${cw - 2}" height="${ch - 2}" rx="3" fill="${blend(v)}" ${tipAttr(D.reg[k] + ' · ' + D.cat[j], [['Profit', moneyFull(v)]])}/>`;
        s += `<text x="${padL + j * cw + cw / 2}" y="${r * ch + ch / 2 + 4}" text-anchor="middle" style="pointer-events:none;${strong ? 'fill:#fff' : 'fill:' + css('--text')}">${Math.round(v / 1e3)}</text>`; });
    });
    $('c_heat').innerHTML = s + '</svg>'; bindTips($('c_heat'));
    $('c_heat').querySelectorAll('rect').forEach(r => r.onclick = () => { hideTip(); F.reg = F.reg === +r.dataset.r && F.cat === +r.dataset.c ? -1 : +r.dataset.r;
      F.cat = F.reg === -1 ? -1 : +r.dataset.c; render(); });
  }
}
let rz; addEventListener('resize', () => { clearTimeout(rz); rz = setTimeout(render, 150); });
render();
</script>
</body>
</html>
"""

OUT.write_text(HTML.replace("__DATA__", payload), encoding="utf-8")
print(f"Saved {OUT.relative_to(ROOT)}  ({OUT.stat().st_size / 1e6:.2f} MB, {len(df):,} rows embedded)")
