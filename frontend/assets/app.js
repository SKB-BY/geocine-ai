const map = L.map("map").setView([53.9, 27.55], 5);
L.tileLayer("https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png", { attribution: "&copy; OpenStreetMap &copy; CARTO", maxZoom: 19 }).addTo(map);
const layer = L.layerGroup().addTo(map);
function kindColor(kind) {
  return { selfie: "#22d3ee", content: "#a78bfa", film: "#ef4444", investment: "#3b82f6", both: "#a78bfa" }[kind] || "#a78bfa";
}
function renderMarkers(items) {
  layer.clearLayers();
  const bounds = [];
  for (const item of items) {
    const marker = L.circleMarker([item.lat, item.lon], { radius: 8, color: kindColor(item.kind), fillColor: kindColor(item.kind), fillOpacity: 0.9, weight: 1 }).addTo(layer);
    marker.bindPopup(`<b>${item.name}</b><br>${item.country}<br>${item.price_tier || "free"}`);
    bounds.push([item.lat, item.lon]);
  }
  if (bounds.length) map.fitBounds(bounds, { padding: [40, 40], maxZoom: 6 });
}
function renderCards(items) {
  document.getElementById("results").innerHTML = items.map((item) => `<article class="card"><h3>${item.name}</h3><p>${item.country}${item.region ? " · " + item.region : ""}</p><div class="meta"><span>${item.kind}</span><span>совпадение ${(item.match_score ?? 0).toFixed(2)}</span></div></article>`).join("");
}
async function loadAll() {
  const res = await fetch("/api/locations");
  if (!res.ok) throw new Error("Сервер не отвечает. Поднимите docker compose up");
  const data = await res.json();
  renderMarkers(data.items); renderCards(data.items);
  document.getElementById("status").textContent = `${data.count} точек в каталоге`;
}
async function runScout(path, extra = {}) {
  const body = { query: document.getElementById("query").value.trim(), kind: document.getElementById("kind").value || null, plan_code: (document.getElementById("plan") || {}).value || "free", limit: 20, ...extra };
  document.getElementById("status").textContent = "ищем…";
  const res = await fetch(path, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) });
  const data = await res.json();
  if (!res.ok) { document.getElementById("status").textContent = (data.detail && data.detail.message) || "Лимит на сегодня кончился"; return; }
  const parsed = document.getElementById("parsed");
  if (parsed) parsed.textContent = `теги: ${(data.parsed.tags || []).join(", ") || "—"}`;
  if (data.quota && document.getElementById("quota")) document.getElementById("quota").textContent = `тариф ${data.quota.plan}: ${data.quota.used} из ${data.quota.limit}`;
  renderMarkers(data.results); renderCards(data.results);
  document.getElementById("status").textContent = `нашли ${data.results.length} мест`;
}
document.getElementById("analyze").addEventListener("click", () => runScout("/api/scout"));
document.getElementById("invest").addEventListener("click", () => runScout("/api/investments/analyze", { max_risk: 0.75, radius_km: 20000 }));
const send = document.getElementById("spot-send");
if (send) send.addEventListener("click", async () => {
  const c = map.getCenter();
  const title = document.getElementById("spot-title").value.trim();
  const description = document.getElementById("spot-desc").value.trim();
  if (title.length < 3 || description.length < 3) { document.getElementById("status").textContent = "Нужны название и короткое описание"; return; }
  const res = await fetch("/api/spots", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ title, description, audience: document.getElementById("kind").value, lon: c.lng, lat: c.lat }) });
  const data = await res.json();
  document.getElementById("status").textContent = data.ok ? "Точку приняли на модерацию" : "Не отправилось";
});
loadAll().catch((e) => { document.getElementById("status").textContent = e.message; });
