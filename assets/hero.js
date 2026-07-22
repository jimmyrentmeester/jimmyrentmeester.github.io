/* Cover-animatie + binnenschuiven bij scrollen.
 *
 * Alles hierin is decoratie. Zonder JavaScript blijft de pagina compleet:
 * de cover is dan een egaal donker paneel en niets is verborgen. Daarom
 * zet dit script zelf de .js-klasse — de CSS verbergt pas iets als het
 * script draait en het dus ook weer zichtbaar kan maken.
 *
 * Het veld is een puntenraster waar rimpelingen doorheen lopen: één per
 * muisbeweging, en af en toe eentje uit zichzelf. De kleuren zijn die van
 * de vier apps, zodat de kop dezelfde taal spreekt als het werklog.
 */
(function () {
  "use strict";

  var root = document.documentElement;
  root.classList.add("js");

  var reduce = matchMedia("(prefers-reduced-motion: reduce)");

  /* ── binnenschuiven ───────────────────────────────────────────
   * Volgorde is hier het hele punt: we verbergen pas iets nadat we
   * zeker weten dat we het ook weer kunnen tonen. Wat al in beeld
   * staat wordt nooit verborgen, en een failsafe-timer haalt alles
   * tevoorschijn mocht de observer nooit vuren.
   * ─────────────────────────────────────────────────────────────── */
  var revealables = [].slice.call(document.querySelectorAll(".reveal"));
  function show(el) { el.classList.remove("pre"); el.classList.add("in"); }
  function showAll() { revealables.forEach(show); }

  if (!reduce.matches && "IntersectionObserver" in window) {
    var hidden = revealables.filter(function (el) {
      return el.getBoundingClientRect().top > innerHeight * 0.92;
    });
    hidden.forEach(function (el) { el.classList.add("pre"); });
    revealables.forEach(function (el) { if (hidden.indexOf(el) === -1) show(el); });

    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) { show(e.target); io.unobserve(e.target); }
      });
    }, { rootMargin: "0px 0px -6% 0px", threshold: 0.04 });
    hidden.forEach(function (el) { io.observe(el); });

    // Vangnet: gaat er iets mis, dan staat er na 10 seconden hoe dan ook
    // een leesbare pagina in plaats van lege ruimte.
    setTimeout(showAll, 10000);
  }

  /* ── het veld ───────────────────────────────────────────────── */
  var canvas = document.getElementById("field");
  if (!canvas || reduce.matches) return;

  var ctx = canvas.getContext("2d", { alpha: true });
  if (!ctx) return;

  var COLORS = [
    [ 51, 242, 255],   // GRID_BREAKER
    [122, 110, 243],   // BabyBeam
    [201, 166,  89],   // WristVault
    [143, 179, 217]    // Stillwater
  ];
  var SPACING = 30, DPR = Math.min(window.devicePixelRatio || 1, 2);
  var w = 0, h = 0, dots = [], ripples = [], raf = null, running = false;
  var colorIndex = 0, lastSpawn = 0, lastPointer = { x: -1, y: -1 };

  function build() {
    var rect = canvas.getBoundingClientRect();
    w = Math.max(1, Math.round(rect.width));
    h = Math.max(1, Math.round(rect.height));
    canvas.width = Math.round(w * DPR);
    canvas.height = Math.round(h * DPR);
    ctx.setTransform(DPR, 0, 0, DPR, 0, 0);

    dots = [];
    for (var y = SPACING / 2; y < h; y += SPACING) {
      for (var x = SPACING / 2; x < w; x += SPACING) {
        // Naar onderen toe uitdunnen, zodat de tekst bovenin rustig blijft.
        dots.push({ x: x, y: y, base: 0.05 + 0.11 * (y / h) });
      }
    }
  }

  function addRipple(x, y) {
    if (ripples.length > 7) ripples.shift();
    ripples.push({ x: x, y: y, t: 0, c: COLORS[colorIndex % COLORS.length] });
    colorIndex++;
  }

  var LIFE = 2400;          // ms dat een rimpeling leeft
  var SPEED = 0.19;         // px per ms dat de ring uitzet
  var BAND = 46;            // dikte van de ring

  function frame(now) {
    if (!running) return;
    ctx.clearRect(0, 0, w, h);

    // Vanzelf een rimpeling, zodat het veld ook zonder muis leeft.
    if (now - lastSpawn > 2600) {
      addRipple(Math.random() * w, Math.random() * h * 0.85);
      lastSpawn = now;
    }

    for (var r = ripples.length - 1; r >= 0; r--) {
      ripples[r].t += 16.7;
      if (ripples[r].t > LIFE) ripples.splice(r, 1);
    }

    for (var i = 0; i < dots.length; i++) {
      var d = dots[i], a = d.base, cr = 242, cg = 233, cb = 216, dx = 0, dy = 0;

      for (var j = 0; j < ripples.length; j++) {
        var rp = ripples[j];
        var radius = rp.t * SPEED;
        var vx = d.x - rp.x, vy = d.y - rp.y;
        var dist = Math.sqrt(vx * vx + vy * vy);
        var off = Math.abs(dist - radius);
        if (off > BAND) continue;

        var fade = 1 - rp.t / LIFE;                 // rimpeling dooft uit
        var edge = Math.cos((off / BAND) * Math.PI * 0.5);
        var power = edge * edge * fade;
        if (power <= 0.001) continue;

        a += power * 0.75;
        cr = rp.c[0]; cg = rp.c[1]; cb = rp.c[2];
        if (dist > 0.001) {                         // puntjes iets meeduwen
          dx += (vx / dist) * power * 3.5;
          dy += (vy / dist) * power * 3.5;
        }
      }

      if (a <= 0.012) continue;
      if (a > 0.85) a = 0.85;
      ctx.fillStyle = "rgba(" + cr + "," + cg + "," + cb + "," + a.toFixed(3) + ")";
      var s = a > 0.3 ? 2.1 : 1.5;
      ctx.fillRect(d.x + dx - s / 2, d.y + dy - s / 2, s, s);
    }

    raf = requestAnimationFrame(frame);
  }

  function start() {
    if (running) return;
    running = true;
    lastSpawn = performance.now();
    raf = requestAnimationFrame(frame);
  }
  function stop() {
    running = false;
    if (raf) cancelAnimationFrame(raf);
    raf = null;
  }

  /* Alleen tekenen zolang de cover in beeld is en het tabblad actief is. */
  var cover = canvas.parentElement;
  if ("IntersectionObserver" in window) {
    new IntersectionObserver(function (e) {
      e[0].isIntersecting ? start() : stop();
    }, { threshold: 0.01 }).observe(cover);
  } else {
    start();
  }
  document.addEventListener("visibilitychange", function () {
    document.hidden ? stop() : start();
  });

  cover.addEventListener("pointermove", function (e) {
    var rect = canvas.getBoundingClientRect();
    var x = e.clientX - rect.left, y = e.clientY - rect.top;
    var dx = x - lastPointer.x, dy = y - lastPointer.y;
    if (dx * dx + dy * dy < 2200) return;      // niet bij elk pixeltje
    lastPointer.x = x; lastPointer.y = y;
    addRipple(x, y);
  }, { passive: true });

  cover.addEventListener("pointerdown", function (e) {
    var rect = canvas.getBoundingClientRect();
    addRipple(e.clientX - rect.left, e.clientY - rect.top);
  }, { passive: true });

  var resizeTimer;
  addEventListener("resize", function () {
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(build, 160);
  });

  // Zet de voorkeur live om als iemand hem tijdens het bezoek wijzigt.
  reduce.addEventListener("change", function () {
    if (reduce.matches) { stop(); ctx.clearRect(0, 0, w, h); showAll(); }
    else start();
  });

  window.addEventListener("pageshow", showAll);   // terug via de back-knop

  build();
})();
