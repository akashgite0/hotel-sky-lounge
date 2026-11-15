#!/usr/bin/env python3
"""Generate index.html for Hotel Sky Lounge from menu.json.

Usage: python3 build.py
Reads menu.json in the same directory, writes index.html.
Menu items are rendered server-side so the full menu is in the HTML (SEO + no-JS friendly).
"""
import html
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
DATA = json.loads((HERE / "menu.json").read_text(encoding="utf-8"))
R = DATA["restaurant"]
SWIGGY = "https://www.swiggy.com/city/nanded/hotel-sky-lounge-restaurant-nila-road-harsh-nagar-rest751068"

VEG_CATEGORIES = {"starters-veg", "main-veg", "sabzi", "breads", "salad-finger",
                  "beverages", "dessert", "rice-biryani"}
NONVEG_CATEGORIES = {"starters-nonveg", "mughlai-nonveg", "seafood"}
NONVEG_WORDS = ["chicken", "mutton", "fish", "prawn", "crab", "egg", "keema",
                "kheema", "boti", "paya", "bheja", "bater", "meat", "lamb",
                "seafood", "non veg", "tandoori fish"]


def is_veg(cat_id, name):
    if cat_id in VEG_CATEGORIES:
        return True
    if cat_id in NONVEG_CATEGORIES:
        return False
    low = name.lower()
    return not any(w in low for w in NONVEG_WORDS)


def esc(s):
    return html.escape(str(s), quote=True)


def tag_html(tag):
    if not tag:
        return ""
    cls = "tag spicy" if tag.lower() == "spicy" else "tag"
    return f'<span class="tag mi-tag {cls}">{esc(tag)}</span>'


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
<meta property="og:image" content="images/exterior-night.jpg">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,500;0,9..144,600;0,9..144,700;1,9..144,500&family=Manrope:wght@400;600;700;800&display=swap" rel="stylesheet">
<link rel="stylesheet" href="styles.css">
<script>document.documentElement.classList.add('js');</script>
<link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>✦</text></svg>">
<script type="application/ld+json">
{ld_json}
</script>
</head>
<body>

<header class="header">
  <div class="wrap header-inner">
    <a class="wordmark" href="#top">SKY <span>LOUNGE</span></a>
    <nav class="nav" aria-label="Main">
      <a href="#about">About</a>
      <a href="#signatures">Signatures</a>
      <a href="#menu">Menu</a>
      <a href="#gallery">Gallery</a>
      <a href="#visit">Visit Us</a>
    </nav>
    <div class="header-actions">
      <a class="phone-link" href="tel:{esc(R['phone'])}">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72c.13.96.36 1.9.7 2.81a2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45c.91.34 1.85.57 2.81.7A2 2 0 0 1 22 16.92z"/></svg>
        {esc(R['phoneDisplay'])}
      </a>
      <a class="btn btn-gold btn-sm" href="{esc(R['zomato'])}" target="_blank" rel="noopener">Order Online</a>
    </div>
    <button class="burger" aria-label="Open menu" aria-expanded="false">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M3 6h18M3 12h18M3 18h18"/></svg>
    </button>
  </div>
</header>

<main id="top">

<!-- HERO -->
<section class="hero">
  <div class="hero-bg"><img src="images/exterior-night.jpg" alt="Hotel Sky Lounge tower lit up at night, Nanded" fetchpriority="high"></div>
  <div class="wrap hero-inner">
    <p class="eyebrow">Family Restaurant &amp; Bar — Nanded</p>
    <h1>Hotel <em>Sky&nbsp;Lounge</em></h1>
    <p class="hero-sub">Tandoor, Mughlai, dum biryani and seafood — served under the lights on Nila Road. Family dining and a full bar, under one roof.</p>
    <div class="hero-chips">
      <span class="chip"><span class="star">★</span> 4.1 · 126 Google reviews</span>
      <span class="chip"><span class="dot-open"></span> Open today · 11 AM – 12 AM</span>
      <span class="chip">₹1,300 for two</span>
    </div>
    <div class="hero-ctas">
      <a class="btn btn-gold" href="#menu">Explore the Menu</a>
      <a class="btn btn-outline" href="{esc(R['zomato'])}" target="_blank" rel="noopener">Order on Zomato</a>
      <a class="btn btn-outline" href="{esc(SWIGGY)}" target="_blank" rel="noopener">Order on Swiggy</a>
    </div>
  </div>
</section>

<!-- MARQUEE -->
<div class="marquee" aria-hidden="true">
  <div class="marquee-track">
    <span>North Indian</span><span>Mughlai</span><span>Dum Biryani</span><span>Seafood</span><span>Indo Chinese</span><span>Tandoor</span><span>Full Bar</span><span>Desserts</span>
    <span>North Indian</span><span>Mughlai</span><span>Dum Biryani</span><span>Seafood</span><span>Indo Chinese</span><span>Tandoor</span><span>Full Bar</span><span>Desserts</span>
  </div>
</div>

<!-- ABOUT -->
<section id="about" class="section-pad">
  <div class="wrap about-grid">
    <div class="about-photo reveal"><img src="images/interior.jpg" alt="Dining room at Hotel Sky Lounge with marble tables and red chairs" loading="lazy"></div>
    <div class="about-copy reveal">
      <p class="eyebrow">The Restaurant</p>
      <h2 style="font-size:clamp(2rem,4.6vw,3.1rem);margin:12px 0 4px;">An evening out,<br>done properly.</h2>
      <p>On Nila Road in Nanded, Sky Lounge pairs a <strong>separate family dining room</strong> with a <strong>full bar section</strong> — so dinner with the family and drinks with friends never get in each other's way.</p>
      <p>The kitchen runs from the clay oven to the wok: handis that slow-cook for hours, tandoori kebabs, coastal seafood, and dum biryanis that guests come back for. Come at night, when the building lights up and the terrace mood takes over.</p>
      <div class="stats">
        <div class="stat"><b>{total_items}+</b><span>Dishes</span></div>
        <div class="stat"><b>4.1 ★</b><span>Google rating</span></div>
        <div class="stat"><b>13 hrs</b><span>Open daily</span></div>
      </div>
      <div class="features">
        <span class="feature">Family &amp; bar sections</span>
        <span class="feature">Full bar</span>
        <span class="feature">Home delivery</span>
        <span class="feature">Takeaway</span>
        <span class="feature">Indoor seating</span>
        <span class="feature">Digital payments</span>
      </div>
    </div>
  </div>
</section>

<!-- SIGNATURES -->
<section id="signatures" class="signatures section-pad">
  <div class="wrap">
    <div class="section-head reveal">
      <p class="eyebrow">From the Kitchen</p>
      <h2>Signatures worth the trip</h2>
      <p>The dishes guests talk about most — straight off the menu, at menu prices.</p>
    </div>
    <div class="sig-grid">
      <article class="sig-card reveal">
        <img src="images/biryani.jpg" alt="Chicken dum biryani" loading="lazy">
        <div class="sig-body"><h3>Chicken Dum Biryani</h3><p>Fragrant basmati layered with marinated chicken, sealed and slow-cooked on dum.</p>
        <div class="sig-foot"><span class="price">₹290</span><span class="tag">Bestseller</span></div></div>
      </article>
      <article class="sig-card reveal">
        <img src="images/prawns.jpg" alt="Ghee roast prawns" loading="lazy">
        <div class="sig-body"><h3>Ghee Roast Prawns</h3><p>Sea prawns marinated 24 hours, roasted in ghee with Mangalorean spice.</p>
        <div class="sig-foot"><span class="price">₹490</span><span class="tag">Signature</span></div></div>
      </article>
      <article class="sig-card reveal">
        <img src="images/chilli-chicken.jpg" alt="Chicken chilli" loading="lazy">
        <div class="sig-body"><h3>Chicken Chilli</h3><p>Wok-tossed chicken with green peppers, onion and a fiery chilli-garlic glaze.</p>
        <div class="sig-foot"><span class="price">₹340</span><span class="tag spicy">Spicy</span></div></div>
      </article>
      <article class="sig-card reveal">
        <img src="images/noodles.jpg" alt="Hakka noodles" loading="lazy">
        <div class="sig-body"><h3>Hakka Noodles</h3><p>Smoky wok-tossed noodles with peppers, cabbage and red chilli.</p>
        <div class="sig-foot"><span class="price">from ₹260</span></div></div>
      </article>
      <article class="sig-card reveal">
        <img src="images/tandoori-fish.jpg" alt="Tandoori fish" loading="lazy">
        <div class="sig-body"><h3>Tandoori Fish</h3><p>Whole fish coated in red spice, chargrilled in the clay oven, with chutney.</p>
        <div class="sig-foot"><span class="price">₹410</span></div></div>
      </article>
      <article class="sig-card reveal">
        <img src="images/naan.jpg" alt="Fresh tandoori naan in a basket" loading="lazy">
        <div class="sig-body"><h3>Tandoori Breads</h3><p>Baked fresh in the tandoor — butter naan, garlic naan, laccha paratha and more.</p>
        <div class="sig-foot"><span class="price">from ₹25</span></div></div>
      </article>
    </div>
  </div>
</section>

<!-- MENU -->
<section id="menu" class="section-pad">
  <div class="wrap">
    <div class="section-head reveal">
      <p class="eyebrow">The Menu</p>
      <h2>Every dish, every price.</h2>
      <p>The full menu as served at the restaurant. Search for a dish, or filter to vegetarian only.</p>
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

<!-- GALLERY -->
<section id="gallery" class="section-pad" style="padding-top:0;">
  <div class="wrap">
    <div class="section-head reveal">
      <p class="eyebrow">Gallery</p>
      <h2>The place, at night.</h2>
      <p>Real photos from the restaurant and its kitchen.</p>
    </div>
    <div class="gallery-grid reveal">
      <figure class="g-item wide"><img src="images/exterior-night.jpg" alt="The Sky Lounge tower, lit up at night" loading="lazy"><figcaption>The tower, lit up at night</figcaption></figure>
      <figure class="g-item tall"><img src="images/interior.jpg" alt="The family dining room" loading="lazy"><figcaption>The family dining room</figcaption></figure>
      <figure class="g-item"><img src="images/biryani.jpg" alt="Chicken biryani" loading="lazy"><figcaption>Chicken biryani</figcaption></figure>
      <figure class="g-item"><img src="images/prawns.jpg" alt="Ghee roast prawns" loading="lazy"><figcaption>Ghee roast prawns</figcaption></figure>
      <figure class="g-item"><img src="images/chilli-chicken.jpg" alt="Chicken chilli" loading="lazy"><figcaption>Chicken chilli</figcaption></figure>
      <figure class="g-item"><img src="images/noodles.jpg" alt="Hakka noodles" loading="lazy"><figcaption>Hakka noodles</figcaption></figure>
      <figure class="g-item"><img src="images/tandoori-fish.jpg" alt="Tandoori fish" loading="lazy"><figcaption>Tandoori fish</figcaption></figure>
      <figure class="g-item"><img src="images/fried-rice.jpg" alt="Egg fried rice" loading="lazy"><figcaption>Egg fried rice</figcaption></figure>
      <figure class="g-item wide"><img src="images/naan.jpg" alt="Fresh tandoori naan in a basket" loading="lazy"><figcaption>Fresh tandoori naan</figcaption></figure>
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
      <article class="review-card reveal"><blockquote>“Beautiful ambiance. Do visit at night. Food is their USP.”</blockquote><footer>— GOOGLE REVIEW</footer></article>
      <article class="review-card reveal"><blockquote>“Chicken biryani and kebabs are too good. The atmosphere at night feels charming.”</blockquote><footer>— GOOGLE REVIEW</footer></article>
      <article class="review-card reveal"><blockquote>“Very nice property. Separate family and bar sections, well arranged.”</blockquote><footer>— GOOGLE REVIEW</footer></article>
    </div>
  </div>
</section>

<!-- VISIT -->
<section id="visit" class="section-pad">
  <div class="wrap visit-grid">
    <div class="visit-info reveal">
      <p class="eyebrow">Visit Us</p>
      <h2>Find your table.</h2>
      <div class="visit-row">
        <span class="v-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0Z"/><circle cx="12" cy="10" r="3"/></svg></span>
        <div><b>Address</b><p>{esc(R['address'])}</p></div>
      </div>
      <div class="visit-row">
        <span class="v-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/></svg></span>
        <div><b>Hours</b><p>Open all days · 11:00 AM – 12:00 AM</p></div>
      </div>
      <div class="visit-row">
        <span class="v-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72c.13.96.36 1.9.7 2.81a2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45c.91.34 1.85.57 2.81.7A2 2 0 0 1 22 16.92z"/></svg></span>
        <div><b>Phone</b><p><a href="tel:{esc(R['phone'])}">{esc(R['phoneDisplay'])}</a></p></div>
      </div>
      <div class="visit-row">
        <span class="v-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><rect x="2" y="2" width="20" height="20" rx="5"/><circle cx="12" cy="12" r="4"/><circle cx="17.5" cy="6.5" r="0.5" fill="currentColor"/></svg></span>
        <div><b>Instagram</b><p><a href="{esc(R['instagram'])}" target="_blank" rel="noopener">{esc(R['instagramHandle'])}</a></p></div>
      </div>
      <div class="visit-ctas">
        <a class="btn btn-gold" href="{esc(R['maps'])}" target="_blank" rel="noopener">Get Directions</a>
        <a class="btn btn-outline" href="tel:{esc(R['phone'])}">Call the Restaurant</a>
      </div>
    </div>
    <div class="map-frame reveal">
      <iframe title="Map — Hotel Sky Lounge, Nanded" src="https://www.google.com/maps?q=19.193374,77.278159&amp;z=16&amp;output=embed" loading="lazy" referrerpolicy="no-referrer-when-downgrade" allowfullscreen></iframe>
    </div>
  </div>
</section>

<!-- ORDER STRIP -->
<section class="order-strip">
  <div class="wrap">
    <div><h3>Hungry already?</h3><p>Order Sky Lounge at home — delivery and takeaway, every day.</p></div>
    <div class="order-btns">
      <a class="btn btn-gold" href="{esc(R['zomato'])}" target="_blank" rel="noopener">Order on Zomato</a>
      <a class="btn btn-outline" href="{esc(SWIGGY)}" target="_blank" rel="noopener">Order on Swiggy</a>
    </div>
  </div>
</section>

</main>

<footer>
  <div class="wrap">
    <div class="footer-grid">
      <a class="wordmark" href="#top">SKY <span>LOUNGE</span></a>
      <nav aria-label="Footer">
        <a href="#about">About</a>
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

<div class="sticky-bar">
  <a class="btn btn-outline" href="tel:{esc(R['phone'])}">Call</a>
  <a class="btn btn-gold" href="{esc(R['zomato'])}" target="_blank" rel="noopener">Order on Zomato</a>
  <a class="btn btn-outline" href="#menu">Menu</a>
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
