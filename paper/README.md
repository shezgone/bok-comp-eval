# Paper draft — KG-RAG evaluation

Target venue: ISWC 2026 In-Use Track (Springer LNCS, ~16 pages).

## Build

Requires XeLaTeX (for `kotex` Korean rendering of inline domain examples).

```bash
cd paper/
xelatex main && bibtex main && xelatex main && xelatex main
# → main.pdf
```

Or in Overleaf: upload all files (or push as a git project), set the
compiler to **XeLaTeX**.

## Migrating to LNCS template

The current `main.tex` uses `\documentclass{article}` for portability.
For ISWC submission:

1. Download `llncs.cls` and `splncs04.bst` from the
   [Springer LNCS page](https://www.springer.com/gp/computer-science/lncs/conference-proceedings-guidelines).
2. Replace the class line in `main.tex`:
   ```tex
   \documentclass[runningheads]{llncs}
   ```
3. Drop article-only packages that LNCS overrides
   (`geometry`, `fancyhdr` if added).
4. Update `\bibliographystyle{plainnat}` to `\bibliographystyle{splncs04}`.

## Structure

```
paper/
  main.tex              # entry, includes all sections + bib
  refs.bib              # 11 placeholder entries — VERIFY before submission
  sections/             # one .tex per section
    abstract.tex
    01_intro.tex
    02_related.tex
    03_system.tex
    04_setup.tex
    05_results.tex
    06_mechanism.tex
    07_discussion.tex
    08_limitations.tex
    09_conclusion.tex
    A_appendix.tex
  tables/
    eval_set.tex          # 100q distribution
    overall_acc.tex       # 4 LLM × 8 backend, 95% bootstrap CI
    mcnemar.tex           # 8 KG-vs-context paired tests
    token_cost.tex        # 5 surface forms, size + accuracy
  figures/                # all TikZ + pgfplots (no external assets)
    main_bar.tex          # KG agent vs in-context (per LLM)
    form_sensitivity.tex  # Llama-4 form sensitivity bars
    nl_pareto.tex         # acc vs token cost scatter
    boundary_oos.tex      # closed-world out_of_scope per LLM
```

## Pre-submission checklist

- [ ] Verify all `refs.bib` entries against arXiv / Semantic Scholar /
      DBLP. The current file has explicit `note = {verify}` flags.
- [ ] Confirm 16-page fit after switching to `llncs.cls`.
- [ ] Re-run `eval/analyze_pilot.py --gold eval/full_questions.jsonl`
      and verify all numbers in `tables/` match.
- [ ] Korean text renders correctly under XeLaTeX + kotex.
- [ ] All figure / table cross-references resolve.
- [ ] Reproducibility: GitHub repo URL is correct in
      `09_conclusion.tex`.
