# Hotel Sky Lounge — Website

Official website for **Hotel Sky Lounge – Family Restaurant & Bar**, Jay Bhawani Chowk,
Nila Road, Nanded, Maharashtra 431605.

- Live site: https://hotel-sky-lounge.vercel.app/ (Vercel, auto-deploys from `main`)
- Stack: plain HTML + CSS + JavaScript. No build step, no framework.
- Design: Taj-inspired luxe for a restaurant — dark espresso, ivory and antique gold, grand serif typography, story-first sections (welcome, our story, experiences), a small elegant curated menu section, staggered gallery. Scroll-driven parallax throughout (fixed hero, drifting photo layers, full-bleed bands).
- The full menu data lives in `menu.json`; `index.html` is generated from it, but only a small curated selection (19 dishes, verified against `menu.json` at build time) is shown on the site, by design.

## Structure

| File | Purpose |
|---|---|
| `index.html` | The whole site (generated — do not hand-edit the menu section) |
| `styles.css` | All styling |
| `script.js` | Parallax engine, reveals, gallery lightbox, mobile nav |
| `menu.json` | Restaurant details + full menu with prices (source of truth; the site shows a curated selection) |
| `build.py` | Generates `index.html` from `menu.json`, verifying curated dish prices |
| `images/` | Real photos from the Google listing + AI-generated editorial images (`ai-*.jpg`) |
| `vercel.json` | Vercel deployment config (caching headers) |

## Updating the menu

1. Edit prices or dishes in `menu.json`.
2. Run `python3 build.py` to regenerate `index.html`.
3. Commit and push — Vercel redeploys automatically.

## Key facts

- Hours: open all days, 11:00 AM – 12:00 AM
- Phone: +91 77098 89104
- Instagram: [@hotel.skylounge](https://www.instagram.com/hotel.skylounge)
- Order online: [Zomato](https://www.zomato.com/nanded/hotel-sky-lounge-nanded-locality/order) and [Swiggy](https://www.swiggy.com/city/nanded/hotel-sky-lounge-restaurant-nila-road-harsh-nagar-rest751068)
- No table booking on the site, by design.

## Photos

Photos in `images/` are from the restaurant's Google Maps listing (interior,
exterior, and menu dishes). The full gallery on Google has 200+ photos; more can
be added to `images/` and referenced in the gallery section of `build.py`.
Files named `ai-*.jpg` are AI-generated editorial images used for the hero,
story, dining-room band and bar sections.
