"""Generate a static page per product (/vases/h1 -> p/vases/h1.html) and sitemap.xml.

Runs on every Vercel deploy (see vercel.json), so the product pages are always built from the
current index.html: each one is index.html with the product's own title, description, canonical
URL, social preview and product content already in the HTML.
Run locally with: python build_pages.py
"""
import html
import json
import os
import re
from datetime import date

SITE = 'https://www.decoransdesign.com'
ROOT = os.path.dirname(os.path.abspath(__file__))


def attr(attrs, name):
    m = re.search(r'\b' + name + r'="([^"]*)"', attrs)
    return html.unescape(m.group(1)) if m else ''


def parse_products(page):
    products = []
    for m in re.finditer(r'<div class="card"([^>]*)>', page):
        attrs = m.group(1)
        link = re.search(r"location\.href='/([a-z-]+)/(h\d+)'", attrs)
        if not link:
            continue
        body = page[m.end():m.end() + 6000]
        thumb = re.search(r'<img src="([^"]+)" alt="([^"]*)"', body)
        title = re.search(r'<h3>(.*?)</h3>', body, re.S)
        desc = re.search(r'<p>(.*?)</p>', body, re.S)
        gallery = []
        for entry in attr(attrs, 'data-gallery').split(';'):
            parts = entry.strip().split('|')
            if parts[0]:
                gallery.append((parts[0], parts[1] if len(parts) > 1 else ''))
        products.append({
            'cat': link.group(1),
            'code': link.group(2),
            'name': html.unescape(re.sub(r'<[^>]+>', '', title.group(1))).strip() if title else link.group(2).upper(),
            'desc': attr(attrs, 'data-full-description') or (html.unescape(re.sub(r'<[^>]+>', '', desc.group(1))).strip() if desc else ''),
            'thumb': (thumb.group(1), html.unescape(thumb.group(2))) if thumb else ('', ''),
            'gallery': gallery,
            'price': attr(attrs, 'data-price'),
        })
    return products


def first_sentence(text):
    m = re.match(r'^.*?[.!?](\s|$)', text)
    return (m.group(0) if m else text).strip()


def set_meta(page, pattern, replacement):
    new, n = re.subn(pattern, lambda _: replacement, page, count=1)
    assert n == 1, pattern
    return new


def build_page(template, p):
    e = lambda s: html.escape(s, quote=True)
    url = SITE + '/' + p['cat'] + '/' + p['code']
    title = p['name'] + ' | 3D Printable STL File | Decorans Design'
    meta_desc = p['name'] + ': print-ready STL/OBJ file. ' + first_sentence(p['desc'])
    image = p['gallery'][0][0] if p['gallery'] else p['thumb'][0]
    image_abs = SITE + '/' + image
    code_label = 'Code: ' + p['code'].upper() + ' · 3D Print Design'

    page = template
    page = set_meta(page, r'<title>.*?</title>', '<title>' + e(title) + '</title>')
    page = set_meta(page, r'<meta name="description" content="[^"]*">', '<meta name="description" content="' + e(meta_desc) + '">')
    page = set_meta(page, r'<link rel="canonical" href="[^"]*">', '<link rel="canonical" href="' + url + '">')
    page = set_meta(page, r'<meta property="og:type" content="[^"]*">', '<meta property="og:type" content="product">')
    page = set_meta(page, r'<meta property="og:title" content="[^"]*">', '<meta property="og:title" content="' + e(p['name'] + ' | Decorans Design') + '">')
    page = set_meta(page, r'<meta property="og:description" content="[^"]*">', '<meta property="og:description" content="' + e(meta_desc) + '">')
    page = set_meta(page, r'<meta property="og:image" content="[^"]*">', '<meta property="og:image" content="' + e(image_abs) + '">')
    page = set_meta(page, r'<meta property="og:url" content="[^"]*">', '<meta property="og:url" content="' + url + '">')
    page = set_meta(page, r'<meta name="twitter:title" content="[^"]*">', '<meta name="twitter:title" content="' + e(p['name'] + ' | Decorans Design') + '">')
    page = set_meta(page, r'<meta name="twitter:description" content="[^"]*">', '<meta name="twitter:description" content="' + e(meta_desc) + '">')
    page = set_meta(page, r'<meta name="twitter:image" content="[^"]*">', '<meta name="twitter:image" content="' + e(image_abs) + '">')

    schema = {
        '@context': 'https://schema.org',
        '@type': 'Product',
        'name': p['name'],
        'sku': p['code'].upper(),
        'description': p['desc'],
        'image': [SITE + '/' + src for src, _ in p['gallery']] or [image_abs],
        'brand': {'@type': 'Brand', 'name': 'Decorans Design'},
        'url': url,
    }
    if p['price']:
        schema['offers'] = {'@type': 'Offer', 'price': p['price'], 'priceCurrency': 'USD',
                            'availability': 'https://schema.org/InStock', 'url': url}
    head_extra = (
        '<script>window.PRODUCT_ROUTE=' + json.dumps(p['code']) + ';</script>\n'
        '<style>main > section,.hero{display:none}</style>\n'
        '<script type="application/ld+json">' + json.dumps(schema, ensure_ascii=False).replace('</', '<\\/') + '</script>\n'
    )
    page = page.replace('</head>', head_extra + '</head>', 1)

    # product content already in the HTML (the page script fills in the rest: specs, 3D model, cart)
    page = set_meta(page, r'<div id="productPage" class="product-page" aria-hidden="true">',
                    '<div id="productPage" class="product-page is-open page-visible" aria-hidden="false">')
    page = set_meta(page, r'<span id="productCode" class="product-code"></span>',
                    '<span id="productCode" class="product-code">' + e(code_label) + '</span>')
    page = set_meta(page, r'<h2 id="productTitle"></h2>', '<h1 id="productTitle">' + e(p['name']) + '</h1>')
    page = set_meta(page, r'<p id="productDescription" class="product-description"></p>',
                    '<p id="productDescription" class="product-description">' + e(p['desc']) + '</p>')
    page = set_meta(page, r'<img id="productImage" src="" alt="">',
                    '<img id="productImage" src="' + e(p['thumb'][0]) + '" alt="' + e(p['thumb'][1]) + '">')
    if p['gallery']:
        imgs = ''.join('<img src="' + e(src) + '" alt="' + e(alt) + '">' for src, alt in p['gallery'])
        page = set_meta(page, r'<div id="productGallery" class="product-gallery" style="display:none;"></div>',
                        '<div id="productGallery" class="product-gallery" style="display:grid;">' + imgs + '</div>')
        page = set_meta(page, r'<div class="product-layout">', '<div class="product-layout has-photo-grid">')
        page = set_meta(page, r'<div class="product-image">', '<div class="product-image" style="display:none;">')
    return page


def main():
    template = open(os.path.join(ROOT, 'index.html'), encoding='utf-8').read()
    products = parse_products(template)
    assert products, 'no product cards found in index.html'
    for p in products:
        out = os.path.join(ROOT, 'p', p['cat'], p['code'] + '.html')
        os.makedirs(os.path.dirname(out), exist_ok=True)
        with open(out, 'w', encoding='utf-8', newline='\n') as f:
            f.write(build_page(template, p))

    today = date.today().isoformat()
    urls = [SITE + '/'] + [SITE + '/' + p['cat'] + '/' + p['code'] for p in products]
    with open(os.path.join(ROOT, 'sitemap.xml'), 'w', encoding='utf-8', newline='\n') as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n')
        for u in urls:
            f.write('  <url><loc>' + u + '</loc><lastmod>' + today + '</lastmod></url>\n')
        f.write('</urlset>\n')
    print('built', len(products), 'product pages and sitemap.xml')


if __name__ == '__main__':
    main()
