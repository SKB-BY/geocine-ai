const map = L.map("map").setView([53.9, 27.55], 5);
L.tileLayer("https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png", { attribution: "&copy; OpenStreetMap", maxZoom: 19 }).addTo(map);
const layer = L.layerGroup().addTo(map);
function renderMarkers(items) {
  layer.clearLayers(); const bounds = [];
  for (const item of items || []) {
    if (item.lat == null) continue;
    L.circleMarker([item.lat, item.lon], { radius: 8, color: "#ef4444", fillOpacity: 0.9 }).addTo(layer)
      .bindPopup(`<b>${item.name}</b><br>${item.city || ""} ${item.country || ""}<br>${item.why || ""}`);
    bounds.push([item.lat, item.lon]);
  }
  if (bounds.length) map.fitBounds(bounds, { padding: [40, 40], maxZoom: 6 });
}
function renderCards(items) {
  document.getElementById("results").innerHTML = (items || []).map((item) => `
    <article class="card"><h3>${item.name}</h3>
    <p>${item.city || ""} ${item.country || ""}</p>
    <p>${(item.epoch_labels || []).join(", ")}</p>
    ${item.why ? `<p>${item.why}</p>` : ""}
    ${item.photos && item.photos.length ? `<div class="shots">${item.photos.slice(0,5).map(p => `<img src="${p.url}" alt="">`).join("")}</div>` : ""}
    </article>`).join("");
}
async function runScout(path) {
  const body = { query: document.getElementById("query").value.trim(), kind: document.getElementById("kind").value, limit: 12 };
  const epoch = document.getElementById("epoch");
  if (epoch && epoch.value) body.epochs = [epoch.value];
  document.getElementById("status").textContent = "ищем…";
  const res = await fetch(path, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) });
  const data = await res.json();
  if (!res.ok) { document.getElementById("status").textContent = "не вышло"; return; }
  renderMarkers(data.results); renderCards(data.results);
  const labels = (data.filters && data.filters.epoch_labels) || [];
  document.getElementById("parsed").textContent = labels.length ? "эпоха: " + labels.join(", ") : "";
  document.getElementById("status").textContent = "нашли " + (data.results || []).length;
}
document.getElementById("analyze").addEventListener("click", () => {
  runScout(document.getElementById("kind").value === "film" ? "/api/film/locations" : "/api/scout");
});
const st = document.getElementById("studios");
if (st) st.addEventListener("click", () => runScout("/api/studios/search"));
document.getElementById("invest").addEventListener("click", () => runScout("/api/investments/analyze"));
