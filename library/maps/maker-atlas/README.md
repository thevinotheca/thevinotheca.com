# The Maker Atlas

A curated global reference of wine makers — estates, domaines, and houses across the world's principal wine regions — presented as a clickable world map with a downloadable PDF companion volume. Sibling instrument to [The Vineyard Atlas](https://github.com/jskarabot18/grand-cru-atlas) within [Vinotheca](https://jskarabot18.github.io/vinotheca/).

The atlas answers a specific question: where, on the map of the world, are the wine makers of established reputation, and what do they make? It is a curated reference, not a ranking — makers appear because they illustrate their region or grape clearly, not because they are ranked above others.

## Status

**Pilot.** Three estates encoded (Mosel: Joh. Jos. Prüm, Egon Müller, Schloss Lieser). Target: approximately 160 makers across the world's principal wine-producing regions. First full edition planned for 2026.

## Coverage

The atlas's coverage discipline draws on publicly established wine-education traditions (UC Davis enology and viticulture, the Peynaud line of sensory analysis, the Australian Wine Research Institute's public work, official appellation and regulatory bodies' published material, and standard reference works). It does not derive from, reproduce, or depend on any commercial certification body's proprietary curriculum or methodology.

Inclusion is based on durable recognition in public sources. The atlas does not use prices, scores, critic lists, or user ratings as selection criteria.

## Architecture

A single self-contained `index.html` file serving a Leaflet map over OpenStreetMap-derived tiles, with maker data in a separate `estates.json` file. No build step. No tracking. No analytics. No external dependencies beyond the Leaflet library and the openly licensed map tiles.

## Running locally

Clone and open `index.html` in any modern browser. No server required for the prototype; once `estates.json` is loaded via `fetch()` (planned for the post-pilot version), a simple local server is needed:

```bash
python3 -m http.server 8000
# then open http://localhost:8000
```

## License

Published under the **Creative Commons Attribution-NonCommercial 4.0 International** licence (CC BY-NC 4.0). See [LICENSE](./LICENSE).

## Part of Vinotheca

- [Vinotheca](https://jskarabot18.github.io/vinotheca/) — the umbrella library
- [The Vineyard Atlas](https://github.com/jskarabot18/grand-cru-atlas) — sibling volume, organized by grape rather than by place
- [Codex Vini](https://github.com/jskarabot18/codex-vini) — the personal-track instrument

Correspondence: [skarabot@yahoo.com](mailto:skarabot@yahoo.com)
