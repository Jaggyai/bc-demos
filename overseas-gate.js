/* Overseas Roofing — private 7-day preview gate + dashboard theme.
   Shared by the website (/surrey/roofers/overseas-roofing-ltd/) and the dashboard (/dashboard/?buyers=roofing).
   NOTE: this is a client-side gate for a sales demo. It keeps casual visitors out and ends the preview on the expiry date,
   but anyone who reads the page source can get around it, so nothing sensitive may live on these pages (only the 3-row preview does). */
(function () {
  var HASH = "efb2652c62b7bba01dc52bcbac3ee7e5a44fa84d473e74038b99e13dd98b8930"; // sha256 of the lowercase password
  var EXPIRES = new Date("2026-11-29T23:59:59-07:00").getTime();                  // preview ends: end of day Nov 29 (PT)
  var KEY = "ovr_preview_ok";
  var isDash = /\/dashboard\/?$|\/dashboard\/index\.html$/.test(location.pathname);
  if (isDash && !/buyers/.test(location.search)) return;                          // other demos stay open

  var doc = document.documentElement;
  doc.classList.add("ovr-lock");
  var st = document.createElement("style");
  st.textContent =
    "html.ovr-lock body>*:not(#ovr-gate){visibility:hidden!important}" +
    "#ovr-gate{position:fixed;inset:0;z-index:2147483647;display:flex;align-items:center;justify-content:center;padding:20px;font-family:Barlow,-apple-system,Segoe UI,Roboto,sans-serif;" +
    "background:radial-gradient(900px 600px at 70% 10%,rgba(255,106,19,.20),transparent 60%),#15171a;color:#eef2f8}" +
    "#ovr-gate .c{width:420px;max-width:94vw;background:#1f2327;border:1px solid rgba(255,255,255,.1);border-radius:22px;padding:34px 30px;box-shadow:0 30px 80px rgba(0,0,0,.55)}" +
    "#ovr-gate .b{display:flex;align-items:center;gap:12px;margin-bottom:18px}" +
    "#ovr-gate .m{width:44px;height:44px;border-radius:12px;background:linear-gradient(135deg,#ff6a13,#e04f00);display:grid;place-items:center;color:#fff;font-weight:900}" +
    "#ovr-gate h1{font-size:21px;font-weight:800;line-height:1.2}#ovr-gate p{color:#9aa7bd;font-size:14px;line-height:1.5;margin:6px 0 18px}" +
    "#ovr-gate input{width:100%;padding:13px 14px;background:#15171a;border:1px solid rgba(255,255,255,.12);border-radius:11px;color:#fff;font-size:15px;font-family:inherit}" +
    "#ovr-gate input:focus{outline:2px solid rgba(255,106,19,.6);border-color:transparent}" +
    "#ovr-gate button{width:100%;margin-top:12px;padding:13px;border:0;border-radius:11px;background:linear-gradient(135deg,#ff6a13,#e04f00);color:#fff;font-weight:800;font-size:15px;cursor:pointer;font-family:inherit}" +
    "#ovr-gate .e{color:#fca5a5;font-size:13px;min-height:18px;margin-top:10px}#ovr-gate .f{margin-top:16px;font-size:12px;color:#6b7894;text-align:center}" +
    "#ovr-pill{position:fixed;left:14px;bottom:14px;z-index:2147483000;background:rgba(21,23,26,.88);backdrop-filter:blur(8px);color:#ff6a13;border:1px solid rgba(255,106,19,.4);border-radius:99px;padding:7px 13px;font:600 12px Outfit,-apple-system,Segoe UI,sans-serif}";
  if (isDash) st.textContent +=
    ":root{--bg:#15171a!important;--bg2:#1b1e22!important;--surface:#1f2327!important;--surface2:#272c31!important;--line:rgba(255,255,255,.10)!important;--brand:#ff6a13!important;--brand2:#e04f00!important;--brandsoft:rgba(255,106,19,.16)!important;--grad:linear-gradient(135deg,#ff6a13,#e04f00)!important}" +
    "body{background:radial-gradient(1200px 700px at 80% -10%,rgba(255,106,19,.08) 0,transparent 60%),#15171a!important}" +
    ".btn,.logo-mark{color:#fff!important}.logo-word{font-family:'Big Shoulders Stencil Display','Arial Narrow',Impact,sans-serif!important;text-transform:uppercase;line-height:.95;font-size:17px!important;letter-spacing:.5px!important}#ovr-gate h1,#ovr-gate .b div{font-family:'Big Shoulders Stencil Display','Arial Narrow',Impact,sans-serif;text-transform:uppercase;letter-spacing:.5px}#login{display:none!important}.nav button.active{color:#ff6a13}a[style*='a5b4fc']{color:#c9a36a!important}";
  var fl=document.createElement("link");fl.rel="stylesheet";fl.href="https://fonts.googleapis.com/css2?family=Big+Shoulders+Stencil+Display:wght@700;800;900&family=Barlow:wght@400;600;700&display=swap";(document.head || doc).appendChild(fl);
  (document.head || doc).appendChild(st);

  function sha(s) {
    return crypto.subtle.digest("SHA-256", new TextEncoder().encode(s)).then(function (b) {
      return Array.prototype.map.call(new Uint8Array(b), function (x) { return ("0" + x.toString(16)).slice(-2); }).join("");
    });
  }
  function now() { // server clock first (harder to fake than the device clock), device clock as fallback
    var t = (location.hostname === "localhost" && /__now=/.test(location.search)) ? new Date(decodeURIComponent(location.search.split("__now=")[1].split("&")[0])).getTime() : null;
    if (t) return Promise.resolve(t);
    return fetch(location.pathname + "?_=" + Date.now(), { method: "HEAD", cache: "no-store" })
      .then(function (r) { var d = r.headers.get("Date"); return d ? new Date(d).getTime() : Date.now(); })
      .catch(function () { return Date.now(); });
  }
  function daysLeft(t) { return Math.max(1, Math.floor((EXPIRES - t) / 86400000) + (EXPIRES - t > 0 ? 0 : 0)); }
  function branding() {
    if (!isDash) return;
    document.title = "Overseas Roofing — Owner Dashboard";
    var go = function () {
      var m = document.querySelector(".sidebar .logo-mark"), w = document.querySelector(".sidebar .logo-word");
      if (m) m.textContent = "OR";
      if (w) w.innerHTML = "Overseas<br><span>Roofing</span>";
      var f = document.querySelector(".side-foot"); if (f && !f.querySelector(".pw")) f.insertAdjacentHTML("beforeend", '<div class="pw" style="margin-top:8px;font-size:11px;opacity:.6">Powered by JaggyAI</div>');
      document.querySelectorAll("*").forEach(function (e) { if (!e.children.length && /^owner@/.test((e.textContent || "").trim())) e.textContent = "Preview account"; });
      var l = document.querySelector("link[rel=icon]"); if (l) l.href = "data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><rect width='100' height='100' rx='22' fill='%23ff6a13'/><text x='50' y='68' font-size='52' text-anchor='middle' fill='white' font-family='Arial' font-weight='bold'>OR</text></svg>";
    };
    if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", go); else go();
  }
  function unlock(t) {
    doc.classList.remove("ovr-lock");
    var g = document.getElementById("ovr-gate"); if (g) g.remove();
    var p = document.createElement("div"); p.id = "ovr-pill";
    p.textContent = "Private preview · " + daysLeft(t) + " day" + (daysLeft(t) === 1 ? "" : "s") + " left";
    (document.body || doc).appendChild(p);
    branding();
    if (isDash) { var b = document.getElementById("loginBtn"); if (b) b.click(); }  // skip the demo login screen
  }
  function gate(t, expired) {
    var d = document.createElement("div"); d.id = "ovr-gate";
    d.innerHTML = '<div class="c"><div class="b"><div class="m">OR</div><div style="font-weight:800">Overseas Roofing Ltd.</div></div>' +
      (expired
        ? '<h1>Your 7-day preview has ended</h1><p>This private preview expired on Nov 29. Contact Jag at JaggyAI to keep your website and dashboard going.</p>'
        : '<h1>' + (isDash ? 'Owner dashboard' : 'Your new website') + ' — private preview</h1><p>Prepared for Overseas Roofing Ltd. Enter the password you were sent. Preview access ends Nov 29.</p>' +
          '<form id="ovr-f"><input id="ovr-pw" type="password" placeholder="Password" autocomplete="off" autofocus><button type="submit">Open preview</button><div class="e" id="ovr-e"></div></form>') +
      '<div class="f">Concept by JaggyAI · sample content</div></div>';
    (document.body || doc).appendChild(d);
    if (expired) return;
    document.getElementById("ovr-f").addEventListener("submit", function (e) {
      e.preventDefault();
      var v = document.getElementById("ovr-pw").value.trim().toLowerCase();
      sha(v).then(function (h) {
        now().then(function (t2) {
          if (t2 > EXPIRES) { d.remove(); gate(t2, true); return; }
          if (h === HASH) { try { localStorage.setItem(KEY, HASH); } catch (x) {} unlock(t2); }
          else { var el = document.getElementById("ovr-e"); el.textContent = "That password is not right."; }
        });
      });
    });
  }
  function start() {
    now().then(function (t) {
      if (t > EXPIRES) { gate(t, true); return; }
      var ok = false; try { ok = localStorage.getItem(KEY) === HASH; } catch (e) {}
      if (ok) unlock(t); else gate(t, false);
    });
  }
  if (document.body) start(); else document.addEventListener("DOMContentLoaded", start);
})();
