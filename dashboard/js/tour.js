/* JaggyAI guided tour — self-contained, no deps */
(function () {
  const $ = s => document.querySelector(s);
  const goTab = v => { const b = document.querySelector('.nav button[data-v="' + v + '"]'); if (b) b.click(); };

  // Each step: tab to open, CSS selector to highlight (null = centered), title, text.
  const STEPS = [
    { tab: "dashboard", sel: null, title: "Welcome to your demo 👋",
      text: "This is the JaggyAI Automation Suite — the app you show prospects on a sales call. Take this 60-second tour and you'll know every screen. Click <b>Next</b>." },
    { tab: "dashboard", sel: ".sidebar .nav", title: "This is your menu",
      text: "Six screens live here. You'll click these to move around. The tour will open each one for you." },
    { tab: "dashboard", sel: ".kpis", title: "The headline numbers",
      text: "A business owner glances here every morning: leads, revenue booked, close rate. The fake data shows a healthy roofing company." },
    { tab: "dashboard", sel: ".kpi.accent", title: "Your #1 selling number",
      text: "<b>47-second</b> response time. A normal business takes ~47 <b>hours</b> to reply to a lead. That gap is the money they're losing — and what you're fixing." },
    { tab: "dashboard", sel: "#feed", title: "Live automation feed",
      text: "Like a security-camera log — every automatic action the system just took (texts sent, reviews requested, jobs booked)." },
    { tab: "leads", sel: ".tablewrap", title: "Leads (CRM) = your customer list",
      text: "Every lead, sorted <b>🔥 Hot / 🌤️ Warm / ❄️ Cold</b> so you call the ready-to-buy ones first. <b>Click any row</b> later to see their full history." },
    { tab: "pipeline", sel: ".board", title: "Pipeline = the same people, as a board",
      text: "Watch each job slide from <b>New Lead → Won → Completed</b>. Nothing gets forgotten. Some people prefer this view over the list." },
    { tab: "automations", sel: ".auto-list", title: "The robots doing the work",
      text: "Each row is a task the system handles 24/7 — instant replies, follow-ups, invoices, review requests. The switches turn them on/off (try one!)." },
    { tab: "simulator", sel: "#simBtn", title: "⭐ This is your money-maker",
      text: "On a real call, click <b>Simulate a new lead</b> — a customer comes in and gets auto-texted back in 47 seconds, live. Seeing it = the moment they buy." },
    { tab: "assistant", sel: ".chat", title: "The 24/7 AI chatbot",
      text: "Answers customer questions and books jobs at 2am. Type <b>“I have a leak”</b> later and watch it reply like a real receptionist." },
    { tab: "dashboard", sel: null, title: "That's the whole tour! 🚀",
      text: "You've seen all 6 screens. Practice the <b>Live Demo</b> tab until it's smooth — that's your pitch. Replay this tour anytime with the <b>Take a Tour</b> button up top." },
  ];

  let i = 0, overlay, pop, current;

  function build() {
    overlay = document.createElement("div"); overlay.className = "tour-overlay";
    overlay.addEventListener("click", end);
    pop = document.createElement("div"); pop.className = "tour-pop";
    pop.addEventListener("click", e => e.stopPropagation());
    document.body.appendChild(overlay); document.body.appendChild(pop);
  }

  function clearSpot() { if (current) { current.classList.remove("tour-spot"); current = null; } }

  function render() {
    const s = STEPS[i];
    goTab(s.tab);
    setTimeout(() => {
      clearSpot();
      const el = s.sel ? $(s.sel) : null;
      const dots = STEPS.map((_, n) => '<i class="' + (n === i ? "on" : "") + '"></i>').join("");
      pop.innerHTML =
        '<button class="tp-skip">Skip ✕</button>' +
        '<div class="tp-step">Step ' + (i + 1) + ' of ' + STEPS.length + '</div>' +
        '<div class="tp-title">' + s.title + '</div>' +
        '<div class="tp-text">' + s.text + '</div>' +
        '<div class="tp-row"><div class="tp-dots">' + dots + '</div><div class="tp-btns">' +
        (i > 0 ? '<button class="tp-back">Back</button>' : '') +
        '<button class="tp-next">' + (i === STEPS.length - 1 ? "Done 🎉" : "Next →") + '</button>' +
        '</div></div><div class="tp-arrow"></div>';
      pop.querySelector(".tp-skip").onclick = end;
      pop.querySelector(".tp-next").onclick = next;
      const back = pop.querySelector(".tp-back"); if (back) back.onclick = prev;

      overlay.classList.add("show");
      if (el) {
        el.classList.add("tour-spot"); current = el;
        el.scrollIntoView({ block: "center", behavior: "smooth" });
        setTimeout(() => position(el), 260);
      } else {
        position(null);
      }
      pop.classList.add("show");
    }, 70);
  }

  function position(el) {
    const arrow = pop.querySelector(".tp-arrow");
    if (!el) { // centered
      pop.style.top = (window.innerHeight / 2 - pop.offsetHeight / 2) + "px";
      pop.style.left = (window.innerWidth / 2 - pop.offsetWidth / 2) + "px";
      if (arrow) arrow.style.display = "none";
      return;
    }
    if (arrow) arrow.style.display = "";
    const r = el.getBoundingClientRect();
    const pw = pop.offsetWidth, ph = pop.offsetHeight, gap = 18;
    let top, left, below = true;
    if (r.bottom + gap + ph < window.innerHeight) { top = r.bottom + gap; below = true; }
    else if (r.top - gap - ph > 0) { top = r.top - gap - ph; below = false; }
    else { top = Math.max(12, window.innerHeight / 2 - ph / 2); }
    left = r.left + r.width / 2 - pw / 2;
    left = Math.max(12, Math.min(left, window.innerWidth - pw - 12));
    pop.style.top = top + "px"; pop.style.left = left + "px";
    if (arrow) {
      const ax = r.left + r.width / 2 - left - 7;
      arrow.style.left = Math.max(14, Math.min(ax, pw - 28)) + "px";
      if (below) { arrow.style.top = "-7px"; arrow.style.transform = "rotate(45deg)"; }
      else { arrow.style.top = (ph - 7) + "px"; arrow.style.transform = "rotate(225deg)"; }
    }
  }

  function next() { if (i === STEPS.length - 1) return end(); i++; render(); }
  function prev() { if (i > 0) { i--; render(); } }
  function start() { i = 0; if (!overlay) build(); render(); }
  function end() {
    clearSpot();
    if (overlay) overlay.classList.remove("show");
    if (pop) pop.classList.remove("show");
    setTimeout(() => { if (overlay) overlay.remove(); if (pop) pop.remove(); overlay = pop = null; }, 220);
    try { localStorage.setItem("jaggy_tour_seen", "1"); } catch (e) {}
  }

  window.startTour = start;

  // Wire the topbar button + auto-start on first visit after login.
  document.addEventListener("DOMContentLoaded", () => {
    const btn = document.getElementById("tourBtn");
    if (btn) btn.addEventListener("click", start);
    const login = document.getElementById("loginBtn");
    if (login) login.addEventListener("click", () => {
      let seen = false; try { seen = localStorage.getItem("jaggy_tour_seen"); } catch (e) {}
      if (!seen) setTimeout(start, 750);
      else { const b = document.getElementById("tourBtn"); if (b) b.classList.add("pulse"); }
    });
  });
})();
