"""
BC Demos site generator.
Reads No_Website_Leads_Combined.xlsx, generates per-business demo HTML.
Currently configured for: Victoria plumbers.
"""
import pandas as pd
import re, os, datetime, sys
sys.stdout.reconfigure(encoding='utf-8')

XLSX = r'C:/Users/jmang/OneDrive/Desktop/No_Website_Leads_Combined.xlsx'
OUT_ROOT = r'C:/Users/jmang/OneDrive/Desktop/Claude access/bc-demos'

# Per-city config: slug, regional label (for "Greater {region}"), neighborhoods (10-14 chips)
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

def city_info(city_name: str):
    """Return (slug, region_label, neighborhoods) for a city. None if unknown."""
    if not city_name or pd.isna(city_name):
        return None
    return CITY_CONFIG.get(str(city_name).strip())

# ---------------- helpers ----------------

def slugify(name: str) -> str:
    s = name.lower()
    s = re.sub(r"[''`]", '', s)
    s = re.sub(r'[^a-z0-9]+', '-', s)
    s = re.sub(r'-+', '-', s).strip('-')
    return s

def clean_name(name: str) -> str:
    # Strip trailing digits glued to Ltd/Inc/Corp (data dedup artifact)
    name = re.sub(r'(Ltd|Inc|Corp)\d+\b', r'\1', name)
    return name.strip()

def brand_mark(name: str) -> str:
    # Take first letter of first 2 significant words (skip articles)
    skip = {'the', 'a', 'an', '&', 'and', 'of'}
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

# ---------------- plumber template renderer ----------------

def render_plumber(b: dict) -> str:
    name = b['name']
    mark = b['mark']
    phone_tel = b['phone_tel']
    phone_display = b['phone_display']
    has_phone = b['has_phone']
    street = b['street']
    has_address = b['has_address']
    has_rating = b['has_rating']
    rating = b['rating']
    reviews = b['reviews']
    city = b['city']
    region = b.get('region', f'Greater {city}')
    neighborhoods = b.get('neighborhoods', [city])
    year = datetime.datetime.now().year

    # Conditional: nav CTA
    nav_cta = (
        f'<a href="tel:{phone_tel}" class="nav-cta">'
        f'<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"/></svg>'
        f'{phone_display}</a>'
    ) if has_phone else (
        '<a href="#contact" class="nav-cta">Free Quote</a>'
    )

    # Conditional: hero CTAs
    hero_ctas = ''
    if has_phone:
        hero_ctas += (
            f'<a href="tel:{phone_tel}" class="btn-primary">'
            f'<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"/></svg>'
            f'Call {phone_display}</a>'
        )
    hero_ctas += (
        '<a href="#contact" class="btn-secondary">Request Free Quote'
        '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><line x1="5" y1="12" x2="19" y2="12"/><polyline points="12 5 19 12 12 19"/></svg></a>'
    )

    # Conditional: trust bar (4 items) - swap rating tile if no rating
    rating_tile = (
        f'<div class="trust-item"><div class="trust-num">{rating}<span style="color: #ffc940;">★</span></div>'
        f'<div class="trust-label">{int(reviews)} Google Reviews</div></div>'
    ) if has_rating else (
        f'<div class="trust-item"><div class="trust-num">Local</div>'
        f'<div class="trust-label">{city}-Based</div></div>'
    )

    # Hero subhead - subtle adjustment if no phone
    hero_sub = (
        'Family-owned. Licensed. Insured. From emergency leaks to full bathroom renovations, '
        f'{name} keeps {city} homes running with quality plumbing and gas work you can trust.'
    )

    # Testimonial neighborhoods (use real local neighborhoods)
    nb = neighborhoods + ['Local','Downtown','Westside']  # fallbacks
    nb1, nb2, nb3 = nb[1] if len(nb) > 1 else city, nb[2] if len(nb) > 2 else city, nb[3] if len(nb) > 3 else city

    # Conditional: reviews section
    if has_rating:
        reviews_block = f'''
<section class="reviews" id="reviews">
  <div class="container reviews-inner">
    <div class="reviews-head">
      <div class="section-eyebrow" style="color: var(--orange);">Real Customer Reviews</div>
      <h2 class="section-title">Trusted by {city} homeowners.</h2>
      <div class="google-rating">
        <div class="google-rating-num">{rating}</div>
        <div>
          <div class="google-rating-stars">★★★★★</div>
          <div class="google-rating-count">Based on {int(reviews)} Google reviews</div>
        </div>
      </div>
    </div>
    <div class="testimonials">
      <div class="testimonial">
        <div class="testimonial-stars">★★★★★</div>
        <p class="testimonial-quote">"Called in the morning with a leaking water heater. They were at my house within hours, replaced it cleanly, and the price was exactly what they quoted. Honest crew."</p>
        <div class="testimonial-author">
          <div class="testimonial-avatar">SM</div>
          <div><div class="testimonial-name">Sarah M.</div><div class="testimonial-meta">{nb1} · Verified Google Review</div></div>
        </div>
      </div>
      <div class="testimonial">
        <div class="testimonial-stars">★★★★★</div>
        <p class="testimonial-quote">"Honestly the only plumber I trust in {city}. Always professional, always fair. Showed up on time, fixed the problem, didn't try to upsell me anything I didn't need."</p>
        <div class="testimonial-author">
          <div class="testimonial-avatar">DC</div>
          <div><div class="testimonial-name">David C.</div><div class="testimonial-meta">{nb2} · Verified Google Review</div></div>
        </div>
      </div>
      <div class="testimonial">
        <div class="testimonial-stars">★★★★★</div>
        <p class="testimonial-quote">"Full bathroom remodel — they handled the rough-in, fixtures, and gas line for our new tankless heater. Clean work, on schedule, and they cleaned up better than they found it."</p>
        <div class="testimonial-author">
          <div class="testimonial-avatar">JL</div>
          <div><div class="testimonial-name">Jennifer L.</div><div class="testimonial-meta">{nb3} · Verified Google Review</div></div>
        </div>
      </div>
    </div>
  </div>
</section>'''
    else:
        reviews_block = ''

    # Contact info items (conditional on phone/address)
    contact_items = ''
    if has_phone:
        contact_items += f'''
      <div class="contact-info-item">
        <div class="contact-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"/></svg></div>
        <div><div class="contact-label">Call Us 24/7</div><div class="contact-value"><a href="tel:{phone_tel}">{phone_display}</a></div></div>
      </div>'''
    if has_address:
        contact_items += f'''
      <div class="contact-info-item">
        <div class="contact-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/></svg></div>
        <div><div class="contact-label">Visit Us</div><div class="contact-value">{street}<br>{city}, BC</div></div>
      </div>'''
    contact_items += '''
      <div class="contact-info-item">
        <div class="contact-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg></div>
        <div><div class="contact-label">Hours</div><div class="contact-value">Mon–Fri: 7am – 6pm<br>Emergency: 24/7</div></div>
      </div>'''
    if has_rating:
        contact_items += f'''
      <div class="contact-info-item">
        <div class="contact-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg></div>
        <div><div class="contact-label">Google Rating</div><div class="contact-value">{rating} ★ · {int(reviews)} reviews</div></div>
      </div>'''

    # Final CTA - phone or form
    if has_phone:
        final_cta_btn = (
            f'<a href="tel:{phone_tel}" class="btn-white">'
            f'<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"/></svg>'
            f'Call {phone_display} Now</a>'
        )
    else:
        final_cta_btn = '<a href="#contact" class="btn-white">Request Free Quote →</a>'

    # Footer contact
    footer_contact = ''
    if has_phone:
        footer_contact += f'<li><a href="tel:{phone_tel}">{phone_display}</a></li>'
    if has_address:
        footer_contact += f'<li>{street}</li><li>{city}, BC</li>'
    footer_contact += '<li>Mon–Fri 7am–6pm</li><li>24/7 Emergency</li>'

    # Brand sub
    brand_sub = 'Plumbing & Gas · ' + city + ' BC'

    # Service area chips (dynamic per city)
    area_chips_html = '\n      '.join(f'<div class="area-chip">{n}</div>' for n in neighborhoods)

    # Footer area chips (first 5)
    footer_area_html = '\n        '.join(f'<li>{n}</li>' for n in neighborhoods[:5])

    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="description" content="{name} — Trusted {city} plumbers. Licensed, insured. Emergency plumbing, drain cleaning, water heaters, gas fitting.">
<title>{name} | {city}'s Trusted Plumbing & Gas Experts</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap" rel="stylesheet">
<style>
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
:root {{
  --navy: #0a2540; --navy-dark: #061a30; --orange: #ff6b35; --orange-dark: #e55525;
  --gray-50: #f8fafc; --gray-100: #f1f5f9; --gray-200: #e2e8f0; --gray-500: #64748b;
  --gray-700: #334155; --gray-900: #0f172a; --white: #ffffff;
  --shadow: 0 10px 40px rgba(10, 37, 64, 0.08); --shadow-lg: 0 20px 60px rgba(10, 37, 64, 0.15);
}}
html {{ scroll-behavior: smooth; }}
body {{ font-family: 'Inter', system-ui, sans-serif; color: var(--gray-900); line-height: 1.6; -webkit-font-smoothing: antialiased; }}
img {{ max-width: 100%; display: block; }}
a {{ color: inherit; text-decoration: none; }}
.nav {{ position: fixed; top: 0; left: 0; right: 0; background: rgba(255,255,255,0.96); backdrop-filter: blur(12px); z-index: 100; box-shadow: 0 1px 0 rgba(10,37,64,0.06); }}
.nav-inner {{ max-width: 1200px; margin: 0 auto; padding: 16px 24px; display: flex; align-items: center; justify-content: space-between; gap: 24px; }}
.brand {{ display: flex; align-items: center; gap: 12px; }}
.brand-mark {{ width: 40px; height: 40px; background: var(--navy); color: var(--white); border-radius: 8px; display: flex; align-items: center; justify-content: center; font-weight: 900; font-size: 18px; letter-spacing: -0.5px; }}
.brand-text {{ font-weight: 800; font-size: 17px; letter-spacing: -0.3px; color: var(--navy); }}
.brand-sub {{ font-size: 11px; color: var(--gray-500); font-weight: 500; text-transform: uppercase; letter-spacing: 0.8px; }}
.nav-links {{ display: flex; gap: 32px; }}
.nav-links a {{ font-size: 14px; font-weight: 500; color: var(--gray-700); transition: color 0.2s; }}
.nav-links a:hover {{ color: var(--orange); }}
.nav-cta {{ background: var(--orange); color: var(--white); padding: 12px 22px; border-radius: 8px; font-weight: 700; font-size: 14px; transition: all 0.2s; display: inline-flex; align-items: center; gap: 8px; }}
.nav-cta:hover {{ background: var(--orange-dark); transform: translateY(-1px); }}
@media (max-width: 768px) {{ .nav-links {{ display: none; }} .brand-sub {{ display: none; }} }}
.hero {{ position: relative; min-height: 92vh; padding-top: 90px; display: flex; align-items: center; overflow: hidden; background: var(--navy); }}
.hero-bg {{ position: absolute; inset: 0; background: linear-gradient(110deg, rgba(10,37,64,0.92) 0%, rgba(10,37,64,0.70) 50%, rgba(10,37,64,0.40) 100%), url('../../../assets/plumber/hero.jpg') center/cover; }}
.hero-content {{ position: relative; max-width: 1200px; margin: 0 auto; padding: 60px 24px; width: 100%; }}
.hero-eyebrow {{ display: inline-flex; align-items: center; gap: 8px; background: rgba(255,107,53,0.15); color: var(--orange); padding: 8px 16px; border-radius: 100px; font-size: 13px; font-weight: 600; margin-bottom: 24px; border: 1px solid rgba(255,107,53,0.25); }}
.hero-eyebrow::before {{ content: ''; width: 8px; height: 8px; background: var(--orange); border-radius: 50%; box-shadow: 0 0 12px var(--orange); animation: pulse 2s infinite; }}
@keyframes pulse {{ 0%, 100% {{ opacity: 1; }} 50% {{ opacity: 0.5; }} }}
.hero h1 {{ color: var(--white); font-size: clamp(38px, 5.5vw, 68px); font-weight: 900; line-height: 1.05; letter-spacing: -1.5px; margin-bottom: 24px; max-width: 760px; }}
.hero h1 span {{ color: var(--orange); }}
.hero-sub {{ color: rgba(255,255,255,0.85); font-size: clamp(17px, 1.6vw, 20px); max-width: 580px; margin-bottom: 40px; line-height: 1.6; }}
.hero-ctas {{ display: flex; gap: 16px; flex-wrap: wrap; margin-bottom: 48px; }}
.btn-primary {{ background: var(--orange); color: var(--white); padding: 18px 32px; border-radius: 10px; font-weight: 700; font-size: 16px; display: inline-flex; align-items: center; gap: 10px; transition: all 0.2s; box-shadow: 0 8px 24px rgba(255,107,53,0.35); }}
.btn-primary:hover {{ background: var(--orange-dark); transform: translateY(-2px); box-shadow: 0 12px 32px rgba(255,107,53,0.45); }}
.btn-secondary {{ background: rgba(255,255,255,0.1); color: var(--white); padding: 18px 32px; border-radius: 10px; font-weight: 600; font-size: 16px; display: inline-flex; align-items: center; gap: 10px; border: 1px solid rgba(255,255,255,0.2); transition: all 0.2s; backdrop-filter: blur(10px); }}
.btn-secondary:hover {{ background: rgba(255,255,255,0.18); border-color: rgba(255,255,255,0.35); }}
.hero-trust {{ display: flex; gap: 40px; flex-wrap: wrap; padding-top: 32px; border-top: 1px solid rgba(255,255,255,0.12); }}
.trust-item {{ color: rgba(255,255,255,0.9); }}
.trust-num {{ font-size: 28px; font-weight: 800; color: var(--white); letter-spacing: -0.5px; }}
.trust-label {{ font-size: 13px; color: rgba(255,255,255,0.65); font-weight: 500; }}
section {{ padding: 100px 24px; }}
.container {{ max-width: 1200px; margin: 0 auto; }}
.section-eyebrow {{ display: inline-block; color: var(--orange); font-weight: 700; font-size: 13px; letter-spacing: 1.5px; text-transform: uppercase; margin-bottom: 16px; }}
.section-title {{ font-size: clamp(32px, 4vw, 48px); font-weight: 800; color: var(--navy); letter-spacing: -1px; line-height: 1.15; margin-bottom: 20px; }}
.section-sub {{ font-size: 18px; color: var(--gray-500); max-width: 640px; line-height: 1.6; }}
.services {{ background: var(--gray-50); }}
.services-head {{ text-align: center; max-width: 720px; margin: 0 auto 64px; }}
.services-head .section-sub {{ margin: 0 auto; }}
.services-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 24px; }}
.service-card {{ background: var(--white); padding: 36px 32px; border-radius: 16px; transition: all 0.3s; border: 1px solid var(--gray-200); }}
.service-card:hover {{ transform: translateY(-6px); box-shadow: var(--shadow-lg); border-color: transparent; }}
.service-icon {{ width: 56px; height: 56px; background: rgba(255,107,53,0.1); border-radius: 12px; display: flex; align-items: center; justify-content: center; margin-bottom: 24px; color: var(--orange); }}
.service-icon svg {{ width: 28px; height: 28px; }}
.service-card h3 {{ font-size: 20px; font-weight: 700; color: var(--navy); margin-bottom: 12px; letter-spacing: -0.3px; }}
.service-card p {{ color: var(--gray-500); font-size: 15px; line-height: 1.6; }}
.why {{ background: var(--white); }}
.why-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 80px; align-items: center; }}
@media (max-width: 900px) {{ .why-grid {{ grid-template-columns: 1fr; gap: 48px; }} }}
.why-image {{ position: relative; border-radius: 20px; overflow: hidden; box-shadow: var(--shadow-lg); }}
.why-image img {{ width: 100%; height: 100%; object-fit: cover; aspect-ratio: 4/5; }}
.why-badge {{ position: absolute; bottom: 24px; left: 24px; background: var(--white); padding: 20px 24px; border-radius: 14px; box-shadow: var(--shadow); display: flex; align-items: center; gap: 16px; }}
.why-badge-num {{ font-size: 36px; font-weight: 900; color: var(--orange); letter-spacing: -1px; line-height: 1; }}
.why-badge-label {{ font-size: 12px; color: var(--gray-500); font-weight: 600; text-transform: uppercase; letter-spacing: 1px; }}
.why-badge-sub {{ font-size: 14px; color: var(--navy); font-weight: 700; }}
.why-list {{ margin-top: 32px; display: flex; flex-direction: column; gap: 20px; }}
.why-item {{ display: flex; gap: 16px; align-items: flex-start; }}
.why-check {{ width: 28px; height: 28px; background: var(--orange); border-radius: 50%; display: flex; align-items: center; justify-content: center; flex-shrink: 0; color: var(--white); }}
.why-check svg {{ width: 16px; height: 16px; }}
.why-item-title {{ font-weight: 700; color: var(--navy); margin-bottom: 4px; font-size: 16px; }}
.why-item-desc {{ font-size: 14px; color: var(--gray-500); line-height: 1.5; }}
.reviews {{ background: var(--navy); color: var(--white); position: relative; overflow: hidden; }}
.reviews::before {{ content: ''; position: absolute; inset: 0; background: url('../../../assets/plumber/services.jpg') center/cover; opacity: 0.08; }}
.reviews-inner {{ position: relative; }}
.reviews-head {{ text-align: center; margin-bottom: 64px; }}
.reviews-head .section-title {{ color: var(--white); }}
.reviews-head .section-sub {{ color: rgba(255,255,255,0.7); margin: 0 auto; }}
.google-rating {{ display: inline-flex; align-items: center; gap: 20px; background: rgba(255,255,255,0.06); padding: 20px 32px; border-radius: 16px; margin-bottom: 24px; border: 1px solid rgba(255,255,255,0.1); }}
.google-rating-num {{ font-size: 48px; font-weight: 900; color: var(--white); letter-spacing: -1.5px; line-height: 1; }}
.google-rating-stars {{ font-size: 22px; color: #ffc940; letter-spacing: 3px; margin-bottom: 4px; }}
.google-rating-count {{ font-size: 13px; color: rgba(255,255,255,0.65); }}
.testimonials {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 24px; }}
.testimonial {{ background: rgba(255,255,255,0.05); padding: 32px; border-radius: 16px; border: 1px solid rgba(255,255,255,0.1); }}
.testimonial-stars {{ color: #ffc940; letter-spacing: 2px; margin-bottom: 16px; font-size: 14px; }}
.testimonial-quote {{ color: rgba(255,255,255,0.92); font-size: 15px; line-height: 1.7; margin-bottom: 24px; }}
.testimonial-author {{ display: flex; align-items: center; gap: 12px; }}
.testimonial-avatar {{ width: 44px; height: 44px; background: var(--orange); border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: 700; color: var(--white); font-size: 16px; }}
.testimonial-name {{ font-weight: 700; color: var(--white); font-size: 14px; }}
.testimonial-meta {{ font-size: 12px; color: rgba(255,255,255,0.55); }}
.area {{ background: var(--gray-50); text-align: center; }}
.area-head {{ max-width: 720px; margin: 0 auto 48px; }}
.area-head .section-sub {{ margin: 0 auto; }}
.area-grid {{ display: flex; flex-wrap: wrap; justify-content: center; gap: 12px; max-width: 800px; margin: 0 auto; }}
.area-chip {{ background: var(--white); padding: 14px 24px; border-radius: 100px; font-weight: 600; color: var(--navy); border: 1px solid var(--gray-200); font-size: 14px; transition: all 0.2s; }}
.area-chip:hover {{ border-color: var(--orange); color: var(--orange); transform: translateY(-2px); }}
.contact {{ background: var(--white); }}
.contact-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 64px; align-items: start; }}
@media (max-width: 900px) {{ .contact-grid {{ grid-template-columns: 1fr; gap: 48px; }} }}
.contact-info-block {{ background: var(--gray-50); padding: 40px; border-radius: 20px; }}
.contact-info-item {{ display: flex; gap: 20px; align-items: flex-start; padding: 20px 0; border-bottom: 1px solid var(--gray-200); }}
.contact-info-item:last-child {{ border-bottom: none; }}
.contact-icon {{ width: 48px; height: 48px; background: var(--white); border-radius: 12px; display: flex; align-items: center; justify-content: center; color: var(--orange); flex-shrink: 0; box-shadow: var(--shadow); }}
.contact-icon svg {{ width: 22px; height: 22px; }}
.contact-label {{ font-size: 12px; color: var(--gray-500); font-weight: 600; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 4px; }}
.contact-value {{ font-size: 17px; color: var(--navy); font-weight: 700; }}
.contact-value a:hover {{ color: var(--orange); }}
.contact-form h2 {{ margin-bottom: 8px; }}
.contact-form-sub {{ color: var(--gray-500); margin-bottom: 32px; }}
.form-row {{ display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-bottom: 16px; }}
@media (max-width: 600px) {{ .form-row {{ grid-template-columns: 1fr; }} }}
.form-field {{ display: flex; flex-direction: column; gap: 6px; margin-bottom: 16px; }}
.form-field label {{ font-size: 13px; font-weight: 600; color: var(--gray-700); }}
.form-field input, .form-field textarea, .form-field select {{ padding: 14px 16px; border: 1px solid var(--gray-200); border-radius: 10px; font-size: 15px; font-family: inherit; transition: border-color 0.2s; background: var(--white); }}
.form-field input:focus, .form-field textarea:focus, .form-field select:focus {{ outline: none; border-color: var(--orange); }}
.form-field textarea {{ resize: vertical; min-height: 120px; }}
.form-submit {{ background: var(--orange); color: var(--white); padding: 16px 32px; border: none; border-radius: 10px; font-weight: 700; font-size: 16px; cursor: pointer; transition: all 0.2s; box-shadow: 0 8px 24px rgba(255,107,53,0.3); width: 100%; }}
.form-submit:hover {{ background: var(--orange-dark); transform: translateY(-2px); }}
.final-cta {{ background: linear-gradient(135deg, var(--orange) 0%, var(--orange-dark) 100%); color: var(--white); text-align: center; padding: 80px 24px; }}
.final-cta h2 {{ font-size: clamp(28px, 4vw, 42px); font-weight: 800; margin-bottom: 16px; letter-spacing: -0.5px; }}
.final-cta p {{ font-size: 18px; margin-bottom: 32px; opacity: 0.95; max-width: 580px; margin-left: auto; margin-right: auto; }}
.final-cta .btn-white {{ background: var(--white); color: var(--orange); padding: 18px 36px; border-radius: 10px; font-weight: 700; font-size: 17px; display: inline-flex; align-items: center; gap: 10px; transition: all 0.2s; box-shadow: 0 12px 32px rgba(0,0,0,0.15); }}
.final-cta .btn-white:hover {{ transform: translateY(-2px); box-shadow: 0 16px 40px rgba(0,0,0,0.2); }}
.footer {{ background: var(--navy-dark); color: rgba(255,255,255,0.7); padding: 64px 24px 32px; }}
.footer-grid {{ max-width: 1200px; margin: 0 auto; display: grid; grid-template-columns: 2fr 1fr 1fr 1fr; gap: 48px; margin-bottom: 48px; }}
@media (max-width: 768px) {{ .footer-grid {{ grid-template-columns: 1fr 1fr; gap: 32px; }} }}
.footer h4 {{ color: var(--white); font-size: 14px; font-weight: 700; margin-bottom: 20px; text-transform: uppercase; letter-spacing: 1px; }}
.footer ul {{ list-style: none; }}
.footer ul li {{ margin-bottom: 10px; font-size: 14px; }}
.footer ul li a:hover {{ color: var(--orange); }}
.footer-brand p {{ font-size: 14px; line-height: 1.7; max-width: 360px; margin-top: 16px; }}
.footer-bottom {{ max-width: 1200px; margin: 0 auto; padding-top: 32px; border-top: 1px solid rgba(255,255,255,0.1); display: flex; justify-content: space-between; flex-wrap: wrap; gap: 16px; font-size: 13px; }}
</style>
</head>
<body>

<nav class="nav">
  <div class="nav-inner">
    <a href="#" class="brand">
      <div class="brand-mark">{mark}</div>
      <div><div class="brand-text">{name}</div><div class="brand-sub">{brand_sub}</div></div>
    </a>
    <div class="nav-links">
      <a href="#services">Services</a><a href="#why">Why Us</a>
      {('<a href="#reviews">Reviews</a>' if has_rating else '')}<a href="#contact">Contact</a>
    </div>
    {nav_cta}
  </div>
</nav>

<section class="hero">
  <div class="hero-bg"></div>
  <div class="hero-content">
    <div class="hero-eyebrow">Available Now · Same-Day Service</div>
    <h1>{city}'s Trusted <span>Plumbing & Gas</span> Experts.</h1>
    <p class="hero-sub">{hero_sub}</p>
    <div class="hero-ctas">{hero_ctas}</div>
    <div class="hero-trust">
      <div class="trust-item"><div class="trust-num">Local</div><div class="trust-label">{city}-Based</div></div>
      {rating_tile}
      <div class="trust-item"><div class="trust-num">24/7</div><div class="trust-label">Emergency Service</div></div>
      <div class="trust-item"><div class="trust-num">100%</div><div class="trust-label">Licensed & Insured</div></div>
    </div>
  </div>
</section>

<section class="services" id="services">
  <div class="container">
    <div class="services-head">
      <div class="section-eyebrow">What We Do</div>
      <h2 class="section-title">Full-Service Plumbing & Gas Solutions</h2>
      <p class="section-sub">From a dripping tap to a full repipe, our certified plumbers handle every job with the craftsmanship {city} homeowners trust.</p>
    </div>
    <div class="services-grid">
      <div class="service-card"><div class="service-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2L4 7v10l8 5 8-5V7l-8-5zM12 22V12M4 7l8 5 8-5"/></svg></div><h3>Emergency Repairs</h3><p>Burst pipes, major leaks, no hot water — we respond fast, day or night, with no overtime surprises.</p></div>
      <div class="service-card"><div class="service-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/></svg></div><h3>Drain Cleaning</h3><p>Clogged sinks, slow drains, sewer backups. Camera inspection and hydro-jetting available.</p></div>
      <div class="service-card"><div class="service-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M2 12h6l3-9 4 18 3-9h4"/></svg></div><h3>Water Heaters</h3><p>Tank, tankless, heat-pump installs. Service, repair, and replacement of any major brand.</p></div>
      <div class="service-card"><div class="service-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/></svg></div><h3>Gas Fitting</h3><p>Certified gas line installation, repair, and inspection. Furnaces, ranges, BBQs, fireplaces.</p></div>
      <div class="service-card"><div class="service-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 21V10a4 4 0 0 1 4-4h10a4 4 0 0 1 4 4v11"/><path d="M3 21h18M9 21V14M15 21V14M12 6V2"/></svg></div><h3>Bathroom & Kitchen</h3><p>Full renovations and fixture upgrades — toilets, faucets, showers, garburators, dishwashers.</p></div>
      <div class="service-card"><div class="service-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg></div><h3>Leak Detection</h3><p>Non-invasive leak location using thermal imaging and acoustic detection. We find it before we cut.</p></div>
    </div>
  </div>
</section>

<section class="why" id="why">
  <div class="container">
    <div class="why-grid">
      <div class="why-image">
        <img src="../../../assets/plumber/about.jpg" alt="{name} master plumber">
        <div class="why-badge"><div class="why-badge-num">★</div><div><div class="why-badge-sub">Trusted Local</div><div class="why-badge-label">{city} Plumber</div></div></div>
      </div>
      <div>
        <div class="section-eyebrow">Why {city} Chooses Us</div>
        <h2 class="section-title">Old-school craftsmanship. Modern service.</h2>
        <p style="color: var(--gray-500); font-size: 17px; line-height: 1.7;">We run our business the way you'd want a plumber to: real-time arrival updates, upfront pricing, and clean job sites every single time.</p>
        <div class="why-list">
          <div class="why-item"><div class="why-check"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3"><polyline points="20 6 9 17 4 12"/></svg></div><div><div class="why-item-title">Upfront, Flat-Rate Pricing</div><div class="why-item-desc">Know the cost before we lift a wrench. No surprises, no hourly meter running.</div></div></div>
          <div class="why-item"><div class="why-check"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3"><polyline points="20 6 9 17 4 12"/></svg></div><div><div class="why-item-title">Licensed Red Seal Plumbers</div><div class="why-item-desc">Every tech is fully ticketed, gas-certified, and background-checked.</div></div></div>
          <div class="why-item"><div class="why-check"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3"><polyline points="20 6 9 17 4 12"/></svg></div><div><div class="why-item-title">5-Year Workmanship Warranty</div><div class="why-item-desc">If our work fails, we come back free. That's our promise.</div></div></div>
          <div class="why-item"><div class="why-check"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3"><polyline points="20 6 9 17 4 12"/></svg></div><div><div class="why-item-title">Same-Day Service Available</div><div class="why-item-desc">Most calls answered same-day. 24/7 emergency line always open.</div></div></div>
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
      <h2 class="section-title">Proudly serving {region}.</h2>
      <p class="section-sub">From downtown to the outskirts, our trucks cover every neighbourhood in the area.</p>
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
        <h2 class="section-title" style="margin-bottom: 32px;">Need a plumber? We're ready.</h2>
        <div class="contact-info-block">{contact_items}</div>
      </div>
      <div class="contact-form">
        <h2 class="section-title">Request a free quote</h2>
        <p class="contact-form-sub">Tell us what's going on. We'll get back to you within 1 business hour.</p>
        <form>
          <div class="form-row">
            <div class="form-field"><label>First Name</label><input type="text" placeholder="Your name"></div>
            <div class="form-field"><label>Phone</label><input type="tel" placeholder="(250) 555-0000"></div>
          </div>
          <div class="form-field"><label>Email</label><input type="email" placeholder="you@example.com"></div>
          <div class="form-field"><label>Service Needed</label><select><option>Emergency Repair</option><option>Drain Cleaning</option><option>Water Heater</option><option>Gas Fitting</option><option>Bathroom / Kitchen</option><option>Leak Detection</option><option>Other / Not Sure</option></select></div>
          <div class="form-field"><label>Tell us what's going on</label><textarea placeholder="Describe the issue or project..."></textarea></div>
          <button type="submit" class="form-submit">Send My Request →</button>
        </form>
      </div>
    </div>
  </div>
</section>

<section class="final-cta">
  <div class="container">
    <h2>Got a plumbing problem? Let's solve it today.</h2>
    <p>One call. Fast response. Honest pricing.</p>
    {final_cta_btn}
  </div>
</section>

<footer class="footer">
  <div class="footer-grid">
    <div class="footer-brand">
      <div class="brand"><div class="brand-mark">{mark}</div><div><div class="brand-text" style="color: white;">{name}</div><div class="brand-sub">{brand_sub}</div></div></div>
      <p>Family-owned and operated in {city}, BC. Licensed Red Seal plumbers and certified gas fitters serving {region}.</p>
    </div>
    <div><h4>Services</h4><ul><li><a href="#services">Emergency Repairs</a></li><li><a href="#services">Drain Cleaning</a></li><li><a href="#services">Water Heaters</a></li><li><a href="#services">Gas Fitting</a></li><li><a href="#services">Leak Detection</a></li></ul></div>
    <div><h4>Service Area</h4><ul>
        {footer_area_html}
      </ul></div>
    <div><h4>Contact</h4><ul>{footer_contact}</ul></div>
  </div>
  <div class="footer-bottom">
    <div>© {year} {name}. All rights reserved.</div>
    <div>Licensed · Insured · Red Seal Certified</div>
  </div>
</footer>

</body>
</html>'''
    return html

# ---------------- main ----------------

def main():
    df = pd.read_excel(XLSX)
    plumbers = df[df['Category 1'] == 'Plumber'].copy()
    print(f'Total BC plumbers: {len(plumbers)}')
    print()

    generated = []
    used_slugs = {}  # (city_slug, biz_slug) -> count, for collision suffixing
    by_city_count = {}

    for _, row in plumbers.iterrows():
        raw_name = str(row['Business Name'])
        name = clean_name(raw_name)
        biz_slug = slugify(name)
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
            # Unknown / missing city → generic BC bucket
            city = 'British Columbia'
            city_slug = 'bc'
            region = 'British Columbia'
            neighborhoods = ['Vancouver','Surrey','Burnaby','Richmond','Victoria','Kelowna','Kamloops','Nanaimo','Abbotsford','Chilliwack','Prince George','Coquitlam']
        else:
            city_slug, region, neighborhoods = info
            city = str(raw_city).strip()

        # Slug collision protection
        key = (city_slug, biz_slug)
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

        html = render_plumber(biz)
        out_dir = os.path.join(OUT_ROOT, city_slug, 'plumbers', final_slug)
        os.makedirs(out_dir, exist_ok=True)
        out_path = os.path.join(out_dir, 'index.html')
        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(html)
        url = f'{city_slug}/plumbers/{final_slug}/'
        generated.append((name, url, city, has_phone, has_address, has_rating))
        by_city_count[city] = by_city_count.get(city, 0) + 1

    print('=' * 70)
    print(f'Generated {len(generated)} plumber sites across {len(by_city_count)} cities')
    print()
    print('Sites per city:')
    for c, n in sorted(by_city_count.items(), key=lambda x: -x[1]):
        print(f'  {c}: {n}')
    print()
    print('Sample GitHub Pages URLs (showing 1 per city):')
    seen_cities = set()
    for n, u, c, _, _, _ in generated:
        if c not in seen_cities:
            print(f'  https://jaggyai.github.io/bc-demos/{u}  ({n})')
            seen_cities.add(c)

if __name__ == '__main__':
    main()
