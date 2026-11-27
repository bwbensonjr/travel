// Open and scroll to the excursion named in the URL fragment (#exc-<id>),
// and keep the fragment in sync when an excursion is opened.
(function () {
  "use strict";

  function openTarget() {
    var id = decodeURIComponent(location.hash.slice(1));
    if (id.indexOf("exc-") !== 0) return;
    var el = document.getElementById(id);
    if (!el || el.tagName !== "DETAILS") return;
    document.querySelectorAll(".exc.target").forEach(function (x) { x.classList.remove("target"); });
    el.open = true;
    el.classList.add("target");
    el.scrollIntoView({ block: "start" });
    var summary = el.querySelector("summary");
    if (summary) summary.focus({ preventScroll: true });
  }

  document.querySelectorAll("details.exc").forEach(function (el) {
    el.addEventListener("toggle", function () {
      if (el.open && history.replaceState) {
        history.replaceState(null, "", "#" + el.id);
      }
    });
  });

  window.addEventListener("hashchange", openTarget);
  openTarget();
})();
