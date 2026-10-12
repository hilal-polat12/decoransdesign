# Decorans Design

Static site for www.decoransdesign.com, deployed on Vercel.

## How it is built

- `index.html` is the home page and the single source for everything else: layout, styles, script, the 80 product cards and the category intro texts (`#categoryIntros`).
- `build_pages.py` runs on every Vercel deploy (`vercel.json`) and generates from `index.html`:
  - one page per product, `/vases/h1` → `p/vases/h1.html`
  - one page per category, `/reliefs` → `c/reliefs.html`
  - `sitemap.xml`
- `p/`, `c/` and `sitemap.xml` are generated and not committed.
- `sitemap-state.json` is committed: it remembers when each page's content last changed, for the dates in the sitemap.
- `terms.html`, `license.html`, `refund-policy.html`, `privacy-policy.html` and `404.html` are plain pages styled by `legal.css`.

## Editing

- Product: edit its `.card` block in `index.html` (name, description, `data-tech`, `data-gallery`, `data-price`) and its line in `PRODUCT_SPECS`.
- Category title and description: `CATEGORIES` in `build_pages.py` (and `CATEGORY_TITLES` in `index.html`). Category intro text: `#categoryIntros` in `index.html`.
- After editing, run `python build_pages.py` and commit `sitemap-state.json` together with the change.
