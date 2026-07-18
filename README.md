# The Albiceleste Anomaly

**An open, reproducible investigation into World Cup officiating and Argentina, 1930–2026.**

For ninety-two years — from the first World Cup to the eve of Qatar 2022 — referees treated
Argentina like anyone else. Every penalty in between says so; this project checked all of them.
Then, starting in Qatar 2022, the two decisions referees have the most discretion over —
**penalty awards and VAR overturns** — swung Argentina's way at roughly **five times the going
rate** (~1 in 2,200 by chance) and **8–1** respectively, while every independently verifiable
channel (fouls, tackles, cards-per-foul, per-referee behavior, results against ratings) stayed
normal — and the same team in CONMEBOL's Copa América shows none of it.

This repository contains **everything**: every dataset, every script, every methodological
choice, every null result, and the static website that presents it. The claim is narrow and
the evidence is auditable. We invite you to try to break it.

## The website

`site/` is a fully self-contained static site (no build step, no framework):

```
cd site && python -m http.server 8000    # then open http://localhost:8000
```

## Reproduce the analysis

Requirements: Python 3.11+ with `pandas`, `numpy`, `scipy`, `statsmodels`.

```
pip install pandas numpy scipy statsmodels
python analysis/build_stats.py               # core per-team/per-match tables (1930-2022)
python analysis/deep_analysis.py             # EB shrinkage, FDR scan, DiD, Poisson GLM
python analysis/integrate_2026.py            # 2026 cards/fouls integration
python analysis/integrate_pens_awarded.py    # archival penalties 1990-2010
python analysis/final_decision_analysis.py   # penalties-awarded era tests, VAR, leniency
python analysis/referee_analysis.py          # crews, repeat pairings, confederation mix
python analysis/referee_comparison.py        # per-official win% vs baselines
python analysis/referee_records.py           # Argentina's record with each official
python analysis/conmebol_refs.py             # CONMEBOL-peers referee mix
python analysis/draw_difficulty.py           # group difficulty (Elo), knockout paths
python analysis/stage_paths.py               # stage-by-stage knockout opponents
python analysis/draw_seeding_analysis.py     # pots + FIFA-rank draw views
python analysis/robustness_impact_eras.py    # stress tests, decision impact, president eras
python analysis/player_defense_analysis.py   # the whistle study (tackles/fouls/cards)
python analysis/within_referee.py            # within-referee fingerprint test
python analysis/assignment_simulation.py     # referee-assignment Monte Carlo (slow, ~4 min)
python analysis/elo_forensics.py             # Elo residuals + hierarchical pair model (~2 min)
python analysis/hypothetical_paths.py        # projected run-to-final difficulty at the draw
python analysis/export_site_data.py          # regenerates site/data.js from all outputs
```

Every script reads from `data/` and writes to `data/processed/`; paths are repo-relative.

## What's in the data

| Folder | Contents | Provenance |
|---|---|---|
| `data/worldcup-1930-2022/` | matches, goals, bookings, penalty kicks, referees, standings | fjelstul/worldcup academic dataset (CC-BY-4.0) |
| `data/international-results/` | all internationals 1872–2026 | martj42/international_results |
| `data/worldcup-2026/` | 2026 matches, referees, per-match cards | compiled from Wikipedia + ESPN, cross-verified |
| `data/penalties-historical/` | **every penalty awarded 1930–2010, per incident** | RSSSF + Linguasport + press, triple-checked |
| `data/officiating-extra/` | squad discipline 2014–2026, all VAR overturns + confirmed reviews | FBref (archived), REFSIX, ESPN trackers |
| `data/referee-teams/` | full officiating crews for all 1,066 matches 1930–2026 | RSSSF + Wikipedia + FIFA, double-sourced |
| `data/elo/` | pre-tournament Elo, every participant 1930–2026 | eloratings.net, spot-verified |
| `data/seedings/` | draw pots + pre-tournament FIFA rankings | Wikipedia + FIFA fact sheets |
| `data/player-defense/` | 3,119 player-tournament defensive rows + foul-by-foul events | FBref + StatsBomb Open Data |
| `data/copa-america/` | Argentina's full Copa record + squad discipline | Wikipedia, RSSSF, FBref |
| `data/contested-calls/` | 26 contested moments with official-video links | press-sourced, both directions |

Each folder carries its own `NOTES.md`/`SOURCES.md` with per-row provenance, verification
trails, and honestly-graded coverage gaps. See `DATA_SOURCES.md` for licenses and attribution.

## Methodology

- `analysis/RESULTS.md` — the master findings document
- `analysis/KPI_FRAMEWORK.md` — what we measure and why (decisions, never execution)
- `analysis/subreports/` — full methods for the four referee-forensics studies and the
  draw-projection model

The dossier's standards: every metric is a **referee decision** (a penalty counts when awarded,
not when scored); every headline number carries its probability under fair treatment; multiple
comparisons are corrected; **null results are published with the same prominence as positive
ones** (four independent tests cleared routine officiating — that's in the site's verdict);
and known limitations (survivorship bias in foul counts, the 14-match post-2022 sample,
unlogged VAR checks) are stated where the reader can't miss them.

## Contributing

Spotted an error? Open an issue with a source. Have a contested moment from a 2022/2026
Argentina match? Submit it through the site's tape section — every submission is verified
against footage and press before publication. See `CONTRIBUTING.md`.

## License

Code: MIT. Our compiled datasets: CC-BY-4.0. Upstream data remains under its original terms —
see `DATA_SOURCES.md` for full attribution, including the StatsBomb Open Data license.

---

*The statistics identify a pattern. They do not, on their own, identify a mechanism or an
actor. Allegations referenced in the site's Context section are reported allegations; no
charges have been filed.*
