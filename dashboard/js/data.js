/* JaggyAI Automation Suite — demo data
   Self-contained. No external calls. Globals consumed by app.js. */

window.JAGGY = (function () {
  const CLIENT = {
    name: "Acme Roofing",
    city: "Surrey, BC",
    logoInitials: "AR",
    phone: "(778) 555-0100",
  };

  // Mirrors the Airtable CRM build. Stages drive the pipeline board.
  const STAGES = ["New Lead", "Contacted", "Quote Sent", "Won", "Scheduled", "Completed", "Lost"];

  const SOURCES = ["Website Chatbot", "Google LSA", "Google Ads", "Facebook Ads", "Website Form", "Referral"];

  const LEADS = [
    { id: 1,  name: "Dave Sandhu",    phone: "778-555-0142", email: "dave.sandhu@gmail.com",  city: "Surrey",          service: "Roof Replacement", source: "Google LSA",   stage: "New Lead",  score: "Hot",  value: 14200, response: "38 sec",    date: "Jun 9, 8:12 AM",  followups: 0, notes: "Asphalt shingle replacement, ~1,800 sq ft. Insurance claim after wind damage. Auto-text sent in 38s, asked to book inspection." },
    { id: 2,  name: "Jennifer Wong",  phone: "604-555-0188", email: "jenwong88@outlook.com",   city: "Burnaby",         service: "Leak / Emergency", source: "Google Ads",   stage: "Contacted", score: "Hot",  value: 2400,  response: "52 sec",    date: "Jun 8, 11:47 PM", followups: 1, notes: "Active leak in master bedroom ceiling. Submitted at 11:47pm — bot booked emergency visit for next morning automatically. The 'never miss a lead' hero example." },
    { id: 3,  name: "Mark Thompson",  phone: "778-555-0210", email: "mthompson@shaw.ca",       city: "Coquitlam",       service: "Roof Replacement", source: "Facebook Ads", stage: "Quote Sent", score: "Warm", value: 18750, response: "1 min 5 sec", date: "Jun 6, 5:30 PM",  followups: 2, notes: "Full tear-off + metal roof upgrade. Quote sent via e-sign link. 2 follow-ups sent automatically, opened quote twice." },
    { id: 4,  name: "Priya Patel",    phone: "604-555-0176", email: "priya.patel@gmail.com",   city: "Richmond",        service: "Roof Repair",      source: "Website Form", stage: "Won",       score: "Hot",  value: 3850,  response: "41 sec",    date: "Jun 4, 2:05 PM",  followups: 1, notes: "Missing/cracked shingles repair. Signed contract, deposit paid. Workflow auto-created job folder + QuickBooks invoice." },
    { id: 5,  name: "Greg Olsen",     phone: "778-555-0233", email: "golsen@telus.net",        city: "Langley",         service: "Roof Replacement", source: "Referral",     stage: "Scheduled", score: "Hot",  value: 21400, response: "2 min",     date: "May 30, 7:22 PM", followups: 0, notes: "Cedar shake to architectural shingle. Install booked Jun 16, crew calendar updated automatically, customer got confirmation text." },
    { id: 6,  name: "Amanda Foster",  phone: "604-555-0299", email: "afoster@gmail.com",       city: "North Vancouver", service: "Inspection",       source: "Google Ads",   stage: "Completed", score: "Warm", value: 9600,  response: "49 sec",    date: "May 22, 11:10 AM",followups: 1, notes: "Started as a free inspection lead, upsold to partial re-roof. Job done. Auto review-request text sent — left 5-star Google review." },
    { id: 7,  name: "Tyler Reid",     phone: "778-555-0301", email: "tyler.reid@gmail.com",    city: "Maple Ridge",     service: "Gutters",          source: "Facebook Ads", stage: "Contacted", score: "Warm", value: 1850,  response: "44 sec",    date: "Jun 7, 4:40 PM",  followups: 2, notes: "Gutter guard install. Replied to follow-up #2, asked about pricing. Warm." },
    { id: 8,  name: "Susan Mitchell", phone: "604-555-0155", email: "smitchell@shaw.ca",       city: "West Vancouver",  service: "Roof Replacement", source: "Google LSA",   stage: "Quote Sent", score: "Warm", value: 27800, response: "58 sec",    date: "Jun 5, 10:25 AM", followups: 1, notes: "Premium slate-look composite, large home. High-value quote out. Auto follow-up keeping it warm." },
    { id: 9,  name: "Carlos Mendez",  phone: "778-555-0277", email: "cmendez@gmail.com",       city: "New Westminster", service: "Roof Repair",      source: "Website Form", stage: "New Lead",  score: "Warm", value: 2950,  response: "36 sec",    date: "Jun 9, 7:55 AM",  followups: 0, notes: "Flashing repair around chimney. Just came in this morning, auto-responder fired, awaiting reply." },
    { id: 10, name: "Rachel Kim",     phone: "604-555-0318", email: "rachelkim@outlook.com",   city: "Delta",           service: "Leak / Emergency", source: "Google Ads",   stage: "Won",       score: "Hot",  value: 4600,  response: "47 sec",    date: "Jun 3, 8:15 PM",  followups: 1, notes: "Emergency leak repair, signed same week. Workflow handled contract + scheduling end to end." },
    { id: 11, name: "Brian Côté",     phone: "778-555-0190", email: "bcote@telus.net",         city: "Port Coquitlam",  service: "Inspection",       source: "Facebook Ads", stage: "Lost",      score: "Cold", value: 0,     response: "51 sec",    date: "May 28, 1:00 PM", followups: 4, notes: "Tire-kicker, just wanted a free inspection for insurance. 4 follow-ups, no booking. Auto-marked Lost after sequence ended — no human time wasted." },
    { id: 12, name: "Nicole Brar",    phone: "604-555-0264", email: "nicole.brar@gmail.com",   city: "Abbotsford",      service: "Roof Replacement", source: "Referral",     stage: "Completed", score: "Hot",  value: 16900, response: "40 sec",    date: "May 18, 9:30 AM", followups: 0, notes: "Referral from Priya Patel. Full replacement completed. Review request auto-sent, referral reward triggered." },
  ];

  // Live-activity feed (most recent first). The simulate button prepends to this.
  const ACTIVITY = [
    { time: "Just now",   icon: "bolt",  text: "Auto-response SMS sent to <b>Carlos Mendez</b> in 36 sec" },
    { time: "12 min ago", icon: "sms",   text: "Follow-up #2 sent to <b>Tyler Reid</b> — replied, marked Warm" },
    { time: "1 hr ago",   icon: "star",  text: "Review request sent to <b>Amanda Foster</b> — left 5★ on Google" },
    { time: "3 hrs ago",  icon: "doc",   text: "Quote e-signed by <b>Mark Thompson</b> — $18,750" },
    { time: "Last night", icon: "moon",  text: "<b>Jennifer Wong</b> booked emergency visit at 11:47 PM (you were asleep)" },
    { time: "Yesterday",  icon: "check", text: "Won-job workflow ran for <b>Rachel Kim</b>: contract → invoice → calendar" },
  ];

  // Automations shown on the Automations tab.
  const AUTOMATIONS = [
    { name: "Instant Lead Response",  on: true,  desc: "New lead → SMS + email in seconds, 24/7.",                 stat: "1,247 sent · avg 47 sec · 0 missed" },
    { name: "Missed-Call Text-Back",  on: true,  desc: "Missed call → instant 'sorry we missed you' text.",        stat: "312 recovered calls" },
    { name: "4-Step Follow-Up Drip",  on: true,  desc: "No reply? Auto SMS/email on day 1, 2, 4, 7.",              stat: "68% reply rate" },
    { name: "Quote Follow-Up",        on: true,  desc: "Quote sent but not signed → nudge sequence.",              stat: "+22% close rate" },
    { name: "Won-Job Workflow",       on: true,  desc: "Won → contract, e-sign, invoice, calendar, crew alert.",   stat: "~30 min saved / job" },
    { name: "Review Request",         on: true,  desc: "Job completed → ask for a Google review.",                 stat: "41 reviews · 4.9★ avg" },
    // --- LEAD GENERATION layer (brings NEW leads in, vs. converting existing ones) ---
    { name: "Google Business Booster", on: true, desc: "Keeps your Google listing optimized + auto-posts weekly so you show up in the map pack.", stat: "Top-3 local pack" },
    { name: "Review Engine → Ranking", on: true, desc: "More 5★ reviews = higher Google ranking = more calls. Runs automatically.", stat: "+37 reviews → +28% calls" },
    { name: "Ad Lead Capture",         on: true, desc: "Google/Facebook ad leads drop straight into your CRM + get the instant response.", stat: "$3.10 cost/lead" },
    { name: "Database Reactivation",   on: false, desc: "Texts past customers a seasonal offer to generate brand-new jobs from people you already know.", stat: "Paused" },
  ];

  // Revenue (last 4 weeks) for the dashboard trend chart.
  const REVENUE_TREND = [
    { label: "3 wks ago", value: 8200 },
    { label: "2 wks ago", value: 14600 },
    { label: "Last wk",   value: 11250 },
    { label: "This wk",   value: 22300 },
  ];

  // AI assistant knowledge — keyword-matched canned answers (feels like a real bot).
  const BOT_KB = [
    { keys: ["flat roof","flat","low slope"],                 a: "Yes! We install and repair flat & low-slope roofs (TPO, EPDM and torch-on). Want me to book a free inspection?" },
    { keys: ["area","serve","location","where","surrey","vancouver","langley"], a: "We cover all of Metro Vancouver & the Fraser Valley — Surrey, Burnaby, Langley, Coquitlam, Richmond and surrounding areas. What city are you in?" },
    { keys: ["price","cost","quote","estimate","how much","ballpark"], a: "Most roof replacements run $12k–$28k depending on size & material; repairs start around $400. I can get you an exact quote after a quick free inspection — want to book one?" },
    { keys: ["leak","emergency","urgent","water","dripping"],  a: "That sounds urgent — we offer emergency leak service and can usually be out within 24 hours. What's the best number to reach you, and I'll get a tech assigned right now." },
    { keys: ["book","appointment","inspection","schedule","when"], a: "Great — I can book a free inspection. What day works best, morning or afternoon? I'll text you a confirmation." },
    { keys: ["warranty","guarantee"],                          a: "All our work carries a workmanship warranty (up to 10 yrs) plus the manufacturer's material warranty. Happy to send details — what's your email?" },
    { keys: ["insurance","claim","storm","wind","hail"],       a: "We work with insurance claims all the time and can document storm/wind damage for your adjuster. Want to book a free damage inspection?" },
    { keys: ["financing","payment","finance","monthly"],       a: "Yes, we offer financing with monthly plans on larger jobs. I can include options with your quote — shall I book the inspection first?" },
    { keys: ["hours","open","time"],                           a: "Our crews work Mon–Sat, and this assistant + our booking line run 24/7 so you never have to wait. How can I help?" },
    { keys: ["hi","hello","hey","yo"],                         a: "Hi there! 👋 Thanks for reaching out to Acme Roofing. Are you looking for a repair, a full replacement, or an emergency leak fix?" },
    { keys: ["thanks","thank you","great","awesome"],          a: "You're welcome! 🙌 Anything else I can help with, or should I go ahead and book that free inspection?" },
  ];
  const BOT_FALLBACK = "Good question! I can help with roof repairs, replacements, leaks, inspections, pricing and booking. The fastest next step is a free inspection — want me to set one up?";

  // KPIs derived from leads.
  function kpis() {
    const booked = LEADS.filter(l => ["Won","Scheduled","Completed"].includes(l.stage))
                        .reduce((s,l)=>s+l.value,0);
    const openPipe = LEADS.filter(l => ["Quote Sent","Contacted","New Lead"].includes(l.stage))
                        .reduce((s,l)=>s+l.value,0);
    const won = LEADS.filter(l => ["Won","Scheduled","Completed"].includes(l.stage)).length;
    const closeable = LEADS.filter(l => l.stage !== "New Lead").length;
    const closeRate = Math.round((won / closeable) * 100);
    return { leads: LEADS.length, booked, openPipe, closeRate, avgResp: "47 sec", lost: 0 };
  }

  /* ---------- MULTI-TENANT BRANDING ----------
     If the page is opened with ?name=...&city=...&cat=..., rebrand the whole
     dashboard for that business. This is what lets ONE app serve all 1,400+
     demo sites — each gets their own branded dashboard from a URL. */
  const SERVICE_MAP = {
    "plumber":              ["Drain Cleaning","Leak / Emergency","Water Heater","Repipe","Fixture Install","Inspection"],
    "electrician":          ["Panel Upgrade","Rewire","Lighting Install","EV Charger","Emergency / No Power","Inspection"],
    "hvac contractor":      ["AC Install","Furnace Repair","Heat Pump","Maintenance","Emergency / No Heat","Duct Cleaning"],
    "landscaper":           ["Lawn Care","Yard Cleanup","Hardscaping","Irrigation","Tree / Hedge","Design Consult"],
    "general contractor":   ["Renovation","Home Addition","Kitchen Remodel","Bathroom Remodel","Repair / Emergency","Estimate"],
    "construction company": ["Renovation","New Build","Framing","Remodel","Repair / Emergency","Estimate"],
    "contractor":           ["Renovation","Addition","Remodel","Repair","Emergency Call-out","Estimate"],
    "excavating contractor":["Excavation","Grading","Drainage","Foundation Dig","Demolition","Site Prep"],
    "dry wall contractor":  ["Drywall Install","Patch / Repair","Taping & Mudding","Texture","Ceiling","Estimate"],
    "handyman/handywoman/handyperson": ["Repairs","Install / Assembly","Painting","Drywall Patch","Odd Jobs","Estimate"],
    "interior designer":    ["Consultation","Full Redesign","Space Planning","Staging","Materials & Color","Estimate"],
    "concrete contractor":  ["Driveway","Patio","Foundation","Sidewalk","Concrete Repair","Estimate"],
    "roofer":               ["Roof Replacement","Roof Repair","Leak / Emergency","Inspection","Gutters","Estimate"],
  };
  const DEFAULT_SERVICES = ["New Project","Repair","Maintenance","Emergency Call-out","Consultation","Estimate"];

  function initials(s){ return (s||"").replace(/[^A-Za-z ]/g,"").split(/\s+/).filter(Boolean).slice(0,2).map(w=>w[0].toUpperCase()).join("")||"JA"; }
  function slugify(s){ return (s||"").toLowerCase().replace(/[^a-z0-9]+/g,"-").replace(/^-|-$/g,""); }

  try {
    const p = new URLSearchParams(window.location.search);
    const bizName = p.get("name");
    if (bizName) {
      const city = p.get("city") || "British Columbia";
      const cat  = (p.get("cat") || "").toLowerCase().trim();
      const services = SERVICE_MAP[cat] || DEFAULT_SERVICES;
      const emergencyIdx = Math.max(0, services.findIndex(s => /emergency|leak|no power|no heat/i.test(s)));

      CLIENT.name = bizName;
      CLIENT.city = city;
      CLIENT.logoInitials = initials(bizName);
      CLIENT.phone = p.get("phone") || CLIENT.phone;
      CLIENT.email = "owner@" + (slugify(bizName) || "yourbusiness") + ".ca";
      CLIENT.category = p.get("cat") || "Service Business";
      CLIENT.website = p.get("site") || "";
      CLIENT.branded = true;

      // Remap each sample lead's service to this trade so it reads correctly.
      LEADS.forEach((l, idx) => {
        l.service = (l.score === "Hot" && (l.stage === "New Lead" || l.stage === "Contacted") && idx % 3 === 0)
          ? services[emergencyIdx] : services[idx % services.length];
      });
    } else {
      CLIENT.email = "owner@acmeroofing.ca";
      CLIENT.category = "Roofing";
      CLIENT.branded = false;
    }
  } catch (e) { /* file:// or no params — keep Acme defaults */ CLIENT.email = CLIENT.email || "owner@acmeroofing.ca"; }

  /* ---------- INBOUND LEADS FROM THE WEBSITE (chatbot / form) ----------
     The website chatbot writes leads to localStorage['jaggy_inbound_leads']
     (shared origin in production) and/or passes one via ?inbound=<json>.
     We pull them in so a website submission shows up live in the dashboard. */
  CLIENT.newInbound = 0;
  function ingest(lead, label) {
    if (!lead || !lead.name) return;
    LEADS.unshift({
      id: 1000 + LEADS.length,
      name: lead.name,
      phone: lead.phone || "",
      email: lead.email || ((lead.name || "lead").toLowerCase().replace(/[^a-z0-9]+/g, ".") + "@email.com"),
      city: lead.city || CLIENT.city,
      service: lead.service || (SERVICE_MAP[(CLIENT.category || "").toLowerCase()] || DEFAULT_SERVICES)[0],
      source: lead.source || "Website Chatbot",
      stage: "New Lead", score: "Hot",
      value: 0, response: "instant", date: "Just now", followups: 0,
      notes: (lead.msg || "Came in through the website.") + " — auto-captured, owner notified."
    });
    CLIENT.newInbound++;
    ACTIVITY.unshift({ time: "Just now", icon: "bolt",
      text: "New <b>" + (lead.source || "Website Chatbot") + "</b> lead — <b>" + (lead.name || "") + "</b> — auto-replied instantly" });
  }
  try {
    const ip = new URLSearchParams(window.location.search).get("inbound");
    if (ip) ingest(JSON.parse(decodeURIComponent(ip)), "url");
  } catch (e) {}
  try {
    const stored = JSON.parse(localStorage.getItem("jaggy_inbound_leads") || "[]");
    // Only show ones for this business (or all if dashboard isn't branded).
    stored.slice(-8).forEach(l => {
      if (!CLIENT.branded || !l.business || l.business === CLIENT.name) ingest(l, "ls");
    });
  } catch (e) {}

  return { CLIENT, STAGES, SOURCES, LEADS, ACTIVITY, AUTOMATIONS, REVENUE_TREND, BOT_KB, BOT_FALLBACK, kpis };
})();
