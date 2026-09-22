const map = L.map("map").setView([53.9, 27.55], 5);
L.tileLayer("https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png", { attribution: "&copy; OpenStreetMap &copy; CARTO", maxZoom: 19 }).addTo(map);
const layer = L.layerGroup().addTo(map);
function kindColor(kind) {
  return { selfie: "#22d3ee", content: "#a78bfa", film: "#ef4444", investment: "#3b82f6" }[kind] || "#a78bfa";
}
function renderMarkers(items) {
  layer.clearLayers();
  const bounds = [];
  for (const item of items) {
    const marker = L.circleMarker([item.lat, item.lon], { radius: 8, color: kindColor(item.kind), fillColor: kindColor(item.kind), fillOpacity: 0.9, weight: 1 }).addTo(layer);
    marker.bindPopup(`<b>${item.name}</b><br>${item.city || item.region || ""} ${item.country || ""}` +
      (item.facility_type ? `<br>${item.facility_type} · павильонов ${item.stages_count || "—"}` : "") +
      (item.virtual_production ? "<br>virtual production / LED" : "") +
      (item.day_rate_usd_from ? `<br>день от $${item.day_rate_usd_from}` : "") +
      (item.permit_office ? `<br>пермит: ${item.permit_office}` : ""));
    bounds.push([item.lat, item.lon]);
  }
  if (bounds.length) map.fitBounds(bounds, { padding: [40, 40], maxZoom: 5 });
}
function renderCards(items) {
  document.getElementById("results").innerHTML = items.map((item) => `
    <article class="card"><h3>${item.name}</h3>
    <p>${item.city || item.region || ""} ${item.country || ""}</p>
    <div class="meta"><span>${item.facility_type || item.kind}</span>
    <span>${item.virtual_production ? "LED/VP" : (item.price_tier || "")}</span>
    <span>${item.day_rate_usd_from ? "от $" + item.day_rate_usd_from : ""}</span></div>
    ${item.permit_office ? `<p>пермит: ${item.permit_office}</p>` : ""}</article>`).join("");
}
async function loadAll() {
  const film = document.getElementById("kind").value === "film";
  const res = await fetch(film ? "/api/studios" : "/api/locations");
  if (!res.ok) throw new Error("Сервер не отвечает");
  const data = await res.json();
  renderMarkers(data.items); renderCards(data.items);
  document.getElementById("status").textContent = film ? `${data.count} студий` : `${data.count} точек`;
}
async function runScout(path) {
  const body = { query: document.getElementById("query").value.trim(), kind: document.getElementById("kind").value, plan_code: document.getElementById("plan").value, limit: 20, lon: map.getCenter().lng, lat: map.getCenter().lat, radius_km: 200 };
  document.getElementById("status").textContent = "ищем…";
  const res = await fetch(path, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) });
  const data = await res.json();
  if (!res.ok) { document.getElementById("status").textContent = (data.detail && data.detail.message) || "не вышло"; return; }
  renderMarkers(data.results); renderCards(data.results);
  document.getElementById("status").textContent = `нашли ${data.results.length}`;
}
document.getElementById("analyze").addEventListener("click", () => {
  const film = document.getElementById("kind").value === "film";
  runScout(film ? "/api/studios/search" : "/api/scout");
});
const st = document.getElementById("studios");
if (st) st.addEventListener("click", () => { document.getElementById("kind").value = "film"; runScout("/api/studios/search"); });
document.getElementById("invest").addEventListener("click", () => runScout("/api/investments/analyze"));
loadAll().catch((e) => { document.getElementById("status").textContent = e.message; });
