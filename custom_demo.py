"""
One-off custom demo builder. Add new businesses here to generate
demo sites for any company outside the BC spreadsheet.
Usage: python custom_demo.py
"""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from generate_sites import render_business, CATEGORY_CONFIG, slugify, brand_mark, clean_name, format_phone

OUT_ROOT = r'C:/Users/jmang/OneDrive/Desktop/Claude access/bc-demos'

# ============ CUSTOM BUSINESSES ============
# Add entries here, run script to generate.

CUSTOM = [
    {
        'category': 'landscapers',
        'name': 'Lima Earth Construction Ltd.',
        'phone': None,  # Not listed on their site
        'street': '10835 115 Street',
        'city': 'Edmonton',
        'province': 'AB',
        'rating': None,
        'reviews': None,
        'region': 'Edmonton & Capital Region',
        'neighborhoods': ['Edmonton','Sherwood Park','Devon','St. Albert','Beaumont','Fort Saskatchewan','Leduc','Spruce Grove','Stony Plain'],
        # Optional overrides
        'tagline': 'All your landscaping needs taken care of.',
        'email': 'info@limaearthconstruction.ca',
        'city_slug': 'edmonton',
    },
]

# ============ RENDER ============

def make(entry):
    cat_key = entry['category']
    cfg = CATEGORY_CONFIG[cat_key]

    name = clean_name(entry['name'])
    biz_slug = slugify(name)
    mark = brand_mark(name)
    phone_tel, phone_display = format_phone(entry.get('phone'))
    has_phone = phone_tel is not None
    street = entry.get('street')
    has_address = bool(street)
    rating = entry.get('rating')
    reviews = entry.get('reviews')
    has_rating = rating is not None and reviews is not None

    biz = {
        'name': name, 'mark': mark, 'slug': biz_slug,
        'phone_tel': phone_tel or '', 'phone_display': phone_display or '',
        'has_phone': has_phone,
        'street': street or '', 'has_address': has_address,
        'rating': rating, 'reviews': reviews, 'has_rating': has_rating,
        'city': entry['city'],
        'region': entry['region'],
        'neighborhoods': entry['neighborhoods'],
    }

    html = render_business(biz, cfg)

    # If the business has an email (no phone), inject an email row into contact section
    if not has_phone and entry.get('email'):
        email = entry['email']
        email_block = (
            '<div class="contact-info-item">'
            '<div class="contact-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/><polyline points="22,6 12,13 2,6"/></svg></div>'
            f'<div><div class="contact-label">Email Us</div><div class="contact-value"><a href="mailto:{email}">{email}</a></div></div>'
            '</div>'
        )
        # Insert before the "Hours" item
        html = html.replace(
            '<div class="contact-info-item"><div class="contact-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg></div><div><div class="contact-label">Hours</div>',
            email_block + '<div class="contact-info-item"><div class="contact-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg></div><div><div class="contact-label">Hours</div>',
            1
        )

    out_dir = os.path.join(OUT_ROOT, entry['city_slug'], 'landscapers', biz_slug)
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, 'index.html')
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(html)

    url = f"https://jaggyai.github.io/bc-demos/{entry['city_slug']}/landscapers/{biz_slug}/"
    print(f'OK {name}')
    print(f'   Local: {out_path}')
    print(f'   Live URL: {url}')
    return out_path

if __name__ == '__main__':
    for e in CUSTOM:
        make(e)
