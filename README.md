# Vinotheca

**A library of wine works.**

Live site: [thevinotheca.com](https://thevinotheca.com)

A collection of wine works built by Jure Skarabot. Atlases, tools, studies, oracles, codices — each one approaches wine from a different direction. The library is organised into two parts: works that look at wine in general (Part I), and works that record one person's experience of wine (Part II).

## Part I — The Library

### Maps

1. **[The Maker Atlas](/library/maps/maker-atlas/)** — a global reference of wine makers, estates, domaines, and houses, organised by place.
2. **[The Vineyard Atlas](/library/maps/vineyard-atlas/)** — the world's greatest vineyards, organised by grape variety.

### Works (paired Tool + Study)

3. **[Grape Affinities](/library/inquiries/grape-affinities/)** — a similarity network of 101 grape varieties (the tool); paired with **[The Body of Wine](/library/inquiries/body-of-wine/)** (the study).
4. **[Region Affinities](/library/inquiries/region-affinities/)** — a similarity network of 59 wine regions (the tool); paired with **[The Soul of Wine](/library/inquiries/soul-of-wine/)** (the study).

### Correspondence

5. **[Region Resonances](/library/correspondence/region-resonances/)** — an oracle that maps a feeling, phrase, or situation to wine regions whose temperament matches.
6. **[Grape Resonances](/library/correspondence/grape-resonances/)** — the same oracular instrument, tuned to grape varieties.

## Part II — The Personal Codex

7. **[Codex Vini](/chronicle/codex-vini/)** — a personal wine atlas of bottles tasted.
8. **[Codex Vinitorum](/chronicle/codex-vinitorum/)** — a personal codex of winemakers met in person.

## About this repository

This repository hosts Vinotheca. The works above no longer live in separate repositories — they live in this directory, at the addresses linked above, and are published together as one site.

The site deploys on push to `main` via Cloudflare Pages. There is no build step and no dependencies: Cloudflare Pages is configured to build nothing, and the pages are plain files. The three Vite leaves — Region Affinities, Region Resonances, Grape Resonances — are the exception to plain files, and they are committed here as built output rather than built on deploy.

## License

Creative Commons Attribution-NonCommercial 4.0 International (CC BY-NC 4.0) — see [LICENSE](LICENSE).

You are free to share and adapt the material, provided you give appropriate credit and do not use it for commercial purposes.

## Contact

Jure Skarabot · New York · [skarabot@yahoo.com](mailto:skarabot@yahoo.com)
