// Hotel Sky Lounge — interactions: header, nav, menu tabs/search/filter, lightbox, reveal.
(function () {
  "use strict";

  /* Header state */
  var header = document.querySelector(".header");
  var onScroll = function () {
    header.classList.toggle("scrolled", window.scrollY > 24);
  };
  window.addEventListener("scroll", onScroll, { passive: true });
  onScroll();

  /* Mobile nav */
  var burger = document.querySelector(".burger");
  var nav = document.querySelector(".nav");
  burger.addEventListener("click", function () {
    var open = nav.classList.toggle("open");
    burger.setAttribute("aria-expanded", open ? "true" : "false");
  });
  nav.querySelectorAll("a").forEach(function (a) {
    a.addEventListener("click", function () { nav.classList.remove("open"); });
  });

  /* Menu tabs */
  var tabs = Array.prototype.slice.call(document.querySelectorAll(".tab"));
  var panels = Array.prototype.slice.call(document.querySelectorAll(".menu-panel"));
  var resultsBox = document.getElementById("searchResults");
  var searchInput = document.getElementById("menuSearch");
  var vegToggle = document.getElementById("vegOnly");

  function showPanel(id) {
    tabs.forEach(function (t) { t.classList.toggle("active", t.dataset.target === id); });
    panels.forEach(function (p) { p.classList.toggle("active", p.id === id); });
    resultsBox.classList.remove("active");
  }
  tabs.forEach(function (t) {
    t.addEventListener("click", function () {
      searchInput.value = "";
      showPanel(t.dataset.target);
      applyVegFilter();
      t.scrollIntoView({ behavior: "smooth", inline: "center", block: "nearest" });
    });
  });

  /* Veg-only filter */
  function applyVegFilter() {
    var vegOnly = vegToggle.checked;
    document.querySelectorAll(".menu-item").forEach(function (item) {
      var isVeg = item.dataset.veg === "1";
      item.style.display = vegOnly && !isVeg ? "none" : "";
    });
    document.querySelectorAll(".rn-table tbody tr").forEach(function (row) {
      row.style.display = vegOnly && row.dataset.veg === "0" ? "none" : "";
    });
  }
  vegToggle.addEventListener("change", applyVegFilter);

  /* Search across all items */
  var allItems = Array.prototype.slice.call(document.querySelectorAll(".menu-item"));
  searchInput.addEventListener("input", function () {
    var q = searchInput.value.trim().toLowerCase();
    if (!q) {
      resultsBox.classList.remove("active");
      var activeTab = document.querySelector(".tab.active");
      if (activeTab) showPanel(activeTab.dataset.target);
      applyVegFilter();
      return;
    }
    panels.forEach(function (p) { p.classList.remove("active"); });
    tabs.forEach(function (t) { t.classList.remove("active"); });
    var grouped = {};
    var order = [];
    allItems.forEach(function (item) {
      var hay = (item.dataset.search || "").toLowerCase();
      if (hay.indexOf(q) === -1) return;
      if (vegToggle.checked && item.dataset.veg !== "1") return;
      var cat = item.dataset.category;
      if (!grouped[cat]) { grouped[cat] = []; order.push(cat); }
      grouped[cat].push(item);
    });
    var html = "";
    if (!order.length) {
      html = '<p class="no-results">Nothing on the menu matches "' +
        q.replace(/</g, "&lt;") + '". Try another dish.</p>';
    } else {
      order.forEach(function (cat) {
        html += '<h3 class="search-group-title">' + cat + "</h3><div class='menu-cols'>";
        grouped[cat].forEach(function (item) {
          var clone = item.cloneNode(true);
          clone.style.display = "";
          html += clone.outerHTML;
        });
        html += "</div>";
      });
    }
    resultsBox.innerHTML = html;
    resultsBox.classList.add("active");
  });

  /* Gallery lightbox */
  var lightbox = document.getElementById("lightbox");
  var lbImg = document.getElementById("lbImg");
  var lbCap = document.getElementById("lbCap");
  var galleryItems = Array.prototype.slice.call(document.querySelectorAll(".g-item"));
  var current = 0;
  function openLb(i) {
    current = i;
    var img = galleryItems[i].querySelector("img");
    lbImg.src = img.src;
    lbImg.alt = img.alt;
    lbCap.textContent = img.alt;
    lightbox.classList.add("open");
    document.body.style.overflow = "hidden";
  }
  function closeLb() {
    lightbox.classList.remove("open");
    document.body.style.overflow = "";
  }
  galleryItems.forEach(function (g, i) {
    g.addEventListener("click", function () { openLb(i); });
  });
  lightbox.addEventListener("click", function (e) {
    if (e.target === lightbox || e.target.classList.contains("lb-close")) closeLb();
  });
  document.addEventListener("keydown", function (e) {
    if (!lightbox.classList.contains("open")) return;
    if (e.key === "Escape") closeLb();
    if (e.key === "ArrowRight") openLb((current + 1) % galleryItems.length);
    if (e.key === "ArrowLeft") openLb((current - 1 + galleryItems.length) % galleryItems.length);
  });

  /* Reveal on scroll */
  var io = new IntersectionObserver(function (entries) {
    entries.forEach(function (entry) {
      if (entry.isIntersecting) {
        entry.target.classList.add("in");
        io.unobserve(entry.target);
      }
    });
  }, { threshold: 0.12 });
  document.querySelectorAll(".reveal").forEach(function (el) { io.observe(el); });
})();
