# docs-source

LaTeX sources for the five PDFs in this repo's documentation set.

## Files

- `TasteRank_Summary.tex` — plain-language overview
- `TasteRank_Technical_Appendix.tex` — algorithms and computation
- `TasteRank_Methods_Primer.tex` — guide to the methods
- `TasteRank_Data_Appendix.tex` — sources and edge tables
- `TasteRank_Grape_Reference.tex` — variety-by-variety reference cards

Helper data files (`\input{}`-included by the documents above):
- `data_rows.tex` — the 341 edges in the similarity network (used by Data Appendix)
- `grape_entries.tex` — the 101 grape entries (used by Grape Reference)

Shared preamble:
- `vinotheca-preamble.tex` — shared family preamble (typography, colours, environments)

The shared preamble is identical to the copies in `region-affinities` and
`region-resonances`. If amended, all three copies should be updated together.

## Recompiling

Each main `.tex` file compiles to a same-name `.pdf` in this repo's root.
From inside the `docs-source/` directory:

```bash
pdflatex -interaction=nonstopmode TasteRank_Summary.tex
pdflatex -interaction=nonstopmode TasteRank_Summary.tex   # second pass for refs
mv TasteRank_Summary.pdf ../
```

Run twice for cross-references and ToC. Then move the `.pdf` to the repo
root (where `index.html` links it) and clean up the auxiliary files
(`*.aux`, `*.log`, `*.out`, `*.toc`).

The Data Appendix and Grape Reference depend on `data_rows.tex` and
`grape_entries.tex` respectively, via `\input{}`. They must be in the
same directory as the parent `.tex` when compiling.

## Note on the tool name

The PDFs are named with the `TasteRank_` prefix because they document
the TasteRank algorithm — the underlying method. The tool itself is
called "Grape Affinities" in the user-facing wordmark, but the algorithm
name (and therefore the documentation name) stays.

## Editing

The shared preamble defines:
- typography (EB Garamond body, Cormorant Garamond display, IM Fell English SC for small caps)
- the `wine` accent colour
- shared environments (`\frontmatter`, `\methodsbox`, etc.)

Changes to the preamble affect all five documents — recompile all of them.
