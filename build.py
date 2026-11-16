#!/usr/bin/env python3
"""Generate index.html for Hotel Sky Lounge v2 (parallax editorial) from menu.json.

Usage: python3 build.py
Reads menu.json in the same directory, writes index.html.
Menu items are rendered server-side so the full menu is in the HTML (SEO + no-JS friendly).
"""
import html
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
DATA = json.loads((HERE / "menu.json").read_text(encoding="utf-8"))
R = DATA["restaurant"]
SWIGGY = "https://www.swiggy.com/city/nanded/hotel-sky-lounge-restaurant-nila-road-harsh-nagar-rest751068"

VEG_CATEGORIES = {"starters-veg", "main-veg", "sabzi", "breads", "salad-finger",
                  "beverages", "dessert", "rice-biryani"}
NONVEG_CATEGORIES = {"starters-nonveg", "mughlai-nonveg", "seafood"}
NONVEG_RE = re.compile(
    r"\b(chicken|mutton|fish|prawns?|crabs?|eggs?|keema|kheema|boti|paya|"
    r"bheja|bater|meat|lamb|seafood|murg|raan|non veg)\b"
)


def is_veg(cat_id, name):
    if cat_id in VEG_CATEGORIES:
        return True
    if cat_id in NONVEG_CATEGORIES:
        return False
    return not NONVEG_RE.search(name.lower())


def esc(s):
    return html.escape(str(s), quote=True)


def tag_html(tag):
    if not tag:
        return ""
    cls = "tag spicy" if tag.lower() == "spicy" else "tag"
    return f'<span class="mi-tag {cls}">{esc(tag)}</span>'


def item_html(cat, item):
    veg = is_veg(cat["id"], item["name"])
    dot = '<span class="veg-dot" title="Veg"></span>' if veg else '<span class="veg-dot nonveg" title="Non-veg"></span>'
    desc = f'<p class="mi-desc">{esc(item["desc"])}</p>' if item.get("desc") else ""
    note = f'<span class="mi-note">{esc(item["note"])}</span>' if item.get("note") else ""
    search = esc(f'{item["name"]} {item.get("desc", "")}')
    return (
        f'<article class="menu-item" data-veg="{"1" if veg else "0"}" '
        f'data-category="{esc(cat["title"])}" data-search="{search}">'
        f"{dot}<div class='mi-main'><div class='mi-name-row'>"
        f"<h3 class='mi-name'>{esc(item['name'])}</h3>{tag_html(item.get('tag'))}"
        f"</div>{desc}</div>"
        f"<div class='mi-price'>{note}&#8377;{esc(item['price'])}</div></article>"
    )


def panel_html(cat, first):
    active = " active" if first else ""
    if "table" in cat:
        t = cat["table"]
        ths = "".join(f"<th>{esc(c)}</th>" for c in t["columns"])
        rows = ""
        for row in t["rows"]:
            tds = "".join(f"<td>&#8377;{esc(p)}</td>" for p in row["prices"])
            rows += f"<tr><td>{esc(row['name'])}</td>{tds}</tr>"
        body = (f'<div style="overflow-x:auto"><table class="rn-table">'
                f"<thead><tr><th></th>{ths}</tr></thead><tbody>{rows}</tbody></table></div>")
        return f'<div class="menu-panel{active}" id="panel-{cat["id"]}" role="tabpanel">{body}</div>'
    items = "".join(item_html(cat, it) for it in cat["items"])
    return (f'<div class="menu-panel{active}" id="panel-{cat["id"]}" role="tabpanel">'
            f'<div class="menu-cols">{items}</div></div>')


tabs = "".join(
    f'<button class="tab{" active" if i == 0 else ""}" data-target="panel-{c["id"]}" role="tab">{esc(c["title"])}</button>'
    for i, c in enumerate(DATA["menu"])
)
panels = "".join(panel_html(c, i == 0) for i, c in enumerate(DATA["menu"]))

total_items = sum(len(c.get("items", c.get("table", {}).get("rows", []))) for c in DATA["menu"])

ld = {
    "@context": "https://schema.org",
    "@type": "Restaurant",
    "name": R["name"],
    "slogan": R["tagline"],
    "servesCuisine": R["cuisines"],
    "priceRange": "₹₹",
    "telephone": R["phone"],
    "address": {
        "@type": "PostalAddress",
        "streetAddress": "Jay Bhawani Chowk, Nila Road",
        "addressLocality": "Nanded",
        "addressRegion": "Maharashtra",
        "postalCode": "431605",
        "addressCountry": "IN",
    },
    "geo": {"@type": "GeoCoordinates", "latitude": 19.193374, "longitude": 77.278159},
    "openingHoursSpecification": {
        "@type": "OpeningHoursSpecification",
        "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
        "opens": "11:00",
        "closes": "00:00",
    },
    "aggregateRating": {"@type": "AggregateRating", "ratingValue": "4.1", "reviewCount": "126"},
    "acceptsReservations": "False",
    "sameAs": [R["instagram"], R["maps"], R["zomato"], SWIGGY],
}
ld_json = json.dumps(ld, ensure_ascii=False, indent=2)

WAVES = """<div class="waves" data-plx="0.03" aria-hidden="true"><svg width="520" height="150" viewBox="0 0 520 150" fill="none"><path d="M0 75 C 65 30, 130 120, 195 75 C 260 30, 325 120, 390 75 C 455 30, 490 60, 520 75" stroke="#571f18" stroke-width="1" opacity="0.45"/><path d="M0 100 C 65 55, 130 145, 195 100 C 260 55, 325 145, 390 100 C 455 55, 490 85, 520 100" stroke="#b93a26" stroke-width="1" opacity="0.35"/></svg></div>"""

HTML = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Hotel Sky Lounge — Family Restaurant &amp; Bar, Nanded</title>
<meta name="description" content="Hotel Sky Lounge, Nanded — family restaurant & bar on Nila Road. Tandoor, Mughlai, dum biryani & seafood. Open daily 11 AM–12 AM. Order on Zomato & Swiggy.">
<meta property="og:title" content="Hotel Sky Lounge — Family Restaurant & Bar, Nanded">
<meta property="og:description" content="Tandoor, Mughlai, dum biryani & seafood on Nila Road, Nanded. Open daily 11 AM–12 AM.">
<meta property="og:type" content="website">
<meta property="og:image" content="images/ai-hero.jpg">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,500;0,600;1,500;1,600&family=Jost:wght@200;300;400;500&family=Manrope:wght@400;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="styles.css">
<link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>✦</text></svg>">
<script>document.documentElement.classList.add('js');</script>
<script type="application/ld+json">
{ld_json}
</script>
</head>
<body>

<header class="header">
  <div class="wrap header-inner">
    <nav class="nav" aria-label="Main">
      <a href="#menu">Menu</a>
      <a href="#story">Story</a>
    </nav>
    <a class="monogram" href="#top" aria-label="Sky Lounge — home">SL</a>
    <nav class="nav right" aria-label="Main">
      <a href="#gallery">Gallery</a>
      <a href="#visit">Visit</a>
      <a class="order-link" href="{esc(R['zomato'])}" target="_blank" rel="noopener">Order</a>
    </nav>
    <button class="burger" aria-label="Open menu" aria-expanded="false">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"><path d="M3 7h18M3 12h18M3 17h18"/></svg>
    </button>
  </div>
</header>
<nav class="mobile-nav" aria-label="Mobile">
  <a href="#menu">Menu</a>
  <a href="#story">Story</a>
  <a href="#gallery">Gallery</a>
  <a href="#visit">Visit</a>
  <a href="{esc(R['zomato'])}" target="_blank" rel="noopener">Order on Zomato</a>
  <a href="{esc(SWIGGY)}" target="_blank" rel="noopener">Order on Swiggy</a>
</nav>

<!-- HERO : fixed, the page scrolls over it -->
<section class="hero" id="top" aria-label="Hotel Sky Lounge">
  <img class="bg" src="images/ai-hero.jpg" alt="Overhead feast of butter chicken, tandoori chicken, naan and chutneys" fetchpriority="high">
  <div class="hero-inner">
    <div class="wrap">
      <h1 class="display">Sky Lounge</h1>
      <p class="hero-sub">Fire, patience &amp; the art of the handi — on Nila Road, Nanded.</p>
      <div class="hero-meta">
        <span><span class="star">★</span> 4.1 · 126 Google reviews</span>
        <span>Open today · 11 AM – 12 AM</span>
        <span>Family restaurant &amp; bar</span>
      </div>
    </div>
  </div>
  <span class="scroll-cue">Scroll</span>
</section>

<div class="page">
<main>

<!-- INTRO -->
<section class="intro section-pad">
  <div class="wrap">
    <p class="eyebrow reveal">01 — The Restaurant</p>
    <p class="statement reveal reveal-d1">A table set for the family, <em>a fire kept for the flavour.</em></p>
    <p class="lead reveal reveal-d2">On Nila Road in Nanded, Sky Lounge keeps two rooms under one roof — a calm family dining room, and a full bar of its own. Between them, one kitchen: clay ovens, slow handis, and biryanis guests return for.</p>
    <div class="intro-stats reveal">
      <div><b>{total_items}+</b><span>Dishes</span></div>
      <div><b>4.1 ★</b><span>Google rating</span></div>
      <div><b>13 hrs</b><span>Open daily</span></div>
    </div>
  </div>
  <div style="position:absolute;right:4%;top:60px;">{WAVES}</div>
</section>

<!-- STORY -->
<section id="story" class="section-pad" style="padding-top:20px;">
  <div class="wrap story-grid">
    <div class="story-photo-main">
      <div data-plx="0.06"><img src="images/ai-tandoor.jpg" alt="Chef garnishing a sizzling tandoori platter beside the clay oven" loading="lazy"></div>
      <div class="story-photo-small" data-plx="0.08"><img src="images/interior.jpg" alt="The family dining room at Hotel Sky Lounge" loading="lazy"></div>
      <p class="caption"><i>The tandoor,</i> lit every morning &nbsp;·&nbsp; <i>the dining room,</i> as it is</p>
    </div>
    <div class="story-copy reveal">
      <p class="eyebrow">02 — From the Fire</p>
      <h2 class="display">Slow food,<br><span class="serif-it">cooked fast &amp; hot.</span></h2>
      <p>Marinades rest for a day. Handis seal and slow-cook for hours. Kebabs meet the clay oven only when the coals are right. <strong>Nothing here is hurried except the service.</strong></p>
      <p>Come at night, when the tower lights up and the whole building glows over Nila Road — that is when Sky Lounge feels most itself.</p>
      <ul class="story-list">
        <li><span>Family &amp; bar sections</span><span>separate, always</span></li>
        <li><span>Full bar</span><span>at the restaurant</span></li>
        <li><span>Home delivery</span><span>Zomato &amp; Swiggy</span></li>
        <li><span>Takeaway</span><span>call ahead</span></li>
      </ul>
    </div>
  </div>
</section>

<!-- SIGNATURES -->
<section id="signatures" class="signatures section-pad">
  <div class="wrap">
    <div class="sec-head reveal">
      <span class="num">03</span>
      <h2 class="display">Signatures</h2>
      <span class="rule"></span>
      <span class="serif-it" style="font-size:1.4rem;color:var(--wine);">from the kitchen</span>
    </div>

    <article class="sig-row">
      <div class="sig-photo" data-plx="0.05"><img src="images/biryani.jpg" alt="Chicken dum biryani" loading="lazy"></div>
      <div class="sig-body reveal"><span class="sig-index">No. 01</span><h3>Chicken Dum Biryani</h3><p>Fragrant basmati layered with marinated chicken, sealed and slow-cooked on dum.</p><div class="sig-foot"><span class="sig-price">₹290</span><span class="tag">Bestseller</span></div></div>
    </article>
    <article class="sig-row">
      <div class="sig-photo" data-plx="0.09"><img src="images/prawns.jpg" alt="Ghee roast prawns" loading="lazy"></div>
      <div class="sig-body reveal"><span class="sig-index">No. 02</span><h3>Ghee Roast Prawns</h3><p>Sea prawns marinated 24 hours, roasted in ghee with Mangalorean spice.</p><div class="sig-foot"><span class="sig-price">₹490</span><span class="tag">Signature</span></div></div>
    </article>
    <article class="sig-row">
      <div class="sig-photo" data-plx="0.05"><img src="images/chilli-chicken.jpg" alt="Chicken chilli" loading="lazy"></div>
      <div class="sig-body reveal"><span class="sig-index">No. 03</span><h3>Chicken Chilli</h3><p>Wok-tossed chicken with green peppers, onion and a fiery chilli-garlic glaze.</p><div class="sig-foot"><span class="sig-price">₹340</span><span class="tag spicy">Spicy</span></div></div>
    </article>
    <article class="sig-row">
      <div class="sig-photo" data-plx="0.09"><img src="images/noodles.jpg" alt="Hakka noodles" loading="lazy"></div>
      <div class="sig-body reveal"><span class="sig-index">No. 04</span><h3>Hakka Noodles</h3><p>Smoky wok-tossed noodles with peppers, cabbage and red chilli.</p><div class="sig-foot"><span class="sig-price">from ₹260</span></div></div>
    </article>
    <article class="sig-row">
      <div class="sig-photo" data-plx="0.05"><img src="images/tandoori-fish.jpg" alt="Tandoori fish" loading="lazy"></div>
      <div class="sig-body reveal"><span class="sig-index">No. 05</span><h3>Tandoori Fish</h3><p>Whole fish coated in red spice, chargrilled in the clay oven, with chutney.</p><div class="sig-foot"><span class="sig-price">₹410</span></div></div>
    </article>
    <article class="sig-row">
      <div class="sig-photo" data-plx="0.09"><img src="images/naan.jpg" alt="Fresh tandoori naan in a basket" loading="lazy"></div>
      <div class="sig-body reveal"><span class="sig-index">No. 06</span><h3>Tandoori Breads</h3><p>Baked fresh in the tandoor — butter naan, garlic naan, laccha paratha and more.</p><div class="sig-foot"><span class="sig-price">from ₹25</span></div></div>
    </article>
  </div>
</section>

<!-- PARALLAX BAND -->
<section class="band" aria-label="The dining room at night">
  <div class="band-img"><img src="images/ai-interior.jpg" alt="Candlelit dining room with brass lamps and velvet chairs" loading="lazy"></div>
  <div class="band-quote">
    <blockquote>“Come at night, when the building lights up.”</blockquote>
    <cite>The Sky Lounge evenings</cite>
  </div>
</section>

<!-- MENU -->
<section id="menu" class="section-pad">
  <div class="wrap">
    <div class="sec-head reveal">
      <span class="num">04</span>
      <h2 class="display">The Menu</h2>
      <span class="rule"></span>
      <span class="serif-it" style="font-size:1.4rem;color:var(--wine);">every dish, every price</span>
    </div>
    <div class="menu-tools reveal">
      <div class="search-box">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="11" cy="11" r="7"/><path d="m21 21-4.3-4.3"/></svg>
        <input id="menuSearch" type="search" placeholder="Search the menu — try &quot;biryani&quot;…" aria-label="Search the menu">
      </div>
      <label class="veg-toggle"><input type="checkbox" id="vegOnly"><span class="switch"></span> Veg only</label>
    </div>
    <div class="tabs reveal" role="tablist" aria-label="Menu categories">{tabs}</div>
    {panels}
    <div class="search-results" id="searchResults"></div>
    <p class="menu-note">Prices in Indian Rupees (₹), as per the restaurant menu. <span class="veg-dot" title="Veg"></span> vegetarian · <span class="veg-dot nonveg" title="Non-veg"></span> non-vegetarian. The bar menu is available at the restaurant — ask our team. Menu items and prices may change; call <a href="tel:{esc(R['phone'])}">{esc(R['phoneDisplay'])}</a> to confirm.</p>
  </div>
</section>

<!-- BAR -->
<section id="bar" class="section-pad" style="padding-top:20px;">
  <div class="wrap bar-grid">
    <div class="bar-photo" data-plx="0.07"><img src="images/ai-bar.jpg" alt="Smoked cocktail and chocolate dessert on the bar counter" loading="lazy"></div>
    <div class="bar-copy reveal">
      <p class="eyebrow">05 — Bar &amp; Beverages</p>
      <h2 class="display">After dinner,<br><span class="serif-it">something slower.</span></h2>
      <p>A full bar, kept in its own section — so the evening can stretch a little longer. Alongside it, the kitchen's own coolers and desserts, made the same unhurried way.</p>
      <ul class="bar-list">
        <li><b>Full bar</b><span>menu at the restaurant</span></li>
        <li><b>Lassi</b><span>₹80</span></li>
        <li><b>Cold coffee</b><span>₹110</span></li>
        <li><b>Fresh lime soda</b><span>₹60</span></li>
        <li><b>Sizzling brownie</b><span>₹270</span></li>
      </ul>
    </div>
  </div>
</section>

<!-- GALLERY -->
<section id="gallery" class="section-pad" style="padding-top:30px;">
  <div class="wrap">
    <div class="sec-head reveal">
      <span class="num">06</span>
      <h2 class="display">Gallery</h2>
      <span class="rule"></span>
      <span class="serif-it" style="font-size:1.4rem;color:var(--wine);">the place, at night</span>
    </div>
    <div class="stagger">
      <div class="stagger-row">
        <figure class="g-item g-a" data-plx="0.04"><img src="images/exterior-night.jpg" alt="The Sky Lounge tower, lit up at night" loading="lazy"><figcaption><i>The tower,</i> lit up at night</figcaption></figure>
        <figure class="g-item g-b" data-plx="0.07"><img src="images/noodles.jpg" alt="Hakka noodles" loading="lazy"><figcaption><i>Hakka noodles,</i> from the wok</figcaption></figure>
        <figure class="g-item g-c" data-plx="0.07"><img src="images/biryani.jpg" alt="Chicken biryani" loading="lazy"><figcaption><i>Chicken biryani</i></figcaption></figure>
        <figure class="g-item g-d" data-plx="0.05"><img src="images/chilli-chicken.jpg" alt="Chicken chilli" loading="lazy"><figcaption><i>Chicken chilli</i></figcaption></figure>
        <figure class="g-item g-e" data-plx="0.06"><img src="images/tandoori-fish.jpg" alt="Tandoori fish" loading="lazy"><figcaption><i>Tandoori fish</i></figcaption></figure>
        <figure class="g-item g-f" data-plx="0.06"><img src="images/naan.jpg" alt="Fresh tandoori naan in a basket" loading="lazy"><figcaption><i>Fresh tandoori naan</i></figcaption></figure>
        <figure class="g-item g-g" data-plx="0.08"><img src="images/fried-rice.jpg" alt="Egg fried rice" loading="lazy"><figcaption><i>Egg fried rice</i></figcaption></figure>
      </div>
    </div>
  </div>
</section>

<!-- REVIEWS -->
<section class="reviews section-pad">
  <div class="wrap">
    <div class="review-top reveal">
      <span class="big-rating">4.1</span>
      <div><div class="stars">★★★★☆</div><p>126 Google reviews — and counting.</p></div>
    </div>
    <div class="review-grid">
      <article class="review-card reveal"><blockquote>“Beautiful ambiance. Do visit at night. Food is their USP.”</blockquote><footer>— Google review</footer></article>
      <article class="review-card reveal reveal-d1"><blockquote>“Chicken biryani and kebabs are too good. The atmosphere at night feels charming.”</blockquote><footer>— Google review</footer></article>
      <article class="review-card reveal reveal-d2"><blockquote>“Very nice property. Separate family and bar sections, well arranged.”</blockquote><footer>— Google review</footer></article>
    </div>
  </div>
</section>

<!-- VISIT -->
<section id="visit" class="section-pad">
  <div class="wrap visit-grid">
    <div class="visit-info reveal">
      <p class="eyebrow">07 — Visit Us</p>
      <h2 class="display">Find your<br><span class="serif-it">table.</span></h2>
      <dl class="visit-lines">
        <div><dt>Address</dt><dd>{esc(R['address'])}</dd></div>
        <div><dt>Hours</dt><dd>Open all days · 11:00 AM – 12:00 AM</dd></div>
        <div><dt>Phone</dt><dd><a href="tel:{esc(R['phone'])}">{esc(R['phoneDisplay'])}</a></dd></div>
        <div><dt>Instagram</dt><dd><a href="{esc(R['instagram'])}" target="_blank" rel="noopener">{esc(R['instagramHandle'])}</a></dd></div>
      </dl>
      <div class="visit-ctas">
        <a class="btn-line solid" href="{esc(R['maps'])}" target="_blank" rel="noopener">Get Directions</a>
        <a class="btn-line" href="tel:{esc(R['phone'])}">Call the Restaurant</a>
      </div>
    </div>
    <div class="map-frame reveal reveal-d1">
      <iframe title="Map — Hotel Sky Lounge, Nanded" src="https://www.google.com/maps?q=19.193374,77.278159&amp;z=16&amp;output=embed" loading="lazy" referrerpolicy="no-referrer-when-downgrade" allowfullscreen></iframe>
    </div>
  </div>
</section>

<!-- ORDER STRIP -->
<section class="order-strip">
  <div class="wrap">
    <div><h3>Hungry already?</h3><p>Order Sky Lounge at home — delivery and takeaway, every day.</p></div>
    <div class="order-btns">
      <a class="btn-line solid" href="{esc(R['zomato'])}" target="_blank" rel="noopener">Order on Zomato</a>
      <a class="btn-line" href="{esc(SWIGGY)}" target="_blank" rel="noopener">Order on Swiggy</a>
    </div>
  </div>
</section>

</main>

<footer>
  <div class="wrap">
    <p class="foot-mark display">Sky <span class="serif-it">Lounge</span></p>
    <div class="footer-grid">
      <nav aria-label="Footer">
        <a href="#story">Story</a>
        <a href="#signatures">Signatures</a>
        <a href="#menu">Menu</a>
        <a href="#gallery">Gallery</a>
        <a href="#visit">Visit Us</a>
      </nav>
      <nav aria-label="Order and social">
        <a href="{esc(R['zomato'])}" target="_blank" rel="noopener">Zomato</a>
        <a href="{esc(SWIGGY)}" target="_blank" rel="noopener">Swiggy</a>
        <a href="{esc(R['instagram'])}" target="_blank" rel="noopener">Instagram</a>
        <a href="{esc(R['maps'])}" target="_blank" rel="noopener">Google Maps</a>
      </nav>
    </div>
    <div class="footer-bottom">
      <span>© 2026 Hotel Sky Lounge, Nanded. All rights reserved.</span>
      <span>Family Restaurant &amp; Bar · Open daily 11 AM – 12 AM</span>
    </div>
  </div>
</footer>
</div>

<div class="lightbox" id="lightbox" role="dialog" aria-modal="true" aria-label="Photo viewer">
  <button class="lb-close" aria-label="Close">×</button>
  <img id="lbImg" src="" alt="">
  <p class="lb-cap" id="lbCap"></p>
</div>

<script src="script.js"></script>
</body>
</html>
"""

(HERE / "index.html").write_text(HTML, encoding="utf-8")
print(f"Wrote index.html ({len(HTML)} bytes), {total_items} menu entries, {len(DATA['menu'])} categories")
