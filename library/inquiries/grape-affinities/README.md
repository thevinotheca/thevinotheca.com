# Grape Affinities

A map of how grape varieties relate to one another. An interactive force-directed network visualization of wine grape variety similarity, built on a 13-dimension sensory profile drawn from established wine-tasting methodology (UC Davis, Peynaud, and related structured tasting frameworks). The graph uses the **TasteRank algorithm** — eigenvector centrality on a sensory similarity network — to rank 101 grape varieties by their structural importance, and Clauset–Newman–Moore greedy modularity optimization to identify six natural clusters.

## Live Site

**[→ Open Grape Affinities](https://jskarabot18.github.io/tasterank-explorer/)**

## What's Inside

- **Force-directed graph** built with [D3.js](https://d3js.org/) showing 101 grape varieties and 341 similarity edges
- **TasteRank scores** — eigenvector centrality measuring each variety's structural importance in the network (how similar it is to other highly-connected varieties)
- **6 communities** detected via the Clauset–Newman–Moore greedy modularity algorithm:
  - C0 · Full-bodied Mediterranean Reds (Sagrantino, Nero d'Avola, Syrah, Mourvèdre…)
  - C1 · Light & Aromatic cross-boundary (Riesling, Sauvignon Blanc, Assyrtiko…)
  - C2 · Mid-weight Structured Reds (Pinot Noir, Nebbiolo, Sangiovese, Nerello Mascalese…)
  - C3 · Rich Textural Whites (Chardonnay, Viognier, Marsanne, Sémillon…)
  - C4 · Mineral / Crisp Whites (Grüner Veltliner, Verdicchio, Chenin Blanc…)
  - C5 · Lean Neutral & Aromatic Whites (Gewürztraminer, Muscat Blanc, Ugni Blanc…)
- **Sensory profile visualization** — 13-dimension radar for each variety (color depth, aromatic intensity, floral, fruit ripeness, herbal/earthy, spice/oak, acidity, tannin, body, alcohol, flavor intensity, finish, complexity)
- **Cosine similarity edges** connecting each variety to its K=5 nearest neighbors

## Files

| File | Description |
|------|-------------|
| `index.html` | Self-contained interactive network visualization |
| `docs/summary.pdf` | Overview of methodology and key findings |
| `docs/technical-appendix.pdf` | Full technical details: graph construction, centrality math, community detection |
| `docs/methods-primer.pdf` | Plain-language guide to the procedure for readers who want to follow the reasoning without the equations |
| `docs/data-appendix.pdf` | Complete sensory profiles, rankings, and community assignments |
| `docs/grape-reference.pdf` | One-paragraph profiles for all 101 grape varieties |
| `README.md` | This file |
| `LICENSE` | CC BY-NC 4.0 license |

## How to Use

Open the [live site](https://jskarabot18.github.io/tasterank-explorer/) in any modern browser. Click any node to see its sensory profile and connected varieties. Click a community in the left panel to isolate it. Use the search bar to find a specific grape. Drag nodes to rearrange the layout. Press `Esc` to reset.

To run locally, open `index.html` in a browser — no build tools or server required.

## Methodology

Each grape variety is profiled on 13 sensory dimensions (scored 0–5) drawn from the structured tasting tradition that runs from Peynaud through the modern descriptive frameworks developed at UC Davis, AWRI, and the major national wine schools. The dimensions and scores are the author's synthesis, not a reproduction of any single proprietary grid. Pairwise cosine similarity is computed across all 101 varieties, and each variety is connected to its 5 most similar neighbors (K-nearest-neighbor graph). Eigenvector centrality on this network produces the TasteRank score — varieties that are similar to other highly-central varieties score highest. Community structure is detected using the Clauset–Newman–Moore greedy modularity algorithm, yielding six coherent clusters that align well with traditional grape family intuitions while revealing some unexpected cross-boundary connections.

## Key Findings

- **Sagrantino** ranks #1 — the most structurally central grape in the network, deeply connected to the Mediterranean red cluster
- **Community boundaries track sensory logic**, not geography: Nerello Mascalese clusters with Pinot Noir (C2), not with its Sicilian neighbor Nero d'Avola (C0)
- **Riesling and Assyrtiko** are structural outliers among whites — high acidity and complexity place them in the Light & Aromatic community (C1) rather than with mineral whites

## License

This work is licensed under [Creative Commons Attribution-NonCommercial 4.0 International (CC BY-NC 4.0)](https://creativecommons.org/licenses/by-nc/4.0/). You are free to share and adapt this material for non-commercial purposes with attribution.

---

*Jure Skarabot · New York*
