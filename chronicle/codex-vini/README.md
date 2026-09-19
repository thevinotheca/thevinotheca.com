# Codex Vini

*In vino veritas.*

An interactive personal wine atlas — every wine I have tasted, plotted on a map, filterable by country, region, grape, colour, and rating. A sibling to [The Vineyard Atlas](/library/maps/vineyard-atlas/) and part of [Vinotheca](/), published from this repository.

## Live site

**[→ Open Codex Vini](/chronicle/codex-vini/)**

## What's inside

The site is organised into three sections:

- **The Book** — sortable, searchable, filterable table of every wine tasted
- **The Atlas** — interactive map (Leaflet + CARTO basemap) with one pin per wine, sized by rating and coloured by grape variety
- **The Collection** — eight charts visualising the codex: rating distribution, colour share, vintage distribution, all countries / regions / grapes, and average rating broken down by country and by grape

Plus:

- **Cross-linked filters** — clicking any filter updates both the map and the table simultaneously; rating buttons let you isolate a single score
- **Documents dropdown** — about, how-to, the 101 TasteRank grape profiles, and 57 Soul of Wine regional terroir profiles, all built into the page
- **Growing weekly** as new bottles are tasted

Each wine is tagged with:
- Producer, wine name, vintage, rating (0–10 scale), date tasted
- Country and region (pinned to a geographic centroid)
- Grape variety or named blend — drawn from a taxonomy of the 101 [TasteRank](https://tasterank.com/) varieties plus named wine categories (Bordeaux Blend, Barolo, Brunello di Montalcino, Châteauneuf-du-Pape Blend, etc.)
- Wine colour / style (red, white, rosé, sparkling)

## Files

| File | Purpose |
|---|---|
| `index.html` | The main app — self-contained HTML + CSS + JS |
| `add_wine.html` | In-browser form for adding new wines |
| `wines.json` | Single source of truth — every wine as a JSON object |
| `grapes.json` | Grape taxonomy (101 varieties + named blends + additional varieties) |
| `regions.json` | Region → lat/lng lookup |
| `grape_profiles.json` | One-paragraph reference for each of the 101 TasteRank grape varieties |
| `region_profiles.json` | Terroir profile (climate, soils, varieties, winemaking, history) for 57 regions, from Soul of Wine |
| `README.md` | This file |
| `LICENSE` | CC BY-NC 4.0 |

## How to use

Open the [live site](/chronicle/codex-vini/) in any modern browser. Use the filters in the left panel to narrow by country, grape, colour, or rating. Click any pin on the map for a full wine card. Click any row in The Book to fly the map to that wine. Click any of the **Reset** buttons or press `Esc` to clear all filters and return the map to its default Europe view.

To run locally, use a local server (`python3 -m http.server` from the repository root) and open `http://localhost:8000/chronicle/codex-vini/`. The page loads `wines.json`, `grapes.json`, and `regions.json` via `fetch()`, which most browsers block under the `file://` protocol — opening `index.html` by double-click will render the layout but show zero wines.

## Adding a new wine

Entries are added through the in-browser form. The generated JSON is landed by the helper script rather than pasted into `wines.json` by hand.

1. Open [`add_wine.html`](/chronicle/codex-vini/add_wine.html)
2. Fill in producer, wine, vintage, country, region, grape, and rating. The country, region, and grape fields autocomplete from existing values but accept anything new you type
3. Click **Generate JSON** and **Copy to clipboard**
4. In Terminal, run the `add_entry.py wine` command that the form's **Next steps** panel names for this entry
5. The script validates the entry and writes it to `wines.json` — and to `grapes.json` in the same run when the grape is new — then commits and pushes. The site deploys on push to `main` via Cloudflare Pages

The form blocks submission for new regions until the region exists in `regions.json` (see below). This is intentional: pin coordinates can't be made up at the form, so the region has to exist in the lookup before a wine can use it.

### Schema

Every wine is a JSON object of this shape:

```json
{
  "id": "clos-des-papes-cdp-2007",
  "producer": "Clos Des Papes",
  "wine": "Châteauneuf-du-Pape",
  "vintage": "2007",
  "country": "France",
  "region": "Southern Rhône",
  "grape": "Châteauneuf-du-Pape Blend",
  "color": "red",
  "rating": 10.0,
  "date_tasted": "2025-09-26",
  "lat": 44.056,
  "lng": 4.832
}
```

- `id` — stable slug of `producer-wine-vintage`, URL-safe
- `vintage` — four-digit year or `"NV"` (non-vintage)
- `grape` — a TasteRank variety, a named blend, or an additional variety in `grapes.json`. The form will generate a `grapes.json` snippet for any grape it doesn't recognise
- `color` — one of `red`, `white`, `rosé`, `sparkling`
- `rating` — number, one decimal, 0–10
- `date_tasted` — ISO date `YYYY-MM-DD`
- `lat` / `lng` — taken from `regions.json` for the wine's region

## Adding a new region or grape

**New region.** Add the region from Terminal with the `add_entry.py region "NAME" LAT LNG --codex vini` command, giving a sensible centroid for the region (the main town, the heart of the vineyard area). The form's tips panel gives the command in full. The form requires the region to exist before it will accept a wine from that region — otherwise the pin would have nowhere to go.

**New grape variety.** Just type the grape into the form and it will generate a `grapes.json` fragment below the wine entry; the script lands both in one run, so there is no separate step. You'll need to pick a colour manually since auto-detection only works on known varieties.

## Taxonomy philosophy

Wines are categorized by **a single grape/category field**, where grape varieties and named wine categories sit as peers. A Barolo is tagged `"Barolo"` (not decomposed to `"Nebbiolo"`). A Châteauneuf-du-Pape is tagged `"Châteauneuf-du-Pape Blend"` (not `"Grenache"`). A varietal Grenache from Gredos is tagged `"Grenache"`. This matches how sommeliers, wine lists, and retail actually organize wine — the named wine is its own identity, not a derivative of its dominant grape.

Borderline cases are handled individually.

## About

This project grew out of 20+ years of wine collecting and tasting. It is a personal reference tool — a codex of every wine I have notable memory of having tasted, organized for my own lookup and reflection.

The grape reference draws on my [TasteRank Grape Variety Reference](/library/inquiries/grape-affinities/), which provides one-paragraph profiles of 101 varieties. The regional terroir profiles draw on my [Soul of Wine](/library/inquiries/soul-of-wine/) project.

## License

This work is licensed under [Creative Commons Attribution-NonCommercial 4.0 International (CC BY-NC 4.0)](https://creativecommons.org/licenses/by-nc/4.0/). You are free to share and adapt this material for non-commercial purposes with attribution.

---

*Jure Skarabot · New York · 2026*

## Part of Vinotheca

One of the works of [Vinotheca](https://thevinotheca.com), a library of wine works, published at https://thevinotheca.com/chronicle/codex-vini/. The works share one repository, one licence and one site.
