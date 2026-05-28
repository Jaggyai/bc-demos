"""
BC Demos site generator — config-driven.
Reads No_Website_Leads_Combined.xlsx, generates per-business demo HTML
using CATEGORY_CONFIG entries (one per trade vertical).
"""
import pandas as pd
import re, os, datetime, sys
sys.stdout.reconfigure(encoding='utf-8')

XLSX = r'C:/Users/jmang/OneDrive/Desktop/No_Website_Leads_Combined.xlsx'
OUT_ROOT = r'C:/Users/jmang/OneDrive/Desktop/Claude access/bc-demos'

# ============ CITY CONFIG ============

CITY_CONFIG = {
    'Victoria':       ('victoria',       'Greater Victoria',     ['Victoria','Oak Bay','Saanich','Esquimalt','View Royal','Colwood','Langford','Sooke','Sidney','North Saanich','Central Saanich','James Bay','Fairfield','Fernwood']),
    'Surrey':         ('surrey',         'Surrey & South Fraser',['Surrey','Newton','Cloverdale','Fleetwood','Guildford','Whalley','South Surrey','White Rock','Delta','Langley','Tsawwassen','Ladner']),
    'Vancouver':      ('vancouver',      'Metro Vancouver',      ['Downtown','West End','Kitsilano','Mount Pleasant','Fairview','Kerrisdale','Marpole','East Vancouver','Strathcona','Yaletown','Point Grey','Dunbar']),
    'Chilliwack':     ('chilliwack',     'the Fraser Valley',    ['Chilliwack','Sardis','Promontory','Yarrow','Cultus Lake','Rosedale','Greendale','Vedder Crossing','Hope','Agassiz']),
    'Abbotsford':     ('abbotsford',     'the Fraser Valley',    ['Abbotsford','Mission','Aldergrove','Sumas Mountain','McCallum','Clearbrook','Sevenoaks','East Abbotsford','West Abbotsford','Matsqui']),
    'Kelowna':        ('kelowna',        'the Okanagan',         ['Kelowna','West Kelowna','Lake Country','Peachland','Glenmore','Rutland','Mission','Mid-Town','Lower Mission','Upper Mission']),
    'Kamloops':       ('kamloops',       'the Thompson-Okanagan',['Kamloops','Brocklehurst','North Shore','Sahali','Aberdeen','Westsyde','Valleyview','Juniper Ridge','Dallas','Barnhartvale']),
    'Richmond':       ('richmond',       'Metro Vancouver',      ['Richmond','Steveston','Brighouse','Thompson','Hamilton','East Richmond','Sea Island','Bridgeport','Granville','Broadmoor']),
    'Prince George':  ('prince-george',  'Northern BC',          ['Prince George','College Heights','Hart','Heritage','Westwood','Foothills','College Park','Spruceland','Pinewood','Lakewood']),
    'Nanaimo':        ('nanaimo',        'Central Vancouver Island', ['Nanaimo','Lantzville','Cedar','Chase River','North Nanaimo','South Nanaimo','Departure Bay','Hammond Bay','Pleasant Valley','Old City']),
    'Burnaby':        ('burnaby',        'Metro Vancouver',      ['Burnaby','Brentwood','Metrotown','Edmonds','Lougheed','Burnaby Heights','North Burnaby','South Burnaby','Cariboo','Capitol Hill']),
    'Coquitlam':      ('coquitlam',      'Metro Vancouver',      ['Coquitlam','Port Coquitlam','Port Moody','Burke Mountain','Westwood Plateau','Coquitlam Centre','Maillardville','Eagle Ridge']),
    'New Westminster':('new-westminster','Metro Vancouver',      ['New Westminster','Queens Park','Sapperton','Uptown','Downtown','Glenbrooke North','West End','Connaught Heights']),
    'North Vancouver':('north-vancouver','the North Shore',      ['North Vancouver','Lynn Valley','Lonsdale','Deep Cove','Capilano','Edgemont','Grouse Mountain','Seymour']),
    'Rosedale':       ('rosedale',       'the Fraser Valley',    ['Rosedale','Chilliwack','Sardis','Greendale','Yarrow','Promontory','Agassiz']),
    'CPG':            ('prince-george',  'Northern BC',          ['Prince George','College Heights','Hart','Heritage','Westwood','Foothills']),
    'Victoria West':  ('victoria',       'Greater Victoria',     ['Victoria','Esquimalt','Saanich','Oak Bay','View Royal','Colwood','Langford']),
}

def city_info(city_name):
    if not city_name or pd.isna(city_name):
        return None
    return CITY_CONFIG.get(str(city_name).strip())

# ============ HELPERS ============

def slugify(name: str) -> str:
    s = name.lower()
    s = re.sub(r"[''`]", '', s)
    s = re.sub(r'[^a-z0-9]+', '-', s)
    s = re.sub(r'-+', '-', s).strip('-')
    return s

def clean_name(name: str) -> str:
    name = re.sub(r'(Ltd|Inc|Corp)\d+\b', r'\1', name)
    return name.strip()

def brand_mark(name: str) -> str:
    skip = {'the','a','an','&','and','of'}
    words = [w for w in re.split(r'[\s\-]+', name) if w and w.lower() not in skip]
    letters = ''.join(w[0].upper() for w in words[:2])
    return letters or 'BC'

def format_phone(raw):
    if pd.isna(raw) or not raw:
        return None, None
    digits = re.sub(r'\D', '', str(raw))
    if digits.startswith('1') and len(digits) == 11:
        digits = digits[1:]
    if len(digits) != 10:
        return None, None
    tel = '+1' + digits
    display = f'({digits[0:3]}) {digits[3:6]}-{digits[6:10]}'
    return tel, display

# ============ SVG ICON LIBRARY ============

SVG_PHONE = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"/></svg>'
SVG_ARROW = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><line x1="5" y1="12" x2="19" y2="12"/><polyline points="12 5 19 12 12 19"/></svg>'
SVG_PIN = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/></svg>'
SVG_CLOCK = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>'
SVG_STAR = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>'
SVG_CHECK = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3"><polyline points="20 6 9 17 4 12"/></svg>'

# Service-card icons (named for clarity in configs)
ICONS = {
    'emergency': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2L4 7v10l8 5 8-5V7l-8-5zM12 22V12M4 7l8 5 8-5"/></svg>',
    'clock': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/></svg>',
    'chart': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M2 12h6l3-9 4 18 3-9h4"/></svg>',
    'shield': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/></svg>',
    'building': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 21V10a4 4 0 0 1 4-4h10a4 4 0 0 1 4 4v11"/><path d="M3 21h18M9 21V14M15 21V14M12 6V2"/></svg>',
    'search': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>',
    'home': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>',
    'wrench': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"/></svg>',
    'bars': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M2 20h.01M7 20v-4M12 20v-8M17 20V8M22 4v16"/></svg>',
    'bolt': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>',
    'leaf': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M2 22s4-10 14-10c4 0 6 2 6 2s-2 8-12 8c-4 0-8 0-8 0z"/><path d="M2 22c0-6 4-12 12-12"/></svg>',
    'droplet': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2.69l5.66 5.66a8 8 0 1 1-11.31 0z"/></svg>',
    'tree': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 22V8M8 8a4 4 0 0 1 8 0M5 12a3 3 0 1 1 6 0M13 12a3 3 0 1 1 6 0"/></svg>',
    'truck': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="1" y="3" width="15" height="13"/><polygon points="16 8 20 8 23 11 23 16 16 16 16 8"/><circle cx="5.5" cy="18.5" r="2.5"/><circle cx="18.5" cy="18.5" r="2.5"/></svg>',
    'pickaxe': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 3l6 6M9 9l9 9M21 3l-9 9M3 21l9-9"/></svg>',
    'paint': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M19 11h2a1 1 0 0 1 1 1v2a1 1 0 0 1-1 1h-2zM5 11h14v6a4 4 0 0 1-4 4H9a4 4 0 0 1-4-4z"/></svg>',
    'layers': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="12 2 2 7 12 12 22 7 12 2"/><polyline points="2 17 12 22 22 17"/><polyline points="2 12 12 17 22 12"/></svg>',
    'thermometer': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 14.76V3.5a2.5 2.5 0 0 0-5 0v11.26a4.5 4.5 0 1 0 5 0z"/></svg>',
    'snow': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="12" y1="2" x2="12" y2="22"/><line x1="2" y1="12" x2="22" y2="12"/><line x1="4.93" y1="4.93" x2="19.07" y2="19.07"/><line x1="19.07" y1="4.93" x2="4.93" y2="19.07"/></svg>',
    'grid': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/></svg>',
    'sparkles': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 3v3M12 18v3M3 12h3M18 12h3M5.6 5.6l2.1 2.1M16.3 16.3l2.1 2.1M5.6 18.4l2.1-2.1M16.3 7.7l2.1-2.1"/></svg>',
    'hammer': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 12l-8.5 8.5a2.12 2.12 0 0 1-3-3L11 9"/><path d="M17.64 15L22 10.64L17.64 6.27"/><path d="M5 14l-4 4"/></svg>',
    'cube': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/></svg>',
    'fence': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 18V8l2-2v12M10 18V6l2-2v14M16 18V8l2-2v12"/><line x1="2" y1="12" x2="22" y2="12"/><line x1="2" y1="18" x2="22" y2="18"/></svg>',
}

# ============ SHARED CSS ============

CSS = '''
* { margin: 0; padding: 0; box-sizing: border-box; }
:root {
  --navy: #0a2540; --navy-dark: #061a30; --orange: #ff6b35; --orange-dark: #e55525;
  --gray-50: #f8fafc; --gray-100: #f1f5f9; --gray-200: #e2e8f0; --gray-500: #64748b;
  --gray-700: #334155; --gray-900: #0f172a; --white: #ffffff;
  --shadow: 0 10px 40px rgba(10, 37, 64, 0.08); --shadow-lg: 0 20px 60px rgba(10, 37, 64, 0.15);
}
html { scroll-behavior: smooth; }
body { font-family: 'Inter', system-ui, sans-serif; color: var(--gray-900); line-height: 1.6; -webkit-font-smoothing: antialiased; }
img { max-width: 100%; display: block; }
a { color: inherit; text-decoration: none; }
.nav { position: fixed; top: 0; left: 0; right: 0; background: rgba(255,255,255,0.96); backdrop-filter: blur(12px); z-index: 100; box-shadow: 0 1px 0 rgba(10,37,64,0.06); }
.nav-inner { max-width: 1200px; margin: 0 auto; padding: 16px 24px; display: flex; align-items: center; justify-content: space-between; gap: 24px; }
.brand { display: flex; align-items: center; gap: 12px; }
.brand-mark { width: 40px; height: 40px; background: var(--navy); color: var(--white); border-radius: 8px; display: flex; align-items: center; justify-content: center; font-weight: 900; font-size: 18px; letter-spacing: -0.5px; }
.brand-text { font-weight: 800; font-size: 17px; letter-spacing: -0.3px; color: var(--navy); }
.brand-sub { font-size: 11px; color: var(--gray-500); font-weight: 500; text-transform: uppercase; letter-spacing: 0.8px; }
.nav-links { display: flex; gap: 32px; }
.nav-links a { font-size: 14px; font-weight: 500; color: var(--gray-700); transition: color 0.2s; }
.nav-links a:hover { color: var(--orange); }
.nav-cta { background: var(--orange); color: var(--white); padding: 12px 22px; border-radius: 8px; font-weight: 700; font-size: 14px; transition: all 0.2s; display: inline-flex; align-items: center; gap: 8px; }
.nav-cta:hover { background: var(--orange-dark); transform: translateY(-1px); }
.nav-cta svg { width: 16px; height: 16px; }
@media (max-width: 768px) { .nav-links { display: none; } .brand-sub { display: none; } }
.hero { position: relative; min-height: 92vh; padding-top: 90px; display: flex; align-items: center; overflow: hidden; background: var(--navy); }
.hero-bg { position: absolute; inset: 0; }
.hero-content { position: relative; max-width: 1200px; margin: 0 auto; padding: 60px 24px; width: 100%; }
.hero-eyebrow { display: inline-flex; align-items: center; gap: 8px; background: rgba(255,107,53,0.15); color: var(--orange); padding: 8px 16px; border-radius: 100px; font-size: 13px; font-weight: 600; margin-bottom: 24px; border: 1px solid rgba(255,107,53,0.25); }
.hero-eyebrow::before { content: ''; width: 8px; height: 8px; background: var(--orange); border-radius: 50%; box-shadow: 0 0 12px var(--orange); animation: pulse 2s infinite; }
@keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.5; } }
.hero h1 { color: var(--white); font-size: clamp(38px, 5.5vw, 68px); font-weight: 900; line-height: 1.05; letter-spacing: -1.5px; margin-bottom: 24px; max-width: 760px; }
.hero h1 span { color: var(--orange); }
.hero-sub { color: rgba(255,255,255,0.85); font-size: clamp(17px, 1.6vw, 20px); max-width: 580px; margin-bottom: 40px; line-height: 1.6; }
.hero-ctas { display: flex; gap: 16px; flex-wrap: wrap; margin-bottom: 48px; }
.btn-primary { background: var(--orange); color: var(--white); padding: 18px 32px; border-radius: 10px; font-weight: 700; font-size: 16px; display: inline-flex; align-items: center; gap: 10px; transition: all 0.2s; box-shadow: 0 8px 24px rgba(255,107,53,0.35); }
.btn-primary:hover { background: var(--orange-dark); transform: translateY(-2px); box-shadow: 0 12px 32px rgba(255,107,53,0.45); }
.btn-primary svg, .btn-secondary svg { width: 20px; height: 20px; }
.btn-secondary { background: rgba(255,255,255,0.1); color: var(--white); padding: 18px 32px; border-radius: 10px; font-weight: 600; font-size: 16px; display: inline-flex; align-items: center; gap: 10px; border: 1px solid rgba(255,255,255,0.2); transition: all 0.2s; backdrop-filter: blur(10px); }
.btn-secondary:hover { background: rgba(255,255,255,0.18); border-color: rgba(255,255,255,0.35); }
.hero-trust { display: flex; gap: 40px; flex-wrap: wrap; padding-top: 32px; border-top: 1px solid rgba(255,255,255,0.12); }
.trust-item { color: rgba(255,255,255,0.9); }
.trust-num { font-size: 28px; font-weight: 800; color: var(--white); letter-spacing: -0.5px; }
.trust-label { font-size: 13px; color: rgba(255,255,255,0.65); font-weight: 500; }
section { padding: 100px 24px; }
.container { max-width: 1200px; margin: 0 auto; }
.section-eyebrow { display: inline-block; color: var(--orange); font-weight: 700; font-size: 13px; letter-spacing: 1.5px; text-transform: uppercase; margin-bottom: 16px; }
.section-title { font-size: clamp(32px, 4vw, 48px); font-weight: 800; color: var(--navy); letter-spacing: -1px; line-height: 1.15; margin-bottom: 20px; }
.section-sub { font-size: 18px; color: var(--gray-500); max-width: 640px; line-height: 1.6; }
.services { background: var(--gray-50); }
.services-head { text-align: center; max-width: 720px; margin: 0 auto 64px; }
.services-head .section-sub { margin: 0 auto; }
.services-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 24px; }
.service-card { background: var(--white); padding: 36px 32px; border-radius: 16px; transition: all 0.3s; border: 1px solid var(--gray-200); }
.service-card:hover { transform: translateY(-6px); box-shadow: var(--shadow-lg); border-color: transparent; }
.service-icon { width: 56px; height: 56px; background: rgba(255,107,53,0.1); border-radius: 12px; display: flex; align-items: center; justify-content: center; margin-bottom: 24px; color: var(--orange); }
.service-icon svg { width: 28px; height: 28px; }
.service-card h3 { font-size: 20px; font-weight: 700; color: var(--navy); margin-bottom: 12px; letter-spacing: -0.3px; }
.service-card p { color: var(--gray-500); font-size: 15px; line-height: 1.6; }
.why { background: var(--white); }
.why-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 80px; align-items: center; }
@media (max-width: 900px) { .why-grid { grid-template-columns: 1fr; gap: 48px; } }
.why-image { position: relative; border-radius: 20px; overflow: hidden; box-shadow: var(--shadow-lg); }
.why-image img { width: 100%; height: 100%; object-fit: cover; aspect-ratio: 4/5; }
.why-badge { position: absolute; bottom: 24px; left: 24px; background: var(--white); padding: 20px 24px; border-radius: 14px; box-shadow: var(--shadow); display: flex; align-items: center; gap: 16px; }
.why-badge-num { font-size: 36px; font-weight: 900; color: var(--orange); letter-spacing: -1px; line-height: 1; }
.why-badge-label { font-size: 12px; color: var(--gray-500); font-weight: 600; text-transform: uppercase; letter-spacing: 1px; }
.why-badge-sub { font-size: 14px; color: var(--navy); font-weight: 700; }
.why-list { margin-top: 32px; display: flex; flex-direction: column; gap: 20px; }
.why-item { display: flex; gap: 16px; align-items: flex-start; }
.why-check { width: 28px; height: 28px; background: var(--orange); border-radius: 50%; display: flex; align-items: center; justify-content: center; flex-shrink: 0; color: var(--white); }
.why-check svg { width: 16px; height: 16px; }
.why-item-title { font-weight: 700; color: var(--navy); margin-bottom: 4px; font-size: 16px; }
.why-item-desc { font-size: 14px; color: var(--gray-500); line-height: 1.5; }
.reviews { background: var(--navy); color: var(--white); position: relative; overflow: hidden; }
.reviews-bg { position: absolute; inset: 0; opacity: 0.08; }
.reviews-inner { position: relative; }
.reviews-head { text-align: center; margin-bottom: 64px; }
.reviews-head .section-title { color: var(--white); }
.reviews-head .section-sub { color: rgba(255,255,255,0.7); margin: 0 auto; }
.google-rating { display: inline-flex; align-items: center; gap: 20px; background: rgba(255,255,255,0.06); padding: 20px 32px; border-radius: 16px; margin-bottom: 24px; border: 1px solid rgba(255,255,255,0.1); }
.google-rating-num { font-size: 48px; font-weight: 900; color: var(--white); letter-spacing: -1.5px; line-height: 1; }
.google-rating-stars { font-size: 22px; color: #ffc940; letter-spacing: 3px; margin-bottom: 4px; }
.google-rating-count { font-size: 13px; color: rgba(255,255,255,0.65); }
.testimonials { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 24px; }
.testimonial { background: rgba(255,255,255,0.05); padding: 32px; border-radius: 16px; border: 1px solid rgba(255,255,255,0.1); }
.testimonial-stars { color: #ffc940; letter-spacing: 2px; margin-bottom: 16px; font-size: 14px; }
.testimonial-quote { color: rgba(255,255,255,0.92); font-size: 15px; line-height: 1.7; margin-bottom: 24px; }
.testimonial-author { display: flex; align-items: center; gap: 12px; }
.testimonial-avatar { width: 44px; height: 44px; background: var(--orange); border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: 700; color: var(--white); font-size: 16px; }
.testimonial-name { font-weight: 700; color: var(--white); font-size: 14px; }
.testimonial-meta { font-size: 12px; color: rgba(255,255,255,0.55); }
.area { background: var(--gray-50); text-align: center; }
.area-head { max-width: 720px; margin: 0 auto 48px; }
.area-head .section-sub { margin: 0 auto; }
.area-grid { display: flex; flex-wrap: wrap; justify-content: center; gap: 12px; max-width: 800px; margin: 0 auto; }
.area-chip { background: var(--white); padding: 14px 24px; border-radius: 100px; font-weight: 600; color: var(--navy); border: 1px solid var(--gray-200); font-size: 14px; transition: all 0.2s; }
.area-chip:hover { border-color: var(--orange); color: var(--orange); transform: translateY(-2px); }
.contact { background: var(--white); }
.contact-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 64px; align-items: start; }
@media (max-width: 900px) { .contact-grid { grid-template-columns: 1fr; gap: 48px; } }
.contact-info-block { background: var(--gray-50); padding: 40px; border-radius: 20px; }
.contact-info-item { display: flex; gap: 20px; align-items: flex-start; padding: 20px 0; border-bottom: 1px solid var(--gray-200); }
.contact-info-item:last-child { border-bottom: none; }
.contact-icon { width: 48px; height: 48px; background: var(--white); border-radius: 12px; display: flex; align-items: center; justify-content: center; color: var(--orange); flex-shrink: 0; box-shadow: var(--shadow); }
.contact-icon svg { width: 22px; height: 22px; }
.contact-label { font-size: 12px; color: var(--gray-500); font-weight: 600; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 4px; }
.contact-value { font-size: 17px; color: var(--navy); font-weight: 700; }
.contact-value a:hover { color: var(--orange); }
.contact-form h2 { margin-bottom: 8px; }
.contact-form-sub { color: var(--gray-500); margin-bottom: 32px; }
.form-row { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-bottom: 16px; }
@media (max-width: 600px) { .form-row { grid-template-columns: 1fr; } }
.form-field { display: flex; flex-direction: column; gap: 6px; margin-bottom: 16px; }
.form-field label { font-size: 13px; font-weight: 600; color: var(--gray-700); }
.form-field input, .form-field textarea, .form-field select { padding: 14px 16px; border: 1px solid var(--gray-200); border-radius: 10px; font-size: 15px; font-family: inherit; transition: border-color 0.2s; background: var(--white); }
.form-field input:focus, .form-field textarea:focus, .form-field select:focus { outline: none; border-color: var(--orange); }
.form-field textarea { resize: vertical; min-height: 120px; }
.form-submit { background: var(--orange); color: var(--white); padding: 16px 32px; border: none; border-radius: 10px; font-weight: 700; font-size: 16px; cursor: pointer; transition: all 0.2s; box-shadow: 0 8px 24px rgba(255,107,53,0.3); width: 100%; }
.form-submit:hover { background: var(--orange-dark); transform: translateY(-2px); }
.final-cta { background: linear-gradient(135deg, var(--orange) 0%, var(--orange-dark) 100%); color: var(--white); text-align: center; padding: 80px 24px; }
.final-cta h2 { font-size: clamp(28px, 4vw, 42px); font-weight: 800; margin-bottom: 16px; letter-spacing: -0.5px; }
.final-cta p { font-size: 18px; margin-bottom: 32px; opacity: 0.95; max-width: 580px; margin-left: auto; margin-right: auto; }
.final-cta .btn-white { background: var(--white); color: var(--orange); padding: 18px 36px; border-radius: 10px; font-weight: 700; font-size: 17px; display: inline-flex; align-items: center; gap: 10px; transition: all 0.2s; box-shadow: 0 12px 32px rgba(0,0,0,0.15); }
.final-cta .btn-white:hover { transform: translateY(-2px); box-shadow: 0 16px 40px rgba(0,0,0,0.2); }
.footer { background: var(--navy-dark); color: rgba(255,255,255,0.7); padding: 64px 24px 32px; }
.footer-grid { max-width: 1200px; margin: 0 auto; display: grid; grid-template-columns: 2fr 1fr 1fr 1fr; gap: 48px; margin-bottom: 48px; }
@media (max-width: 768px) { .footer-grid { grid-template-columns: 1fr 1fr; gap: 32px; } }
.footer h4 { color: var(--white); font-size: 14px; font-weight: 700; margin-bottom: 20px; text-transform: uppercase; letter-spacing: 1px; }
.footer ul { list-style: none; }
.footer ul li { margin-bottom: 10px; font-size: 14px; }
.footer ul li a:hover { color: var(--orange); }
.footer-brand p { font-size: 14px; line-height: 1.7; max-width: 360px; margin-top: 16px; }
.footer-bottom { max-width: 1200px; margin: 0 auto; padding-top: 32px; border-top: 1px solid rgba(255,255,255,0.1); display: flex; justify-content: space-between; flex-wrap: wrap; gap: 16px; font-size: 13px; }
'''

# ============ CATEGORY CONFIG ============
# Each entry defines the copy/services/testimonials for one trade vertical.
# All other rendering is shared via render_business().

CATEGORY_CONFIG = {
    'plumbers': {
        'assets': 'plumber',
        'industry': 'Plumbing & Gas',
        'role': 'plumber',
        'role_title': 'Plumber',
        'page_title_suffix': "{city}'s Trusted Plumbing & Gas Experts",
        'meta_desc': '{name} — Trusted {city} plumbers. Licensed, insured. Emergency plumbing, drain cleaning, water heaters, gas fitting.',
        'hero_eyebrow': 'Available Now · Same-Day Service',
        'hero_h1_pre': "{city}'s Trusted ",
        'hero_h1_hl': 'Plumbing & Gas',
        'hero_h1_post': ' Experts.',
        'hero_sub': 'Family-owned. Licensed. Insured. From emergency leaks to full bathroom renovations, {name} keeps {city} homes running with quality plumbing and gas work you can trust.',
        'nav_cta_noquote': 'Free Quote',
        'hero_cta_secondary': 'Request Free Quote',
        'trust3_num': '24/7', 'trust3_label': 'Emergency Service',
        'trust4_num': '100%', 'trust4_label': 'Licensed & Insured',
        'services_eyebrow': 'What We Do',
        'services_title': 'Full-Service Plumbing & Gas Solutions',
        'services_sub': 'From a dripping tap to a full repipe, our certified plumbers handle every job with the craftsmanship {city} homeowners trust.',
        'services': [
            ('emergency', 'Emergency Repairs', 'Burst pipes, major leaks, no hot water — we respond fast, day or night, with no overtime surprises.'),
            ('clock', 'Drain Cleaning', 'Clogged sinks, slow drains, sewer backups. Camera inspection and hydro-jetting available.'),
            ('chart', 'Water Heaters', 'Tank, tankless, heat-pump installs. Service, repair, and replacement of any major brand.'),
            ('shield', 'Gas Fitting', 'Certified gas line installation, repair, and inspection. Furnaces, ranges, BBQs, fireplaces.'),
            ('building', 'Bathroom & Kitchen', 'Full renovations and fixture upgrades — toilets, faucets, showers, garburators, dishwashers.'),
            ('search', 'Leak Detection', 'Non-invasive leak location using thermal imaging and acoustic detection. We find it before we cut.'),
        ],
        'badge_label': '{city} Plumber',
        'why_title': 'Old-school craftsmanship. Modern service.',
        'why_sub': "We run our business the way you'd want a plumber to: real-time arrival updates, upfront pricing, and clean job sites every single time.",
        'why_points': [
            ('Upfront, Flat-Rate Pricing', 'Know the cost before we lift a wrench. No surprises, no hourly meter running.'),
            ('Licensed Red Seal Plumbers', 'Every tech is fully ticketed, gas-certified, and background-checked.'),
            ('5-Year Workmanship Warranty', "If our work fails, we come back free. That's our promise."),
            ('Same-Day Service Available', 'Most calls answered same-day. 24/7 emergency line always open.'),
        ],
        'reviews_title': 'Trusted by {city} homeowners.',
        'testimonials': [
            ('SM', 'Sarah M.', '"Called in the morning with a leaking water heater. They were at my house within hours, replaced it cleanly, and the price was exactly what they quoted. Honest crew."'),
            ('DC', 'David C.', '"Honestly the only plumber I trust in {city}. Always professional, always fair. Showed up on time, fixed the problem, didn\'t try to upsell me anything I didn\'t need."'),
            ('JL', 'Jennifer L.', '"Full bathroom remodel — they handled the rough-in, fixtures, and gas line for our new tankless heater. Clean work, on schedule, and they cleaned up better than they found it."'),
        ],
        'area_sub': 'From downtown to the outskirts, our trucks cover every neighbourhood in the area.',
        'contact_title': "Need a plumber? We're ready.",
        'form_title': 'Request a free quote',
        'form_sub': "Tell us what's going on. We'll get back to you within 1 business hour.",
        'form_type_label': 'Service Needed',
        'form_options': ['Emergency Repair', 'Drain Cleaning', 'Water Heater', 'Gas Fitting', 'Bathroom / Kitchen', 'Leak Detection', 'Other / Not Sure'],
        'form_message_label': "Tell us what's going on",
        'form_message_placeholder': 'Describe the issue or project...',
        'form_submit': 'Send My Request →',
        'final_cta_title': "Got a plumbing problem? Let's solve it today.",
        'final_cta_sub': 'One call. Fast response. Honest pricing.',
        'final_cta_btn_phone': 'Call {phone} Now',
        'final_cta_btn_form': 'Request Free Quote →',
        'footer_para': 'Family-owned and operated in {city}, BC. Licensed Red Seal plumbers and certified gas fitters serving {region}.',
        'footer_services': ['Emergency Repairs', 'Drain Cleaning', 'Water Heaters', 'Gas Fitting', 'Leak Detection'],
        'footer_cert': 'Licensed · Insured · Red Seal Certified',
        'contact_label_phone': 'Call Us 24/7',
        'hours': ('Mon–Fri: 7am – 6pm', 'Emergency: 24/7'),
    },
    'contractors': {
        'assets': 'contractor',
        'industry': 'Construction & Renovation',
        'role': 'contractor', 'role_title': 'Builder',
        'page_title_suffix': "{city} General Contractor & Custom Home Builder",
        'meta_desc': '{name} — Trusted {city} general contractor. Custom homes, renovations, additions. Licensed, insured, on-budget, on-schedule.',
        'hero_eyebrow': 'Now Booking · Free Consultations',
        'hero_h1_pre': '{city} ', 'hero_h1_hl': 'Custom Homes', 'hero_h1_post': ' & Renovation Experts.',
        'hero_sub': 'Licensed. Insured. Family-owned. From kitchen remodels to ground-up custom builds, {name} delivers quality construction across {region} — on schedule, on budget, every time.',
        'nav_cta_noquote': 'Free Estimate', 'hero_cta_secondary': 'Get a Free Estimate',
        'trust3_num': '2-Yr', 'trust3_label': 'Workmanship Warranty',
        'trust4_num': '100%', 'trust4_label': 'Licensed & Insured',
        'services_eyebrow': 'What We Build',
        'services_title': 'From Custom Homes to Full Renovations',
        'services_sub': "Whether you're starting from scratch or transforming what's already there, our crews bring the same craftsmanship to every project — big or small.",
        'services': [
            ('home', 'Custom Home Builds', 'Ground-up new construction, designed around how you actually live. From foundation to finish.'),
            ('wrench', 'Major Renovations', "Whole-home transformations, structural rework, open-concept conversions. We handle the messy stuff."),
            ('building', 'Kitchen & Bath Remodels', 'Premium finishes, modern layouts, smart storage. Where the home actually gets used.'),
            ('shield', 'Additions & Extensions', 'Second storeys, garages, in-law suites, sunrooms. Add the square footage you need.'),
            ('bars', 'Commercial Buildouts', 'Office, retail, restaurant fit-outs. Permit-savvy crews who know commercial code.'),
            ('clock', 'Design-Build Services', 'One team, one timeline, one budget. We handle design, permits, and build under one roof.'),
        ],
        'badge_label': '{city} Builder',
        'why_title': 'Built right. Delivered on time.',
        'why_sub': 'Every project gets a detailed scope, a clear timeline, and a single point of contact. No mystery change orders. No "the trades didn\'t show" excuses. Just clean execution.',
        'why_points': [
            ('Detailed, Upfront Quotes', 'Line-item breakdowns. You know exactly what every dollar is doing before we break ground.'),
            ('Licensed & WCB Insured', 'Fully ticketed, bonded, and insured. Your home and our crew are protected.'),
            ('2-Year Workmanship Warranty', 'We stand behind every job. If our work fails, we come back free.'),
            ('On-Schedule, On-Budget', 'Weekly progress updates. No surprise overruns. We hit the dates we commit to.'),
        ],
        'reviews_title': 'Trusted by {city} homeowners.',
        'testimonials': [
            ('MR', 'Michael R.', '"Did a full kitchen renovation for us — finished on time, on budget, and the quality is incredible. Worth every dollar. Crew was professional from start to finish."'),
            ('KH', 'Karen H.', '"Built our custom home from the ground up. Communication was perfect, every decision was made WITH us not for us. We\'re moved in and still amazed at the craftsmanship. Would 100% hire again."'),
            ('TB', 'Tom B.', '"Two-storey addition with a basement suite. They handled permits, design, demo, and build. We never felt out of the loop. Honest, skilled, and fair priced."'),
        ],
        'area_sub': 'Residential and commercial projects throughout the region.',
        'contact_title': "Got a project? Let's scope it.",
        'form_title': 'Request a free estimate',
        'form_sub': "Tell us about your project. We'll get back to you within 1 business day with next steps.",
        'form_type_label': 'Project Type',
        'form_options': ['Custom Home Build', 'Major Renovation', 'Kitchen Remodel', 'Bathroom Remodel', 'Addition / Extension', 'Commercial Project', 'Other / Not Sure'],
        'form_message_label': 'Tell us about your project',
        'form_message_placeholder': "Square footage, timeline, budget range, anything you've already decided...",
        'form_submit': 'Send My Project Details →',
        'final_cta_title': "Got a build or reno in mind? Let's talk.",
        'final_cta_sub': 'Free consultations. Detailed quotes. No surprises.',
        'final_cta_btn_phone': 'Call {phone} Today',
        'final_cta_btn_form': 'Get a Free Estimate →',
        'footer_para': 'Family-owned general contractor based in {city}, BC. Custom homes, renovations, and commercial projects throughout {region}. Licensed, bonded, and WCB insured.',
        'footer_services': ['Custom Home Builds', 'Major Renovations', 'Kitchen & Bath', 'Additions', 'Design-Build'],
        'footer_cert': 'Licensed · Bonded · WCB Insured',
        'contact_label_phone': 'Call Us',
        'hours': ('Mon–Fri: 7am – 6pm', 'Sat by appointment'),
        'area_title_verb': 'building across',
    },
    'electricians': {
        'assets': 'electrician',
        'industry': 'Electrical Services',
        'role': 'electrician', 'role_title': 'Electrician',
        'page_title_suffix': "{city}'s Trusted Electrical Contractors",
        'meta_desc': '{name} — Licensed {city} electricians. Panel upgrades, EV chargers, wiring, lighting, repairs. 24/7 emergency service.',
        'hero_eyebrow': 'Available Now · 24/7 Emergency',
        'hero_h1_pre': "{city}'s Licensed ", 'hero_h1_hl': 'Electricians', 'hero_h1_post': ' & EV Charger Experts.',
        'hero_sub': 'Red Seal certified. Fully insured. From panel upgrades to whole-home rewires, {name} delivers safe, code-compliant electrical work across {region} — every time.',
        'nav_cta_noquote': 'Free Quote', 'hero_cta_secondary': 'Request Free Quote',
        'trust3_num': '24/7', 'trust3_label': 'Emergency Service',
        'trust4_num': '100%', 'trust4_label': 'Licensed & Insured',
        'services_eyebrow': 'What We Do',
        'services_title': 'Full-Service Residential & Commercial Electrical',
        'services_sub': "From a flickering light switch to a new service panel, our Red Seal electricians handle every job to code — fast, clean, and warrantied.",
        'services': [
            ('bolt', 'Panel Upgrades & Service', '100A, 200A, 400A. Old fuse panels swapped for modern breakers. BC Hydro coordination handled.'),
            ('home', 'Whole-Home Rewires', 'Old knob-and-tube? Aluminum? We bring your home up to current code, room by room.'),
            ('chart', 'EV Charger Installs', 'Level 2 home chargers, Tesla wall connectors, commercial DC fast. SaveBC rebate eligible installs.'),
            ('sparkles', 'Lighting Design & Install', 'Pot lights, smart switches, landscape lighting, dimmers, in-cabinet strips, accent lighting.'),
            ('emergency', 'Repairs & Troubleshooting', 'Tripping breakers, dead outlets, mystery loads. We diagnose fast and fix it right.'),
            ('bars', 'Commercial & Tenant Improvements', 'Office, retail, restaurant electrical. New circuits, lighting plans, permit drawings.'),
        ],
        'badge_label': '{city} Electrician',
        'why_title': 'Code-correct. Clean install. Backed by warranty.',
        'why_sub': "Electrical isn't a place to cut corners. We pull every permit, ground every neutral, label every breaker. The kind of work that passes inspection on the first visit.",
        'why_points': [
            ('Red Seal Certified Techs', 'Every electrician on our crew is fully ticketed, bonded, and police-checked.'),
            ('Permits & Inspections Handled', "We pull permits and book inspections so you don't have to. Always to code, always passed."),
            ('5-Year Workmanship Warranty', 'If anything we install fails within 5 years, we come back and fix it free.'),
            ('Upfront, Fixed-Price Quotes', "No hourly meter running. You know the cost before we open a wall."),
        ],
        'reviews_title': 'Trusted by {city} homeowners.',
        'testimonials': [
            ('JT', 'James T.', '"Did our panel upgrade and EV charger install in one day. Cleanly run conduit, labelled every breaker. Total pros."'),
            ('LK', 'Linda K.', '"We had a tripping breaker mystery for months. They diagnosed it in 20 minutes and fixed it the same visit. Honest pricing, no upsell."'),
            ('PS', 'Paul S.', '"Whole-home rewire on a 1960s house. They were respectful of the place, cleaned up daily, finished on schedule. Inspection passed first try."'),
        ],
        'area_sub': 'Residential, commercial, and service calls throughout the region.',
        'contact_title': "Need an electrician? Let's get it sorted.",
        'form_title': 'Request a free quote',
        'form_sub': "Tell us what you need. We'll respond within 1 business hour.",
        'form_type_label': 'Service Needed',
        'form_options': ['Panel Upgrade', 'EV Charger Install', 'Whole-Home Rewire', 'Lighting Install', 'Repair / Troubleshoot', 'Commercial Work', 'Other / Not Sure'],
        'form_message_label': 'Tell us what you need',
        'form_message_placeholder': 'Describe the project or issue...',
        'form_submit': 'Send My Request →',
        'final_cta_title': "Need an electrician? We're ready.",
        'final_cta_sub': 'One call. Fast response. Code-correct work, every time.',
        'final_cta_btn_phone': 'Call {phone} Now',
        'final_cta_btn_form': 'Request Free Quote →',
        'footer_para': 'Family-owned electrical contractor in {city}, BC. Red Seal certified, fully insured, serving {region} with residential and commercial electrical work.',
        'footer_services': ['Panel Upgrades', 'EV Chargers', 'Rewires', 'Lighting', 'Repairs'],
        'footer_cert': 'Licensed · Insured · Red Seal Certified',
        'contact_label_phone': 'Call Us 24/7',
        'hours': ('Mon–Fri: 7am – 6pm', 'Emergency: 24/7'),
    },
    'landscapers': {
        'assets': 'landscaper',
        'industry': 'Landscape Design & Maintenance',
        'role': 'landscaper', 'role_title': 'Landscaper',
        'page_title_suffix': '{city} Landscape Design, Maintenance & Hardscaping',
        'meta_desc': '{name} — Trusted {city} landscapers. Design, lawn care, hardscaping, irrigation. Free estimates.',
        'hero_eyebrow': 'Now Booking · Spring & Summer',
        'hero_h1_pre': '{city} ', 'hero_h1_hl': 'Landscape', 'hero_h1_post': ' Design, Care & Maintenance.',
        'hero_sub': 'Award-winning landscape design. Reliable seasonal maintenance. From new builds to weekly mow-and-blow, {name} keeps {region} yards looking their best.',
        'nav_cta_noquote': 'Free Estimate', 'hero_cta_secondary': 'Get a Free Estimate',
        'trust3_num': 'Insured', 'trust3_label': 'Crews & Equipment',
        'trust4_num': '100%', 'trust4_label': 'Satisfaction Guarantee',
        'services_eyebrow': 'What We Do',
        'services_title': 'Full-Service Landscape Solutions',
        'services_sub': "Whether you want a brand new outdoor space or just want your lawn to look its best every week, our crews handle it all.",
        'services': [
            ('leaf', 'Landscape Design', 'Custom design plans for new builds, renovations, and re-imagined yards. 2D & 3D renderings available.'),
            ('tree', 'Lawn Care & Mowing', 'Weekly mowing, trimming, edging, blowing. Reliable schedules. Healthy lawns, happy neighbours.'),
            ('cube', 'Hardscaping', 'Stone patios, retaining walls, walkways, paver driveways. Built to last decades.'),
            ('droplet', 'Irrigation & Sprinklers', 'New installs, repairs, smart controllers. Water-wise systems that save you money.'),
            ('sparkles', 'Garden & Planting', 'Beds, borders, native plants, perennials, mature trees. Curated to your style and climate.'),
            ('snow', 'Seasonal Cleanups & Snow', 'Spring + fall cleanups, gutter clearing, snow removal. Property maintenance year-round.'),
        ],
        'badge_label': '{city} Landscaper',
        'why_title': 'Outdoors that look great. Year after year.',
        'why_sub': "Beautiful yards take more than weekly mowing. We bring designers, horticulturists, and skilled crews together so your outdoor space gets better every season.",
        'why_points': [
            ('Certified Horticulturists', 'Trained crews who know plants, soil, and climate. Right plant in the right place every time.'),
            ('Fully Insured Crews', 'Liability + WCB insured. Your property and our team are protected.'),
            ('Reliable Schedule', "When we say we'll be there Tuesday, we're there Tuesday. No no-shows."),
            ('Free On-Site Estimates', "We walk the property with you, listen to what you want, then quote it. No pressure."),
        ],
        'reviews_title': 'Trusted by {city} homeowners.',
        'testimonials': [
            ('AB', 'Anna B.', '"Best decision we made was hiring these guys. Our front yard went from forgotten to the prettiest on the street. They listen, they care, they show up."'),
            ('RD', 'Rick D.', '"Full backyard redesign — flagstone patio, garden beds, irrigation, the works. Finished early, on budget, and the design is exactly what we wanted."'),
            ('MC', 'Megan C.', '"Reliable weekly maintenance since 2022. Lawn always looks perfect, beds always tidy. Never have to chase them down. Worth every dollar."'),
        ],
        'area_sub': 'Residential and commercial landscape services across the region.',
        'contact_title': "Got a yard to transform? Let's chat.",
        'form_title': 'Request a free estimate',
        'form_sub': "Tell us about your property. We'll set up a free on-site walkthrough.",
        'form_type_label': 'Service Needed',
        'form_options': ['Landscape Design', 'Lawn Maintenance', 'Hardscaping', 'Irrigation', 'Garden Install', 'Seasonal Cleanup', 'Other / Not Sure'],
        'form_message_label': 'Tell us about your yard',
        'form_message_placeholder': 'Size, what you have, what you want, timeline...',
        'form_submit': 'Send My Request →',
        'final_cta_title': "Ready to love your yard again?",
        'final_cta_sub': 'Free estimates. Honest advice. Beautiful results.',
        'final_cta_btn_phone': 'Call {phone} Today',
        'final_cta_btn_form': 'Get a Free Estimate →',
        'footer_para': 'Local landscape company in {city}, BC. Design, maintenance, hardscaping, and seasonal property care throughout {region}.',
        'footer_services': ['Landscape Design', 'Lawn Care', 'Hardscaping', 'Irrigation', 'Cleanups'],
        'footer_cert': 'Insured · ISA Certified · WCB Covered',
        'contact_label_phone': 'Call Us',
        'hours': ('Mon–Sat: 7am – 6pm', 'Closed Sundays'),
    },
    'excavating': {
        'assets': 'excavator',
        'industry': 'Excavating & Site Prep',
        'role': 'excavator operator', 'role_title': 'Operator',
        'page_title_suffix': '{city} Excavating, Demolition & Site Preparation',
        'meta_desc': '{name} — Licensed {city} excavating contractor. Site prep, foundation digging, demolition, drainage. Insured operators.',
        'hero_eyebrow': 'Booking This Season',
        'hero_h1_pre': '{city} ', 'hero_h1_hl': 'Excavating', 'hero_h1_post': ' & Site Prep Specialists.',
        'hero_sub': 'Heavy equipment. Skilled operators. From a single-day stump removal to full subdivision site prep, {name} brings the iron and the experience to do it right.',
        'nav_cta_noquote': 'Free Estimate', 'hero_cta_secondary': 'Get a Free Estimate',
        'trust3_num': 'WCB', 'trust3_label': 'Insured Operators',
        'trust4_num': '100%', 'trust4_label': 'Safety Certified',
        'services_eyebrow': 'What We Do',
        'services_title': 'Heavy-Duty Excavating & Site Services',
        'services_sub': "Modern fleet of excavators, skid steers, and dump trucks operated by certified, experienced crews.",
        'services': [
            ('pickaxe', 'Site Preparation', 'Clearing, grubbing, grading, surveying. Get your build site ready for foundations.'),
            ('hammer', 'Demolition', 'Whole-home, garage, and structure demolition. Permit handling and disposal included.'),
            ('truck', 'Foundation Digs', 'Basement holes, footing trenches, dig-down conversions. Precision to grade.'),
            ('layers', 'Trenching & Utilities', 'Water, sewer, gas, electrical service trenches. BC One Call coordination handled.'),
            ('cube', 'Drainage & Grading', 'French drains, perimeter drains, swales, surface grading. Solve drainage right.'),
            ('home', 'Driveways & Parking Pads', 'Excavate, base prep, compact. Ready for paving, concrete, or gravel.'),
        ],
        'badge_label': '{city} Excavator',
        'why_title': 'The right iron. The right operator. Done right.',
        'why_sub': "Site work is the hidden foundation of every great build. Get it wrong and you pay for years. We get it right the first time.",
        'why_points': [
            ('Modern, Maintained Fleet', '5-ton mini-ex to 30-ton excavators. Tracked, wheeled, and skid steer options.'),
            ('Certified, Insured Operators', "Years of seat time, all WCB insured, all police-checked. Safety first, always."),
            ('Permits & Locates Handled', "We pull permits, call before we dig, coordinate with utilities. Nothing skipped."),
            ('Clean Job Sites Daily', "We leave the property cleaner than we found it. Every single day."),
        ],
        'reviews_title': 'Trusted by {city} builders & homeowners.',
        'testimonials': [
            ('GW', 'Greg W.', '"Excavated our basement for the new addition. Operator was incredibly precise — barely touched the existing slab. Cleaned up perfect. Best operator we\'ve worked with."'),
            ('JF', 'Janelle F.', '"Tore down our old garage and prepped the pad in one day. Permit, demo, haul-away, grade — turn-key. Highly recommend."'),
            ('BM', 'Bryan M.', '"Solved our flooding issues with a French drain install. They diagnosed it correctly when two other contractors got it wrong. Honest crew."'),
        ],
        'area_sub': 'Residential, commercial, and subdivision site work across the region.',
        'contact_title': "Got a site that needs work? Let's see it.",
        'form_title': 'Request a free estimate',
        'form_sub': "Tell us about the project. We'll set up a free on-site assessment.",
        'form_type_label': 'Service Needed',
        'form_options': ['Site Preparation', 'Demolition', 'Foundation Dig', 'Trenching', 'Drainage', 'Driveway / Parking', 'Other / Not Sure'],
        'form_message_label': 'Tell us about the site',
        'form_message_placeholder': 'Lot size, what you need done, timeline, access notes...',
        'form_submit': 'Send My Request →',
        'final_cta_title': "Got a site to prep? Let's dig in.",
        'final_cta_sub': 'Free estimates. Insured operators. Clean execution.',
        'final_cta_btn_phone': 'Call {phone} Today',
        'final_cta_btn_form': 'Get a Free Estimate →',
        'footer_para': 'Excavating & site preparation contractor in {city}, BC. Heavy equipment, certified operators, and full WCB coverage serving {region}.',
        'footer_services': ['Site Prep', 'Demolition', 'Foundation', 'Trenching', 'Drainage'],
        'footer_cert': 'Licensed · WCB Insured · Safety Certified',
        'contact_label_phone': 'Call Us',
        'hours': ('Mon–Fri: 7am – 5pm', 'Saturdays by request'),
    },
    'drywall': {
        'assets': 'drywall',
        'industry': 'Drywall, Paint & Stucco',
        'role': 'drywaller', 'role_title': 'Finisher',
        'page_title_suffix': '{city} Drywall, Painting & Interior Finishing',
        'meta_desc': '{name} — {city} drywall, paint, insulation, and stucco specialists. Clean finishes, on-schedule delivery.',
        'hero_eyebrow': 'Now Booking',
        'hero_h1_pre': '{city} ', 'hero_h1_hl': 'Drywall, Paint', 'hero_h1_post': ' & Interior Finish.',
        'hero_sub': 'Smooth walls. Crisp lines. Clean job sites. From a single bedroom touch-up to whole-home interiors, {name} brings the finishing touch homes deserve.',
        'nav_cta_noquote': 'Free Quote', 'hero_cta_secondary': 'Get a Free Quote',
        'trust3_num': 'Insured', 'trust3_label': 'Crews & Materials',
        'trust4_num': '100%', 'trust4_label': 'Satisfaction Guarantee',
        'services_eyebrow': 'What We Do',
        'services_title': 'Full Interior Finish Solutions',
        'services_sub': "Drywall, mudding, taping, painting, texture, insulation, and stucco — all under one roof, all to the same exacting standard.",
        'services': [
            ('grid', 'Drywall Installation', 'New builds, additions, basement finishes, ceilings. Cleanly hung, perfectly aligned.'),
            ('sparkles', 'Mudding & Taping', 'Three-coat finishes, Level 5 smooth, knockdown texture, orange peel. Whatever the room needs.'),
            ('paint', 'Interior Painting', 'Premium paints, dustless prep, crisp cut-ins. Walls, trim, ceilings, doors.'),
            ('layers', 'Insulation', 'Batt, blown-in, spray foam. Increase comfort, lower energy bills, meet code.'),
            ('home', 'Stucco & Exterior', 'Acrylic stucco, EIFS, traditional cement. Patches, repairs, full re-coats.'),
            ('wrench', 'Repairs & Touch-Ups', 'Cracks, holes, water damage, popcorn ceiling removal. Make it look brand new.'),
        ],
        'badge_label': '{city} Finisher',
        'why_title': 'Finished walls. Spotless job sites.',
        'why_sub': "Interior finishing is where the build feels like a home. We treat your space the way we'd want ours treated — clean tools, drop sheets, daily cleanup.",
        'why_points': [
            ('Master-Level Finishers', 'Years of taping, mudding, and paint experience. Level 5 finish capable.'),
            ('Dust Control & Drop Sheets', "We protect your floors, your furniture, and your air quality. Always."),
            ('Premium Paints & Materials', 'We use Benjamin Moore, Sherwin-Williams, Cloverdale. No bargain-bin shortcuts.'),
            ('Clean-Up Same Day', "Job site is spotless before we leave. You shouldn't have to clean after us."),
        ],
        'reviews_title': 'Trusted by {city} homeowners.',
        'testimonials': [
            ('RW', 'Rebecca W.', '"Repainted our entire main floor — walls, trim, ceilings. Crisp lines, no drips, perfect cleanup. Felt like a new house when they left."'),
            ('JC', 'John C.', '"Finished the basement drywall — Level 5 in the theatre room. Walls are mirror smooth. Painters couldn\'t believe the prep job."'),
            ('AT', 'Amy T.', '"Removed all the popcorn ceilings and re-textured. No drama, no dust everywhere, no mess. Honest pricing too."'),
        ],
        'area_sub': 'Residential and commercial interior finishing across the region.',
        'contact_title': "Got walls that need work?",
        'form_title': 'Request a free quote',
        'form_sub': "Tell us about your project. We'll get back to you within 1 business day.",
        'form_type_label': 'Service Needed',
        'form_options': ['Drywall Install', 'Drywall Repair', 'Interior Painting', 'Stucco', 'Insulation', 'Texture / Finish', 'Other / Not Sure'],
        'form_message_label': 'Tell us about the project',
        'form_message_placeholder': 'Rooms, square footage, finishes, timeline...',
        'form_submit': 'Send My Request →',
        'final_cta_title': "Ready for finished walls done right?",
        'final_cta_sub': 'Free quotes. Clean crews. Premium materials.',
        'final_cta_btn_phone': 'Call {phone} Today',
        'final_cta_btn_form': 'Get a Free Quote →',
        'footer_para': 'Drywall, paint, and finishing contractor in {city}, BC. Residential and commercial interior work throughout {region}.',
        'footer_services': ['Drywall Install', 'Mudding & Taping', 'Painting', 'Insulation', 'Stucco'],
        'footer_cert': 'Licensed · Insured · WCB Covered',
        'contact_label_phone': 'Call Us',
        'hours': ('Mon–Fri: 7am – 6pm', 'Sat by appointment'),
    },
    'concrete': {
        'assets': 'concrete',
        'industry': 'Concrete, Masonry & Paving',
        'role': 'mason', 'role_title': 'Mason',
        'page_title_suffix': '{city} Concrete, Masonry & Paving Contractor',
        'meta_desc': '{name} — Trusted {city} concrete, masonry, and paving specialists. Driveways, foundations, walkways, retaining walls.',
        'hero_eyebrow': 'Now Booking · Spring & Summer',
        'hero_h1_pre': '{city} ', 'hero_h1_hl': 'Concrete', 'hero_h1_post': ' & Masonry Specialists.',
        'hero_sub': 'Decades of experience. Built to last generations. From driveways to retaining walls to stamped patios, {name} pours and sets stone the way it should be done.',
        'nav_cta_noquote': 'Free Estimate', 'hero_cta_secondary': 'Get a Free Estimate',
        'trust3_num': 'Insured', 'trust3_label': 'Crews & Trucks',
        'trust4_num': '100%', 'trust4_label': 'Built-to-Last Warranty',
        'services_eyebrow': 'What We Build',
        'services_title': 'Full-Service Concrete & Masonry',
        'services_sub': "From precision pours to artisan masonry, our crews bring craftsmanship to every project, big or small.",
        'services': [
            ('home', 'Driveways & Walkways', 'Plain, stamped, exposed aggregate, broom-finish. Permits and forms handled.'),
            ('cube', 'Foundations & Footings', 'New builds, additions, repairs, helical pile follow-ups. Engineered to spec.'),
            ('layers', 'Retaining Walls', 'Block, allan block, natural stone, poured concrete. Engineered solutions for grade changes.'),
            ('sparkles', 'Stamped & Decorative', 'Stamped patios, coloured concrete, sandblasted finishes. Concrete that looks expensive.'),
            ('grid', 'Paving & Asphalt', 'Asphalt driveways, parking lots, repairs, sealcoating. Long-life prep work.'),
            ('hammer', 'Brick & Stone Masonry', 'Brick walls, stone veneer, fireplaces, columns, pillars. Old-world craftsmanship.'),
        ],
        'badge_label': '{city} Mason',
        'why_title': 'Pours and stonework that last decades.',
        'why_sub': "We don't skip prep. We don't cheap out on rebar. We don't rush the cure. The work is done the way concrete and stone deserve.",
        'why_points': [
            ('Properly Engineered Forms', 'Tied rebar, proper drainage, code-spec base. The work nobody sees but everyone depends on.'),
            ('Premium Ready-Mix', '32 MPa min for driveways, 25 MPa for walks. We don\'t cut psi to save dollars.'),
            ('5-Year Workmanship Warranty', 'Cracking, settling, finish issues — we come back free if our work fails in 5 years.'),
            ('Clean Sites, Clean Pours', 'Forms removed, slop hauled away, edges cleaned. Spotless when we leave.'),
        ],
        'reviews_title': 'Trusted by {city} homeowners.',
        'testimonials': [
            ('TP', 'Tara P.', '"Stamped concrete patio that looks like flagstone. 5 years later — zero cracks, colour still rich. Best money we spent on the yard."'),
            ('NS', 'Nick S.', '"Driveway replacement. They demoed the old one, prepped base, poured 32 MPa with rebar, finished broom. Done in 3 days. Spotless work."'),
            ('CB', 'Carol B.', '"Retaining wall and stone facade on our fireplace. The masonry work is breathtaking. Old-world craftsmanship is hard to find. So glad we hired them."'),
        ],
        'area_sub': 'Concrete, masonry, and paving across the region.',
        'contact_title': "Got concrete or stone work?",
        'form_title': 'Request a free estimate',
        'form_sub': "Tell us what you're planning. Free on-site assessment available.",
        'form_type_label': 'Service Needed',
        'form_options': ['Driveway / Walkway', 'Foundation', 'Retaining Wall', 'Stamped / Decorative', 'Paving / Asphalt', 'Masonry', 'Other / Not Sure'],
        'form_message_label': 'Tell us about the project',
        'form_message_placeholder': 'Dimensions, finish, timeline, access...',
        'form_submit': 'Send My Request →',
        'final_cta_title': "Ready to pour something that lasts?",
        'final_cta_sub': 'Free estimates. Premium materials. Decades of experience.',
        'final_cta_btn_phone': 'Call {phone} Today',
        'final_cta_btn_form': 'Get a Free Estimate →',
        'footer_para': 'Concrete and masonry contractor in {city}, BC. Driveways, foundations, retaining walls, and decorative finishes throughout {region}.',
        'footer_services': ['Driveways', 'Foundations', 'Retaining Walls', 'Stamped Concrete', 'Masonry'],
        'footer_cert': 'Licensed · Insured · WCB Covered',
        'contact_label_phone': 'Call Us',
        'hours': ('Mon–Sat: 7am – 5pm', 'Closed Sundays'),
    },
    'interior': {
        'assets': 'interior',
        'industry': 'Interior Design & Renovation',
        'role': 'designer', 'role_title': 'Designer',
        'page_title_suffix': '{city} Interior Design & Renovation Studio',
        'meta_desc': '{name} — {city} interior design and renovation studio. Kitchens, baths, full-home transformations.',
        'hero_eyebrow': 'Now Booking · Free Consultations',
        'hero_h1_pre': '{city} ', 'hero_h1_hl': 'Interior Design', 'hero_h1_post': ' & Renovation Studio.',
        'hero_sub': 'Award-winning design. White-glove project management. From a single-room refresh to a whole-home transformation, {name} creates spaces that feel like you.',
        'nav_cta_noquote': 'Book Consultation', 'hero_cta_secondary': 'Book a Consultation',
        'trust3_num': 'Concept', 'trust3_label': 'to Completion',
        'trust4_num': 'Insured', 'trust4_label': 'Studio & Trades',
        'services_eyebrow': 'What We Do',
        'services_title': 'Full-Service Design & Renovation',
        'services_sub': "Design, source, manage, and execute — all in-house. You get one point of contact and a beautifully finished space.",
        'services': [
            ('sparkles', 'Interior Design', 'Concept boards, 3D renders, material curation, lighting plans. Design that fits how you actually live.'),
            ('home', 'Kitchen Remodels', 'Cabinetry, countertops, lighting, layout reworks. The heart of the home, done right.'),
            ('droplet', 'Bath Remodels', 'Steam showers, double vanities, heated floors, freestanding tubs. Spa-level finish.'),
            ('cube', 'Cabinetry & Millwork', 'Custom built-ins, wardrobes, libraries, mudrooms. Made to your space, not from a catalogue.'),
            ('paint', 'Finishes & Styling', 'Paint colours, hardware, lighting, furniture, art. The details that elevate a renovation.'),
            ('building', 'Full-Home Renovations', "Whole-home overhauls. Layout changes, finishes, lighting, the works. One team, one timeline."),
        ],
        'badge_label': '{city} Designer',
        'why_title': 'Design that feels like home.',
        'why_sub': "We don't design for Instagram. We design for the way you live, cook, host, rest. Every choice is intentional, considered, and yours.",
        'why_points': [
            ('Award-Winning Designers', 'Years of residential design experience. Featured in BC Home + Garden, Western Living.'),
            ('In-House Trades', "Painters, finishers, cabinetmakers on staff. No relying on subs who can't agree on dates."),
            ('Fixed-Price Project Budgets', 'We quote the whole project. No mystery line items appearing mid-job.'),
            ('White-Glove Project Management', 'Weekly walkthroughs, schedule updates, clean job sites. We respect your home.'),
        ],
        'reviews_title': 'Loved by {city} homeowners.',
        'testimonials': [
            ('LM', 'Lauren M.', '"Our kitchen is a work of art and somehow still incredibly practical. They listened, sketched, then delivered. Worth every penny."'),
            ('SK', 'Samira K.', '"Whole-home renovation while we were living abroad. They sent weekly video updates, made small decisions for us, finished early. Magical."'),
            ('PD', 'Peter D.', '"Master bath of our dreams. Heated floors, steam shower, custom vanity. Everything about it elevated. The team is genuinely passionate."'),
        ],
        'area_sub': 'Residential design and renovation throughout the region.',
        'contact_title': "Ready to fall in love with your home?",
        'form_title': 'Book a free consultation',
        'form_sub': "Tell us about your space. We'll set up a complimentary 60-minute design consultation.",
        'form_type_label': 'Project Type',
        'form_options': ['Kitchen Remodel', 'Bath Remodel', 'Full-Home Renovation', 'Interior Design', 'Cabinetry', 'Other / Not Sure'],
        'form_message_label': 'Tell us about your space',
        'form_message_placeholder': 'Square footage, style direction, timeline, budget range...',
        'form_submit': 'Book My Consultation →',
        'final_cta_title': "Ready to design something beautiful?",
        'final_cta_sub': 'Complimentary consultations. Personal service. Stunning results.',
        'final_cta_btn_phone': 'Call {phone} Today',
        'final_cta_btn_form': 'Book a Consultation →',
        'footer_para': 'Interior design and renovation studio based in {city}, BC. Kitchens, baths, full-home transformations throughout {region}.',
        'footer_services': ['Interior Design', 'Kitchen Remodels', 'Bath Remodels', 'Cabinetry', 'Full-Home Renos'],
        'footer_cert': 'Licensed · Insured · WCB Covered',
        'contact_label_phone': 'Call Studio',
        'hours': ('Mon–Fri: 9am – 5pm', 'Weekends by appointment'),
    },
    'hvac': {
        'assets': 'hvac',
        'industry': 'HVAC, Heating & Cooling',
        'role': 'HVAC technician', 'role_title': 'Technician',
        'page_title_suffix': '{city} HVAC, Heating & Cooling Specialists',
        'meta_desc': '{name} — Licensed {city} HVAC contractor. Furnaces, AC, heat pumps, ductless mini-splits. 24/7 service.',
        'hero_eyebrow': 'Available Now · 24/7 Emergency',
        'hero_h1_pre': "{city}'s Trusted ", 'hero_h1_hl': 'Heating', 'hero_h1_post': ' & Cooling Experts.',
        'hero_sub': 'Heat pump specialists. Furnace pros. AC experts. From a no-heat emergency to a complete system replacement, {name} keeps {region} homes comfortable year-round.',
        'nav_cta_noquote': 'Free Quote', 'hero_cta_secondary': 'Get a Free Quote',
        'trust3_num': '24/7', 'trust3_label': 'Emergency Service',
        'trust4_num': '100%', 'trust4_label': 'Licensed & Insured',
        'services_eyebrow': 'What We Do',
        'services_title': 'Full-Service Heating, Cooling & Air',
        'services_sub': "Modern, energy-efficient systems installed and serviced by ticketed gas-and-refrigeration techs.",
        'services': [
            ('thermometer', 'Furnaces', 'Gas, electric, propane. New installs, replacements, repairs, tune-ups. Lennox, Carrier, Trane.'),
            ('snow', 'Air Conditioning', 'Central AC, ductless splits, heat pumps. Energy-efficient cooling for BC summers.'),
            ('chart', 'Heat Pumps', 'Cold-climate heat pumps with $11K+ rebate eligibility. Heating + cooling, one system.'),
            ('emergency', 'Emergency Repairs', "No heat in the middle of winter? No cold air in summer? We're on call 24/7."),
            ('clock', 'Maintenance Tune-Ups', 'Annual checks, filter changes, coil cleans. Keep your warranty valid, your bills low.'),
            ('sparkles', 'Indoor Air Quality', 'HRVs, ERVs, humidifiers, HEPA filtration, UV lights. Clean air, every breath.'),
        ],
        'badge_label': '{city} HVAC Tech',
        'why_title': 'Comfort done right. Backed by warranty.',
        'why_sub': "Your HVAC system is the heartbeat of your home. We install it properly, size it correctly, and stand behind the work for years.",
        'why_points': [
            ('Red Seal Gas + Refrigeration Techs', "All certified, all bondable. Every install is to code, every time."),
            ('Manufacturer-Trained', 'Lennox, Carrier, Trane, Mitsubishi factory trained. We know your system inside out.'),
            ('Rebate Paperwork Handled', "Up to $11,000 in heat pump rebates available. We handle the applications for you."),
            ('10-Year Warranty Available', 'Parts and labour warranty extensions on most major brand installs.'),
        ],
        'reviews_title': 'Trusted by {city} homeowners.',
        'testimonials': [
            ('NF', 'Nadia F.', '"Heat pump install — they handled the rebate paperwork ($8K back). System is whisper-quiet, hydro bill dropped 40%. So glad we switched."'),
            ('GH', 'Greg H.', '"No heat on a Saturday in January. Called at 8am, tech was here by 11, fixed by noon. Honest pricing, no overtime gouging. Lifelong customers."'),
            ('YS', 'Yulia S.', '"Annual maintenance contract for 4 years now. Furnace runs like new. They always show up on time, never push unnecessary upsells."'),
        ],
        'area_sub': 'Residential and commercial HVAC service across the region.',
        'contact_title': "Need HVAC service? Let's get you comfortable.",
        'form_title': 'Request a free quote',
        'form_sub': "Tell us what's going on. We respond within 1 business hour.",
        'form_type_label': 'Service Needed',
        'form_options': ['Furnace Service', 'AC Install / Repair', 'Heat Pump', 'Emergency Repair', 'Maintenance', 'Indoor Air Quality', 'Other / Not Sure'],
        'form_message_label': "Tell us what's happening",
        'form_message_placeholder': 'System type, age, what\'s wrong, urgency...',
        'form_submit': 'Send My Request →',
        'final_cta_title': "Cold? Hot? Stuck? We can help today.",
        'final_cta_sub': '24/7 emergency service. Licensed techs. Honest pricing.',
        'final_cta_btn_phone': 'Call {phone} Now',
        'final_cta_btn_form': 'Get a Free Quote →',
        'footer_para': 'Heating, cooling, and HVAC contractor in {city}, BC. Furnaces, AC, heat pumps, and indoor air quality systems throughout {region}.',
        'footer_services': ['Furnaces', 'Air Conditioning', 'Heat Pumps', 'Repairs', 'Maintenance'],
        'footer_cert': 'Licensed · Insured · Red Seal Certified',
        'contact_label_phone': 'Call Us 24/7',
        'hours': ('Mon–Fri: 7am – 6pm', 'Emergency: 24/7'),
    },
    'flooring': {
        'assets': 'flooring',
        'industry': 'Flooring & Tile',
        'role': 'flooring installer', 'role_title': 'Installer',
        'page_title_suffix': '{city} Flooring Installation & Tile Specialists',
        'meta_desc': '{name} — Trusted {city} flooring contractor. Hardwood, tile, vinyl, carpet, refinishing. Premium materials.',
        'hero_eyebrow': 'Now Booking',
        'hero_h1_pre': '{city} ', 'hero_h1_hl': 'Flooring', 'hero_h1_post': ' & Tile Specialists.',
        'hero_sub': 'Premium hardwood. Designer tile. Luxury vinyl. From a single bathroom to whole-home flooring, {name} installs floors that look beautiful and last decades.',
        'nav_cta_noquote': 'Free Estimate', 'hero_cta_secondary': 'Get a Free Estimate',
        'trust3_num': 'Insured', 'trust3_label': 'Crews & Materials',
        'trust4_num': '100%', 'trust4_label': 'Satisfaction Guarantee',
        'services_eyebrow': 'What We Install',
        'services_title': 'Full-Service Flooring Solutions',
        'services_sub': "From premium hardwood to designer tile to budget-friendly luxury vinyl — we install it all to manufacturer spec.",
        'services': [
            ('layers', 'Hardwood Flooring', 'Solid oak, maple, hickory, engineered, hand-scraped, wide-plank. Installed and finished on-site.'),
            ('grid', 'Tile & Stone', 'Porcelain, ceramic, marble, slate, mosaic. Bathrooms, kitchens, entries, fireplaces.'),
            ('home', 'Luxury Vinyl Plank', 'Waterproof, kid-proof, dog-proof. The look of hardwood with none of the maintenance.'),
            ('cube', 'Carpet', 'Wall-to-wall, area rugs, stairs. Premium pile, quality underlay, lifetime stretch warranty.'),
            ('sparkles', 'Refinishing & Restoration', 'Sand, stain, finish your existing hardwood. Bring 50-year-old floors back to life.'),
            ('shield', 'Subfloor Repair & Levelling', 'Squeaks, soft spots, height differences, moisture issues. Solve it before you install.'),
        ],
        'badge_label': '{city} Installer',
        'why_title': 'Floors that look perfect. Installed to last.',
        'why_sub': "Most flooring complaints come from bad install, not bad materials. We prep the subfloor, acclimate the wood, hide every seam. Done right.",
        'why_points': [
            ('Manufacturer-Trained Installers', "Hardwood, tile, vinyl, carpet — all installed to spec to keep warranties valid."),
            ('Proper Subfloor Prep', "Levelling, moisture testing, acclimation. The boring stuff that makes floors last."),
            ('Premium Materials Only', "We work with quality suppliers. No mystery-brand laminate from the auction lot."),
            ('Lifetime Installation Warranty', "We stand behind our install for life. If our install fails, we fix it free."),
        ],
        'reviews_title': 'Trusted by {city} homeowners.',
        'testimonials': [
            ('AM', 'Aaron M.', '"Whole-home hardwood install. Wide-plank white oak, sand-finished on site. Three weeks of work, zero complaints, the floors are stunning."'),
            ('JN', 'Jenna N.', '"Bathroom tile job — heated floors, niche, shower bench. Tile work is flawless. They sent dimensional drawings before cutting a single piece."'),
            ('CR', 'Chris R.', '"Refinished our 1950s oak floors instead of replacing. Looks brand new at a fraction of the cost. Best advice we got."'),
        ],
        'area_sub': 'Residential and commercial flooring across the region.',
        'contact_title': "Got floors to install or refinish?",
        'form_title': 'Request a free estimate',
        'form_sub': "Tell us about the rooms. We'll set up a free on-site measure.",
        'form_type_label': 'Material',
        'form_options': ['Hardwood', 'Tile / Stone', 'Luxury Vinyl', 'Carpet', 'Refinishing', 'Subfloor Repair', 'Other / Not Sure'],
        'form_message_label': 'Tell us about the project',
        'form_message_placeholder': 'Rooms, square footage, current floors, desired material, timeline...',
        'form_submit': 'Send My Request →',
        'final_cta_title': "Ready for floors you love?",
        'final_cta_sub': 'Free estimates. Premium materials. Lifetime install warranty.',
        'final_cta_btn_phone': 'Call {phone} Today',
        'final_cta_btn_form': 'Get a Free Estimate →',
        'footer_para': 'Flooring and tile contractor in {city}, BC. Hardwood, tile, vinyl, carpet, refinishing throughout {region}.',
        'footer_services': ['Hardwood', 'Tile', 'Luxury Vinyl', 'Carpet', 'Refinishing'],
        'footer_cert': 'Licensed · Insured · Manufacturer Certified',
        'contact_label_phone': 'Call Us',
        'hours': ('Mon–Fri: 8am – 6pm', 'Sat by appointment'),
    },
    'handyman': {
        'assets': 'handyman',
        'industry': 'Handyman Services',
        'role': 'handyman', 'role_title': 'Handyman',
        'page_title_suffix': '{city} Handyman & Property Maintenance',
        'meta_desc': '{name} — Reliable {city} handyman. Repairs, mounting, assembly, small jobs done right. Insured, on-time.',
        'hero_eyebrow': 'Available Now · Same-Week Booking',
        'hero_h1_pre': '{city} ', 'hero_h1_hl': 'Handyman', 'hero_h1_post': ' Services. Reliable. Insured.',
        'hero_sub': "That growing honey-do list? Done. {name} brings tools, skills, and reliability to every small job — so you can spend weekends on what actually matters.",
        'nav_cta_noquote': 'Free Quote', 'hero_cta_secondary': 'Request Free Quote',
        'trust3_num': 'Same', 'trust3_label': 'Week Booking',
        'trust4_num': 'Insured', 'trust4_label': '& WCB Covered',
        'services_eyebrow': 'What We Do',
        'services_title': 'The Trusted One-Call Handyman',
        'services_sub': "From fixing a squeaky door to mounting a 75-inch TV to assembling that IKEA monster — we handle the dozens of small things on your list.",
        'services': [
            ('wrench', 'Repairs & Fixes', 'Doors, drawers, faucets, drains, fences, gates. The small stuff that piles up.'),
            ('cube', 'Furniture Assembly', 'IKEA, Wayfair, Costco. Cribs, beds, shelving, desks. Done in hours, not days.'),
            ('chart', 'Mounting & Hanging', 'TVs, shelves, art, mirrors, curtain rods, bike hooks. Studs found, levels true.'),
            ('leaf', 'Yardwork & Cleanup', 'Lawn mowing, hedge trimming, leaf cleanup, junk hauling, pressure washing.'),
            ('home', 'Small Carpentry', "Baseboards, trim, shelves, gates, deck repairs. Honest cuts, tight joints."),
            ('paint', 'Paint Touch-Ups', 'Walls, trim, doors, deck stain. Match the colour, fix the dings, refresh the room.'),
        ],
        'badge_label': '{city} Handyman',
        'why_title': 'The reliable trade for the small jobs.',
        'why_sub': "Big contractors won't return your calls for a 2-hour job. We will. We do the small jobs other trades skip — done right, done quickly, done fairly.",
        'why_points': [
            ('On-Time Every Time', "You get an arrival window we hit. Stuck in traffic? We text. No silent no-shows."),
            ('Honest Hourly Rates', "Posted hourly rate, posted minimum. No mystery service fees, no hidden trip charges."),
            ('Insured & WCB Covered', "Liability + WCB insured. If anything goes sideways, you're protected."),
            ('Full Tool Kit, Every Visit', 'Drills, levels, ladders, saws, fasteners. We arrive ready to work, not ready to leave for supplies.'),
        ],
        'reviews_title': 'Trusted by {city} homeowners.',
        'testimonials': [
            ('CP', 'Catherine P.', '"4 hours, my entire list — door fixed, TV mounted, ceiling fan installed, shelves up. Pleasant, professional, fairly priced. Booking again next month."'),
            ('JE', 'Jose E.', '"Reliable monthly maintenance — anything small that comes up around the rental, he handles. Tenants love him. Saving us so much time."'),
            ('RD', 'Rachel D.', '"Pressure washed our entire deck, repaired two rotted boards, and re-stained the whole thing in one weekend. Perfect."'),
        ],
        'area_sub': 'Residential handyman services across the region.',
        'contact_title': "Got a list of small jobs?",
        'form_title': 'Request a free quote',
        'form_sub': "Tell us what's on the list. We'll get back to you within 1 business day.",
        'form_type_label': 'Service Needed',
        'form_options': ['General Repairs', 'Furniture Assembly', 'TV / Shelves / Mounting', 'Yardwork', 'Small Carpentry', 'Paint Touch-Ups', 'Other / Mixed List'],
        'form_message_label': 'What needs doing?',
        'form_message_placeholder': 'List as many items as you have — we can usually knock most out in one visit...',
        'form_submit': 'Send My Request →',
        'final_cta_title': "Ready to clear that to-do list?",
        'final_cta_sub': 'Same-week booking. Insured & on-time. Honest hourly rates.',
        'final_cta_btn_phone': 'Call {phone} Today',
        'final_cta_btn_form': 'Request Free Quote →',
        'footer_para': 'Reliable handyman and property maintenance in {city}, BC. Small repairs, big help. Serving {region}.',
        'footer_services': ['Repairs', 'Mounting', 'Assembly', 'Yardwork', 'Small Carpentry'],
        'footer_cert': 'Insured · WCB Covered · BBB Member',
        'contact_label_phone': 'Call Us',
        'hours': ('Mon–Sat: 8am – 6pm', 'Closed Sundays'),
    },
    'carpenter': {
        'assets': 'carpenter',
        'industry': 'Custom Carpentry & Millwork',
        'role': 'carpenter', 'role_title': 'Carpenter',
        'page_title_suffix': '{city} Custom Carpentry, Cabinetry & Millwork',
        'meta_desc': '{name} — Master carpenter in {city}. Custom cabinets, built-ins, trim, millwork. Heirloom-quality craftsmanship.',
        'hero_eyebrow': 'Now Booking · Custom Commissions',
        'hero_h1_pre': '{city} ', 'hero_h1_hl': 'Custom Carpentry', 'hero_h1_post': ' & Millwork.',
        'hero_sub': "Heirloom-quality. Built by hand. From custom cabinetry to architectural millwork to dream built-ins, {name} crafts wood the way it deserves to be crafted.",
        'nav_cta_noquote': 'Discuss Project', 'hero_cta_secondary': "Let's Discuss Your Project",
        'trust3_num': 'Heirloom', 'trust3_label': 'Quality Builds',
        'trust4_num': 'Insured', 'trust4_label': 'Shop & Install',
        'services_eyebrow': 'What We Build',
        'services_title': 'Custom Carpentry & Cabinetry',
        'services_sub': "Designed to your space, milled in our shop, installed with care. Wood done right.",
        'services': [
            ('cube', 'Custom Cabinetry', 'Kitchens, baths, libraries, mudrooms, garages. Designed and built to your space.'),
            ('home', 'Built-Ins', 'Bookshelves, media units, window seats, banquettes. Beautiful storage that fits.'),
            ('grid', 'Trim & Millwork', 'Crown, baseboards, casing, wainscoting, panelling. Architectural detail that elevates.'),
            ('shield', 'Custom Doors & Frames', 'Interior, exterior, barn doors, pocket doors. Solid wood, perfectly hung.'),
            ('hammer', 'Stairs & Railings', 'Custom stair builds, treads, balustrades, glass + wood combos.'),
            ('sparkles', 'Furniture Commissions', 'One-of-a-kind tables, beds, dressers, desks. Built to last generations.'),
        ],
        'badge_label': '{city} Carpenter',
        'why_title': 'Wood done the right way.',
        'why_sub': "Mass-produced cabinets and big-box millwork are everywhere. We build the alternative — heirloom-quality work that fits your home and lasts a lifetime.",
        'why_points': [
            ('Master Craftsmen', 'Decades of carpentry, joinery, and finishing experience. The work shows it.'),
            ('Premium Hardwoods', 'White oak, walnut, maple, cherry, mahogany. FSC-certified when available.'),
            ('Shop-Milled, Site-Installed', 'Precise machining in our shop, careful install in your home. Minimal mess.'),
            ('Lifetime Craftsmanship Warranty', 'Joinery, glue, finish — if our work fails, we make it right. For life.'),
        ],
        'reviews_title': 'Trusted by {city} homeowners & designers.',
        'testimonials': [
            ('ER', 'Eric R.', '"Custom walnut media built-in spanning a 14-foot wall. Stunning grain match, hidden cable runs, soft-close everything. Worth every dollar."'),
            ('FK', 'Fiona K.', '"Wainscoting throughout the dining room and stairway. The mitres are so tight you can\'t find them. Real craftsman work."'),
            ('JV', 'James V.', '"Custom kitchen cabinetry — white oak with brass inlay pulls. Better than anything in a magazine. We get compliments constantly."'),
        ],
        'area_sub': 'Custom commissions, residential and commercial, throughout the region.',
        'contact_title': "Got a custom project in mind?",
        'form_title': "Let's discuss your project",
        'form_sub': "Tell us what you're imagining. Free design consultations available.",
        'form_type_label': 'Project Type',
        'form_options': ['Custom Cabinetry', 'Built-Ins', 'Trim / Millwork', 'Doors & Frames', 'Stairs / Railings', 'Furniture', 'Other / Not Sure'],
        'form_message_label': 'Tell us about the project',
        'form_message_placeholder': 'Room, vision, wood preferences, timeline, inspiration links...',
        'form_submit': 'Send My Project Details →',
        'final_cta_title': "Ready to commission something beautiful?",
        'final_cta_sub': 'Free design consultations. Heirloom-quality builds. Personal service.',
        'final_cta_btn_phone': 'Call {phone} Today',
        'final_cta_btn_form': "Let's Discuss Your Project →",
        'footer_para': 'Custom carpentry, cabinetry, and millwork shop in {city}, BC. Heirloom-quality builds for residential and commercial clients throughout {region}.',
        'footer_services': ['Cabinetry', 'Built-Ins', 'Trim & Millwork', 'Doors', 'Furniture'],
        'footer_cert': 'Insured · Master Craftsmen · BC Owned',
        'contact_label_phone': 'Call Shop',
        'hours': ('Mon–Fri: 8am – 5pm', 'Saturdays by appointment'),
    },
    'fence-deck': {
        'assets': 'fence-deck',
        'industry': 'Decks, Fences & Outdoor Builds',
        'role': 'deck builder', 'role_title': 'Builder',
        'page_title_suffix': '{city} Custom Decks, Fences & Outdoor Structures',
        'meta_desc': '{name} — {city} custom deck and fence builders. Cedar, composite, vinyl, glass railings. Built to last.',
        'hero_eyebrow': 'Now Booking · Summer Builds',
        'hero_h1_pre': '{city} ', 'hero_h1_hl': 'Decks, Fences', 'hero_h1_post': ' & Outdoor Builds.',
        'hero_sub': "Premium cedar. Low-maintenance composite. Crystal-clear glass railings. From a backyard fence to a multi-tier deck, {name} builds outdoor spaces that last decades.",
        'nav_cta_noquote': 'Free Estimate', 'hero_cta_secondary': 'Get a Free Estimate',
        'trust3_num': '2-Yr', 'trust3_label': 'Workmanship Warranty',
        'trust4_num': 'Insured', 'trust4_label': 'Crews & WCB',
        'services_eyebrow': 'What We Build',
        'services_title': 'Custom Outdoor Structures',
        'services_sub': "Designed for how you actually live outside. Built with materials that hold up to BC weather.",
        'services': [
            ('fence', 'Wood Fences', 'Cedar, pressure-treated, custom designs. Privacy, picket, lattice tops, gates.'),
            ('shield', 'Vinyl & Composite Fences', 'Maintenance-free options that look great year after year. Lifetime warranties available.'),
            ('layers', 'Custom Decks', 'Cedar, pressure-treated, composite. Multi-tier, wrap-around, with built-in seating.'),
            ('grid', 'Composite Decking', 'Trex, TimberTech, Fiberon. 25+ year warranties, zero refinishing needed.'),
            ('cube', 'Railings', 'Wood, aluminum, glass panels, cable. Building-code compliant, beautifully finished.'),
            ('home', 'Pergolas & Privacy Walls', 'Shade structures, privacy walls, lattice screens, outdoor rooms.'),
        ],
        'badge_label': '{city} Deck Builder',
        'why_title': 'Outdoor builds that hold up.',
        'why_sub': "Decks and fences live outside. Sun, rain, snow, freeze-thaw. We build with materials and methods that handle BC weather decade after decade.",
        'why_points': [
            ('Premium Materials Only', 'Western Red Cedar, Trex composite, marine-grade fasteners. No bargain-bin shortcuts.'),
            ('Engineered to Code', "Footings, ledger boards, joist spacing — everything to code, everything inspected."),
            ('2-Year Workmanship Warranty', "If our build sags, splits, or wobbles within 2 years, we come back and fix it free."),
            ('Permit Handling Included', "Builds over 24 sq metres need permits. We pull them so you don't have to."),
        ],
        'reviews_title': 'Trusted by {city} homeowners.',
        'testimonials': [
            ('SK', 'Steve K.', '"Two-tier cedar deck with built-in seating and glass railings. Stunning. Crew was professional, finished early, and cleaned up perfectly."'),
            ('LA', 'Lisa A.', '"Backyard fence replacement — 180 feet of horizontal cedar with steel posts. Engineered, levelled, finished. Best looking fence on the street."'),
            ('MR', 'Marcus R.', '"Trex composite deck install. Hidden fasteners, perfect mitres, no gaps. Looks better than the picture in the brochure."'),
        ],
        'area_sub': 'Residential outdoor builds throughout the region.',
        'contact_title': "Ready to build outside?",
        'form_title': 'Request a free estimate',
        'form_sub': "Tell us about your project. We'll set up a free on-site walkthrough.",
        'form_type_label': 'Project Type',
        'form_options': ['Wood Fence', 'Vinyl / Composite Fence', 'Wood Deck', 'Composite Deck', 'Railings', 'Pergola / Privacy', 'Other / Not Sure'],
        'form_message_label': 'Tell us about the project',
        'form_message_placeholder': 'Dimensions, material preferences, timeline, site access...',
        'form_submit': 'Send My Request →',
        'final_cta_title': "Ready for the deck or fence of your dreams?",
        'final_cta_sub': 'Free estimates. Premium materials. Built to last decades.',
        'final_cta_btn_phone': 'Call {phone} Today',
        'final_cta_btn_form': 'Get a Free Estimate →',
        'footer_para': 'Custom deck and fence builder in {city}, BC. Cedar, composite, vinyl, glass railings throughout {region}.',
        'footer_services': ['Wood Fences', 'Composite Fences', 'Cedar Decks', 'Composite Decks', 'Railings'],
        'footer_cert': 'Licensed · Insured · WCB Covered',
        'contact_label_phone': 'Call Us',
        'hours': ('Mon–Sat: 7am – 6pm', 'Closed Sundays'),
    },
}

# Map Category 1 value → CATEGORY_CONFIG key
CATEGORY_ROUTING = {
    # Plumbers
    'Plumber': 'plumbers',
    'Plumbing supply store': 'plumbers',
    'Gasfitter': 'plumbers',
    'Gas installation service': 'plumbers',
    # Contractors
    'General contractor': 'contractors',
    'General Contractor': 'contractors',
    'Construction company': 'contractors',
    'Construction Company': 'contractors',
    'Contractor': 'contractors',
    'Home builder': 'contractors',
    'Custom home builder': 'contractors',
    'Modular home builder': 'contractors',
    'Steel construction company': 'contractors',
    'Metal construction company': 'contractors',
    # Electricians
    'Electrician': 'electricians',
    'Electrical installation service': 'electricians',
    'Auto electrical service': 'electricians',
    'Security system installation service': 'electricians',
    'Electrical engineer': 'electricians',
    'Electronics engineer': 'electricians',
    # Landscapers
    'Landscaper': 'landscapers',
    'Landscape designer': 'landscapers',
    'Landscape Gardener': 'landscapers',
    'Gardener': 'landscapers',
    'Landscape lighting designer': 'landscapers',
    'Lawn sprinkler system contractor': 'landscapers',
    'Lawn care service': 'landscapers',
    'Tree service': 'landscapers',
    'Landscaping supply store': 'landscapers',
    'Wholesale plant nursery': 'landscapers',
    'Lawn mower store': 'landscapers',
    # Excavating
    'Excavating contractor': 'excavating',
    'Demolition contractor': 'excavating',
    'Well drilling contractor': 'excavating',
    'Drilling contractor': 'excavating',
    'Earth works company': 'excavating',
    'Logging contractor': 'excavating',
    'Road construction company': 'excavating',
    'Snow removal service': 'excavating',
    # Drywall / Paint / Stucco / Insulation
    'Dry wall contractor': 'drywall',
    'Dry Wall Contractor': 'drywall',
    'Insulation contractor': 'drywall',
    'Insulation Contractor': 'drywall',
    'Painting': 'drywall',
    'Painter': 'drywall',
    'Stucco contractor': 'drywall',
    # Concrete / Masonry / Paving
    'Concrete contractor': 'concrete',
    'Masonry contractor': 'concrete',
    'Paving contractor': 'concrete',
    'Asphalt contractor': 'concrete',
    'Marble contractor': 'concrete',
    'Ready mix concrete supplier': 'concrete',
    'Ready-Mix Concrete Supplier': 'concrete',
    'Foundation': 'concrete',
    'Granite supplier': 'concrete',
    # Interior Design / Remodelers
    'Interior designer': 'interior',
    'Bathroom remodeler': 'interior',
    'Kitchen remodeler': 'interior',
    'Kitchen Renovator': 'interior',
    'Interior construction contractor': 'interior',
    'Remodeler': 'interior',
    'Countertop contractor': 'interior',
    # HVAC
    'HVAC contractor': 'hvac',
    'Heating contractor': 'hvac',
    'Air conditioning contractor': 'hvac',
    'Mechanical contractor': 'hvac',
    'Sheet metal contractor': 'hvac',
    'Furnace repair service': 'hvac',
    'Boiler supplier': 'hvac',
    'Air conditioning system supplier': 'hvac',
    'Heating equipment supplier': 'hvac',
    # Flooring
    'Flooring contractor': 'flooring',
    'Tile contractor': 'flooring',
    'Floor refinishing service': 'flooring',
    'Wood floor installation service': 'flooring',
    'Floor sanding and polishing service': 'flooring',
    'Flooring store': 'flooring',
    'Wood and laminate flooring supplier': 'flooring',
    'Plywood supplier': 'flooring',
    # Handyman
    'Handyman/Handywoman/Handyperson': 'handyman',
    'Property maintenance': 'handyman',
    'Property Maintenance': 'handyman',
    'Repair service': 'handyman',
    'Home help': 'handyman',
    'Pressure washing service': 'handyman',
    'House cleaning service': 'handyman',
    'Gutter cleaning service': 'handyman',
    'Window cleaning service': 'handyman',
    'Cleaning service': 'handyman',
    'Janitorial service': 'handyman',
    # Carpenter
    'Saw mill': 'carpenter',
    'Woodworker': 'carpenter',
    'Carpenter': 'carpenter',
    'Cabinet maker': 'carpenter',
    'Cabinet store': 'carpenter',
    'Furniture maker': 'carpenter',
    'Door supplier': 'carpenter',
    'Stair contractor': 'carpenter',
    'Construction material wholesaler': 'carpenter',
    # Fence / Deck
    'Fence contractor': 'fence-deck',
    'Railing contractor': 'fence-deck',
    'Deck builder': 'fence-deck',
    'Dock builder': 'fence-deck',
    'Awning supplier': 'fence-deck',
    'Patio enclosure supplier': 'fence-deck',
    'Siding contractor': 'fence-deck',
    'Roofing contractor': 'fence-deck',
    'Window installation service': 'fence-deck',
    'Window supplier': 'fence-deck',
    'Glass shop': 'fence-deck',
    'Glass industry': 'fence-deck',
    'Glass repair service': 'fence-deck',
    'Window tinting service': 'fence-deck',
    # Water damage / restoration → handyman bucket
    'Water damage restoration service': 'handyman',
    'Building restoration service': 'handyman',
    'Waterproofing service': 'handyman',
    'Heritage preservation': 'handyman',
    'Water softening equipment supplier': 'plumbers',
    'Water pump supplier': 'plumbers',
    'Plumbing supply store': 'plumbers',
    'Welder': 'contractors',
    'Machine repair service': 'handyman',
}

# Category slug = folder name under each city
CATEGORY_SLUG = {
    'plumbers': 'plumbers',
    'contractors': 'contractors',
    'electricians': 'electricians',
    'landscapers': 'landscapers',
    'excavating': 'excavating',
    'drywall': 'drywall',
    'concrete': 'concrete',
    'interior': 'interior-design',
    'hvac': 'hvac',
    'flooring': 'flooring',
    'handyman': 'handyman',
    'carpenter': 'carpenter',
    'fence-deck': 'fence-deck',
}

# ============ RENDERER ============

def render_business(biz: dict, cfg: dict) -> str:
    name = biz['name']
    mark = biz['mark']
    phone_tel = biz['phone_tel']
    phone_display = biz['phone_display']
    has_phone = biz['has_phone']
    street = biz['street']
    has_address = biz['has_address']
    has_rating = biz['has_rating']
    rating = biz['rating']
    reviews = biz['reviews']
    city = biz['city']
    region = biz.get('region', f'Greater {city}')
    neighborhoods = biz.get('neighborhoods', [city])
    year = datetime.datetime.now().year
    assets = cfg['assets']

    def fmt(s):
        return s.format(name=name, city=city, region=region, phone=phone_display or '')

    # Nav CTA
    nav_cta = (f'<a href="tel:{phone_tel}" class="nav-cta">{SVG_PHONE}{phone_display}</a>'
               if has_phone else
               f'<a href="#contact" class="nav-cta">{cfg["nav_cta_noquote"]}</a>')

    # Hero CTAs
    hero_ctas = ''
    if has_phone:
        hero_ctas += f'<a href="tel:{phone_tel}" class="btn-primary">{SVG_PHONE}Call {phone_display}</a>'
    hero_ctas += f'<a href="#contact" class="btn-secondary">{cfg["hero_cta_secondary"]}{SVG_ARROW}</a>'

    # Trust bar
    rating_tile = (f'<div class="trust-item"><div class="trust-num">{rating}<span style="color:#ffc940;">★</span></div><div class="trust-label">{int(reviews)} Google Reviews</div></div>'
                   if has_rating else
                   f'<div class="trust-item"><div class="trust-num">Local</div><div class="trust-label">{city}-Based</div></div>')

    # Service cards
    services_html = ''
    for icon_key, title, desc in cfg['services']:
        icon = ICONS.get(icon_key, ICONS['wrench'])
        services_html += f'<div class="service-card"><div class="service-icon">{icon}</div><h3>{title}</h3><p>{desc}</p></div>\n      '

    # Why list
    why_html = ''
    for title, desc in cfg['why_points']:
        why_html += f'<div class="why-item"><div class="why-check">{SVG_CHECK}</div><div><div class="why-item-title">{title}</div><div class="why-item-desc">{desc}</div></div></div>\n          '

    # Testimonials neighborhood fallbacks
    nb = neighborhoods + [city, 'Local', 'Downtown', 'Westside']
    nb1, nb2, nb3 = nb[1], nb[2], nb[3]

    # Reviews block (only if has_rating)
    if has_rating:
        t_html = ''
        for i, (avatar, name_, quote) in enumerate(cfg['testimonials']):
            nbi = [nb1, nb2, nb3][i]
            quote_fmt = quote.format(city=city)
            t_html += f'''<div class="testimonial">
        <div class="testimonial-stars">★★★★★</div>
        <p class="testimonial-quote">{quote_fmt}</p>
        <div class="testimonial-author">
          <div class="testimonial-avatar">{avatar}</div>
          <div><div class="testimonial-name">{name_}</div><div class="testimonial-meta">{nbi} · Verified Google Review</div></div>
        </div>
      </div>
      '''
        reviews_block = f'''
<section class="reviews" id="reviews">
  <div class="reviews-bg" style="background: url('../../../assets/{assets}/services.jpg') center/cover;"></div>
  <div class="container reviews-inner">
    <div class="reviews-head">
      <div class="section-eyebrow" style="color: var(--orange);">Real Customer Reviews</div>
      <h2 class="section-title">{fmt(cfg['reviews_title'])}</h2>
      <div class="google-rating">
        <div class="google-rating-num">{rating}</div>
        <div>
          <div class="google-rating-stars">★★★★★</div>
          <div class="google-rating-count">Based on {int(reviews)} Google reviews</div>
        </div>
      </div>
    </div>
    <div class="testimonials">
      {t_html}
    </div>
  </div>
</section>'''
    else:
        reviews_block = ''

    # Contact items
    contact_items = ''
    if has_phone:
        contact_items += f'<div class="contact-info-item"><div class="contact-icon">{SVG_PHONE}</div><div><div class="contact-label">{cfg["contact_label_phone"]}</div><div class="contact-value"><a href="tel:{phone_tel}">{phone_display}</a></div></div></div>'
    if has_address:
        contact_items += f'<div class="contact-info-item"><div class="contact-icon">{SVG_PIN}</div><div><div class="contact-label">Visit Us</div><div class="contact-value">{street}<br>{city}, BC</div></div></div>'
    h1, h2 = cfg['hours']
    contact_items += f'<div class="contact-info-item"><div class="contact-icon">{SVG_CLOCK}</div><div><div class="contact-label">Hours</div><div class="contact-value">{h1}<br>{h2}</div></div></div>'
    if has_rating:
        contact_items += f'<div class="contact-info-item"><div class="contact-icon">{SVG_STAR}</div><div><div class="contact-label">Google Rating</div><div class="contact-value">{rating} ★ · {int(reviews)} reviews</div></div></div>'

    # Form options
    form_options_html = ''.join(f'<option>{o}</option>' for o in cfg['form_options'])

    # Final CTA button
    if has_phone:
        final_cta_btn = f'<a href="tel:{phone_tel}" class="btn-white">{SVG_PHONE}{fmt(cfg["final_cta_btn_phone"])}</a>'
    else:
        final_cta_btn = f'<a href="#contact" class="btn-white">{cfg["final_cta_btn_form"]}</a>'

    # Footer contact
    footer_contact = ''
    if has_phone:
        footer_contact += f'<li><a href="tel:{phone_tel}">{phone_display}</a></li>'
    if has_address:
        footer_contact += f'<li>{street}</li><li>{city}, BC</li>'
    footer_contact += f'<li>{h1}</li><li>{h2}</li>'

    # Footer services list
    footer_services_html = ''.join(f'<li><a href="#services">{s}</a></li>' for s in cfg['footer_services'])

    # Area chips
    area_chips_html = ''.join(f'<div class="area-chip">{n}</div>' for n in neighborhoods)
    footer_area_html = ''.join(f'<li>{n}</li>' for n in neighborhoods[:5])

    brand_sub = f'{cfg["industry"]} · {city} BC'

    nav_reviews_link = '<a href="#reviews">Reviews</a>' if has_rating else ''

    page_title = fmt(cfg['page_title_suffix'])
    meta_desc = fmt(cfg['meta_desc'])

    area_verb = cfg.get('area_title_verb', 'serving')

    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="description" content="{meta_desc}">
<title>{name} | {page_title}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap" rel="stylesheet">
<style>{CSS}</style>
</head>
<body>

<nav class="nav">
  <div class="nav-inner">
    <a href="#" class="brand">
      <div class="brand-mark">{mark}</div>
      <div><div class="brand-text">{name}</div><div class="brand-sub">{brand_sub}</div></div>
    </a>
    <div class="nav-links">
      <a href="#services">Services</a><a href="#why">Why Us</a>{nav_reviews_link}<a href="#contact">Contact</a>
    </div>
    {nav_cta}
  </div>
</nav>

<section class="hero">
  <div class="hero-bg" style="background: linear-gradient(110deg, rgba(10,37,64,0.92) 0%, rgba(10,37,64,0.70) 50%, rgba(10,37,64,0.40) 100%), url('../../../assets/{assets}/hero.jpg') center/cover;"></div>
  <div class="hero-content">
    <div class="hero-eyebrow">{cfg["hero_eyebrow"]}</div>
    <h1>{fmt(cfg["hero_h1_pre"])}<span>{cfg["hero_h1_hl"]}</span>{cfg["hero_h1_post"]}</h1>
    <p class="hero-sub">{fmt(cfg["hero_sub"])}</p>
    <div class="hero-ctas">{hero_ctas}</div>
    <div class="hero-trust">
      <div class="trust-item"><div class="trust-num">Local</div><div class="trust-label">{city}-Based</div></div>
      {rating_tile}
      <div class="trust-item"><div class="trust-num">{cfg["trust3_num"]}</div><div class="trust-label">{cfg["trust3_label"]}</div></div>
      <div class="trust-item"><div class="trust-num">{cfg["trust4_num"]}</div><div class="trust-label">{cfg["trust4_label"]}</div></div>
    </div>
  </div>
</section>

<section class="services" id="services">
  <div class="container">
    <div class="services-head">
      <div class="section-eyebrow">{cfg["services_eyebrow"]}</div>
      <h2 class="section-title">{cfg["services_title"]}</h2>
      <p class="section-sub">{fmt(cfg["services_sub"])}</p>
    </div>
    <div class="services-grid">
      {services_html}
    </div>
  </div>
</section>

<section class="why" id="why">
  <div class="container">
    <div class="why-grid">
      <div class="why-image">
        <img src="../../../assets/{assets}/about.jpg" alt="{name}">
        <div class="why-badge"><div class="why-badge-num">★</div><div><div class="why-badge-sub">Trusted Local</div><div class="why-badge-label">{fmt(cfg["badge_label"])}</div></div></div>
      </div>
      <div>
        <div class="section-eyebrow">Why {city} Chooses Us</div>
        <h2 class="section-title">{cfg["why_title"]}</h2>
        <p style="color: var(--gray-500); font-size: 17px; line-height: 1.7;">{fmt(cfg["why_sub"])}</p>
        <div class="why-list">
          {why_html}
        </div>
      </div>
    </div>
  </div>
</section>
{reviews_block}
<section class="area">
  <div class="container">
    <div class="area-head">
      <div class="section-eyebrow">Service Area</div>
      <h2 class="section-title">Proudly {area_verb} {region}.</h2>
      <p class="section-sub">{fmt(cfg["area_sub"])}</p>
    </div>
    <div class="area-grid">
      {area_chips_html}
    </div>
  </div>
</section>

<section class="contact" id="contact">
  <div class="container">
    <div class="contact-grid">
      <div>
        <div class="section-eyebrow">Get In Touch</div>
        <h2 class="section-title" style="margin-bottom: 32px;">{cfg["contact_title"]}</h2>
        <div class="contact-info-block">{contact_items}</div>
      </div>
      <div class="contact-form">
        <h2 class="section-title">{cfg["form_title"]}</h2>
        <p class="contact-form-sub">{cfg["form_sub"]}</p>
        <form>
          <div class="form-row">
            <div class="form-field"><label>First Name</label><input type="text" placeholder="Your name"></div>
            <div class="form-field"><label>Phone</label><input type="tel" placeholder="(250) 555-0000"></div>
          </div>
          <div class="form-field"><label>Email</label><input type="email" placeholder="you@example.com"></div>
          <div class="form-field"><label>{cfg["form_type_label"]}</label><select>{form_options_html}</select></div>
          <div class="form-field"><label>{cfg["form_message_label"]}</label><textarea placeholder="{cfg["form_message_placeholder"]}"></textarea></div>
          <button type="submit" class="form-submit">{cfg["form_submit"]}</button>
        </form>
      </div>
    </div>
  </div>
</section>

<section class="final-cta">
  <div class="container">
    <h2>{cfg["final_cta_title"]}</h2>
    <p>{cfg["final_cta_sub"]}</p>
    {final_cta_btn}
  </div>
</section>

<footer class="footer">
  <div class="footer-grid">
    <div class="footer-brand">
      <div class="brand"><div class="brand-mark">{mark}</div><div><div class="brand-text" style="color: white;">{name}</div><div class="brand-sub">{brand_sub}</div></div></div>
      <p>{fmt(cfg["footer_para"])}</p>
    </div>
    <div><h4>Services</h4><ul>{footer_services_html}</ul></div>
    <div><h4>Service Area</h4><ul>{footer_area_html}</ul></div>
    <div><h4>Contact</h4><ul>{footer_contact}</ul></div>
  </div>
  <div class="footer-bottom">
    <div>© {year} {name}. All rights reserved.</div>
    <div>{cfg["footer_cert"]}</div>
  </div>
</footer>

</body>
</html>'''
    return html

# ============ MAIN ============

def main():
    df = pd.read_excel(XLSX)

    generated = []
    used_slugs = {}
    by_cat = {}
    by_city_cat = {}
    skipped = []

    for _, row in df.iterrows():
        cat1 = row.get('Category 1')
        if pd.isna(cat1):
            skipped.append(('No Category 1', row.get('Business Name')))
            continue
        cat1_str = str(cat1).strip()
        cfg_key = CATEGORY_ROUTING.get(cat1_str)
        if cfg_key is None:
            skipped.append((cat1_str, row.get('Business Name')))
            continue
        cfg = CATEGORY_CONFIG[cfg_key]
        cat_slug = CATEGORY_SLUG[cfg_key]

        raw_name = str(row['Business Name'])
        name = clean_name(raw_name)
        biz_slug = slugify(name)
        if not biz_slug:
            biz_slug = 'business'
        mark = brand_mark(name)
        phone_tel, phone_display = format_phone(row.get('Phone'))
        has_phone = phone_tel is not None
        street = row.get('Street')
        has_address = bool(pd.notna(street) and str(street).strip())
        rating = row.get('Rating')
        reviews = row.get('Reviews')
        has_rating = bool(pd.notna(rating) and pd.notna(reviews))

        raw_city = row.get('City')
        info = city_info(raw_city)
        if info is None:
            city = 'British Columbia'
            city_slug = 'bc'
            region = 'British Columbia'
            neighborhoods = ['Vancouver','Surrey','Burnaby','Richmond','Victoria','Kelowna','Kamloops','Nanaimo','Abbotsford','Chilliwack','Prince George','Coquitlam']
        else:
            city_slug, region, neighborhoods = info
            city = str(raw_city).strip()

        key = (city_slug, cat_slug, biz_slug)
        used_slugs[key] = used_slugs.get(key, 0) + 1
        final_slug = biz_slug if used_slugs[key] == 1 else f'{biz_slug}-{used_slugs[key]}'

        biz = {
            'name': name, 'mark': mark, 'slug': final_slug,
            'phone_tel': phone_tel or '', 'phone_display': phone_display or '',
            'has_phone': has_phone,
            'street': str(street) if has_address else '', 'has_address': has_address,
            'rating': rating, 'reviews': reviews, 'has_rating': has_rating,
            'city': city, 'region': region, 'neighborhoods': neighborhoods,
        }

        html = render_business(biz, cfg)
        out_dir = os.path.join(OUT_ROOT, city_slug, cat_slug, final_slug)
        os.makedirs(out_dir, exist_ok=True)
        out_path = os.path.join(out_dir, 'index.html')
        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(html)
        url = f'{city_slug}/{cat_slug}/{final_slug}/'
        generated.append((name, url, city, cat_slug))
        by_cat[cat_slug] = by_cat.get(cat_slug, 0) + 1
        by_city_cat.setdefault((city, cat_slug), 0)
        by_city_cat[(city, cat_slug)] += 1

    print('=' * 70)
    print(f'Generated {len(generated)} sites ({len(skipped)} rows skipped)')
    print()
    print('Totals by category:')
    for cat, n in sorted(by_cat.items(), key=lambda x: -x[1]):
        print(f'  {cat}: {n}')
    print()
    if skipped:
        print(f'Skipped categories ({len(skipped)} rows):')
        from collections import Counter
        skip_counter = Counter(s[0] for s in skipped)
        for cat, n in skip_counter.most_common(20):
            print(f'  {cat}: {n}')
    print()
    print('Sample URLs (one per category):')
    seen = set()
    for name_, url, c, cat in generated:
        if cat not in seen:
            print(f'  https://jaggyai.github.io/bc-demos/{url}  ({name_})')
            seen.add(cat)

if __name__ == '__main__':
    main()
