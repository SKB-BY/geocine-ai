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
    if (item.lat == null) continue;
    const marker = L.circleMarker([item.lat, item.lon], { radius: 8, color: kindColor(item.kind), fillColor: kindColor(item.kind), fillOpacity: 0.9, weight: 1 }).addTo(layer);
    marker.bindPopup(`<b>${item.name}</b><br>${item.city || ""} ${item.country || ""}` + (item.why ? `<br>${item.why}` : ""));
    bounds.push([item.lat, item.lon]);
  }
  if (bounds.length) map.fitBounds(bounds, { padding: [40, 40], maxZoom: 6 });
}
function renderCards(items) {
  document.getElementById("results").innerHTML = items.map((item) => `
    <article class="card">
      <h3>${item.name}</h3>
      <p>${item.city || item.region || ""} ${item.country || ""}</p>
      ${item.why ? `<p>${item.why}</p>` : ""}
      ${item.photos && item.photos.length ? `<div class="shots">${item.photos.slice(0,5).map((p) => `<img src="${p.url}" alt="${p.title || item.name}" loading="lazy">`).join("")}</div>` : ""}
    </article>`).join("");
}
async function loadAll() {
  const res = await fetch("/api/locations");
  if (!res.ok) throw new Error("Сервер не отвечает");
  const data = await res.json();
  renderMarkers(data.items); renderCards(data.items);
  document.getElementById("status").textContent = `${data.count} точек`;
}
async function runScout(path) {
  const body = { query: document.getElementById("query").value.trim(), kind: document.getElementById("kind").value, plan_code: document.getElementById("plan").value, limit: 12, lon: map.getCenter().lng, lat: map.getCenter().lat };
  document.getElementById("status").textContent = "ищем…";
  const res = await fetch(path, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) });
  const data = await res.json();
  if (!res.ok) { document.getElementById("status").textContent = "не вышло"; return; }
  renderMarkers(data.results || []); renderCards(data.results || []);
  document.getElementById("status").textContent = `нашли ${(data.results || []).length}`;
}
document.getElementById("analyze").addEventListener("click", () => {
  const film = document.getElementById("kind").value === "film";
  runScout(film ? "/api/film/locations" : "/api/scout");
});
const st = document.getElementById("studios");
if (st) st.addEventListener("click", () => { document.getElementById("kind").value = "film"; runScout("/api/studios/search"); });
document.getElementById("invest").addEventListener("click", () => runScout("/api/investments/analyze"));
const kindSel = document.getElementById("kind");
if (kindSel) kindSel.addEventListener("change", () => {
  if (kindSel.value === "film") document.getElementById("query").value = "Улочки со зданиями 18-19 века";
});
loadAll().catch((e) => { document.getElementById("status").textContent = e.message; });
