// Hotel Sky Lounge v2 — parallax engine, menu, lightbox, nav.
(function () {
  "use strict";

  var reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var fine = window.matchMedia("(pointer: fine)").matches;

  /* ---------- Header state + mobile nav ---------- */
  var header = document.querySelector(".header");
  var burger = document.querySelector(".burger");
  var mobileNav = document.querySelector(".mobile-nav");
  burger.addEventListener("click", function () {
    var open = mobileNav.classList.toggle("open");
    burger.setAttribute("aria-expanded", open ? "true" : "false");
  });
  mobileNav.querySelectorAll("a").forEach(function (a) {
    a.addEventListener("click", function () { mobileNav.classList.remove("open"); });
  });

  /* ---------- Parallax engine ---------- */
  var hero = document.querySelector(".hero");
  var heroImg = hero.querySelector("img.bg");
  var heroInner = document.querySelector(".hero-inner");
  var plxEls = Array.prototype.slice.call(document.querySelectorAll("[data-plx]"));
  var bands = Array.prototype.slice.call(document.querySelectorAll(".band .band-img"));
  var vh = window.innerHeight;
  var ticking = false;

  function onScroll() {
    var y = window.scrollY || window.pageYOffset;
    header.classList.toggle("solid", y > vh * 0.72);
    if (reduceMotion) return;
    // Hero: image drifts down slowly, content rises and fades as the page covers it.
    var p = Math.min(y / vh, 1);
    heroImg.style.transform = "scale(1.12) translate3d(0," + (y * 0.22) + "px,0)";
    heroInner.style.transform = "translate3d(0," + (-y * 0.18) + "px,0)";
    heroInner.style.opacity = String(Math.max(0, 1 - p * 1.25));
    // Generic parallax elements: move relative to viewport centre.
    for (var i = 0; i < plxEls.length; i++) {
      var el = plxEls[i];
      var r = el.getBoundingClientRect();
      if (r.bottom < -100 || r.top > vh + 100) continue;
      var speed = parseFloat(el.getAttribute("data-plx")) || 0.08;
      var offset = (r.top + r.height / 2 - vh / 2) * -speed;
      offset = Math.max(-40, Math.min(40, offset)); // keep drift inside its section
      el.style.transform = "translate3d(0," + offset.toFixed(1) + "px,0)";
    }
    // Full-bleed bands: image taller than its frame, slides within it.
    for (var j = 0; j < bands.length; j++) {
      var band = bands[j];
      var br = band.parentElement.getBoundingClientRect();
      if (br.bottom < -100 || br.top > vh + 100) continue;
      var progress = (br.top + br.height / 2 - vh / 2) / (vh / 2 + br.height / 2);
      var range = br.height * 0.18;
      band.style.transform = "translate3d(0," + (-progress * range).toFixed(1) + "px,0)";
    }
    ticking = false;
  }
  function requestTick() {
    if (!ticking) { ticking = true; requestAnimationFrame(onScroll); }
  }
  window.addEventListener("scroll", requestTick, { passive: true });
  window.addEventListener("resize", function () { vh = window.innerHeight; requestTick(); });
  onScroll();

  /* Subtle pointer drift on the hero for desktop (very gentle). */
  if (fine && !reduceMotion) {
    hero.addEventListener("mousemove", function (e) {
      var dx = (e.clientX / window.innerWidth - 0.5) * 10;
      var dy = (e.clientY / window.innerHeight - 0.5) * 6;
      heroImg.style.translate = dx.toFixed(1) + "px " + dy.toFixed(1) + "px";
    });
  }

  /* ---------- Reveal on scroll ---------- */
  var io = new IntersectionObserver(function (entries) {
    entries.forEach(function (entry) {
      if (entry.isIntersecting) {
        entry.target.classList.add("in");
        io.unobserve(entry.target);
      }
    });
  }, { threshold: 0.12 });
  document.querySelectorAll(".reveal").forEach(function (el) { io.observe(el); });

  /* ---------- Menu tabs / search / veg filter ---------- */
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
    });
  });

  function applyVegFilter() {
    var vegOnly = vegToggle.checked;
    document.querySelectorAll(".menu-item").forEach(function (item) {
      item.style.display = vegOnly && item.dataset.veg !== "1" ? "none" : "";
    });
  }
  vegToggle.addEventListener("change", applyVegFilter);

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
      if ((item.dataset.search || "").toLowerCase().indexOf(q) === -1) return;
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

  /* ---------- Gallery lightbox ---------- */
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
})();
