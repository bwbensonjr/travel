// Registers the service worker and shows offline readiness in the header.
(function () {
  "use strict";
  var status = document.getElementById("offline-status");
  if (!status || !("serviceWorker" in navigator) || !window.caches) return;

  var root = document.body.dataset.root || "";
  var pageVersion = document.body.dataset.build;

  function show(text, cls) {
    status.textContent = text;
    status.className = "status" + (cls ? " " + cls : "");
  }

  function askStatus(worker) {
    if (!worker) return;
    var ch = new MessageChannel();
    ch.port1.onmessage = function (ev) {
      var s = ev.data || {};
      if (s.complete && s.version === pageVersion) show("Available offline", "ok");
      else if (s.complete) showUpdate();
      else show("");
    };
    worker.postMessage({ type: "status" }, [ch.port2]);
  }

  function showUpdate() {
    status.textContent = "";
    var b = document.createElement("button");
    b.type = "button";
    b.className = "btn";
    b.textContent = "Updated, reload";
    b.addEventListener("click", function () { location.reload(); });
    status.appendChild(b);
    status.className = "status";
  }

  navigator.serviceWorker.addEventListener("message", function (ev) {
    if (!ev.data || ev.data.type !== "activated") return;
    if (ev.data.version !== pageVersion) showUpdate();
    else navigator.serviceWorker.ready.then(function (reg) { askStatus(reg.active); });
  });

  navigator.serviceWorker.register(root + "sw.js", { scope: root || "./" })
    .then(function (reg) {
      var worker = reg.active;
      if (worker) askStatus(worker);
      reg.addEventListener("updatefound", function () { show("Saving for offline…"); });
    })
    .catch(function () { show(""); });
})();
