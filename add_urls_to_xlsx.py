"""
Read the original spreadsheet, mirror the generator's routing logic,
add a 'Demo URL' column with the live GitHub Pages URL for each row,
save to a new .xlsx so the original stays untouched.
"""
import pandas as pd
import os, sys
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.dirname(__file__))

from generate_sites import (
    CATEGORY_ROUTING, CATEGORY_SLUG, city_info,
    slugify, clean_name,
)

IN_XLSX = r'C:/Users/jmang/OneDrive/Desktop/No_Website_Leads_Combined.xlsx'
OUT_XLSX = r'C:/Users/jmang/OneDrive/Desktop/No_Website_Leads_With_URLs.xlsx'

BASE = 'https://jaggyai.github.io/bc-demos'

def main():
    df = pd.read_excel(IN_XLSX)
    n = len(df)
    print(f'Loaded {n} rows from {IN_XLSX}')

    # Replay the generator's slug-collision logic
    used_slugs = {}
    urls = []
    no_url_count = 0

    for _, row in df.iterrows():
        cat1 = row.get('Category 1')
        if pd.isna(cat1):
            urls.append('')
            no_url_count += 1
            continue
        cat1_str = str(cat1).strip()
        cfg_key = CATEGORY_ROUTING.get(cat1_str)
        if cfg_key is None:
            urls.append('')
            no_url_count += 1
            continue
        cat_slug = CATEGORY_SLUG[cfg_key]

        raw_name = str(row['Business Name'])
        name = clean_name(raw_name)
        biz_slug = slugify(name)
        if not biz_slug:
            biz_slug = 'business'

        raw_city = row.get('City')
        info = city_info(raw_city)
        if info is None:
            city_slug = 'bc'
        else:
            city_slug = info[0]

        key = (city_slug, cat_slug, biz_slug)
        used_slugs[key] = used_slugs.get(key, 0) + 1
        final_slug = biz_slug if used_slugs[key] == 1 else f'{biz_slug}-{used_slugs[key]}'

        url = f'{BASE}/{city_slug}/{cat_slug}/{final_slug}/'
        urls.append(url)

    # Insert as new column (right after Business Name for easy reading)
    df.insert(1, 'Demo URL', urls)

    # Save
    df.to_excel(OUT_XLSX, index=False)
    print(f'Saved to: {OUT_XLSX}')
    print(f'URLs added: {n - no_url_count} / {n}')
    if no_url_count:
        print(f'Rows without URL: {no_url_count}')
    print()
    print('Sample (first 5):')
    print(df[['Business Name', 'Demo URL']].head(5).to_string())

if __name__ == '__main__':
    main()
