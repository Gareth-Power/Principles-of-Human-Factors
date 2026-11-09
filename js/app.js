/* Principles of Human Factors - field guide.
   A small wiki: an index, one page per topic, a Toolkits page, a glossary
   and search. The words all come from js/content.js (generated from the
   Word document). Nothing is tracked or stored. */
(function () {
  "use strict";
  var G = window.GUIDE;
  var $ = function (s, el) { return (el || document).querySelector(s); };
  var esc = function (s) { return String(s).replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; }); };

  // Toolkits is built here from every TOOL in the guide; it sits in Reference.
  var TOOLKITS = { id: "toolkits", label: "Toolkits", group: "reference", title: "Toolkits" };
  var pages = G.pages.slice();
  var gi = pages.findIndex(function (p) { return p.id === "summary"; });
  pages.splice(gi + 1, 0, TOOLKITS);
  var byId = {}; pages.forEach(function (p) { byId[p.id] = p; });
  var groupLabel = {}; G.groups.forEach(function (g) { groupLabel[g.id] = g.label; });

  /* ---------- index ---------- */
  var side = $("#side");
  function icon(name) {
    var d = {
      tool: '<path d="M14.5 3.5a3.5 3.5 0 0 0-4.6 4.4L3.6 14.2a1.4 1.4 0 0 0 2 2l6.3-6.3a3.5 3.5 0 0 0 4.4-4.6l-2 2-1.8-.3-.3-1.8z"/>',
      book: '<path d="M4 4.5A1.5 1.5 0 0 1 5.5 3H16v12H5.5A1.5 1.5 0 0 0 4 16.5zM4 16.5A1.5 1.5 0 0 0 5.5 18H16"/>'
    }[name];
    return '<svg viewBox="0 0 20 20" aria-hidden="true">' + d + "</svg>";
  }
  side.innerHTML =
    '<div class="ix-links"><a href="#/toolkits" data-page="toolkits">' + icon("tool") + 'Toolkits</a>' +
    '<a href="#/glossary" data-page="glossary">' + icon("book") + "Glossary</a></div>" +
    G.groups.map(function (g) {
      var ps = pages.filter(function (p) { return p.group === g.id; });
      return '<section class="ix-group g-' + g.id + '"><h2 class="ix-head">' + esc(g.label) + "</h2><ul>" +
        ps.map(function (p) { return '<li><a href="#/' + p.id + '" data-page="' + p.id + '">' + esc(p.label) + "</a></li>"; }).join("") +
        "</ul></section>";
    }).join("") +
    '<p class="ix-foot">' + (byId.welcome.html.match(/<p class="subtitle"[^>]*>(.*?)<\/p>/) || [, ""])[1] + "</p>";

  /* ---------- pages ---------- */
  var pageEl = $("#page"), pager = $("#pager");

  function crumb(p) { return '<div class="crumb g-' + p.group + '">' + esc(groupLabel[p.group]) + "</div>"; }

  function renderWelcome(p) {
    // the cover: title, subtitle and picture side by side, then the rest
    var tmp = document.createElement("div"); tmp.innerHTML = p.html;
    var sub = tmp.querySelector(".subtitle"), fig = tmp.querySelector(".fig");
    if (sub) sub.remove(); if (fig) fig.remove();
    var groups = G.groups.filter(function (g) { return g.id !== "start"; });
    return '<div class="home-hero"><div><h1>' + p.title + "</h1>" + (sub ? sub.outerHTML : "") +
      '<div class="home-cta"><a class="sbtn primary" href="#/how-to-use">' + esc(byId["how-to-use"].label) +
      '</a><a class="sbtn" href="#/toolkits">Toolkits</a><a class="sbtn" href="#/glossary">Glossary</a></div></div>' +
      (fig ? fig.outerHTML : "") + "</div>" +
      tmp.innerHTML +
      '<h2 class="home-sec-title" style="margin-top:40px;border:0;padding:0">Topics</h2>' +
      groups.map(function (g) {
        return '<h3 class="tiles-head g-' + g.id + '">' + esc(g.label) + '</h3><div class="tiles">' + pages.filter(function (x) { return x.group === g.id; }).map(function (x) {
          return '<a class="tile g-' + g.id + '" href="#/' + x.id + '"><b>' + esc(x.label) + "</b></a>";
        }).join("") + "</div>";
      }).join("");
  }

  function renderToolkits() {
    var intro = (G.search.find(function (s) { return /^Toolkits - /.test(s.x); }) || {}).x || "";
    return crumb(TOOLKITS) + "<h1>Toolkits</h1>" +
      (intro ? '<p class="lead">' + esc(intro) + "</p>" : "") +
      '<div class="chips">' + G.tools.map(function (t, i) {
        return '<a class="chip" href="#/toolkits/tk' + i + '">' + esc(t.title) + "</a>";
      }).join("") + "</div>" +
      G.tools.map(function (t, i) {
        return '<section class="tk" id="tk' + i + '"><div class="tk-from"><span></span><a href="#/' + t.page + "/" + t.id + '">' +
          esc(byId[t.page].label) + " &rarr;</a></div>" + t.html.replace(/ id="b\d+"/g, "") + "</section>";
      }).join("");
  }

  function renderGlossary(p) {
    return crumb(p) + "<h1>" + p.title + "</h1>" +
      '<input class="gl-filter" id="gl-filter" type="search" placeholder="Filter the glossary" aria-label="Filter the glossary">' +
      p.html + '<p class="gl-none" id="gl-none" hidden>No glossary entries match.</p>';
  }

  function show(id, anchor) {
    var p = byId[id] || byId.welcome;
    var h;
    if (p.id === "welcome") h = renderWelcome(p);
    else if (p.id === "toolkits") h = renderToolkits();
    else if (p.id === "glossary") h = renderGlossary(p);
    else h = crumb(p) + "<h1>" + p.title + "</h1>" + p.html;
    pageEl.innerHTML = h;
    pageEl.className = "page page-" + p.id;
    document.title = (p.id === "welcome" ? "" : p.label + " - ") + "Principles of Human Factors";

    var i = pages.indexOf(p), prev = pages[i - 1], next = pages[i + 1];
    pager.innerHTML =
      (prev ? '<a class="prev" href="#/' + prev.id + '"><small>&larr; Previous</small><b>' + esc(prev.label) + "</b></a>" : "") +
      (next ? '<a class="next" href="#/' + next.id + '"><small>Next &rarr;</small><b>' + esc(next.label) + "</b></a>" : "");

    side.querySelectorAll("a[data-page]").forEach(function (a) {
      if (a.dataset.page === p.id) a.setAttribute("aria-current", "page"); else a.removeAttribute("aria-current");
    });
    var cur = side.querySelector('.ix-group a[aria-current]');
    if (cur) { var r = cur.getBoundingClientRect(), sr = side.getBoundingClientRect();
      if (r.top < sr.top || r.bottom > sr.bottom) cur.scrollIntoView({ block: "center" }); }

    if (p.id === "glossary") wireGlossary();
    closeMenu();

    var target = anchor && document.getElementById(anchor);
    if (target) {
      target.scrollIntoView({ block: "start" });
      target.classList.remove("flash"); void target.offsetWidth; target.classList.add("flash");
    } else {
      window.scrollTo(0, 0);
      $("#main").focus({ preventScroll: true });
    }
  }

  function route() {
    var m = location.hash.replace(/^#\/?/, "").split("/");
    show(decodeURIComponent(m[0] || "welcome"), m[1] && decodeURIComponent(m[1]));
  }
  window.addEventListener("hashchange", route);

  /* ---------- glossary filter ---------- */
  function wireGlossary() {
    var f = $("#gl-filter");
    f.addEventListener("input", function () {
      var q = norm(f.value.trim()), any = false;
      pageEl.querySelectorAll(".gl-row").forEach(function (row) {
        var hit = !q || norm(row.textContent).indexOf(q) >= 0;
        row.hidden = !hit; any = any || hit;
      });
      $("#gl-none").hidden = any;
    });
  }

  /* ---------- images ---------- */
  var viewer = $("#viewer"), lastFocus = null;
  pageEl.addEventListener("click", function (e) {
    var z = e.target.closest(".zoom");
    if (!z) return;
    var img = z.querySelector("img");
    $("#viewer-img").src = img.src; $("#viewer-img").alt = img.alt;
    open(viewer);
  });

  /* ---------- pop-ups ---------- */
  function open(el) { lastFocus = document.activeElement; el.hidden = false; document.body.style.overflow = "hidden";
    (el.querySelector("input") || el.querySelector("[data-close]")).focus(); }
  function close(el) { el.hidden = true; document.body.style.overflow = ""; if (lastFocus) lastFocus.focus(); }
  [viewer, $("#search")].forEach(function (el) {
    el.addEventListener("click", function (e) { if (e.target === el || e.target.closest("[data-close]")) close(el); });
  });

  /* ---------- search ---------- */
  var search = $("#search"), q = $("#q"), results = $("#results"), sel = -1;
  function norm(s) { return s.toLowerCase().normalize("NFD").replace(/[̀-ͯ]/g, "").replace(/[‘’]/g, "'").replace(/[“”]/g, '"'); }
  var INDEX = G.search.map(function (s) { return Object.assign({}, s, { nt: norm(s.t), nx: norm(s.x) }); });
  INDEX.push({ p: "toolkits", b: "", k: "page", t: "Toolkits", x: "Toolkits", nt: "toolkits", nx: "toolkits" });
  var KIND = { page: "Topic", h: "Topic", text: "Topic", tool: "Tool", case: "Case", note: "Note", glossary: "Glossary" };
  var SECTIONS = [["page", "Topics"], ["tool", "Tools"], ["glossary", "Glossary"], ["case", "Cases and notes"], ["text", "In the text"]];

  function snippet(text, words) {
    var n = norm(text), at = -1;
    words.forEach(function (w) { var i = n.indexOf(w); if (i >= 0 && (at < 0 || i < at)) at = i; });
    var start = Math.max(0, at - 50), s = (start ? "…" : "") + text.slice(start, start + 180) + (start + 180 < text.length ? "…" : "");
    return mark(s, words);
  }
  function mark(text, words) {
    var h = esc(text);
    words.forEach(function (w) {
      if (w.length < 2) return;
      var re = new RegExp("(" + w.replace(/[.*+?^${}()|[\]\\]/g, "\\$&") + ")", "gi");
      h = h.replace(/(^|>)([^<]*)/g, function (_, a, b) { return a + b.replace(re, "<mark>$1</mark>"); });
    });
    return h;
  }

  function runSearch() {
    var raw = q.value.trim(), words = norm(raw).split(/\s+/).filter(Boolean);
    sel = -1;
    if (!words.length) {
      results.innerHTML = '<div class="r-hint"><p>Try a word, for example</p><div class="chips">' +
        ["fatigue", "checklist", "bias", "startle", "handover", "authority gradient"].map(function (w) {
          return '<button class="chip" type="button" data-try="' + w + '">' + w + "</button>"; }).join("") + "</div></div>";
      return;
    }
    var hits = INDEX.map(function (s) {
      var all = s.nt + " " + s.nx;
      if (!words.every(function (w) { return all.indexOf(w) >= 0; })) return null;
      var score = 0;
      words.forEach(function (w) { if (s.nt.indexOf(w) >= 0) score += 6; if (new RegExp("\\b" + w).test(all)) score += 2; });
      if (s.k === "page") score += 10; if (s.k === "h") score += 5; if (s.k === "tool") score += 4; if (s.k === "glossary") score += 3;
      return { s: s, score: score };
    }).filter(Boolean).sort(function (a, b) { return b.score - a.score; });

    var seen = {}, html = "", n = 0;
    SECTIONS.forEach(function (sec) {
      var list = hits.filter(function (h) {
        var k = h.s.k === "h" ? "page" : h.s.k === "note" ? "case" : h.s.k;
        return k === sec[0];
      }).filter(function (h) { var key = h.s.p + h.s.b; if (seen[key]) return false; seen[key] = 1; return true; }).slice(0, sec[0] === "text" ? 12 : 8);
      if (!list.length) return;
      html += '<div class="r-sec">' + sec[1] + "</div>";
      list.forEach(function (h) {
        var s = h.s, pg = byId[s.p];
        var title = s.k === "page" ? s.t : s.k === "h" ? s.x : s.k === "text" ? s.t : s.t;
        var snip = s.k === "page" ? "" : s.k === "h" ? "" : snippet(s.x, words);
        html += '<button class="r-item" type="button" role="option" aria-selected="false" data-go="#/' + s.p + (s.b ? "/" + s.b : "") + '">' +
          '<div class="r-top"><span class="r-kind k-' + (s.k === "page" || s.k === "h" || s.k === "text" ? "topic" : s.k) + '">' + KIND[s.k] + "</span>" +
          "<span>" + mark(title, words) + "</span>" + (pg && s.k !== "page" ? '<span class="r-page">' + esc(pg.label) + "</span>" : "") + "</div>" +
          (snip ? '<div class="r-snip">' + snip + "</div>" : "") + "</button>";
        n++;
      });
    });
    results.innerHTML = n ? html : '<div class="r-empty">Nothing matches “' + esc(raw) + '”.</div>';
    if (n) select(0);
  }
  function items() { return Array.prototype.slice.call(results.querySelectorAll(".r-item")); }
  function select(i) {
    var it = items(); if (!it.length) return;
    sel = (i + it.length) % it.length;
    it.forEach(function (el, k) { el.setAttribute("aria-selected", k === sel ? "true" : "false"); });
    it[sel].scrollIntoView({ block: "nearest" });
  }
  function go(href) { close(search); lastFocus = null; if (location.hash === href) route(); else location.hash = href; }

  q.addEventListener("input", runSearch);
  q.addEventListener("keydown", function (e) {
    if (e.key === "ArrowDown") { e.preventDefault(); select(sel + 1); }
    else if (e.key === "ArrowUp") { e.preventDefault(); select(sel - 1); }
    else if (e.key === "Enter") { var it = items()[sel]; if (it) { e.preventDefault(); go(it.dataset.go); } }
  });
  results.addEventListener("click", function (e) {
    var t = e.target.closest("[data-try]"); if (t) { q.value = t.dataset.try; runSearch(); q.focus(); return; }
    var it = e.target.closest(".r-item"); if (it) go(it.dataset.go);
  });
  function openSearch() { open(search); q.select(); runSearch(); }
  $("#search-btn").addEventListener("click", openSearch);

  document.addEventListener("keydown", function (e) {
    var typing = /^(INPUT|TEXTAREA|SELECT)$/.test(document.activeElement.tagName) || document.activeElement.isContentEditable;
    if (e.key === "Escape") {
      if (!search.hidden) close(search); else if (!viewer.hidden) close(viewer); else closeMenu();
      return;
    }
    if (((e.key === "/" && !typing) || (e.key.toLowerCase() === "k" && (e.ctrlKey || e.metaKey))) && search.hidden) {
      e.preventDefault(); openSearch();
    }
  });

  /* ---------- index as a drawer on narrow screens ---------- */
  var menuBtn = $("#menu-btn"), scrim = $("#scrim");
  function closeMenu() { side.classList.remove("open"); scrim.hidden = true; menuBtn.setAttribute("aria-expanded", "false"); }
  menuBtn.addEventListener("click", function () {
    var o = !side.classList.contains("open");
    side.classList.toggle("open", o); scrim.hidden = !o; menuBtn.setAttribute("aria-expanded", String(o));
    if (o) { var a = side.querySelector("a[aria-current]") || side.querySelector("a"); a.focus(); }
  });
  scrim.addEventListener("click", closeMenu);

  route();
})();
