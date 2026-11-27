// Trip map: route, ports, places, day selection, filters, deep links.
(function () {
  "use strict";

  var css = getComputedStyle(document.documentElement);
  function token(name) { return css.getPropertyValue(name).trim(); }
  function esc(s) {
    return String(s == null ? "" : s).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", "\"": "&quot;", "'": "&#39;" }[c];
    });
  }
  function el(id) { return document.getElementById(id); }

  var offlineBox = el("map-offline");
  var tilesFailing = false;
  function updateOffline() {
    offlineBox.hidden = navigator.onLine && !tilesFailing;
  }
  window.addEventListener("online", function () { tilesFailing = false; updateOffline(); });
  window.addEventListener("offline", updateOffline);

  // Day list collapse (phones).
  var sidebar = el("sidebar");
  var toggle = el("sidebar-toggle");
  toggle.addEventListener("click", function () {
    var collapsed = sidebar.classList.toggle("collapsed");
    toggle.textContent = collapsed ? "Show" : "Hide";
    toggle.setAttribute("aria-expanded", String(!collapsed));
    if (window.cruiseMap) setTimeout(function () { window.cruiseMap.invalidateSize(); }, 50);
  });

  if (typeof L === "undefined") {
    // Leaflet failed to load (should not happen once cached); keep the day list usable.
    offlineBox.hidden = false;
    return;
  }

  fetch("trip.json")
    .then(function (r) { if (!r.ok) throw new Error(r.status); return r.json(); })
    .then(init)
    .catch(function (err) {
      console.error("Map failed to load:", err);
      offlineBox.hidden = false;
    });

  function init(DATA) {
    var EXC = DATA.excursions;
    var DAYS = DATA.days;
    var CATS = {};
    DATA.categories.forEach(function (c) { CATS[c.key] = c; });
    var features = DATA.geojson.features;
    var routes = features.filter(function (f) { return f.properties.kind === "route"; });
    var ports = features.filter(function (f) { return f.properties.kind === "port"; });
    var places = features.filter(function (f) { return f.properties.kind === "place"; });
    function dayInfo(n) { return DAYS.find(function (d) { return d.day === n; }); }
    function catColor(key) { return token("--cat-" + (CATS[key] ? key : "other")) || "#666"; }

    var map = L.map("map", { zoomControl: true });
    window.cruiseMap = map;
    var tiles = L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
      maxZoom: 18,
      attribution: "&copy; <a href=\"https://www.openstreetmap.org/copyright\">OpenStreetMap</a> contributors"
    }).addTo(map);
    tiles.on("tileerror", function () {
      if (!navigator.onLine) { tilesFailing = true; updateOffline(); }
    });
    tiles.on("tileload", function () { if (tilesFailing) { tilesFailing = false; updateOffline(); } });
    updateOffline();

    // Keep pop-ups narrower than the map so they never hide under the controls on phones.
    function popupOpts() {
      var w = Math.max(200, Math.min(300, map.getSize().x - 80));
      return { maxWidth: w, minWidth: Math.min(220, w), autoPanPadding: [40, 40] };
    }

    var routeLayer = L.layerGroup().addTo(map);
    var portLayer = L.layerGroup().addTo(map);
    var placeLayer = L.layerGroup().addTo(map);
    var routeColor = token("--color-route");

    routes.forEach(function (f) {
      var line = L.polyline(f.geometry.coordinates.map(function (c) { return [c[1], c[0]]; }), {
        color: routeColor, weight: 3, opacity: 0.85, dashArray: "6 5"
      }).bindTooltip(esc(f.properties.name), { sticky: true });
      line.feature = f;
      routeLayer.addLayer(line);
    });

    function portPopup(p) {
      var rows = p.calls.map(function (c) {
        var t = [c.arrive && "Arrive " + c.arrive, c.depart && "Depart " + c.depart].filter(Boolean).join(", ");
        return "<tr><td><b>Day " + c.day + "</b></td><td>" + esc(c.date) + (t ? "<br>" + esc(t) : "") +
          (c.flags.length ? "<br><span class=\"meta\">" + esc(c.flags.join("; ")) + "</span>" : "") + "</td></tr>";
      }).join("");
      var links = p.calls.map(function (c) {
        return "<a href=\"day/" + c.day + "/\">Day " + c.day + " details</a>";
      }).join(" · ");
      return "<div class=\"pop\"><h3>" + esc(p.name) + "</h3><table>" + rows + "</table>" +
        "<div class=\"go\">" + links + "</div></div>";
    }

    ports.forEach(function (f) {
      var p = f.properties;
      var icon = L.divIcon({
        className: "", iconSize: null, iconAnchor: [13, 13],
        html: "<div class=\"port-marker\">" + esc(p.days.join(" / ")) + "</div>"
      });
      var m = L.marker([f.geometry.coordinates[1], f.geometry.coordinates[0]], {
        icon: icon, zIndexOffset: 1000, title: p.name, keyboard: true
      }).bindPopup(portPopup(p), popupOpts());
      m.feature = f;
      portLayer.addLayer(m);
    });

    // ---------- Filters ----------
    var allExc = Object.keys(EXC).map(function (k) { return EXC[k]; });
    var prices = allExc.map(function (e) { return e.price; }).filter(function (x) { return x != null; });
    var PRICE_MAX = prices.length ? Math.ceil(Math.max.apply(null, prices) / 10) * 10 : 0;
    var LEVEL_ORDER = ["Easy", "Moderate", "Strenuous"];
    var LEVELS = Array.from(new Set(allExc.map(function (e) { return e.activity_level; }).filter(Boolean)))
      .sort(function (a, b) { return (LEVEL_ORDER.indexOf(a) + 1 || 9) - (LEVEL_ORDER.indexOf(b) + 1 || 9); });
    var usedCats = DATA.categories.map(function (c) { return c.key; }).filter(function (k) {
      return places.some(function (f) { return f.properties.category === k; });
    });
    var anyWheelchair = allExc.some(function (e) { return e.wheelchair_accessible === "Yes"; });

    var state;
    function resetState() {
      state = {
        day: state ? state.day : null, search: "", categories: new Set(usedCats), passby: true,
        maxPrice: PRICE_MAX, levels: new Set(LEVELS), wheelchair: false, noexc: true
      };
    }
    resetState();

    function excursionPasses(e) {
      if (!e) return false;
      if (e.price != null && e.price > state.maxPrice) return false;
      if (e.activity_level && !state.levels.has(e.activity_level)) return false;
      if (state.wheelchair && e.wheelchair_accessible !== "Yes") return false;
      return true;
    }

    function placeMatches(f) {
      var p = f.properties;
      if (state.day != null && p.day !== state.day) return false;
      var cat = CATS[p.category] ? p.category : "other";
      if (!state.categories.has(cat)) return false;
      if (!state.passby && p.visit === "passby") return false;
      var excs = p.excursion_ids.map(function (id) { return EXC[id]; }).filter(Boolean);
      if (excs.length === 0) { if (!state.noexc) return false; }
      else if (!excs.some(excursionPasses)) return false;
      if (state.search) {
        var hay = [p.name, p.note, p.category].concat(excs.map(function (e) { return e.title; }))
          .join(" ").toLowerCase();
        if (hay.indexOf(state.search) === -1) return false;
      }
      return true;
    }

    function placePopup(p) {
      var cat = CATS[p.category] || CATS.other;
      var d = dayInfo(p.day);
      var stop = (d.stops.find(function (s) { return s.port_id === p.port_id; }) || d.stops[0]).name.split(",")[0];
      var excs = p.excursion_ids.map(function (id) { return EXC[id]; }).filter(Boolean);
      var html = "<div class=\"pop\"><h3>" + esc(p.name) + "</h3><div class=\"sub\">" +
        esc(cat.one) + " · Day " + p.day + ", " + esc(stop) +
        (p.visit === "passby" ? " · seen in passing" : "") + "</div>";
      if (p.note) html += "<div>" + esc(p.note) + "</div>";
      if (excs.length) {
        html += "<ul>" + excs.map(function (e) {
          var meta = [e.price != null ? "$" + e.price : "", e.duration, e.activity_level].filter(Boolean).join(" · ");
          return "<li" + (excursionPasses(e) ? "" : " style=\"opacity:.55\"") + "><a href=\"day/" + e.day +
            "/#exc-" + esc(e.id) + "\">" + esc(e.title) + "</a><div class=\"meta\">" + esc(meta) + "</div></li>";
        }).join("") + "</ul>";
      }
      html += "<div class=\"go\"><a href=\"day/" + p.day + "/\">Day " + p.day + " details</a></div>";
      if (p.location_check !== "verified") html += "<div class=\"warn\">Location is approximate</div>";
      return html + "</div>";
    }

    var markers = places.map(function (f) {
      var p = f.properties;
      var m = L.circleMarker([f.geometry.coordinates[1], f.geometry.coordinates[0]], {
        radius: p.visit === "passby" ? 4.5 : 6.5,
        color: token("--color-marker-stroke"), weight: 1.5,
        fillColor: catColor(p.category), fillOpacity: p.visit === "passby" ? 0.65 : 0.95
      }).bindTooltip(esc(p.name), { direction: "top", offset: [0, -4] })
        .bindPopup(function () { return placePopup(p); }, popupOpts());
      m.feature = f;
      return m;
    });
    var markerById = {};
    markers.forEach(function (m) { markerById[m.feature.properties.id] = m; });

    function legActive(p) {
      return state.day == null || p.from_day === state.day || p.to_day === state.day ||
        (state.day > p.from_day && state.day < p.to_day);
    }

    function render(fit) {
      placeLayer.clearLayers();
      var shown = markers.filter(function (m) { return placeMatches(m.feature); });
      shown.forEach(function (m) { placeLayer.addLayer(m); });
      routeLayer.eachLayer(function (l) {
        var on = legActive(l.feature.properties);
        l.setStyle({ opacity: on ? 0.9 : 0.25, weight: on ? 3.5 : 2.5 });
      });
      el("match-count").textContent = shown.length + " of " + markers.length + " places" +
        (state.day != null ? " · day " + state.day : "");
      document.querySelectorAll(".day-row").forEach(function (row) {
        var sel = row.dataset.day === "all" ? state.day == null : Number(row.dataset.day) === state.day;
        row.querySelector(".day-select").setAttribute("aria-pressed", String(sel));
      });
      if (fit) fitView(shown);
    }

    function fitView(shown) {
      var b = L.latLngBounds([]);
      if (state.day == null) {
        routeLayer.eachLayer(function (l) { b.extend(l.getBounds()); });
      } else {
        shown.forEach(function (m) { b.extend(m.getLatLng()); });
        portLayer.eachLayer(function (m) {
          if (m.feature.properties.days.indexOf(state.day) !== -1) b.extend(m.getLatLng());
        });
        if (!b.isValid()) {
          routeLayer.eachLayer(function (l) {
            var p = l.feature.properties;
            if (state.day > p.from_day && state.day < p.to_day) b.extend(l.getBounds());
          });
        }
      }
      if (b.isValid()) map.fitBounds(b, { padding: [30, 30], maxZoom: 12 });
    }

    // ---------- Sidebar wiring ----------
    el("day-list").addEventListener("click", function (ev) {
      var btn = ev.target.closest(".day-select");
      if (!btn) return;
      var v = btn.parentElement.dataset.day;
      state.day = v === "all" ? null : Number(v);
      render(true);
    });

    function chip(container, label, color, onChange) {
      var lab = document.createElement("label");
      lab.className = "chip";
      lab.innerHTML = "<input type=\"checkbox\" checked>" +
        (color ? "<span class=\"dot\" style=\"background:" + color + "\"></span>" : "") + esc(label);
      lab.querySelector("input").addEventListener("change", function (ev) {
        lab.classList.toggle("off", !ev.target.checked);
        onChange(ev.target.checked);
        render(false);
      });
      container.appendChild(lab);
    }
    usedCats.forEach(function (k) {
      chip(el("category-chips"), CATS[k].label, catColor(k), function (on) {
        if (on) state.categories.add(k); else state.categories.delete(k);
      });
    });
    if (LEVELS.length) {
      LEVELS.forEach(function (l) {
        chip(el("level-chips"), l, null, function (on) {
          if (on) state.levels.add(l); else state.levels.delete(l);
        });
      });
    } else {
      el("level-block").hidden = true;
    }
    if (!anyWheelchair) el("wheelchair-block").hidden = true;

    var price = el("f-price");
    function priceText() { el("price-label").textContent = state.maxPrice >= PRICE_MAX ? "Any" : "$" + state.maxPrice; }
    if (PRICE_MAX > 0) {
      price.max = PRICE_MAX; price.value = PRICE_MAX; priceText();
      price.addEventListener("input", function () { state.maxPrice = Number(price.value); priceText(); render(false); });
    } else {
      el("price-block").hidden = true;
    }

    el("search").addEventListener("input", function (ev) {
      state.search = ev.target.value.trim().toLowerCase();
      render(false);
    });
    [["f-passby", "passby"], ["f-wheelchair", "wheelchair"], ["f-noexc", "noexc"]].forEach(function (pair) {
      el(pair[0]).addEventListener("change", function (ev) { state[pair[1]] = ev.target.checked; render(false); });
    });
    el("f-reset").addEventListener("click", function () {
      resetState();
      el("search").value = "";
      price.value = PRICE_MAX; priceText();
      document.querySelectorAll(".filters input[type=checkbox]").forEach(function (c) {
        c.checked = c.id !== "f-wheelchair";
      });
      document.querySelectorAll(".filters .chip").forEach(function (c) { c.classList.remove("off"); });
      render(false);
    });

    // ---------- Deep link: ?place=<id> ----------
    var placeId = new URLSearchParams(location.search).get("place");
    var target = placeId && markerById[placeId];
    if (target) {
      state.day = target.feature.properties.day;
      render(false);
      map.setView(target.getLatLng(), 12);
      target.openPopup();
    } else {
      render(true);
    }
  }
})();
