# Codex Vinitorum

*In vino, cognitio.*

A personal record of winemakers I have met — every encounter, plotted on a map, filterable by country, region, event, and affinity signals. A sibling to [Codex Vini](https://jskarabot18.github.io/codex-vini/) and part of [Vinotheca](https://jskarabot18.github.io/vinotheca/).

## Live site

**[→ Open Codex Vinitorum](https://jskarabot18.github.io/codex-vinitorum/)**

## What's inside

The site is organised into three sections:

- **The Book** — sortable, searchable, filterable table of every winemaker met
- **The Atlas** — interactive map (Leaflet + CARTO basemap) with one uniform pin per winemaker, popup showing bio and signals
- **The Collection** — six charts visualising the codex: encounters by country, by region, by event, by year, signal distribution, and signal combinations

Plus:

- **Cross-linked filters** — clicking any row in The Book flies the map to that winemaker and opens their entry; filters update the table independently
- **Affinity signals** — three optional, orthogonal experience-side markers per entry: *Felt close to*, *Memorable encounter*, *Stayed with me*. The signals describe the user's experience of the encounter, not the winemaker as object; they do not compose into a score and do not produce a ranking
- **Add Winemaker form** — in-browser form for generating new entries as encounters happen


Each winemaker is recorded with:

- Name, estate, country, region
- Event and date of meeting (full date in data; year only on public-facing surfaces)
- A short factual bio (~80–110 words) — lineage, training, substantive decisions, estate facts
- Three optional affinity signal flags


## Affinity signals

This codex deliberately does not rate winemakers. Rating people on a personal record reduces a human encounter to a score, and that is not what this record is for. Instead, each entry can carry up to three optional signals, each describing the user's experience of the encounter rather than the winemaker as object:

- **Felt close to** — felt personal closeness with the winemaker
- **Memorable encounter** — the meeting itself stood out
- **Stayed with me** — the encounter persisted in your thinking after it ended

Each signal is independently on or off. The three are orthogonal — they do not combine into a numeric score and they do not produce a ranking. A small fleuron (❧) appears next to entries for each signal they carry, in fixed positional order. Different combinations are visually distinct without implying a hierarchy.

The signals are meant to be rare enough to be meaningful. Most encounters will carry none. The discipline matters: an entry without signals is as honest a record as one with three.

The architectural decision is locked in [PROJECT.md §6.5](https://github.com/jskarabot18/vinotheca/blob/main/PROJECT.md) of the parent Vinotheca repo.


## Files

| File | Purpose |
| --- | --- |
| `index.html` | The main app — self-contained HTML + CSS + JS |
| `add_winemaker.html` | In-browser form for adding new winemakers |
| `winemakers.json` | Single source of truth — every winemaker as a JSON object |
| `regions.json` | Region → lat/lng lookup |
| `README.md` | This file |
| `LICENSE` | CC BY-NC 4.0 |


## How to use

Open the [live site](https://jskarabot18.github.io/codex-vinitorum/) in any modern browser. Use the filters in The Book panel to narrow by country, region, event, or signal. Click any row to fly the map to that winemaker and open their popup. Click any of the **Reset** buttons or press `Esc` to clear all filters.

To run locally, use a local server (`python3 -m http.server` from the repo root) and open `http://localhost:8000/`. The page loads `winemakers.json` and `regions.json` via `fetch()`, which most browsers block under the `file://` protocol — opening `index.html` by double-click will render the layout but show no entries.


## Adding a new winemaker

### Option 1 — In-browser form (recommended)

1. Open `add_winemaker.html` (in the live site or via a local server)
2. Fill in name, estate, country, region, event, date met, and a short factual bio. The country, region, and event fields autocomplete from existing values but accept anything new
3. Coordinates auto-fill from the region's centroid if the region exists in `regions.json`; otherwise override manually
4. Optionally mark any of the three affinity signals
5. Click **Generate JSON** and **Copy to clipboard**
6. Open `winemakers.json` and paste the entry at the start of the array (immediately after the opening `[`)
7. If the region is new, the form generates a `regions.json` snippet alongside the entry — paste that into `regions.json` first
8. Commit and push — GitHub Pages redeploys automatically


### Option 2 — Direct edit on GitHub

1. Open `winemakers.json` on github.com
2. Click the pencil icon to edit
3. Paste a new entry following the schema below
4. Commit


### Schema

Every winemaker is a JSON object of this shape:

```json
{
  "id": "stable-slug-of-name",
  "name": "Full Name",
  "estate": "Estate Name",
  "country": "Country",
  "region": "Region",
  "event": "Event where met",
  "date_met": "YYYY-MM-DD",
  "bio": "Short factual bio paragraph.",
  "lat": 0.0,
  "lng": 0.0,
  "felt_close_to": false,
  "memorable_encounter": false,
  "stayed_with_me": false
}
```

- `id` — stable slug derived from the name, URL-safe
- `bio` — factual paragraph in the ~80–110 word range; lineage, training, substantive decisions, estate facts. No quality-claims, no personal impressions
- `date_met` — ISO date `YYYY-MM-DD` (full date stored; year only shown publicly)
- `lat` / `lng` — from `regions.json` for the winemaker's region, or overridden to estate-specific coordinates
- `felt_close_to`, `memorable_encounter`, `stayed_with_me` — booleans, each independently optional


## Bio discipline

The bios in this codex are written in a factual, encyclopedic register — closer to a producer reference than to wine criticism. The aim:

- *No quality-claims* — avoid "foremost," "greatest," "rivals," "elevated to international recognition"
- *No comparative judgments* — avoid "ranks alongside," "in the same conversation as"
- *No personal impressions* — avoid "at tastings he is...," "magnetic," "warm and gregarious." Character and disposition are not the bio's job; if there is anything to say about the encounter itself, the affinity signals are where it lives
- *Yes to lineage, training, substantive decisions, estate facts* — generation, who they took over from, when they converted to biodynamic, what cuvées they make, what soils, what philosophy is articulated in their winemaking

The bios are working content. They will be refined over time as new information surfaces.


## Architecture

Codex Vinitorum is a Part II artefact under the Vinotheca architecture — a personal codex, not part of the Library. The architectural rule is locked: the Library (Part I: Maps, Works, Correspondence, Reference) and the Personal Codex (Part II) do not interact. Codex Vinitorum is standalone — its content does not feed any of the Library's leaves. The winemakers recorded here populate the codex because they are who I have met, not because they appear in any analytical corpus.

See the parent [Vinotheca PROJECT.md](https://github.com/jskarabot18/vinotheca/blob/main/PROJECT.md) for the full family architecture, including the §6.5 commitment to the three affinity signals as the locked alternative to numeric rating.


## About

This codex grew out of two decades of attending winemaker tastings, dinners, and estate visits. It is a personal reference tool — a record of encounters with the people who make the wine, organised for my own lookup and reflection.

The companion record of wines tasted lives at [Codex Vini](https://jskarabot18.github.io/codex-vini/). The two codices share the same Personal Codex register but do not cross-reference: a wine in Codex Vini may or may not have been made by a winemaker in Codex Vinitorum, and the two records are kept separate by design.


## License

This work is licensed under [Creative Commons Attribution-NonCommercial 4.0 International (CC BY-NC 4.0)](https://creativecommons.org/licenses/by-nc/4.0/). You are free to share and adapt this material for non-commercial purposes with attribution.

---

*Jure Skarabot · New York · 2026*


