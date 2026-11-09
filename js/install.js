/* Installing the guide as an app (a PWA).
   - Registers sw.js, which keeps the guide on the device for offline use.
   - On first launch in a browser, shows the install screen: "Install the
     app" or "Use in the browser". The choice is remembered on this device
     only (localStorage) - nothing is sent anywhere.
   - Android / desktop Chrome and Edge: the browser's own install box.
     iPhone / iPad: the Share -> Add to Home Screen steps (Safari has no
     install box a page can open). Anything else: where the menu option is.
   - "Install as an app" in the index brings the screen back later. */
(function () {
  "use strict";
  var KEY = "hf-install-choice";
  var screen = document.getElementById("install");
  var go = document.getElementById("in-go"), web = document.getElementById("in-web");
  var ios = document.getElementById("in-ios"), manual = document.getElementById("in-manual");
  var deferred = null;

  var installed = function () {
    return window.matchMedia("(display-mode: standalone)").matches || window.navigator.standalone === true;
  };
  var isIOS = /iphone|ipad|ipod/i.test(navigator.userAgent) ||
    (navigator.platform === "MacIntel" && navigator.maxTouchPoints > 1);
  function remember(v) { try { localStorage.setItem(KEY, v); } catch (e) {} }
  function choice() { try { return localStorage.getItem(KEY); } catch (e) { return null; } }

  if ("serviceWorker" in navigator && /^https?:$/.test(location.protocol)) {
    window.addEventListener("load", function () { navigator.serviceWorker.register("sw.js").catch(function () {}); });
  }

  // Chrome / Edge tell us when the guide can be installed; keep that for the button.
  window.addEventListener("beforeinstallprompt", function (e) { e.preventDefault(); deferred = e; });
  window.addEventListener("appinstalled", function () { remember("installed"); hide(); setLink(); });

  var lastFocus = null;
  function show() {
    ios.hidden = true; manual.hidden = true;
    go.hidden = false; go.textContent = "Install the app"; web.textContent = "Use in the browser";
    lastFocus = document.activeElement;
    screen.hidden = false; document.body.style.overflow = "hidden";
    go.focus();
  }
  function hide() {
    screen.hidden = true; document.body.style.overflow = "";
    if (lastFocus && lastFocus.focus) lastFocus.focus();
  }

  go.addEventListener("click", function () {
    if (deferred) {
      deferred.prompt();
      deferred.userChoice.then(function (r) {
        deferred = null;
        if (r.outcome === "accepted") { remember("installed"); hide(); setLink(); }
      });
      return;
    }
    // no install box to open: show how to do it by hand
    (isIOS ? ios : manual).hidden = false;
    go.hidden = true;
    web.textContent = "Done";
  });
  web.addEventListener("click", function () {
    if (!choice()) remember("web");
    hide();
  });
  screen.addEventListener("keydown", function (e) {
    if (e.key === "Escape") { if (!choice()) remember("web"); hide(); }
  });

  // "Install as an app" at the foot of the index, while not installed
  var side = document.getElementById("side");
  function setLink() {
    var old = document.getElementById("ix-install");
    if (old) old.remove();
    if (installed()) return;
    var b = document.createElement("button");
    b.id = "ix-install"; b.type = "button"; b.className = "ix-install";
    b.innerHTML = '<img src="icons/favicon-32.png" alt="" width="20" height="20">Install as an app';
    b.addEventListener("click", show);
    side.appendChild(b);
  }
  setLink();

  if (!installed() && !choice()) show();
})();
