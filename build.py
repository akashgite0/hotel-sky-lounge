#!/usr/bin/env python3
"""Generate index.html for Hotel Sky Lounge v3 (Taj-inspired, story-first) from menu.json.

Usage: python3 build.py
The menu section is a small curated selection. Every curated dish + price is
verified against menu.json at build time (fails loudly on any mismatch).
"""
import html
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
DATA = json.loads((HERE / "menu.json").read_text(encoding="utf-8"))
R = DATA["restaurant"]
SWIGGY = "https://www.swiggy.com/city/nanded/hotel-sky-lounge-restaurant-nila-road-harsh-nagar-rest751068"

# --- Curated menu: (display name, menu.json name, price display, description) ---
CURATED = [
    ("From the Tandoor", [
        ("Classic Tandoori Chicken", "Classic Tandoori Chicken", "750 / 390", "Overnight marinade, roasted over fire"),
        ("Chicken Tikka", "Chicken Tikka", "350", "Boneless, yogurt and spice, grilled over coals"),
        ("Kakori Kabab", "Kakori Kabab", "410", "Minced mutton, grilled with Indian seasoning"),
    ]),
    ("Handis & Mughlai", [
        ("Butter Chicken", "Butter Chicken", "390 / 700", "Chicken tikka in tomato and cream gravy"),
        ("Raan-e-Skyrana", "Raan-e-Skyrana", "1700", "Whole mutton leg, marinated 24+ hours, slow-cooked over charcoal"),
        ("Mutton Rogan Josh", "Mutton Rogan Josh", "420", "Lamb braised with fennel, cloves and cardamom"),
    ]),
    ("Dum Biryanis", [
        ("Chicken Biryani", "Chicken Biryani", "290", "Sealed and slow-cooked on dum"),
        ("Mutton Biryani", "Mutton Biryani", "320", "Sealed and slow-cooked on dum"),
        ("Veg Biryani", "Veg Biryani", "270", "Fragrant basmati, garden vegetables, sealed on dum"),
    ]),
    ("From the Sea", [
        ("Tandoori Prawns", "Tandoori Prawns (Banjara / Chatpata / Lasuni)", "450", "Banjara, chatpata or lasuni"),
        ("Tandoori Fish", "Tandoori Fish (Banjara / Chatpata / Lasuni)", "410", "Banjara, chatpata or lasuni"),
        ("Fish Chilli", "Fish Chilli", "420", "Wok-tossed with chilli and garlic"),
    ]),
    ("From the Wok", [
        ("Chicken Chilli", "Chicken Chilli", "340", "Wok-tossed with peppers and chilli-garlic"),
        ("Chicken 65", "Chicken 65", "340", "The fiery South Indian favourite"),
        ("Hakka Noodles", None, "from 230", "Smoky wok-tossed noodles"),
    ]),
    ("Breads & Sweet Endings", [
        ("Butter Garlic Naan", "Butter Garlic Naan", "80 / 85", "Baked fresh in the tandoor"),
        ("Sizzling Chocolate Brownie", "Sizzling Chocolate Brownie with Vanilla Ice Cream", "270", "With vanilla ice cream, served sizzling"),
        ("Sky's Signature Dessert Platter", "Sky's Signature Dessert Platter", "420", "The house selection"),
        ("Lassi", "Lassi", "80", "Churned fresh"),
    ]),
]


def verify_curated():
    """Every curated price must match menu.json exactly."""
    prices = {}
    for cat in DATA["menu"]:
        for it in cat.get("items", []):
            prices.setdefault(it["name"], set()).add(str(it["price"]))
    table = {}
    for cat in DATA["menu"]:
        if "table" in cat:
            for row in cat["table"]["rows"]:
                table[row["name"]] = [int(p) for p in row["prices"]]
    errors = []
    for group, items in CURATED:
        for display, menu_name, price, _ in items:
            if menu_name is None:  # table item: verify the "from" floor
                floor = min(table[display])
                if price != f"from {floor}":
                    errors.append(f"{display}: site says '{price}', menu floor is {floor}")
                continue
            if menu_name not in prices:
                errors.append(f"{menu_name}: not found in menu.json")
            elif price not in prices[menu_name]:
                errors.append(f"{menu_name}: site says '{price}', menu has {sorted(prices[menu_name])}")
    if errors:
        raise SystemExit("MENU VERIFICATION FAILED:\n" + "\n".join(errors))
    print(f"Menu verified: {sum(len(i) for _, i in CURATED)} curated dishes match menu.json")


verify_curated()


def esc(s):
    return html.escape(str(s), quote=True)


def menu_html():
    out = []
    for group, items in CURATED:
        rows = "".join(
            f"<div class='m-item'><div class='m-row'><span class='m-name'>{esc(d)}</span>"
            f"<span class='m-dots'></span><span class='m-price'>&#8377;{esc(p)}</span></div>"
            f"<p class='m-desc'>{esc(desc)}</p></div>"
            for d, _, p, desc in items
        )
        out.append(f"<div class='menu-group'><h3>{esc(group)}</h3>{rows}</div>")
    return "".join(out)


ld = {
    "@context": "https://schema.org",
    "@type": "Restaurant",
    "name": R["name"],
    "slogan": R["tagline"],
    "servesCuisine": R["cuisines"],
    "priceRange": "₹₹",
    "telephone": R["phone"],
    "foundingDate": "2023-04",
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
MENU = menu_html()

HTML = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Hotel Sky Lounge — Family Restaurant &amp; Bar, Nanded</title>
<meta name="description" content="Hotel Sky Lounge, Nanded — a family restaurant & bar on Nila Road since April 2023. Tandoor, handis, dum biryani & seafood, in a tower that glows at night. Open daily 11 AM–12 AM.">
<meta property="og:title" content="Hotel Sky Lounge — Family Restaurant & Bar, Nanded">
<meta property="og:description" content="A table above the city's rush. Family restaurant & bar on Nila Road, Nanded, since April 2023.">
<meta property="og:type" content="website">
<meta property="og:image" content="images/exterior-night.jpg">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;0,500;0,600;1,400;1,500&family=Jost:wght@200;300;400;500&family=Manrope:wght@400;600;700&display=swap" rel="stylesheet">
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
      <a href="#story">Our Story</a>
      <a href="#experiences">Experiences</a>
    </nav>
    <a class="wordmark" href="#top">Hotel Sky Lounge<small>Nanded · Est. April 2023</small></a>
    <nav class="nav right" aria-label="Main">
      <a href="#menu">Menu</a>
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
  <a href="#story">Our Story</a>
  <a href="#experiences">Experiences</a>
  <a href="#menu">Menu</a>
  <a href="#gallery">Gallery</a>
  <a href="#visit">Visit</a>
  <a href="{esc(R['zomato'])}" target="_blank" rel="noopener">Order on Zomato</a>
  <a href="{esc(SWIGGY)}" target="_blank" rel="noopener">Order on Swiggy</a>
</nav>

<!-- HERO : fixed, the page scrolls over it -->
<section class="hero" id="top" aria-label="Hotel Sky Lounge">
  <img class="bg" src="images/exterior-night.jpg" alt="The Sky Lounge tower, lit up at night over Nila Road" fetchpriority="high">
  <div class="hero-inner">
    <p class="eyebrow">Est. April 2023 · Nanded, Maharashtra</p>
    <h1>Hotel <em>Sky&nbsp;Lounge</em></h1>
    <div class="hero-rule"><span>✦</span></div>
    <p class="hero-sub">An evening above the city.</p>
    <div class="hero-meta">
      <span><span class="star">★</span> 4.1 · 126 Google reviews</span>
      <span>Open today · 11 AM – 12 AM</span>
      <span>Family restaurant &amp; bar</span>
    </div>
  </div>
  <span class="scroll-cue">Scroll<span class="cue-line"></span></span>
</section>

<div class="page">
<main>

<!-- WELCOME -->
<section class="welcome section-pad">
  <div class="wrap">
    <p class="eyebrow reveal">Welcome</p>
    <p class="statement reveal reveal-d1" style="margin-top:22px;">A table above the city's rush — <em>where dinner stretches a little longer than planned.</em></p>
    <p class="reveal reveal-d2">In the heart of Nanded, on Nila Road, Sky Lounge is a family restaurant and bar that treats every evening like an occasion. Warm light, slow food, and a tower that glows when the sun goes down.</p>
    <p class="welcome-sig reveal">— The House of Sky Lounge</p>
  </div>
</section>

<!-- STORY -->
<section id="story" class="dark section-pad">
  <div class="wrap story-grid">
    <div class="story-photo">
      <div class="frame" data-plx="0.05"><img src="images/ai-tandoor.jpg" alt="Chef garnishing a sizzling tandoori platter beside the clay oven" loading="lazy"></div>
      <span class="tagline">Since April 2023</span>
    </div>
    <div class="story-copy reveal">
      <p class="eyebrow">Our Story</p>
      <h2>A tower lit up <em>on Nila Road.</em></h2>
      <p class="dropcap">In April 2023, a tower on Nila Road lit up for the first time. Nanded had known good food for years — but Sky Lounge arrived with a different idea: a restaurant that feels like an occasion, every single evening. A room above the city's rush, where the lights come on as the sun goes down.</p>
      <p>The house keeps two rooms under one roof — a calm family dining room, and a bar of its own — so every kind of evening has its place. Between them, one kitchen, faithful to fire: clay ovens, sealed handis, and marinades that rest a full day before they ever meet the coals.</p>
      <p>What guests return for is simple: <strong>biryanis sealed on dum, kebabs from the tandoor,</strong> and the feeling of the tower at night, glowing over Nila Road.</p>
      <blockquote class="pull-quote">“Unhurried food, warm light, and a table that is always glad to see you.”
      <cite>The Sky Lounge Way</cite></blockquote>
    </div>
  </div>
</section>

<!-- EXPERIENCES -->
<section id="experiences" class="section-pad">
  <div class="wrap">
    <div class="sec-head reveal">
      <p class="eyebrow">Experiences</p>
      <h2>Three ways to spend <em>an evening.</em></h2>
      <div class="ornament"><span>✦</span></div>
      <p class="lead">Every visit finds its own rhythm — choose the room that suits the evening.</p>
    </div>
    <div class="exp-grid">
      <article class="exp-card reveal">
        <div class="exp-photo" data-plx="0.04"><img src="images/interior.jpg" alt="The family dining room at Hotel Sky Lounge" loading="lazy"></div>
        <span class="exp-label">The Family Room</span>
        <h3>Calm tables, warm light</h3>
        <p>Room for everyone — the heart of the house, where families gather and no one is in a hurry.</p>
        <span class="exp-time">Open daily · 11 AM – 12 AM</span>
      </article>
      <article class="exp-card reveal reveal-d1">
        <div class="exp-photo" data-plx="0.07"><img src="images/ai-bar.jpg" alt="Smoked cocktail and chocolate dessert on the bar counter" loading="lazy"></div>
        <span class="exp-label">The Bar</span>
        <h3>Evenings, a little longer</h3>
        <p>A full bar kept in its own section, apart from the family room. The bar menu awaits at the restaurant.</p>
        <span class="exp-time">At the restaurant</span>
      </article>
      <article class="exp-card reveal reveal-d2">
        <div class="exp-photo" data-plx="0.05"><img src="images/ai-interior.jpg" alt="Candlelit dining room with brass lamps and velvet chairs" loading="lazy"></div>
        <span class="exp-label">Evenings at the Tower</span>
        <h3>Come at night</h3>
        <p>When the tower lights up and the whole building glows over Nila Road — that is when Sky Lounge feels most itself.</p>
        <span class="exp-time">Best after sunset</span>
      </article>
    </div>
  </div>
</section>

<!-- PARALLAX BAND -->
<section class="band" aria-label="A feast from the kitchen">
  <div class="band-img"><img src="images/ai-hero.jpg" alt="Overhead feast of butter chicken, tandoori chicken, naan and chutneys" loading="lazy"></div>
  <div class="band-quote">
    <blockquote>“Fire, patience, and the art of the handi.”</blockquote>
    <cite>From the Kitchen</cite>
  </div>
</section>

<!-- MENU -->
<section id="menu" class="section-pad">
  <div class="wrap">
    <div class="sec-head reveal">
      <p class="eyebrow">The Menu</p>
      <h2>A taste of <em>the house.</em></h2>
      <div class="ornament"><span>✦</span></div>
      <p class="lead">A small selection from the kitchen — the dishes guests ask for by name.</p>
    </div>
    <div class="menu-sheet reveal">
      <div class="menu-cols">{MENU}</div>
      <div class="menu-foot">
        <p>Over 200 dishes grace the full menu — <em>available at the restaurant.</em> To taste the house at home, order below.</p>
        <div class="menu-ctas">
          <a class="btn btn-gold" href="{esc(R['zomato'])}" target="_blank" rel="noopener">Order on Zomato</a>
          <a class="btn btn-outline" href="{esc(SWIGGY)}" target="_blank" rel="noopener">Order on Swiggy</a>
        </div>
      </div>
    </div>
  </div>
</section>

<!-- GALLERY -->
<section id="gallery" class="dark section-pad">
  <div class="wrap">
    <div class="sec-head reveal">
      <p class="eyebrow">Gallery</p>
      <h2>The place, <em>at night.</em></h2>
      <div class="ornament"><span>✦</span></div>
    </div>
    <div class="stagger-row">
      <figure class="g-item g-a" data-plx="0.03"><img src="images/exterior-night.jpg" alt="The Sky Lounge tower, lit up at night" loading="lazy"><figcaption><i>The tower,</i> lit up at night</figcaption></figure>
      <figure class="g-item g-b" data-plx="0.06"><img src="images/noodles.jpg" alt="Hakka noodles" loading="lazy"><figcaption><i>Hakka noodles,</i> from the wok</figcaption></figure>
      <figure class="g-item g-c" data-plx="0.05"><img src="images/biryani.jpg" alt="Chicken biryani" loading="lazy"><figcaption><i>Chicken biryani</i></figcaption></figure>
      <figure class="g-item g-d" data-plx="0.04"><img src="images/chilli-chicken.jpg" alt="Chicken chilli" loading="lazy"><figcaption><i>Chicken chilli</i></figcaption></figure>
      <figure class="g-item g-e" data-plx="0.06"><img src="images/tandoori-fish.jpg" alt="Tandoori fish" loading="lazy"><figcaption><i>Tandoori fish</i></figcaption></figure>
      <figure class="g-item g-f" data-plx="0.04"><img src="images/naan.jpg" alt="Fresh tandoori naan in a basket" loading="lazy"><figcaption><i>Fresh tandoori naan</i></figcaption></figure>
      <figure class="g-item g-g" data-plx="0.05"><img src="images/fried-rice.jpg" alt="Egg fried rice" loading="lazy"><figcaption><i>Egg fried rice</i></figcaption></figure>
    </div>
  </div>
</section>

<!-- GUEST WORDS -->
<section class="section-pad">
  <div class="wrap">
    <div class="sec-head reveal">
      <p class="eyebrow">Guest Words</p>
      <h2>What the city <em>says.</em></h2>
      <div class="ornament"><span>✦</span></div>
    </div>
    <div class="voices">
      <article class="voice reveal"><span class="stars">★★★★★</span><blockquote>“Beautiful ambiance. Do visit at night. Food is their USP.”</blockquote><footer>— Google review</footer></article>
      <article class="voice reveal reveal-d1"><span class="stars">★★★★★</span><blockquote>“Chicken biryani and kebabs are too good. The atmosphere at night feels charming.”</blockquote><footer>— Google review</footer></article>
      <article class="voice reveal reveal-d2"><span class="stars">★★★★★</span><blockquote>“Very nice property. Separate family and bar sections, well arranged.”</blockquote><footer>— Google review</footer></article>
    </div>
    <p class="rating-line reveal"><b>4.1</b> from 126 Google reviews — and counting.</p>
  </div>
</section>

<!-- VISIT -->
<section id="visit" class="dark section-pad visit">
  <div class="wrap">
    <p class="eyebrow reveal">Visit Us</p>
    <h2 class="reveal">Find your <em>table.</em></h2>
    <div class="ornament reveal"><span>✦</span></div>
    <dl class="visit-lines reveal">
      <div><dt>Address</dt><dd>{esc(R['address'])}</dd></div>
      <div><dt>Hours</dt><dd>Open all days · 11:00 AM – 12:00 AM</dd></div>
      <div><dt>Phone</dt><dd><a href="tel:{esc(R['phone'])}">{esc(R['phoneDisplay'])}</a></dd></div>
      <div><dt>Instagram</dt><dd><a href="{esc(R['instagram'])}" target="_blank" rel="noopener">{esc(R['instagramHandle'])}</a></dd></div>
    </dl>
    <div class="visit-ctas reveal">
      <a class="btn btn-gold" href="{esc(R['maps'])}" target="_blank" rel="noopener">Get Directions</a>
      <a class="btn btn-outline" href="tel:{esc(R['phone'])}">Call the Restaurant</a>
    </div>
    <div class="map-frame reveal">
      <iframe title="Map — Hotel Sky Lounge, Nanded" src="https://www.google.com/maps?q=19.193374,77.278159&amp;z=16&amp;output=embed" loading="lazy" referrerpolicy="no-referrer-when-downgrade" allowfullscreen></iframe>
    </div>
  </div>
</section>

</main>

<footer>
  <div class="wrap">
    <p class="foot-mark">Sky <em>Lounge</em></p>
    <p class="foot-tag">Family Restaurant &amp; Bar · Nanded · Est. April 2023</p>
    <nav class="footer-nav" aria-label="Footer">
      <a href="#story">Our Story</a>
      <a href="#experiences">Experiences</a>
      <a href="#menu">Menu</a>
      <a href="#gallery">Gallery</a>
      <a href="#visit">Visit Us</a>
      <a href="{esc(R['zomato'])}" target="_blank" rel="noopener">Zomato</a>
      <a href="{esc(SWIGGY)}" target="_blank" rel="noopener">Swiggy</a>
      <a href="{esc(R['instagram'])}" target="_blank" rel="noopener">Instagram</a>
    </nav>
    <div class="footer-bottom">
      <span>© 2026 Hotel Sky Lounge, Nanded. All rights reserved.</span>
      <span>Open daily 11 AM – 12 AM</span>
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
print(f"Wrote index.html ({len(HTML)} bytes)")
