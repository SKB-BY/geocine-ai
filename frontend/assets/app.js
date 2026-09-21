const map = L.map("map").setView([45, 30], 3);
L.tileLayer("https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png", {
  attribution: "&copy; OpenStreetMap &copy; CARTO",
  maxZoom: 19,
}).addTo(map);
const layer = L.layerGroup().addTo(map);
const statusEl = document.getElementById("status");
const resultsEl = document.getElementById("results");
const parsedEl = document.getElementById("parsed");
function kindColor(kind) {
  if (kind === "film") return "#ef4444";
  if (kind === "investment") return "#3b82f6";
  return "#a78bfa";
}
function renderMarkers(items) {
  layer.clearLayers();
  const bounds = [];
  for (const item of items) {
    const marker = L.circleMarker([item.lat, item.lon], {
      radius: 8, color: kindColor(item.kind), fillColor: kindColor(item.kind), fillOpacity: 0.85, weight: 1,
    }).addTo(layer);
    marker.bindPopup(`<b>${item.name}</b><br>${item.country}<br>match: ${item.match_score ?? "—"}`);
    bounds.push([item.lat, item.lon]);
  }
  if (bounds.length) map.fitBounds(bounds, { padding: [40, 40], maxZoom: 6 });
}
function renderCards(items) {
  resultsEl.innerHTML = items.map((item) => `
    <article class="card"><h3>${item.name}</h3>
    <p>${item.country}${item.region ? " · " + item.region : ""}</p>
    <div class="meta"><span>${item.kind}</span>
    <span>match ${(item.match_score ?? 0).toFixed(2)}</span>
    <span>invest ${(item.investment_score ?? 0).toFixed(2)}</span></div></article>`).join("");
}
async function loadAll() {
  statusEl.textContent = "загрузка локаций…";
  const res = await fetch("/api/locations");
  if (!res.ok) throw new Error("API недоступен");
  const data = await res.json();
  renderMarkers(data.items);
  renderCards(data.items);
  statusEl.textContent = `${data.count} локаций`;
}
async function runScout(path, extra = {}) {
  const body = { query: document.getElementById("query").value.trim(), kind: document.getElementById("kind").value || null, limit: 12, ...extra };
  const budgetRaw = document.getElementById("budget").value;
  if (budgetRaw) body.budget_usd = Number(budgetRaw);
  statusEl.textContent = "анализ…";
  const res = await fetch(path, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) });
  const data = await res.json();
  parsedEl.textContent = `tags: ${(data.parsed.tags || []).join(", ") || "—"}`;
  renderMarkers(data.results);
  renderCards(data.results);
  statusEl.textContent = `${data.results.length} результатов`;
}
document.getElementById("analyze").addEventListener("click", () => runScout("/api/scout").catch((e) => statusEl.textContent = e.message));
document.getElementById("invest").addEventListener("click", () => runScout("/api/investments/analyze", { max_risk: 0.7, radius_km: 20000 }).catch((e) => statusEl.textContent = e.message));
loadAll().catch((e) => statusEl.textContent = e.message);
