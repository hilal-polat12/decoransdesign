"""One-off: write the vase technical notes and descriptions in the detailed H85/H86 layout (2026-11-09).

Order of the notes: casting, mold release, size and inside, FDM, clay printing, clay shrinkage, glaze and paint, water.
The inside is only described where the file really is hollow (H2, H3, H20); H8 is a sleeve around a glass cylinder.

    py tools\\vase_texts_2026-11-09.py
"""
import html, os, re

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CAST = ('Made for casting: print a master in PLA or resin, sand it smooth, then pour a silicone mold for plaster '
        'or a multi-part plaster mold for ceramic slip casting.')
SHRINK = 'For clay, scale the model up by about 12% to make up for drying and firing shrinkage.'
WATER = 'Glazed, fired ceramic holds water; plaster and PLA pieces need a glass or plastic liner for fresh flowers.'

TECH = {
    'h2': [CAST,
           'The faceted shaft and the banded collar release easily; the torn, flame-shaped petals at the top are the only real undercuts, so place the parting lines between them or use a flexible silicone mold.',
           'The file is a hollow vase, 151 x 147 x 300 mm, with the opening running down to the floor.',
           'FDM: prints upright on its base plate in one piece. Use 0.2 mm layers for the shaft and 0.12-0.16 mm for the petals and the hammered collar; keep the petal tips at 1.6 mm or more and slow down the last few millimeters.',
           'Clay 3D printing: 1.5-2 mm nozzle, 0.8-1 mm layers and 3-4 mm walls; sharpen the facets and tear the petal edges by hand while leather-hard.',
           SHRINK,
           'Glaze: a dark bronze or iron glaze on the shaft, wiped back from the high points, with a glossy red-orange inside the petals. Painted PLA: dark base coat, bronze or copper dry-brush, then a dark wash wiped back from the high points.',
           WATER + ' For a glowing torch, use battery LED lights only, never an open flame.'],
    'h3': [CAST,
           'The raised ridges wind around the body in one direction and never fold back, so a two- or three-part mold releases along the spiral; only the slanted rim needs a careful parting line.',
           'The file is a hollow vase, 221 x 223 x 300 mm, standing on a small foot ring, with the opening running down to the floor.',
           'FDM: prints upright in one piece. Use 0.16-0.2 mm layers, or 0.12 mm for a smoother ridge surface; 3-4 perimeters keep the ridges crisp. Scale uniformly so the spiral keeps its proportions.',
           'Clay 3D printing: 1.5-2 mm nozzle, 0.8-1 mm layers and 3-4 mm walls; soften the ridge crests with a damp sponge while leather-hard.',
           SHRINK,
           'Glaze: glossy cobalt blue under a crackle glaze, so fine lines run beneath the shine. Painted PLA: sand, prime, paint cobalt blue, add a thin crackle medium, then a high-gloss clear coat.',
           WATER + ' A PLA or PETG print can also be sealed inside.'],
    'h8': ['Made for casting: print a master in PLA or resin, sand it smooth, then pour a silicone mold for plaster; for ceramic slip casting, the open spiral needs a multi-part plaster mold.',
           'The ribbon winds around an open center, so the mold needs a core for the glass opening; the rippled texture has only shallow undercuts and releases cleanly from silicone.',
           'The file is a sleeve, 177 x 168 x 300 mm, built around a clear glass cylinder that holds the water; the glass is not included.',
           'Measure your glass cylinder first and scale the model so it slides in with 1-2 mm clearance; for clay, include the shrinkage in that scaling.',
           'FDM: prints upright in one piece, and the spiral band builds up on itself. Use 0.16-0.2 mm layers, or 0.12 mm to bring out the rippled texture; 3 perimeters and 15% infill are enough.',
           'Clay 3D printing: 1.5-2 mm nozzle, 0.8-1 mm layers and 3-4 mm walls; keep the ribbon thick enough to hold its turn while it dries.',
           SHRINK,
           'Glaze: a soft matte sage green. Painted PLA: sage green matte PLA as printed, or matte sage paint over a light primer.',
           'The glass insert holds the water, so the sleeve itself does not need to be watertight.'],
    'h9': [CAST,
           'The two bulbs and the trapezoid base are smooth and rounded, with spiral ribs on the lower bulb and a groove band on the upper one, so a two-part mold split along the tilt of the figure-eight releases cleanly.',
           'Size: 260 x 178 x 300 mm, leaning to one side on its trapezoid base.',
           'FDM: prints upright on its base in one piece. Translucent amber PETG gives the glass look; use 0.16 mm layers with slower outer walls for a clean, clear surface.',
           'Clay 3D printing: 1.5-2 mm nozzle, 0.8-1 mm layers and 3-4 mm walls; prop the leaning upper bulb while the clay dries.',
           SHRINK,
           'Glaze: a translucent amber or honey glaze that pools darker in the spiral ribs. On PETG, a gloss clear coat deepens the glass-like shine.',
           WATER + ' Check stability with water inside before use, and add weight to the base if printing larger.'],
    'h10': [CAST,
            'The rings step inward as they rise and every step faces up, so the form releases from a two-part mold; the dotted, hammered and ribbed textures are shallow and copy well in silicone.',
            'Size: 233 x 233 x 300 mm, tapering from a wide base to a narrow neck.',
            'FDM: prints upright as one piece. 0.12-0.16 mm layers keep the ring textures distinct, and the stepped rings build up on each other.',
            'Clay 3D printing: 1.5-2 mm nozzle, 0.8-1 mm layers and 3-4 mm walls; press the dotted and hammered textures in by hand while leather-hard if they soften.',
            SHRINK,
            'Glaze: a metallic violet or plum lustre over a dark base. Painted PLA: gloss black primer, violet candy or color-shift paint, then a clear coat; leave the textured rings unsanded, mask them and polish only the smooth rings.',
            WATER + ' A small glass liner also suits a few slim stems.'],
    'h18': [CAST,
            'The three stems braid together and cross over one another, so this form needs a multi-part mold or a flexible silicone mold with the parting line along the braid; the scales, rings and flutes are shallow.',
            'Size: 236 x 126 x 300 mm, with three flared mouths at different heights above a round base.',
            'FDM: prints upright in one piece. 0.12-0.16 mm layers bring out the scales, rings and flutes; use 15-20% infill in the base.',
            'Clay 3D printing: 1.5-2 mm nozzle, 0.8-1 mm layers and 3-4 mm walls; slow down on the leaning stems and let the base firm up before the braid rises.',
            SHRINK,
            'Glaze: a matte stone-gray glaze with a sandy texture, like cast concrete. Painted PLA: stone-effect spray, or gray paint with a light sand texture.',
            WATER + ' Small water tubes in each stem also work; test each mouth with water for leaks before arranging flowers.'],
    'h20': [CAST,
            'Each tier steps in or out on its own, so the form splits cleanly into a two-part mold; only the flared trumpet rim needs a careful parting line.',
            'The file is a hollow vase, 143 x 143 x 300 mm: 3 mm walls, a 4 mm floor and the mouth opening straight into the body; the flared foot is solid.',
            'FDM: prints upright on the flared foot in one piece. 0.12-0.16 mm layers keep the scales, flutes and spiral grooves distinct; the trumpet rim is the widest overhang, so slow it down for a clean edge.',
            'Clay 3D printing: 1.5-2 mm nozzle, 0.8-1 mm layers and 3-4 mm walls; refine the scales and spiral grooves by hand while leather-hard.',
            SHRINK,
            'Glaze: deep violet at the foot fading to soft lavender toward the rim, in a matte finish. Painted PLA: deep violet base, airbrushed to lavender toward the rim, then a matte clear coat.',
            WATER + ' A glass test-tube liner also suits a few long stems.'],
}

MORE = {   # one more sentence on each description, in the voice of H85
    'h2': ' Switched off, it reads as a sculpted bronze torch; with a warm LED inside, the red-orange petals glow like a flame caught in metal.',
    'h3': ' The ridges catch the light differently as you walk past, so the wave seems to keep turning around the body.',
    'h8': ' Change the flowers and the glass stays clear, while the sage ribbon frames every stem like a hand-wrapped sleeve.',
    'h9': ' Seen from the side, the leaning silhouette gives even a single stem a playful, hand-blown look.',
    'h10': ' Every texture is part of the model, so the effect stays whether it is printed, cast in plaster or glazed in ceramic.',
    'h18': ' Each mouth sits at its own height and angle, so even three single stems read as a full arrangement.',
    'h20': ' Every section has its own pattern, so the vase reads like a stack of small turned vessels balanced on its ribbed foot.',
}

path = os.path.join(HERE, 'index.html')
src = open(path, encoding='utf-8').read()
for code, notes in TECH.items():
    m = re.search(r'(<div class="card" data-subcat="vases"[^>]*?onclick="location\.href=\'/vases/%s\';" data-tech=")(.*?)(")' % code, src, flags=re.S)
    assert m, code
    txt = html.escape('\n'.join(notes), quote=True).replace('&#x27;', "'")
    src = src[:m.start(2)] + txt + src[m.end(2):]
    # description: the first <p> after the card's tag line
    i = src.index("location.href='/vases/%s';" % code)
    p0 = src.index('<p>', i)
    p1 = src.index('</p>', p0)
    desc = src[p0 + 3:p1]
    if MORE[code].strip() not in desc:
        src = src[:p1] + MORE[code] + src[p1:]
    print('%s: %d notes, description %d characters' % (code, len(notes), len(src[p0 + 3:src.index('</p>', p0)])))
open(path, 'w', encoding='utf-8', newline='').write(src)
