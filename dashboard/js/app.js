/* JaggyAI Automation Suite — app logic (vanilla JS, no deps) */
(function () {
  const D = window.JAGGY;
  const $ = (s, r = document) => r.querySelector(s);
  const money = n => "$" + n.toLocaleString("en-US");
  const stClass = s => "st-" + s.replace(/[^A-Za-z]/g, "");
  const esc = s => String(s).replace(/[&<>"]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));

  /* ---------- LOGIN ---------- */
  function initLogin() {
    $("#loginBtn").addEventListener("click", e => { e.preventDefault(); enter(); });
    $("#login form").addEventListener("submit", e => { e.preventDefault(); enter(); });
    function enter() {
      $("#login").style.opacity = "0";
      $("#login").style.transition = "opacity .35s";
      setTimeout(() => { $("#login").classList.add("hidden"); $("#app").classList.remove("hidden"); go("dashboard"); }, 350);
    }
  }

  /* ---------- ROUTER ---------- */
  const VIEWS = {
    dashboard: viewDashboard, journey: viewJourney, findleads: viewFindLeads, leads: viewLeads, pipeline: viewPipeline,
    automations: viewAutomations, simulator: viewSimulator, assistant: viewAssistant, bizinfo: viewBusinessInfo,
    calendar: viewCalendar, messages: viewMessages, money: viewMoney
  };
  const TITLES = {
    dashboard: ["Dashboard", "Live overview of " + D.CLIENT.name + "'s lead engine"],
    journey: ["Customer Journey", "Exactly what happens when a customer comes in — step by step, while you work"],
    findleads: ["Find Leads", "Pull a fresh list of local businesses to win — by city and type"],
    bizinfo: ["Business Info", "Tell your chatbot about your business — it answers customers 24/7"],
    calendar: ["Calendar", "Every booked job — add it to your phone with one tap"],
    messages: ["Messages", "Text your customers right from the dashboard"],
    money: ["Quotes & Invoices", "Build a quote, send it, get paid"],
    leads: ["Leads (CRM)", "Every lead, scored and tracked in one place"],
    pipeline: ["Pipeline", "Drag-free Kanban — value at every stage"],
    automations: ["Automations", "The workflows running 24/7 in the background"],
    simulator: ["Live Demo", "Watch a new lead get answered in seconds"],
    assistant: ["AI Assistant", "The 24/7 chatbot that answers & books"]
  };
  function go(v) {
    document.querySelectorAll(".nav button").forEach(b => b.classList.toggle("active", b.dataset.v === v));
    const [t, s] = TITLES[v];
    $("#pageTitle").textContent = t; $("#pageSub").textContent = s;
    VIEWS[v]($("#content"));
  }

  /* ---------- DASHBOARD ---------- */
  function viewDashboard(el) {
    const k = D.kpis();
    const kpiCards = [
      { l: "Leads this month", v: k.leads, t: "▲ 3 new today", accent: false },
      { l: "Avg. speed-to-lead", v: k.avgResp, t: "industry avg: 47 hrs", accent: true },
      { l: "Revenue booked", v: money(k.booked), t: "▲ 18% vs last month", accent: false },
      { l: "Open pipeline", v: money(k.openPipe), t: "4 quotes out", accent: false },
      { l: "Close rate", v: k.closeRate + "%", t: "▲ 9 pts since launch", accent: false },
      { l: "Leads lost to slow follow-up", v: k.lost, t: "the bot answers every one", accent: false, flat: true },
    ];
    el.innerHTML = `
      <div class="grid kpis">
        ${kpiCards.map(c => `
          <div class="card kpi ${c.accent ? "accent" : ""}">
            <div class="label">${c.l}</div>
            <div class="val">${c.v}</div>
            <div class="trend ${c.flat ? "flat" : ""}">${c.t}</div>
          </div>`).join("")}
      </div>
      <div class="grid two-col">
        <div class="card">
          <h3>Revenue booked — last 4 weeks</h3>
          ${sparkline(D.REVENUE_TREND)}
        </div>
        <div class="card">
          <h3>Leads by source</h3>
          ${sourceBars()}
        </div>
      </div>
      <div class="grid two-col" style="margin-top:16px">
        <div class="card">
          <h3>Pipeline value by stage</h3>
          ${stageBars()}
        </div>
        <div class="card">
          <h3><span class="on-dot" style="display:inline-block;width:8px;height:8px;border-radius:50%;background:var(--green)"></span> Live automation activity</h3>
          <div class="feed" id="feed">${D.ACTIVITY.map(feedItem).join("")}</div>
        </div>
      </div>`;
  }
  function feedItem(a, isNew) {
    const ic = { bolt: "⚡", sms: "💬", star: "⭐", doc: "📄", moon: "🌙", check: "✅", phone: "📞" }[a.icon] || "•";
    return `<div class="it ${isNew ? "new" : ""}"><div class="ico">${ic}</div><div><div class="ft">${a.text}</div><div class="fm">${a.time}</div></div></div>`;
  }
  function sourceBars() {
    const counts = {};
    D.SOURCES.forEach(s => counts[s] = 0);
    D.LEADS.forEach(l => counts[l.source]++);
    const max = Math.max(...Object.values(counts));
    return `<div class="bars">${D.SOURCES.map(s => `
      <div class="bar-row"><div class="bl">${s}</div>
        <div class="bar-track"><div class="bar-fill" style="width:${(counts[s] / max) * 100}%"></div></div>
        <div class="bn">${counts[s]}</div></div>`).join("")}</div>`;
  }
  function stageBars() {
    const order = ["New Lead", "Contacted", "Quote Sent", "Won", "Scheduled", "Completed"];
    const sums = {}; order.forEach(s => sums[s] = 0);
    D.LEADS.forEach(l => { if (sums[l.stage] !== undefined) sums[l.stage] += l.value; });
    const max = Math.max(...Object.values(sums), 1);
    return `<div class="bars">${order.map(s => `
      <div class="bar-row"><div class="bl">${s}</div>
        <div class="bar-track"><div class="bar-fill" style="width:${(sums[s] / max) * 100}%"></div></div>
        <div class="bn">${"$" + Math.round(sums[s] / 1000) + "k"}</div></div>`).join("")}</div>`;
  }
  function sparkline(data) {
    const w = 480, h = 120, pad = 8;
    const max = Math.max(...data.map(d => d.value)) * 1.15;
    const step = (w - pad * 2) / (data.length - 1);
    const pts = data.map((d, i) => [pad + i * step, h - pad - (d.value / max) * (h - pad * 2)]);
    const line = pts.map(p => p.join(",")).join(" ");
    const area = `${pad},${h - pad} ${line} ${w - pad},${h - pad}`;
    return `<svg class="spark" viewBox="0 0 ${w} ${h}" preserveAspectRatio="none">
      <defs><linearGradient id="ag" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0" stop-color="#8b5cf6" stop-opacity=".5"/><stop offset="1" stop-color="#8b5cf6" stop-opacity="0"/>
      </linearGradient></defs>
      <polygon points="${area}" fill="url(#ag)"/>
      <polyline points="${line}" fill="none" stroke="#a78bfa" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
      ${pts.map(p => `<circle cx="${p[0]}" cy="${p[1]}" r="3.5" fill="#c4b5fd"/>`).join("")}
    </svg>
    <div style="display:flex;justify-content:space-between;font-size:11px;color:var(--muted2);margin-top:6px">
      ${data.map(d => `<span>${d.label}<br><b style="color:var(--muted)">$${(d.value/1000).toFixed(1)}k</b></span>`).join("")}
    </div>`;
  }

  /* ---------- LEADS (CRM) ---------- */
  let leadFilter = "All", leadSearch = "";
  function viewLeads(el) {
    el.innerHTML = `
      <div class="toolbar">
        <div class="search">🔎<input id="lsearch" placeholder="Search name, city, service…" value="${esc(leadSearch)}"></div>
        ${["All", "Hot", "Warm", "Cold"].map(f => `<button class="chip ${leadFilter === f ? "active" : ""}" data-f="${f}">${f === "All" ? "All scores" : f}</button>`).join("")}
      </div>
      <div class="tablewrap"><table>
        <thead><tr><th>Lead</th><th>Service</th><th>Source</th><th>Stage</th><th>Score</th><th>Response</th><th style="text-align:right">Value</th></tr></thead>
        <tbody id="lbody"></tbody>
      </table></div>`;
    $("#lsearch").addEventListener("input", e => { leadSearch = e.target.value; renderLeadRows(); });
    el.querySelectorAll(".chip").forEach(c => c.addEventListener("click", () => { leadFilter = c.dataset.f; viewLeads(el); }));
    renderLeadRows();
  }
  function renderLeadRows() {
    const q = leadSearch.toLowerCase();
    const rows = D.LEADS.filter(l => (leadFilter === "All" || l.score === leadFilter))
      .filter(l => !q || (l.name + l.city + l.service).toLowerCase().includes(q))
      .map(l => `
        <tr data-id="${l.id}">
          <td><div class="lead-name">${esc(l.name)}</div><div class="lead-sub">${l.city} · ${l.phone}</div></td>
          <td>${l.service}</td><td>${l.source}</td>
          <td><span class="st ${stClass(l.stage)}">${l.stage}</span></td>
          <td><span class="badge b-${l.score}">${l.score === "Hot" ? "🔥" : l.score === "Warm" ? "🌤️" : "❄️"} ${l.score}</span></td>
          <td class="resp">${l.response}</td>
          <td class="val" style="text-align:right">${l.value ? money(l.value) : "—"}</td>
        </tr>`).join("");
    $("#lbody").innerHTML = rows || `<tr><td colspan="7" style="color:var(--muted);text-align:center;padding:30px">No leads match.</td></tr>`;
    $("#lbody").querySelectorAll("tr[data-id]").forEach(tr => tr.addEventListener("click", () => openDrawer(+tr.dataset.id)));
  }

  /* ---------- DRAWER ---------- */
  function openDrawer(id) {
    const l = D.LEADS.find(x => x.id === id); if (!l) return;
    const journey = leadJourney(l);
    $("#drawer").innerHTML = `
      <button class="dx" id="dxBtn">✕</button>
      <div class="dname">${esc(l.name)}</div>
      <div style="margin-bottom:14px"><span class="badge b-${l.score}">${l.score}</span> <span class="st ${stClass(l.stage)}">${l.stage}</span></div>
      <div class="drow"><span class="k">Service</span><b>${l.service}</b></div>
      <div class="drow"><span class="k">Job value</span><b>${l.value ? money(l.value) : "—"}</b></div>
      <div class="drow"><span class="k">Phone</span><b>${l.phone}</b></div>
      <div class="drow"><span class="k">Email</span><b>${esc(l.email)}</b></div>
      <div class="drow"><span class="k">City</span><b>${l.city}</b></div>
      <div class="drow"><span class="k">Source</span><b>${l.source}</b></div>
      <div class="drow"><span class="k">Speed-to-lead</span><b class="resp">${l.response}</b></div>
      <div class="drow"><span class="k">Auto follow-ups</span><b>${l.followups}</b></div>
      ${l.booked ? `<div class="drow"><span class="k">Booked</span><b style="color:var(--green)">${esc(l.booked)}</b></div>` : ""}
      <p style="font-size:13px;color:var(--muted);margin:14px 0 4px">${esc(l.notes)}</p>
      <h3 style="margin-top:18px;font-size:13px;color:var(--muted)">${esc(l.name.split(" ")[0])}'s journey — what the system did</h3>
      <div class="ljourney">${journey.map(s => `
        <div class="lj ${s.done ? "done" : ""}">
          <div class="ljd">${s.done ? "✓" : ""}</div>
          <div><div class="ljt">${s.t}${s.now ? '<span class="lj-now">← they are here</span>' : ""}<span class="ljtag">${s.tag}</span></div>
          <div class="ljm">${s.m}</div></div>
        </div>`).join("")}</div>`;
    $("#drawerBg").classList.add("show"); $("#drawer").classList.add("show");
    $("#dxBtn").addEventListener("click", closeDrawer);
  }
  function closeDrawer() { $("#drawerBg").classList.remove("show"); $("#drawer").classList.remove("show"); }

  // Per-lead journey: which of the 6 automated steps have happened for THIS lead.
  function leadJourney(l) {
    const order = ["New Lead", "Contacted", "Quote Sent", "Won", "Scheduled", "Completed"];
    const isLost = l.stage === "Lost";
    const rank = isLost ? 1 : Math.max(0, order.indexOf(l.stage));
    const first = l.name.split(" ")[0];
    const bookedLine = l.booked ? `Booked for ${l.booked}` : `${first} replied → appointment booked + added to calendar`;
    const steps = [
      { tag: "Capture",  done: true,          t: `Lead captured from ${l.source}`,                         m: l.date, now: rank === 0 && !isLost },
      { tag: "Instant",  done: true,          t: `Auto-response sent in ${l.response}`,                     m: "SMS + email fired, owner notified" },
      { tag: "Booking",  done: rank >= 1 && !isLost, t: bookedLine,                                          m: "24/7 auto-booking", now: l.stage === "Contacted" },
      { tag: "Quote",    done: rank >= 2,      t: `Quote sent${l.value ? " — " + money(l.value) : ""}`,      m: "e-sign link + auto follow-up drip", now: l.stage === "Quote Sent" },
      { tag: "Won-Job",  done: rank >= 3,      t: "Won — paperwork ran itself",                             m: "contract · invoice · crew calendar", now: l.stage === "Won" || l.stage === "Scheduled" },
      { tag: "Review",   done: rank >= 5,      t: "Completed + review request sent",                        m: "5★ → ranks you higher → next lead", now: l.stage === "Completed" },
    ];
    if (isLost) steps.push({ tag: "Auto-close", done: true, t: `Followed up ${l.followups}× — no booking, auto-closed`, m: "zero human time wasted" });
    return steps;
  }

  /* ---------- PIPELINE ---------- */
  function viewPipeline(el) {
    const cols = ["New Lead", "Contacted", "Quote Sent", "Won", "Scheduled", "Completed"];
    el.innerHTML = `<p class="section-note">Click any card to see the full lead + its automation history.</p>
      <div class="board">${cols.map(stage => {
        const items = D.LEADS.filter(l => l.stage === stage);
        const total = items.reduce((s, l) => s + l.value, 0);
        return `<div class="col">
          <h4>${stage}<small>${items.length}</small></h4>
          <div class="total">${total ? money(total) : "—"}</div>
          ${items.map(l => `<div class="pcard" data-id="${l.id}">
            <div class="pn">${esc(l.name)}</div>
            <div class="pmeta">${l.service} · ${l.city}</div>
            <div class="pv">${l.value ? money(l.value) : "—"}</div>
            <div style="margin-top:7px"><span class="badge b-${l.score}">${l.score}</span></div>
          </div>`).join("") || `<div style="color:var(--muted2);font-size:12px;padding:8px 2px">Empty</div>`}
        </div>`;
      }).join("")}</div>`;
    el.querySelectorAll(".pcard").forEach(c => c.addEventListener("click", () => openDrawer(+c.dataset.id)));
  }

  /* ---------- AUTOMATIONS ---------- */
  function viewAutomations(el) {
    const icons = ["⚡", "📞", "🔁", "📄", "🏗️", "⭐", "🔍", "🌟", "🎯", "♻️", "🌱"];
    const live =
      '<div class="card" style="border:1px solid #2a5a3a;background:linear-gradient(135deg,rgba(34,197,94,.12),rgba(34,197,94,.03));margin-bottom:18px">' +
      '<h3 style="color:var(--text)">🟢 Live &amp; Connected — real automations running now</h3>' +
      '<p style="font-size:13px;color:var(--muted);margin:4px 0 14px">These are wired to live automations and actually send. Tap <b>Send a test</b> and a real email lands in seconds — proof, not a promise.</p>' +
      '<div class="auto-list">' +
        '<div class="auto"><div class="ai">⭐</div><div class="amid"><div class="an">Review Engine <span class="pill" style="color:#86efac;background:rgba(34,197,94,.16)">● LIVE</span></div><div class="ad">After a closing, asks the client for a Google review — happy → review link, unhappy → private feedback.</div></div>' +
        '<button class="btn" data-fire="review" style="width:auto;padding:9px 15px">▶ Send a test</button></div>' +
        '<div class="auto"><div class="ai">🧾</div><div class="amid"><div class="an">Email Invoicing <span class="pill" style="color:#86efac;background:rgba(34,197,94,.16)">● LIVE</span></div><div class="ad">Sends a branded invoice automatically and chases payment until it&rsquo;s paid.</div></div>' +
        '<button class="btn" data-fire="invoice" style="width:auto;padding:9px 15px">▶ Send a test</button></div>' +
      '</div></div>';
    el.innerHTML = live + `<p class="section-note">🟣 <b>Convert</b> (turn leads into jobs) + 🟢 <b>Generate</b> (bring new leads in). All run server-side, 24/7 — clients never touch the wiring.</p>
      <div class="auto-list">${D.AUTOMATIONS.map((a, i) => `
        <div class="auto">
          <div class="ai">${icons[i] || "⚙️"}</div>
          <div class="amid"><div class="an">${a.name}</div><div class="ad">${a.desc}</div><div class="astat">${a.stat}</div></div>
          <div class="toggle ${a.on ? "on" : ""}" data-i="${i}"><div class="knob"></div></div>
        </div>`).join("")}</div>`;
    el.querySelectorAll(".toggle").forEach(t => t.addEventListener("click", () => {
      const i = +t.dataset.i; D.AUTOMATIONS[i].on = !D.AUTOMATIONS[i].on;
      t.classList.toggle("on"); D.AUTOMATIONS[i].stat = D.AUTOMATIONS[i].on ? D.AUTOMATIONS[i].stat.replace("Paused", "Active") : "Paused";
      t.parentElement.querySelector(".astat").textContent = D.AUTOMATIONS[i].stat;
    }));
    // Live automation test buttons — fire the real Make.com webhooks
    const HOOKS = {
      review: "https://hook.us2.make.com/5di136oplsbgbrm57bctysagqvfxbu91",
      invoice: "https://hook.us2.make.com/vf1wzgwzwalh5a7k6o2oug9ry7bvtqhv"
    };
    el.querySelectorAll("[data-fire]").forEach(b => b.onclick = () => {
      const kind = b.dataset.fire, biz = D.CLIENT.name;
      const payload = kind === "review"
        ? { customer_name: "Demo Client", customer_email: "jag@jaggyai.com", business_name: biz, review_link: "https://g.page/r/EXAMPLE/review" }
        : { customer_name: "Demo Client", customer_email: "jag@jaggyai.com", business_name: biz, invoice_number: "DEMO-1001", invoice_date: "today", due_date: "in 14 days", service: "Real estate services", amount: "18,500.00", payment_info: "e-transfer to " + (D.CLIENT.email || "owner@business.ca") };
      b.disabled = true; b.textContent = "Sending…";
      fetch(HOOKS[kind], { method: "POST", mode: "no-cors", body: new URLSearchParams(payload) })
        .then(() => { b.textContent = "✓ Sent! Check the inbox"; })
        .catch(() => { b.textContent = "✓ Sent! Check the inbox"; });
    });
  }

  /* ---------- SIMULATOR (the star of the demo) ---------- */
  function viewSimulator(el) {
    el.innerHTML = `
      <p class="section-note">Click <b>Simulate a new lead</b> — watch the system answer before a human could even read the email.</p>
      <div class="sim">
        <div>
          <div class="phone"><div class="notch"></div><div class="pscreen">
            <div class="sms-head"><div class="pav">AR</div><div><div class="pn">Acme Roofing</div><div class="ps">SMS · auto-sent by JaggyAI</div></div></div>
            <div class="sms-body" id="smsBody">
              <div class="bubble them" style="opacity:.5">New lead will appear here…</div>
            </div>
          </div></div>
        </div>
        <div class="sim-side">
          <div class="card">
            <div class="label" style="color:var(--muted);font-size:12px">Response time</div>
            <div class="timer" id="simTimer">0:00</div>
            <div class="sim-steps" id="simSteps">
              ${["New lead submitted (web form)", "Lead saved to CRM", "Auto-SMS fired", "Confirmation email sent", "Owner notified · lead scored"]
                .map(s => `<div class="sim-step"><div class="dot"></div><div>${s}</div></div>`).join("")}
            </div>
            <button class="btn" id="simBtn" style="margin-top:18px">▶ Simulate a new lead</button>
          </div>
        </div>
      </div>`;
    $("#simBtn").addEventListener("click", runSim);
  }
  let simRunning = false;
  function runSim() {
    if (simRunning) return; simRunning = true;
    const btn = $("#simBtn"); btn.textContent = "Running…"; btn.style.filter = "brightness(.8)";
    const steps = document.querySelectorAll("#simStep,  .sim-step"), body = $("#smsBody"), timerEl = $("#simTimer");
    body.innerHTML = "";
    const lead = { name: "Kevin Brar", city: "Surrey", service: "emergency roof leak", phone: "778-555-0480" };

    // incoming "form submission" bubble
    body.innerHTML = `<div class="bubble them"><b>New web form lead</b><br>${lead.name} · ${lead.city}<br>"${lead.service} — water coming in!"<span class="tag">submitted just now</span></div>`;

    const stepEls = document.querySelectorAll(".sim-step");
    const markStep = i => stepEls[i] && stepEls[i].classList.add("done");
    // animated counter that lands on 0:47
    let t = 0; const target = 47;
    const tick = setInterval(() => {
      t += 1; if (t > target) t = target;
      timerEl.textContent = "0:" + String(t).padStart(2, "0");
      if (t >= target) clearInterval(tick);
    }, 28);

    setTimeout(() => markStep(0), 200);
    setTimeout(() => markStep(1), 700);
    setTimeout(() => { // typing then SMS
      markStep(2);
      const typing = document.createElement("div"); typing.className = "typing"; typing.innerHTML = "<i></i><i></i><i></i>";
      body.appendChild(typing); body.scrollTop = body.scrollHeight;
      setTimeout(() => {
        typing.remove();
        body.insertAdjacentHTML("beforeend", `<div class="bubble us">Hi Kevin! 🏠 Thanks for reaching out to Acme Roofing about your ${lead.service}. That sounds urgent — a team member will call you within 15 min. In the meantime, reply YES and I'll lock in an emergency visit for tomorrow AM.<span class="tag">delivered · 47 sec after submit</span></div>`);
        body.scrollTop = body.scrollHeight;
      }, 1100);
    }, 1300);
    setTimeout(() => {
      body.insertAdjacentHTML("beforeend", `<div class="bubble them">YES please!! 🙏<span class="tag">customer replied</span></div>`);
      body.scrollTop = body.scrollHeight; markStep(3);
    }, 3000);
    setTimeout(() => {
      markStep(4);
      body.insertAdjacentHTML("beforeend", `<div class="bubble us">You're booked for tomorrow 8–10 AM. ✅ You'll get a reminder text. — Acme Roofing<span class="tag">auto-booked · added to calendar</span></div>`);
      body.scrollTop = body.scrollHeight;
      // log to dashboard feed + prepend a real lead
      D.LEADS.unshift({ id: 99, name: lead.name, phone: lead.phone, email: "kevin.brar@gmail.com", city: lead.city,
        service: "Leak / Emergency", source: "Website Form", stage: "Contacted", score: "Hot", value: 3200,
        response: "47 sec", date: "Just now", followups: 0, notes: "Live-demo lead. Emergency leak, auto-booked for next morning by the bot." });
      D.ACTIVITY.unshift({ time: "Just now", icon: "bolt", text: "Auto-response SMS sent to <b>Kevin Brar</b> in 47 sec — emergency visit booked" });
      btn.textContent = "✓ Lead answered in 47 sec — run again"; btn.style.filter = ""; simRunning = false;
    }, 4400);
  }

  /* ---------- AI ASSISTANT ---------- */
  function viewAssistant(el) {
    el.innerHTML = `
      <div class="chat">
        <div class="chat-head"><div class="ch-av">🤖</div>
          <div><div style="font-weight:700">${esc(D.CLIENT.name)} Assistant</div>
          <div style="font-size:12px;color:var(--muted)"><span class="on-dot"></span>Online · replies instantly, 24/7</div></div></div>
        <div class="chat-body" id="cbody">
          <div class="msg bot">Hi! 👋 I'm ${esc(D.CLIENT.name)}'s assistant. I can answer questions and book an appointment any time, day or night. What can I help you with today?</div>
        </div>
        <div class="chips" id="cchips">
          ${["What services do you offer?", "What areas do you serve?", "Ballpark price for a job?", "I have an emergency", "Book an appointment"]
            .map(q => `<button class="qchip">${esc(q)}</button>`).join("")}
        </div>
        <div class="chat-input"><input id="cinput" placeholder="Type a message…" autocomplete="off"><button id="csend">➤</button></div>
      </div>`;
    const send = txt => {
      const v = (txt || $("#cinput").value).trim(); if (!v) return;
      $("#cinput").value = "";
      $("#cbody").insertAdjacentHTML("beforeend", `<div class="msg user">${esc(v)}</div>`);
      $("#cbody").scrollTop = $("#cbody").scrollHeight;
      const typing = document.createElement("div"); typing.className = "msg bot"; typing.innerHTML = "<span class='typing' style='background:none;padding:0'><i style='background:#94a3b8'></i><i style='background:#94a3b8'></i><i style='background:#94a3b8'></i></span>";
      $("#cbody").appendChild(typing); $("#cbody").scrollTop = $("#cbody").scrollHeight;
      setTimeout(() => { typing.remove();
        $("#cbody").insertAdjacentHTML("beforeend", `<div class="msg bot">${botReply(v)}</div>`);
        $("#cbody").scrollTop = $("#cbody").scrollHeight;
      }, 650);
    };
    $("#csend").addEventListener("click", () => send());
    $("#cinput").addEventListener("keydown", e => { if (e.key === "Enter") send(); });
    el.querySelectorAll(".qchip").forEach(c => c.addEventListener("click", () => send(c.textContent)));
  }
  function botReply(text) {
    const t = text.toLowerCase();
    for (const e of D.BOT_KB) if (e.keys.some(k => t.includes(k))) return esc(e.a).replace(/\n/g, "<br>");
    return esc(D.BOT_FALLBACK);
  }

  /* ---------- FIND LEADS (the Outscraper-style button owners expect) ---------- */
  var flCity = "", flCat = "", flSearch = "", flResults = null;
  function viewFindLeads(el) {
    var DB = window.LEADS_DB || [];
    var cities = [...new Set(DB.map(d => d.city))].sort();
    var groups = {};
    DB.forEach(d => { (groups[d.group] = groups[d.group] || new Set()).add(d.cat); });
    var groupOrder = ["Referral & Property", "Commercial Accounts", "Trade Partners"];
    var groupHint = {
      "Referral & Property": "They hire trades constantly + send referrals",
      "Commercial Accounts": "Big repeat jobs & service contracts",
      "Trade Partners": "Sub-contract & partner work"
    };
    el.innerHTML =
      '<p class="fl-intro">Pick a <b>city</b> and a <b>lead type</b>, then hit <b>Find Leads</b>. You get a clean list of local businesses — names, phones, emails — ready to call or download. ' + DB.length.toLocaleString() + ' businesses on tap.</p>' +
      '<div class="fl-panel">' +
        '<div class="fl-row">' +
          '<div class="fl-field"><label>City</label><select id="flCity"><option value="">All cities</option>' +
            cities.map(c => '<option' + (flCity === c ? ' selected' : '') + '>' + esc(c) + '</option>').join("") + '</select></div>' +
          '<div class="fl-field" style="flex:1"><label>Keyword (optional)</label><input id="flSearch" placeholder="e.g. dental, RE/MAX, fitness…" value="' + esc(flSearch) + '"></div>' +
          '<button class="fl-go" id="flGo">🔎 Find Leads</button>' +
        '</div>' +
        groupOrder.filter(g => groups[g]).map(g =>
          '<div class="fl-grp"><div class="gl">' + g + ' — <span style="color:var(--muted);text-transform:none;font-weight:600">' + groupHint[g] + '</span></div><div class="fl-cats">' +
          [...groups[g]].map(c => '<button class="fl-cat' + (flCat === c ? ' on' : '') + '" data-c="' + esc(c) + '">' + esc(c) + '</button>').join("") +
          '</div></div>').join("") +
      '</div>' +
      '<div id="flOut"></div>';

    $("#flCity").addEventListener("change", e => { flCity = e.target.value; });
    $("#flSearch").addEventListener("input", e => { flSearch = e.target.value; });
    $("#flSearch").addEventListener("keydown", e => { if (e.key === "Enter") runFind(); });
    el.querySelectorAll(".fl-cat").forEach(b => b.addEventListener("click", () => {
      flCat = (flCat === b.dataset.c) ? "" : b.dataset.c;
      el.querySelectorAll(".fl-cat").forEach(x => x.classList.toggle("on", x.dataset.c === flCat));
    }));
    $("#flGo").addEventListener("click", runFind);
    renderFindResults();
  }
  function runFind() {
    var btn = $("#flGo"); if (!btn) return;
    btn.disabled = true; btn.innerHTML = '<span class="fl-spin"></span> Searching…';
    setTimeout(() => {
      var DB = window.LEADS_DB || [];
      var q = flSearch.toLowerCase().trim();
      flResults = DB.filter(d =>
        (!flCity || d.city === flCity) &&
        (!flCat || d.cat === flCat) &&
        (!q || (d.n + " " + d.cat + " " + d.city).toLowerCase().includes(q)));
      btn.disabled = false; btn.innerHTML = "🔎 Find Leads";
      renderFindResults(true);
    }, 700);
  }
  function renderFindResults(animate) {
    var out = $("#flOut"); if (!out) return;
    if (flResults === null) {
      out.innerHTML = '<div class="tablewrap"><div class="fl-empty"><div class="big">🧲</div><b>Ready when you are.</b><br>Choose a city + a lead type above and hit <b>Find Leads</b>.</div></div>';
      return;
    }
    if (!flResults.length) {
      var DB = window.LEADS_DB || [];
      var cityHasData = !flCity || DB.some(d => d.city === flCity);
      var msg = cityHasData
        ? '<div class="big">🔍</div>No matches — try a different lead type or clear the keyword.'
        : '<div class="big">⏳</div><b>We\'re still gathering live leads for ' + esc(flCity) + '.</b><br>New cities come online every few hours. Try <b>Victoria</b> — it\'s fully loaded now.';
      out.innerHTML = '<div class="tablewrap"><div class="fl-empty">' + msg + '</div></div>';
      return;
    }
    var rows = flResults.slice(0, 400);
    var label = (flCat || "leads") + (flCity ? " in " + flCity : " across BC");
    out.innerHTML =
      '<div class="fl-resbar"><div class="fl-count">' + flResults.length.toLocaleString() + ' <span>found · ' + esc(label) + '</span></div>' +
      '<button class="fl-dl" id="flDl">⬇ Download CSV</button></div>' +
      '<div class="tablewrap"><table><thead><tr><th>Business</th><th>Type</th><th>City</th><th>Phone</th><th>Email</th><th>Website</th><th>Rating</th></tr></thead><tbody>' +
      rows.map(d =>
        '<tr><td class="lead-name">' + esc(d.n) + '<div class="lead-sub">' + esc(d.addr) + '</div></td>' +
        '<td>' + esc(d.cat) + '</td><td>' + esc(d.city) + '</td>' +
        '<td>' + esc(d.phone) + '</td><td class="fl-mail">' + (d.email ? esc(d.email) : '<span style="color:var(--muted2)">—</span>') + '</td>' +
        '<td>' + (d.site ? '<a href="' + esc(d.site) + '" target="_blank" rel="noopener" style="color:#a5b4fc">visit ↗</a>' : '<span style="color:var(--muted2)">—</span>') + '</td>' +
        '<td class="resp">' + (d.rating ? '★ ' + d.rating + ' <span style="color:var(--muted2);font-weight:500">(' + d.reviews + ')</span>' : '<span style="color:var(--muted2)">—</span>') + '</td></tr>').join("") +
      '</tbody></table></div>' +
      (flResults.length > 400 ? '<p class="section-note" style="margin-top:10px">Showing first 400 — narrow by city or keyword, or download the full ' + flResults.length.toLocaleString() + ' as CSV.</p>' : '');
    $("#flDl").addEventListener("click", downloadCSV);
  }
  function downloadCSV() {
    if (!flResults || !flResults.length) return;
    var head = ["Business", "Type", "Group", "City", "Phone", "Email", "Website", "Address", "Rating", "Reviews"];
    var lines = [head.join(",")].concat(flResults.map(d =>
      [d.n, d.cat, d.group, d.city, d.phone, d.email, d.site || "", d.addr, d.rating, d.reviews]
        .map(v => '"' + String(v == null ? "" : v).replace(/"/g, '""') + '"').join(",")));
    var blob = new Blob([lines.join("\n")], { type: "text/csv" });
    var a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = "jaggyai-leads-" + (flCat || "all").toLowerCase().replace(/[^a-z]+/g, "-") + "-" + (flCity || "bc").toLowerCase().replace(/[^a-z]+/g, "-") + ".csv";
    document.body.appendChild(a); a.click(); a.remove();
  }

  /* ---------- BUSINESS INFO (owner teaches the website chatbot) ---------- */
  function bizSlug(s) { return (s || "").toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, ""); }
  function bizKey() { return "jaggy_bizinfo:" + bizSlug(D.CLIENT.name); }
  function loadBizInfo() {
    try { return JSON.parse(localStorage.getItem(bizKey()) || localStorage.getItem("jaggy_bizinfo:__last") || "{}"); }
    catch (e) { return {}; }
  }
  function viewBusinessInfo(el) {
    const info = loadBizInfo();
    const fields = [
      ["about",    "About — what your business does",        "We're a family-run plumbing company serving homeowners and businesses…", "area"],
      ["history",  "Your story / history",                   "Started in 2009 by… / 15+ years serving the area / family-owned…",     "area"],
      ["location", "Location / address",                     "123 Main St, Victoria, BC",                                            "input"],
      ["areas",    "Areas you serve",                        "Greater Victoria, Saanich, Sooke, Sidney",                             "input"],
      ["services", "Services you offer",                     "Drain cleaning, water heaters, leak repair, repiping, emergencies…",   "area"],
      ["hours",    "Business hours",                         "Mon–Sat 7am–6pm · 24/7 emergency line",                                "input"],
      ["pricing",  "Pricing / how you quote",                "Free estimates. Repairs from $150. Financing available on big jobs.",   "area"],
      ["faqs",     "Common questions & answers",             "Are you licensed? Yes, fully licensed & insured. Do you warranty work? Yes, 1-year workmanship warranty.", "area"],
      ["extra",    "Anything else customers ask about",      "Payment methods, warranties, brands you carry, parking, etc.",         "area"],
    ];
    el.innerHTML =
      '<p class="section-note">Fill this in once. Your <b>website chatbot</b> uses it to answer customer questions about your business — 24/7, even the stuff that has nothing to do with booking. The more you add, the smarter it sounds.</p>' +
      '<div class="bizform">' +
      fields.map(f => {
        const v = info[f[0]] || "";
        const ctrl = f[3] === "area"
          ? '<textarea id="bi_' + f[0] + '" placeholder="' + esc(f[2]) + '">' + esc(v) + '</textarea>'
          : '<input id="bi_' + f[0] + '" placeholder="' + esc(f[2]) + '" value="' + esc(v) + '">';
        return '<div class="bifield"><label>' + f[1] + '</label>' + ctrl + '</div>';
      }).join("") +
      '<div class="bisave"><button class="btn" id="biSave" style="width:auto;padding:12px 26px">💾 Save — teach my chatbot</button>' +
      '<span id="biMsg" class="bimsg"></span></div>' +
      '<p class="section-note" style="margin-top:6px">💡 To test it: save here, then open your website (🌐 View Website, top-right), click <b>Chat with us</b>, and ask something like “how long have you been in business?” or “what areas do you serve?”</p>' +
      '<div style="margin-top:20px;background:linear-gradient(135deg,rgba(34,211,238,.10),rgba(99,102,241,.06));border:1px solid #2a3f63;border-radius:14px;padding:18px;display:flex;gap:14px;align-items:flex-start;max-width:780px">' +
        '<div style="font-size:26px">📞</div>' +
        '<div style="flex:1"><div style="font-weight:800;font-size:15px">Phone Receptionist <span class="pill" style="margin-left:6px">Add-on</span></div>' +
        '<div style="color:var(--muted);font-size:13.5px;line-height:1.55;margin-top:5px">Everything above can also answer your <b>phone</b>. Connect your Twilio number and an AI receptionist picks up 24/7 — using this same company info, history, hours and services to answer callers, take messages, and book jobs. Same brain, now on the phone.</div>' +
        '<div style="display:flex;gap:9px;align-items:center;margin-top:12px;flex-wrap:wrap">' +
          '<input placeholder="Your Twilio phone number" disabled style="background:var(--bg2);border:1px solid var(--line);border-radius:9px;padding:9px 12px;color:var(--muted2);font-size:13px;width:220px">' +
          '<button class="btn ghost" disabled style="opacity:.55;cursor:not-allowed">Connect Twilio →</button>' +
          '<span style="font-size:12px;color:var(--muted2)">available when you\'re ready</span>' +
        '</div></div>' +
      '</div>' +
      '</div>';
    el.querySelector("#biSave").onclick = () => {
      const obj = { business: D.CLIENT.name };
      fields.forEach(f => { obj[f[0]] = (document.getElementById("bi_" + f[0]).value || "").trim(); });
      try {
        localStorage.setItem(bizKey(), JSON.stringify(obj));
        localStorage.setItem("jaggy_bizinfo:__last", JSON.stringify(obj));
        el.querySelector("#biMsg").textContent = "✓ Saved! Your website chatbot now knows this.";
      } catch (e) {
        el.querySelector("#biMsg").textContent = "Couldn't save in this browser.";
      }
    };
  }

  /* ---------- CUSTOMER JOURNEY (the story owners actually want) ---------- */
  function scenarioFor() {
    const c = (D.CLIENT.category || "").toLowerCase();
    const M = {
      "roofer":               { cust: "Sarah",   prob: "a roof leak",                       svc: "Roof Repair",       val: "$4,600",  urgent: true,  emoji: "🏠" },
      "plumber":              { cust: "Mike",    prob: "a burst pipe under the sink",       svc: "Emergency Plumbing",val: "$1,800",  urgent: true,  emoji: "🚰" },
      "electrician":          { cust: "Dan",     prob: "half the house losing power",       svc: "Electrical Repair", val: "$2,200",  urgent: true,  emoji: "⚡" },
      "hvac contractor":      { cust: "Linda",   prob: "the furnace quitting on a cold night",svc: "Furnace Repair",  val: "$3,400",  urgent: true,  emoji: "🔥" },
      "landscaper":           { cust: "Jessica", prob: "an overgrown yard + a patio she wants built", svc: "Landscape Design", val: "$6,800", urgent: false, emoji: "🌿" },
      "general contractor":   { cust: "Tom",     prob: "a kitchen renovation",              svc: "Renovation",        val: "$24,000", urgent: false, emoji: "🔨" },
      "construction company": { cust: "Tom",     prob: "a basement build-out",              svc: "Renovation",        val: "$32,000", urgent: false, emoji: "🏗️" },
      "concrete contractor":  { cust: "Raj",     prob: "a cracked driveway to replace",     svc: "Driveway",          val: "$5,200",  urgent: false, emoji: "🧱" },
      "excavating contractor":{ cust: "Paul",    prob: "drainage + grading on a new build", svc: "Site Prep",         val: "$11,500", urgent: false, emoji: "🚜" },
      "realtor":              { cust: "Priya",   prob: "thinking about selling their home", svc: "Listing Appointment", val: "$18,500 commission", urgent: false, emoji: "🏡" },
      "real estate":          { cust: "Priya",   prob: "thinking about selling their home", svc: "Listing Appointment", val: "$18,500 commission", urgent: false, emoji: "🏡" },
      "real estate agent":    { cust: "Priya",   prob: "thinking about selling their home", svc: "Listing Appointment", val: "$18,500 commission", urgent: false, emoji: "🏡" },
    };
    return M[c] || { cust: "Jordan", prob: "a project they need done", svc: "the job", val: "$3,500", urgent: false, emoji: "🛠️" };
  }

  function viewJourney(el) {
    const s = scenarioFor(), biz = D.CLIENT.name, city = D.CLIENT.city;
    const first = s.cust.split(" ")[0];
    const trade = (D.CLIENT.category || "service").toLowerCase();
    const STEPS = [
      { time: s.urgent ? "9:47 PM" : "8:30 PM", tag: "Website + Chatbot", ttl: "A customer arrives — after hours",
        cust: s.urgent
          ? `<b>${s.cust}</b> has <b>${s.prob}</b>. They Google "${trade} ${city}", land on your website, and message the chatbot for help — then expect to wait until morning.`
          : `<b>${s.cust}</b> is browsing after dinner, likes your work, and uses the chatbot to ask about <b>${s.prob}</b>.`,
        sys: ["Your 24/7 AI assistant greets them <b>instantly</b>", "Captures name, phone, and exactly what they need"],
        note: "In a normal business this lead waits till morning — and messages two competitors too." },
      { time: "+ 47 seconds", tag: "Instant Lead Response", ttl: "The system replies before a human could",
        cust: `${first} gets a real reply in under a minute — ${s.urgent ? "at almost 10 at night" : "while relaxing at home"}. Impressed before you've lifted a finger.`,
        sys: [
          `Creates <b>${first}'s</b> record in your CRM, tagged "${s.svc}"`,
          `Texts ${first}: <i>"Hi ${first}! ${s.emoji} Thanks for reaching out to ${biz} — we've got you. Reply YES and I'll lock in your ${s.urgent ? "visit" : "free estimate"}."</i>`,
          "Emails a confirmation of what happens next",
          "Scores them 🔥 Hot and adds to the Pipeline",
          `Texts <b>YOU</b>: "New ${s.svc} lead — ${first}. Auto-replied, awaiting reply."`] },
      { time: s.urgent ? "+ 2 minutes" : "next morning", tag: "Auto-Booking", ttl: "Booked — automatically",
        cust: `${first} replies <b>YES</b>. They're now a booked appointment — and <b>you never touched your phone</b>.`,
        sys: ["Books the appointment into your calendar", "Texts a confirmation + a reminder before the visit", `Moves ${first}'s card to "Contacted" on your Pipeline`] },
      { time: "after your visit", tag: "Follow-Up Drip", ttl: "You quote — the system chases it for you",
        cust: `You show up, do what you do best, and send a <b>${s.val}</b> quote. No nagging — the system keeps ${first} warm.`,
        sys: [`Sends the ${s.val} quote with a one-tap e-sign link`, "If unsigned: Day 1 nudge → Day 2 past-work photos → Day 4 \"still want to go ahead?\"", "Card moves to \"Quote Sent\""] },
      { time: "a few days later", tag: "Won-Job Workflow", ttl: "Won — the paperwork runs itself",
        cust: `${first} signs. ~30 minutes of admin per job — <b>done in seconds</b>, no clipboard.`,
        sys: ["Creates the job folder + contract", "Generates the invoice + deposit request", "Books the job on the crew calendar", `Texts ${first} the start date`, `Pings you: "💰 Job won — ${first}, ${s.val}"`] },
      { time: "after the job", tag: "Review Engine", ttl: "The loop closes — and feeds itself",
        cust: `One happy customer becomes your <b>next</b> lead. The wheel keeps turning while you sleep.`,
        sys: [`Texts ${first}: "Thanks! 🙏 A quick Google review would mean the world"`, "5★ review posts → lifts you in local search → brings in the next customer", `<b>${s.val}</b> logged in Revenue Booked on your Dashboard`] },
    ];

    el.innerHTML = `
      <div class="journey">
        <div class="jbar">
          <button class="jbtn" id="jplay">▶ Play the journey</button>
          <button class="jbtn ghost" id="jall">Show all</button>
          <div class="jprogress" id="jprog">Step 0 of ${STEPS.length}</div>
        </div>
        <p class="section-note" style="margin-top:-8px">This is what your customers experience with ${esc(biz)} on autopilot. <b>You</b> just show up and do the work — the system does everything else.</p>
        <div class="jtimeline">
          ${STEPS.map((st, n) => `
            <div class="jstep" data-n="${n}">
              <div class="jdot">${n + 1}</div>
              <div class="jcard">
                <div class="jtime">${st.time}</div>
                <div class="jttl">${st.ttl}</div>
                <div class="jtag">${st.tag}</div>
                <div class="jcust">${st.cust}</div>
                <ul class="jsys">${st.sys.map(x => `<li>${x}</li>`).join("")}</ul>
                ${st.note ? `<div class="jnote">⚠️ ${st.note}</div>` : ""}
              </div>
            </div>`).join("")}
        </div>
        <div class="jfinal" id="jfinal">
          <h3>${s.emoji} That's the whole job — handled.</h3>
          <div class="jrow"><div class="jk">You did:</div><div class="jv">Showed up and did the ${trade} work. That's it.</div></div>
          <div class="jrow"><div class="jk">The system did:</div><div class="jv">Answered in 47 sec, booked it, chased the quote, ran the paperwork, collected the review — at 9:47 PM while you slept.</div></div>
          <div class="jrow"><div class="jk">Result:</div><div class="jv"><b>${s.val}</b> won from one lead that most businesses would've lost overnight.</div></div>
        </div>
      </div>`;

    const steps = [...el.querySelectorAll(".jstep")], fin = el.querySelector("#jfinal"), prog = el.querySelector("#jprog");
    let shown = 0, timer = null;
    const update = () => { prog.textContent = "Step " + Math.min(shown, STEPS.length) + " of " + STEPS.length; };
    const reveal = n => { if (steps[n]) steps[n].classList.add("on"); shown = n + 1; if (shown >= STEPS.length) fin.classList.add("on"); update(); };
    const showAll = () => { if (timer) clearInterval(timer); steps.forEach((_, n) => reveal(n)); };
    const play = () => {
      if (timer) clearInterval(timer);
      steps.forEach(s2 => s2.classList.remove("on")); fin.classList.remove("on"); shown = 0; update();
      let n = 0; reveal(0);
      timer = setInterval(() => { n++; if (n >= STEPS.length) { clearInterval(timer); return; } reveal(n);
        const t = steps[n]; if (t) t.scrollIntoView({ block: "center", behavior: "smooth" }); }, 1700);
    };
    el.querySelector("#jplay").onclick = play;
    el.querySelector("#jall").onclick = showAll;
    reveal(0); // first step visible on open
  }

  /* ---------- CALENDAR / BOOKINGS (add to phone) ---------- */
  function pad2(n) { return (n < 10 ? "0" : "") + n; }
  function icsDate(d) { return d.getUTCFullYear() + pad2(d.getUTCMonth() + 1) + pad2(d.getUTCDate()) + "T" + pad2(d.getUTCHours()) + pad2(d.getUTCMinutes()) + "00Z"; }
  function fmtTime(d) { let h = d.getHours(), m = d.getMinutes(); const ap = h >= 12 ? "PM" : "AM"; h = h % 12 || 12; return h + ":" + (m < 10 ? "0" : "") + m + " " + ap; }
  function appointments() {
    const base = new Date(); base.setHours(0, 0, 0, 0);
    const slots = [[9, 0, "9:00 AM"], [11, 0, "11:00 AM"], [13, 30, "1:30 PM"], [15, 0, "3:00 PM"]];
    const out = [];
    // real website-chatbot bookings — placed at the exact time the customer chose
    D.LEADS.forEach(l => { if (l.bookedAt) { const d = new Date(l.bookedAt); if (!isNaN(d)) out.push({ lead: l, start: d, end: new Date(d.getTime() + 3600000), label: fmtTime(d), web: true }); } });
    // demo-filler jobs from the pipeline
    D.LEADS.filter(l => !l.bookedAt && ["Won", "Scheduled", "Contacted"].includes(l.stage)).slice(0, 8).forEach((l, i) => {
      const d = new Date(base); d.setDate(base.getDate() + (i % 6));
      const s = slots[i % slots.length]; d.setHours(s[0], s[1], 0, 0);
      out.push({ lead: l, start: d, end: new Date(d.getTime() + 3600000), label: s[2], web: false });
    });
    return out.sort((a, b) => a.start - b.start);
  }
  function gcalUrl(ap) {
    const t = "Job: " + ap.lead.name + " — " + ap.lead.service;
    const det = "Customer: " + ap.lead.name + "\nPhone: " + ap.lead.phone + "\nService: " + ap.lead.service + "\nBooked via " + D.CLIENT.name + ".";
    return "https://calendar.google.com/calendar/render?action=TEMPLATE&text=" + encodeURIComponent(t) +
      "&dates=" + icsDate(ap.start) + "/" + icsDate(ap.end) + "&details=" + encodeURIComponent(det) + "&location=" + encodeURIComponent(ap.lead.city);
  }
  function downloadICS(ap) {
    const ics = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//JaggyAI//EN", "BEGIN:VEVENT",
      "UID:" + ap.start.getTime() + "@jaggyai", "DTSTART:" + icsDate(ap.start), "DTEND:" + icsDate(ap.end),
      "SUMMARY:Job: " + ap.lead.name + " - " + ap.lead.service,
      "DESCRIPTION:Customer " + ap.lead.name + " " + ap.lead.phone, "LOCATION:" + ap.lead.city,
      "END:VEVENT", "END:VCALENDAR"].join("\r\n");
    const u = URL.createObjectURL(new Blob([ics], { type: "text/calendar" }));
    const a = document.createElement("a"); a.href = u; a.download = ap.lead.name.replace(/\s+/g, "_") + ".ics"; a.click();
    setTimeout(() => URL.revokeObjectURL(u), 1000);
  }
  function viewCalendar(el) {
    let cs = {}; try { cs = JSON.parse(localStorage.getItem("jaggy_calendar:" + bizSlug(D.CLIENT.name)) || "{}"); } catch (e) {}
    const aps = appointments();
    const days = {}; aps.forEach(ap => { const k = ap.start.toDateString(); (days[k] = days[k] || []).push(ap); });
    const dayLabel = k => { const d = new Date(k), t = new Date(); t.setHours(0, 0, 0, 0); const diff = Math.round((d - t) / 86400000); return diff === 0 ? "Today" : diff === 1 ? "Tomorrow" : d.toLocaleDateString("en-US", { weekday: "long", month: "short", day: "numeric" }); };
    el.innerHTML =
      '<div class="card" style="max-width:780px;margin-bottom:18px"><h3 style="color:var(--text)">📲 Connect your calendar</h3>' +
      '<p style="font-size:13px;color:var(--muted);margin:6px 0 12px">Add your email, then every booking gets an <b>Add to Calendar</b> button — tap it and the job lands on your phone instantly.</p>' +
      '<div style="display:flex;gap:9px;flex-wrap:wrap;align-items:center">' +
      '<input id="calEmail" placeholder="you@yourbusiness.ca" value="' + esc(cs.email || D.CLIENT.email || "") + '" style="background:var(--bg2);border:1px solid var(--line);border-radius:9px;padding:10px 13px;color:var(--text);font-size:14px;width:250px">' +
      '<button class="btn" id="calSave" style="width:auto;padding:10px 18px">Save</button>' +
      '<span id="calMsg" class="bimsg"></span></div>' +
      '<p style="font-size:12px;color:var(--muted2);margin-top:10px">💡 Want it fully hands-free (no tapping)? Google Calendar 2-way sync connects when you go live.</p></div>' +
      '<p class="section-note">Upcoming jobs — tap <b>📅 Google</b> or <b>⤓ Apple/Outlook</b> to drop any job straight onto your phone.</p>' +
      Object.keys(days).map(k =>
        '<div class="calday"><div class="caldayh">' + dayLabel(k) + '</div>' +
        days[k].map(ap => {
          const idx = aps.indexOf(ap);
          return '<div class="appt' + (ap.web ? ' web' : '') + '"><div class="apptime">' + ap.label + '</div>' +
            '<div class="apptmid"><div class="apptn">' + esc(ap.lead.name) + (ap.web ? ' <span class="webbadge">🌐 booked online</span>' : '') + '</div><div class="apptmeta">' + esc(ap.lead.service) + ' · ' + esc(ap.lead.city) + ' · ' + esc(ap.lead.phone) + '</div></div>' +
            '<div class="apptbtns"><a class="apptbtn g" href="' + gcalUrl(ap) + '" target="_blank" rel="noopener">📅 Google</a>' +
            '<button class="apptbtn ics" data-i="' + idx + '">⤓ Apple/Outlook</button></div></div>';
        }).join("") + '</div>').join("");
    el.querySelector("#calSave").onclick = () => {
      try { localStorage.setItem("jaggy_calendar:" + bizSlug(D.CLIENT.name), JSON.stringify({ email: document.getElementById("calEmail").value.trim() })); el.querySelector("#calMsg").textContent = "✓ Saved"; } catch (e) {}
    };
    el.querySelectorAll(".apptbtn.ics").forEach(b => b.onclick = () => downloadICS(aps[+b.dataset.i]));
  }

  /* ---------- MESSAGES (customer text inbox) ---------- */
  function viewMessages(el) {
    const threads = D.LEADS.slice(0, 8).map((l, i) => {
      const msgs = [
        { me: false, t: "Hi, is this " + D.CLIENT.name + "? I need help with " + l.service.toLowerCase() + "." },
        { me: true, t: "Hi " + l.name.split(" ")[0] + "! Yes — happy to help. Want me to book you a free quote?" },
      ];
      if (i % 2 === 0) msgs.push({ me: false, t: "Yes please — what times do you have?" });
      return { lead: l, msgs, unread: i < 2 };
    });
    el.innerHTML = '<p class="section-note">Text your customers right from here — full history, canned replies, one inbox. (Demo — real two-way texting connects to your number when you go live.)</p>' +
      '<div class="msgwrap"><div class="msglist">' +
      threads.map((th, i) => '<div class="msgli' + (i === 0 ? " active" : "") + '" data-i="' + i + '"><div class="msgav">' + esc(th.lead.name.charAt(0)) + '</div><div class="msgmid"><div class="msgn">' + esc(th.lead.name) + (th.unread ? ' <span class="msgdot"></span>' : "") + '</div><div class="msgprev">' + esc(th.msgs[th.msgs.length - 1].t).slice(0, 34) + '…</div></div></div>').join("") +
      '</div><div class="msgthread" id="msgThread"></div></div>';
    let cur = 0;
    function renderThread() {
      const th = threads[cur];
      document.getElementById("msgThread").innerHTML =
        '<div class="msgthh">' + esc(th.lead.name) + ' · ' + esc(th.lead.phone) + '</div>' +
        '<div class="msgbody">' + th.msgs.map(m => '<div class="mbub ' + (m.me ? "me" : "them") + '">' + esc(m.t) + '</div>').join("") + '</div>' +
        '<div class="msgquick">' + ["On my way 👍", "What's your address?", "You're booked! 🎉", "Here's your quote 📄"].map(q => '<button class="mq">' + esc(q) + '</button>').join("") + '</div>' +
        '<div class="msgin"><input id="msgInput" placeholder="Type a text…"><button class="btn" id="msgSend" style="width:auto;padding:0 18px">Send</button></div>';
      const send = t => { t = (t || document.getElementById("msgInput").value).trim(); if (!t) return; th.msgs.push({ me: true, t }); renderThread(); };
      document.getElementById("msgSend").onclick = () => send();
      document.getElementById("msgInput").addEventListener("keydown", e => { if (e.key === "Enter") send(); });
      document.querySelectorAll("#msgThread .mq").forEach(b => b.onclick = () => send(b.textContent));
    }
    el.querySelectorAll(".msgli").forEach(li => li.onclick = () => { cur = +li.dataset.i; el.querySelectorAll(".msgli").forEach(x => x.classList.remove("active")); li.classList.add("active"); renderThread(); });
    renderThread();
  }

  /* ---------- MONEY (quotes / invoices / payments) ---------- */
  function viewMoney(el) {
    const items = D.LEADS.filter(l => l.value > 0).map(l => ({
      name: l.name, service: l.service, amount: l.value,
      status: l.stage === "Completed" ? "Paid" : (["Won", "Scheduled"].includes(l.stage) ? "Sent" : "Draft")
    }));
    const sum = f => items.filter(f).reduce((s, x) => s + x.amount, 0);
    function rowsHtml() {
      return items.map((it, i) => {
        const badge = it.status === "Paid" ? "st-Won" : (it.status === "Sent" ? "st-QuoteSent" : "st-NewLead");
        const action = it.status === "Sent" ? '<button class="btn" data-pay="' + i + '" style="width:auto;padding:6px 12px;font-size:12px">Collect payment</button>'
          : (it.status === "Draft" ? '<button class="btn ghost" data-send="' + i + '" style="padding:6px 12px;font-size:12px">Send</button>'
            : '<span style="color:#86efac;font-size:12px;font-weight:700">✓ Paid</span>');
        return '<tr><td class="lead-name">' + esc(it.name) + '</td><td>' + esc(it.service) + '</td><td class="val">' + money(it.amount) + '</td><td><span class="st ' + badge + '">' + it.status + '</span></td><td style="text-align:right">' + action + '</td></tr>';
      }).join("");
    }
    function paint() {
      el.querySelector("#mInvoiced").textContent = money(sum(x => x.status !== "Draft"));
      el.querySelector("#mPaid").textContent = money(sum(x => x.status === "Paid"));
      el.querySelector("#mOut").textContent = money(sum(x => x.status === "Sent"));
      el.querySelector("#invBody").innerHTML = rowsHtml();
      el.querySelectorAll("[data-pay]").forEach(b => b.onclick = () => { items[+b.dataset.pay].status = "Paid"; paint(); });
      el.querySelectorAll("[data-send]").forEach(b => b.onclick = () => { items[+b.dataset.send].status = "Sent"; paint(); });
    }
    el.innerHTML =
      '<div class="grid kpis" style="margin-bottom:16px">' +
      '<div class="card kpi"><div class="label">Invoiced</div><div class="val" id="mInvoiced">—</div></div>' +
      '<div class="card kpi"><div class="label">Paid</div><div class="val" id="mPaid" style="color:#86efac">—</div></div>' +
      '<div class="card kpi"><div class="label">Outstanding</div><div class="val" id="mOut" style="color:#fcd34d">—</div></div></div>' +
      '<div class="toolbar"><button class="btn" id="newQuote" style="width:auto;padding:10px 18px">➕ New Quote</button><span class="section-note" style="margin:0">Build a quote → send → get paid. (Real card payments via Stripe when you go live.)</span></div>' +
      '<div id="quoteForm"></div>' +
      '<div class="tablewrap"><table><thead><tr><th>Customer</th><th>Service</th><th>Amount</th><th>Status</th><th style="text-align:right">Action</th></tr></thead><tbody id="invBody"></tbody></table></div>';
    el.querySelector("#newQuote").onclick = () => {
      el.querySelector("#quoteForm").innerHTML = '<div class="card" style="max-width:560px;margin-bottom:14px"><h3 style="color:var(--text)">New quote</h3>' +
        '<input id="qName" class="qin" placeholder="Customer name"><input id="qSvc" class="qin" placeholder="Service / description"><input id="qAmt" class="qin" type="number" placeholder="Amount ($)">' +
        '<button class="btn" id="qSave" style="width:auto;padding:10px 18px;margin-top:4px">Create &amp; Send</button></div>';
      el.querySelector("#qSave").onclick = () => {
        const n = el.querySelector("#qName").value.trim(), s = el.querySelector("#qSvc").value.trim(), a = parseInt(el.querySelector("#qAmt").value) || 0;
        if (!n || !a) return;
        items.unshift({ name: n, service: s || "Service", amount: a, status: "Sent" });
        el.querySelector("#quoteForm").innerHTML = ""; paint();
      };
    };
    paint();
  }

  /* ---------- BRANDING (multi-tenant) ---------- */
  function applyBranding() {
    const c = D.CLIENT;
    const set = (id, val) => { const e = document.getElementById(id); if (e) e.textContent = val; };
    set("loginBiz", "Automation Suite · " + c.name + " client portal");
    set("sideBiz", c.name);
    set("sideCity", c.city);
    set("acctName", c.name);
    set("acctEmail", c.email);
    set("acctAv", c.logoInitials);
    const av = document.querySelector(".acct .av"); if (av) av.textContent = c.logoInitials;
    const loginEmail = document.querySelector('#login input[type="email"]'); if (loginEmail) loginEmail.value = c.email;
    document.title = "JaggyAI — " + c.name;
    if (c.website) {
      const sb = document.getElementById("siteBtn");
      if (sb) { sb.href = c.website; sb.classList.remove("hidden"); }
    }
  }

  function inboundToast() {
    if (!D.CLIENT.newInbound) return;
    const n = D.CLIENT.newInbound;
    const t = document.createElement("div");
    t.style.cssText = "position:fixed;top:18px;right:18px;z-index:300;background:linear-gradient(135deg,#16a34a,#22c55e);color:#fff;padding:14px 18px;border-radius:12px;box-shadow:0 12px 40px rgba(0,0,0,.4);font-weight:700;font-size:14px;max-width:320px;animation:pop .4s ease";
    t.innerHTML = "🔔 " + n + " new lead" + (n > 1 ? "s" : "") + " from your website!<div style='font-weight:500;font-size:12.5px;opacity:.9;margin-top:3px'>Auto-captured + customer texted back. See it in Leads ↓</div>";
    document.body.appendChild(t);
    setTimeout(() => { t.style.transition = "opacity .4s"; t.style.opacity = "0"; setTimeout(() => t.remove(), 400); }, 6000);
  }

  /* ---------- BOOT ---------- */
  document.addEventListener("DOMContentLoaded", () => {
    applyBranding();
    inboundToast();
    initLogin();
    document.querySelectorAll(".nav button").forEach(b => b.addEventListener("click", () => go(b.dataset.v)));
    $("#drawerBg").addEventListener("click", closeDrawer);
  });
})();
