"""Generate static product and category pages and sitemap.xml.

/vases/h1 -> p/vases/h1.html (one per product) and /reliefs -> c/reliefs.html (one per category).
Runs on every Vercel deploy (see vercel.json), so the pages are always built from the current
index.html: each one is index.html with its own title, description, canonical URL, social preview,
structured data and main content already in the HTML.
Run locally with: python build_pages.py
"""
import html
import json
import os
import re

SITE = 'https://www.decoransdesign.com'
ROOT = os.path.dirname(os.path.abspath(__file__))
BRAND = 'Decorans Design'

CATEGORIES = {
    'reliefs': {
        'label': 'Wall Reliefs & Panels',
        'title': 'Wall Relief STL Files for 3D Printing | Decorans Design',
        'desc': '3D printable wall relief and wall panel STL files: layered scenes, mosaics and abstract '
                'panels, modeled at real size and ready to print in sections.',
    },
    'mirrors': {
        'label': 'Mirrors',
        'title': '3D Printable Wall Mirror STL Files | Decorans Design',
        'desc': '3D printable wall mirror frame STL files: sculpted animal, nature and fantasy frames. '
                'Print the frame in sections and have the glass cut locally.',
    },
    'figurines': {
        'label': 'Figurines',
        'title': '3D Printable Figurine STL Files | Decorans Design',
        'desc': '3D printable figurine STL files: animals, fables and fantasy characters, sculpted in '
                'detail and ready to print on FDM or resin printers.',
    },
    'vases': {
        'label': 'Vases & Curios',
        'title': '3D Printable Vase & Curio STL Files | Decorans Design',
        'desc': '3D printable vase, candle holder and curio STL files: sculptural pieces for shelves '
                'and tables, ready to print in PLA, PETG or resin.',
    },
    'lamps': {
        'label': 'Floor Lamps',
        'title': '3D Printable Floor Lamp STL Files | Decorans Design',
        'desc': '3D printable floor lamp STL files: sculptural lamps designed to scale to full height, '
                'print in sections and light with low-heat LEDs.',
    },
}

TITLE_MAX = 60
DESC_MAX = 155


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


def clip(text, limit):
    """Shorten to at most `limit` characters at a word boundary."""
    if len(text) <= limit:
        return text
    cut = text[:limit - 1].rsplit(' ', 1)[0].rstrip(' ,;:-')
    return cut + '…'


def product_title(name):
    for t in (name + ' | 3D Printable STL | ' + BRAND, name + ' STL File | ' + BRAND, name + ' | ' + BRAND):
        if len(t) <= TITLE_MAX:
            return t
    return name + ' | ' + BRAND


def product_description(p):
    text = first_sentence(p['desc'])
    if 'STL' not in text:
        text = p['name'] + ': 3D printable STL and OBJ file. ' + text
    return clip(text, DESC_MAX)


def set_meta(page, pattern, replacement):
    new, n = re.subn(pattern, lambda _: replacement, page, count=1)
    assert n == 1, pattern
    return new


def set_head(page, title, desc, url, og_type, image_abs=None):
    e = lambda s: html.escape(s, quote=True)
    page = set_meta(page, r'<title>.*?</title>', '<title>' + e(title) + '</title>')
    page = set_meta(page, r'<meta name="description" content="[^"]*">', '<meta name="description" content="' + e(desc) + '">')
    page = set_meta(page, r'<link rel="canonical" href="[^"]*">', '<link rel="canonical" href="' + url + '">')
    page = set_meta(page, r'<meta property="og:type" content="[^"]*">', '<meta property="og:type" content="' + og_type + '">')
    page = set_meta(page, r'<meta property="og:title" content="[^"]*">', '<meta property="og:title" content="' + e(title) + '">')
    page = set_meta(page, r'<meta property="og:description" content="[^"]*">', '<meta property="og:description" content="' + e(desc) + '">')
    page = set_meta(page, r'<meta property="og:url" content="[^"]*">', '<meta property="og:url" content="' + url + '">')
    page = set_meta(page, r'<meta name="twitter:title" content="[^"]*">', '<meta name="twitter:title" content="' + e(title) + '">')
    page = set_meta(page, r'<meta name="twitter:description" content="[^"]*">', '<meta name="twitter:description" content="' + e(desc) + '">')
    if image_abs:
        page = set_meta(page, r'<meta property="og:image" content="[^"]*">', '<meta property="og:image" content="' + e(image_abs) + '">')
        page = set_meta(page, r'<meta name="twitter:image" content="[^"]*">', '<meta name="twitter:image" content="' + e(image_abs) + '">')
    return page


def json_ld(data):
    return '<script type="application/ld+json">' + json.dumps(data, ensure_ascii=False).replace('</', '<\\/') + '</script>\n'


def breadcrumb(items):
    return {'@type': 'BreadcrumbList', 'itemListElement': [
        {'@type': 'ListItem', 'position': i + 1, 'name': name, 'item': url} for i, (name, url) in enumerate(items)]}


def common_cleanup(page, keep_codes):
    """Shared changes for generated pages: the hero headline is not this page's H1, the homepage's
    structured data does not belong here, and the cards of other products lose their long texts
    (they are hidden on these pages and would repeat the whole catalog on every page)."""
    page, n = re.subn(r'<h1 class="hero-title">(.*?)</h1>', r'<p class="hero-title">\1</p>', page, count=1)
    assert n == 1, 'hero headline not found'
    page = re.sub(r'<script type="application/ld\+json">.*?</script>\n?', '', page, count=1, flags=re.S)

    def slim(m):
        card = m.group(0)
        code = re.search(r"location\.href='/[a-z-]+/(h\d+)'", card)
        if not code or code.group(1) in keep_codes:
            return card
        head_end = card.index('>') + 1
        head = re.sub(r'\s(data-tech|data-gallery|data-full-description)="[^"]*"', '', card[:head_end])
        return head + re.sub(r'<p>.*?</p>', '', card[head_end:], count=1, flags=re.S)

    return re.sub(r'<div class="card"[^>]*>.*?<div class="card-footer">', slim, page, flags=re.S)


def build_page(template, p):
    e = lambda s: html.escape(s, quote=True)
    cat = CATEGORIES.get(p['cat'], {'label': p['cat'].title()})
    url = SITE + '/' + p['cat'] + '/' + p['code']
    image = p['gallery'][0][0] if p['gallery'] else p['thumb'][0]
    image_abs = SITE + '/' + image
    code_label = 'Code: ' + p['code'].upper() + ' · 3D Print Design'

    page = common_cleanup(template, {p['code']})
    page = set_head(page, product_title(p['name']), product_description(p), url, 'product', image_abs)

    schema = {
        '@context': 'https://schema.org',
        '@type': 'Product',
        'name': p['name'],
        'sku': p['code'].upper(),
        'description': p['desc'],
        'image': [SITE + '/' + src for src, _ in p['gallery']] or [image_abs],
        'brand': {'@type': 'Brand', 'name': BRAND},
        'category': cat['label'],
        'url': url,
    }
    if p['price']:
        schema['offers'] = {'@type': 'Offer', 'price': p['price'], 'priceCurrency': 'USD',
                            'availability': 'https://schema.org/InStock', 'url': url}
    crumbs = dict(breadcrumb([('Home', SITE + '/'), (cat['label'], SITE + '/' + p['cat']), (p['name'], url)]),
                  **{'@context': 'https://schema.org'})
    head_extra = (
        '<script>window.PRODUCT_ROUTE=' + json.dumps(p['code']) + ';</script>\n'
        '<style>main > section,.hero{display:none}</style>\n' + json_ld(schema) + json_ld(crumbs)
    )
    page = page.replace('</head>', head_extra + '</head>', 1)

    # product content already in the HTML (the page script fills in the rest: specs, 3D model, cart)
    page = set_meta(page, r'<a href="#home" id="productBack" class="product-back">[^<]*</a>',
                    '<a href="/' + p['cat'] + '" id="productBack" class="product-back">← Back to ' + e(cat['label']) + '</a>')
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


def build_category(template, key, products):
    e = lambda s: html.escape(s, quote=True)
    cat = CATEGORIES[key]
    url = SITE + '/' + key
    items = [p for p in products if p['cat'] == key]

    page = common_cleanup(template, {p['code'] for p in items})
    page = set_head(page, cat['title'], cat['desc'], url, 'website')
    page = set_meta(page, r'<h2 id="homeCatTitle" class="is-all">[^<]*</h2>',
                    '<h1 id="homeCatTitle">' + e(cat['label']) + '</h1>')

    collection = {
        '@context': 'https://schema.org',
        '@type': 'CollectionPage',
        'name': cat['label'],
        'description': cat['desc'],
        'url': url,
        'isPartOf': {'@type': 'WebSite', 'name': BRAND, 'url': SITE + '/'},
        'mainEntity': {'@type': 'ItemList', 'numberOfItems': len(items), 'itemListElement': [
            {'@type': 'ListItem', 'position': i + 1, 'url': SITE + '/' + p['cat'] + '/' + p['code'], 'name': p['name']}
            for i, p in enumerate(items)]},
    }
    crumbs = dict(breadcrumb([('Home', SITE + '/'), (cat['label'], url)]), **{'@context': 'https://schema.org'})
    page = page.replace('</head>', json_ld(collection) + json_ld(crumbs) + '</head>', 1)
    # hidden inline (not by a stylesheet rule) so the page script can show it again when the
    # visitor switches to Home without a reload
    page = set_meta(page, r'<div class="hero">', '<div class="hero" style="display:none">')
    return page


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(text)


def main():
    template = open(os.path.join(ROOT, 'index.html'), encoding='utf-8').read()
    products = parse_products(template)
    assert products, 'no product cards found in index.html'
    for p in products:
        write(os.path.join(ROOT, 'p', p['cat'], p['code'] + '.html'), build_page(template, p))
    for key in CATEGORIES:
        write(os.path.join(ROOT, 'c', key + '.html'), build_category(template, key, products))

    urls = [SITE + '/'] + [SITE + '/' + k for k in CATEGORIES] + [SITE + '/' + p['cat'] + '/' + p['code'] for p in products]
    lines = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    lines += ['  <url><loc>' + u + '</loc></url>' for u in urls]
    write(os.path.join(ROOT, 'sitemap.xml'), '\n'.join(lines + ['</urlset>', '']))
    print('built', len(products), 'product pages,', len(CATEGORIES), 'category pages and sitemap.xml')


if __name__ == '__main__':
    main()
