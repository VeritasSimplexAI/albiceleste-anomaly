# Contributing

This is an evidence project. The bar for every contribution is the same bar the dossier
holds itself to: **sourced, verifiable, and stated with its uncertainty.**

## Report an error

Open an issue with (1) the number or claim you believe is wrong, (2) where it appears
(exhibit / file), and (3) a source we can check. Errors that survive verification get fixed
in the data, the pipeline is re-run, and the fix is credited in the commit.

## Submit a contested moment (2022 & 2026 Argentina matches)

Use the submission form in the site's tape section — a video link, or a timestamp and
description. Submissions land in a moderated queue and are checked against footage and press
before publication. Verified moments appear on the site credited as community-sourced.
Both directions welcome: calls against Argentina belong in the index too.

## Extend the analysis

PRs welcome. Ground rules:

- **Decisions, not execution.** Metrics measure what referees did, never whether players
  converted the resulting chances.
- **No fabricated data.** Every new data point needs a fetched, citable source; compiled
  files carry per-row `source_url` columns.
- **Publish your nulls.** If your test comes back empty, that result ships with the same
  prominence as a positive one.
- **State the caveat where the reader can't miss it** — survivorship bias, sample size,
  coverage asymmetry.
- Scripts must run with repo-relative paths (`pandas`, `numpy`, `scipy`, `statsmodels`)
  and write to `data/processed/`. Run `python analysis/export_site_data.py` after your
  pipeline changes and check the site renders (`cd site && python -m http.server`).

## What this project is not

It is not a fan site and not a prosecution. The verdict section states precisely what the
data supports and what it does not. Contributions that overstate either direction won't merge.
