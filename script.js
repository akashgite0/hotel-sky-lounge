// Hotel Sky Lounge v3 — parallax engine, reveals, lightbox, nav.
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
    heroImg.style.transform = "scale(1.12) translate3d(0," + (y * 0.2) + "px,0)";
    heroInner.style.transform = "translate3d(0," + (-y * 0.16) + "px,0)";
    heroInner.style.opacity = String(Math.max(0, 1 - p * 1.25));
    // Generic parallax elements: drift gently relative to viewport centre, clamped.
    for (var i = 0; i < plxEls.length; i++) {
      var el = plxEls[i];
      var r = el.getBoundingClientRect();
      if (r.bottom < -100 || r.top > vh + 100) continue;
      var speed = parseFloat(el.getAttribute("data-plx")) || 0.06;
      var offset = (r.top + r.height / 2 - vh / 2) * -speed;
      offset = Math.max(-36, Math.min(36, offset)); // keep drift inside its section
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
      var dx = (e.clientX / window.innerWidth - 0.5) * 8;
      var dy = (e.clientY / window.innerHeight - 0.5) * 5;
      heroImg.style.translate = dx.toFixed(1) + "px " + dy.toFixed(1) + "px";
    });
  }

  /* ---------- Reveal on scroll ---------- */
  var revealEls = document.querySelectorAll(".reveal");
  if ("IntersectionObserver" in window) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add("in");
          io.unobserve(entry.target);
        }
      });
    }, { threshold: 0.12 });
    revealEls.forEach(function (el) { io.observe(el); });
  } else {
    // Very old webviews: never leave content hidden.
    revealEls.forEach(function (el) { el.classList.add("in"); });
  }

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

  window.__slReady = true;
})();
