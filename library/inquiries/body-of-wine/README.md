# The Body of Wine

**A network analysis of the wine grape universe, encoded by sensory similarity.**

A graph-theoretic study of how 101 grape varieties relate to one another in thirteen-dimensional sensory space. The most central grapes are not the most celebrated; the red–white boundary is permeable; the network's structure is not what the trade vocabulary would predict.

🔗 **[Read the study →](https://jskarabot18.github.io/body-of-wine)**

---

## The Question

Structured tasting reads each wine across thirteen sensory dimensions — colour, aroma, fruit, herb, spice, acid, tannin, body, alcohol, flavour, finish, complexity, floral character. The dimensions have organised serious tasting since Peynaud, and they describe wine at the level a trained palate actually engages: not the label, not the region, but the wine itself in the mouth. This study asks what happens if we treat each grape's canonical sensory profile as a point in this thirteen-dimensional space and let the structure between the points speak for itself.

## The Finding

The structure is unevenly distributed. Some grapes sit at the gravitational centre, densely surrounded by similar peers. Others sit at the periphery, distinctive enough to have few close kin. The grapes the wine trade calls noble are systematically peripheral. Distinctiveness has its own value — but it is something the trade vocabulary does not register.

## Three Key Findings

1. **Distinctiveness and centrality are inversely related.** The most central grapes in sensory space are not the most celebrated. Sagrantino, Nero d'Avola, and Lagrein sit at the gravitational core because their profiles are densely surrounded by similar varieties. Pinot Noir (rank 47), Nebbiolo (42), and Riesling (85) sit at the periphery because their profiles are too distinctive to cluster. The trade has been calling distinctiveness *nobility* for two centuries; the network suggests these are not the same property.

2. **The red–white boundary is permeable.** Six natural families emerge from sensory similarity. Five fall cleanly into the colour categories the trade uses; one does not. It holds four ultra-light reds — Schiava, Poulsard, Frappato, Kadarka — clustered with seventeen aromatic whites. Frappato sits closer in body to Loureiro than to most reds. Schiava sits closer to Riesling than to its red-grape peers. At the structural level, colour is secondary to weight and aroma.

3. **White wine centrality peaks with textural mid-weights.** Among whites, the most central varieties are Marsanne, Fiano, Godello, Pinot Gris — medium-bodied, moderately complex, sitting at the centre of the white-grape subspace. The most distinctive whites — Riesling at rank 85, Sauvignon Blanc at 90 — rank near the bottom of the entire 101-variety network. The same inversion that holds for reds holds, even more sharply, for whites.

## The Six Natural Families

| Family | n | R / W | Hub Varieties |
| --- | --- | --- | --- |
| **Full-bodied Mediterranean Reds** | 31 | 31 / 0 | Sagrantino, Nero d'Avola, Lagrein, Negroamaro, Plavac Mali |
| **Light / Aromatic Cross-boundary** | 21 | 4 / 17 | Assyrtiko, Falanghina, Albariño, Riesling, Kadarka |
| **Mid-weight Structured Reds** | 18 | 18 / 0 | Limniona, St. Laurent, Zweigelt, Blaufränkisch, Sangiovese |
| **Rich Textural Whites** | 13 | 0 / 13 | Marsanne, Fiano, Godello, Pinot Gris, Chardonnay |
| **Mineral / Crisp Whites** | 10 | 0 / 10 | Greco, Friulano, Verdicchio, Verdejo, Vermentino |
| **Lean Neutral & Aromatic Whites** | 8 | 0 / 8 | Gewürztraminer, Petit Manseng, Muscat Blanc, Malvasia |

Communities are detected by greedy modularity optimisation (Q ≈ 0.41) — fully model-derived. The character labels are interpretive descriptions of each cluster's centre of gravity.

## Methodology

The study uses graph-theoretic methods on a thirteen-dimensional sensory encoding:

* **Encoding.** Each of 101 grape varieties is described by thirteen sensory dimensions — colour depth, aromatic intensity, floral character, fruit ripeness, herbal/earthy, spice/oak, acidity, tannin, body, alcohol, flavour intensity, finish, complexity — scored 0–5 against canonical varietal typicity.

* **Similarity.** Pairwise similarity between varieties is computed by cosine similarity on the profile vectors. Cosine measures profile shape rather than magnitude, so two grapes with proportionally similar profiles cluster together regardless of overall intensity.

* **Network.** A sparse k-nearest-neighbour graph (k = 5, symmetrised by maximum-weight union) reduces the dense similarity matrix to 101 nodes and 341 edges — sparse enough to reveal community structure, rich enough to support centrality ranking.

* **Centrality and Communities.** Eigenvector centrality on the weighted graph defines TasteRank. Modularity optimisation (Clauset–Newman–Moore greedy algorithm) extracts six communities (Q ≈ 0.41). PageRank, sensitivity to k, and spectral gap analysis confirm the findings are robust to method choice.

## Companion Tool

| Tool | Description |
| --- | --- |
| [**Grape Affinities**](https://jskarabot18.github.io/tasterank-explorer/) | Interactive force-directed visualisation of the 101-variety network. Click any grape to see its sensory profile and its five closest kin. Browse the six natural families. The navigable form of this study. |

## Research Documents

The five documents are hosted in the `tasterank-explorer` repository, alongside the pipeline that produces them.

| Document | Description |
| --- | --- |
| [**Summary**](https://jskarabot18.github.io/tasterank-explorer/docs/summary.pdf) | The full plain-language overview — the question, the encoding, the network construction, the centrality finding, the community structure, and the principal results. |
| [**Technical Appendix**](https://jskarabot18.github.io/tasterank-explorer/docs/technical-appendix.pdf) | The full mathematical framework — cosine similarity, the kNN graph, eigenvector centrality with Perron–Frobenius reasoning, PageRank, modularity, and the implementation pipeline. |
| [**Methods Primer**](https://jskarabot18.github.io/tasterank-explorer/docs/methods-primer.pdf) | A non-technical guide to the procedure for readers who want to follow the reasoning without the equations. Companion to the Technical Appendix. |
| [**Data Appendix**](https://jskarabot18.github.io/tasterank-explorer/docs/data-appendix.pdf) | The complete 101-variety table with sensory profile scores, community assignments, TasteRank scores, and pipeline parameters. |
| [**Grape Reference**](https://jskarabot18.github.io/tasterank-explorer/docs/grape-reference.pdf) | Per-variety descriptive notes covering the character, regional expression, and stylistic range of each of the 101 grapes in the network. |

## Repository Structure

```
body-of-wine/
├── index.html        Landing page (the study)
├── README.md
└── LICENSE
```

The intellectual content of the study lives here as prose. The data, pipeline, and interactive tool live in [`tasterank-explorer`](https://github.com/jskarabot18/tasterank-explorer), the companion Tool repository. Together they form one Work of Vinotheca, presented on the parent catalogue under the name **The Body of Wine** (Study) and **Grape Affinities** (Tool).

## Coverage

* **101 grape varieties:** 53 red, 48 white
* **13 sensory dimensions** drawn from the structured tasting tradition (Peynaud, UC Davis, AWRI, WSET)
* **6 natural families** detected algorithmically by modularity optimisation
* **341 sensory connections** in the symmetrised k-NN graph (k = 5)

## Key References

* Bonacich, P. (1972). Factoring and weighting approaches to status scores and clique identification. *Journal of Mathematical Sociology*, 2(1), 113–120.
* Brin, S. & Page, L. (1998). The anatomy of a large-scale hypertextual web search engine. *Computer Networks*, 30(1–7), 107–117.
* Clauset, A., Newman, M. E. J. & Moore, C. (2004). Finding community structure in very large networks. *Physical Review E*, 70(6), 066111.
* Newman, M. E. J. (2010). *Networks: An Introduction.* Oxford University Press.
* Peynaud, É. (1980). *Le Goût du Vin.* Dunod, Paris.
* Robinson, J., Harding, J. & Vouillamoz, J. (2012). *Wine Grapes: A Complete Guide to 1,368 Vine Varieties.* Ecco/HarperCollins.
* d'Agata, I. (2014). *Native Wine Grapes of Italy.* University of California Press.

---

*The shelf is not the body. The body is what wine does in the mouth.*
