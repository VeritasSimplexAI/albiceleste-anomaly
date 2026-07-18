# RESULTS — Argentina World Cup officiating analysis (1990–2026)

*Compiled 2026-07-16, before the 2026 final (Argentina vs Spain, July 19).
All metrics are referee DECISIONS (awards, cards, overturns), not player execution.
Every number traces to a source listed in the data folders' SOURCES/NOTES files.*

## Headline findings

1. **Penalties awarded — the core anomaly.** 1990–2018 Argentina was exactly
   ordinary (6 awarded for / 5 against in 40 matches; ratios 1.02 / 0.84 vs field).
   Since 2022: **8 penalties awarded in 14 matches (0.57/match) vs a field rate of
   0.11/match — 5.0× the field, p=0.00045** (exact Poisson). That survives even a
   worst-case Bonferroni correction across every team in both tournaments
   (0.00045 × 55 ≈ 0.025). Argentina led BOTH tournaments in penalty awards
   (5 in 2022, next best 2; 3 in 2026, next best 2) while conceding 2 (2022,
   both in the final) and 0 (2026).
2. **VAR overturns lean the same way.** 2018–2026: 8 favorable / 1 unfavorable
   in 18 matches (0.44 favorable/match vs field 0.18; pooled p=0.0195). In 2026
   alone: **5 favorable, 0 against** (p=0.0104) — two opponent goals disallowed,
   2 of their 3 penalties awarded via VAR review, one opponent red card.
   Second-highest net-VAR-per-match of any team with ≥7 VAR-era matches.
3. **The 2022 card anomaly is real but two-sided.** Opponents of Argentina in
   2022 collected yellows at 3.71/match vs field 1.77 (p=0.0004) — the only
   FDR-surviving outlier among every team × metric × era tested. But Argentina
   themselves were carded HARSHLY per foul in 2022 (5.3 fouls/yellow, rank 25/32;
   2018: rank 30/32) — their matches were card-heavy in both directions.
4. **2026 routine officiating is normal.** Cards received exactly at field rate
   (1.29/match), fouls both directions within 10% of field, leniency mid-table
   (17/48). The 2026 anomaly is concentrated ENTIRELY in the high-discretion
   decisions: penalties (3–0) and VAR (5–0).

**Synthesis:** the data does not show blanket favoritism — it shows a pattern
that emerged in 2022 and persists in 2026, concentrated precisely where referee
discretion is highest (penalty awards, VAR overturns) and absent where decisions
are routine and countable (fouls, ordinary bookings). Pre-2022 Argentina shows
no favoritism on any metric in 36 years of data.

## Era table — Argentina vs field (rate ratios, exact Poisson p)

| Metric (per match) | 1990–2018 | 2022 | 2026 |
|---|---|---|---|
| Penalties awarded FOR | 1.02× (p=.83) | **4.80× (p=.007)** | **4.69× (p=.034)** |
| Penalties awarded AGAINST | 0.84× | 1.92× (p=.30) | 0.00× |
| Opponents' yellows | 1.12× (p=.30) | **2.24× (p=.0004)** | 1.33× (p=.31) |
| Own yellows | 1.09× (p=.42) | 1.40× (p=.19) | 1.00× (p=1.0) |
| Opponent dismissals | 1.97× (p=.045) | 5.76× (p=.20) | 2.01× (p=.41) |
| Own dismissals | 1.14× | 0 | 0 |
| Fouls committed / drawn | n/a pre-2014 | 14.3 / 16.4 | 1.10× / 1.07× (both ~field) |
| VAR net (fav−against) | n/a (2018: +1 in 4) | +1 in 7 | **+5 in 7 (p=.010)** |

## Full-history extension (2026-07-17): crews now cover ALL 1,066 matches 1930-2026
- Referee 100% double-sourced for 1930-1986 (412 matches); linesmen 99.6%.
- Data-quality find: the fjelstul dataset misattributes six 1958/1962 matches
  (incl. the 1962 FINAL) to 1998-era referee Levnikov instead of Nikolay
  Latyshev — corrected in our compiled files; flagged for any raw fjelstul use.
- Marciniak-Argentina (4 matches) remains the ONLY 4-match referee-team pairing
  in 96 years; historic 3-match/3-tournament pairs exist (Zsolt-England,
  Klein-Brazil, Griffiths-Yugoslavia).
- Confederation mix all-time: UEFA 75% of Argentina matches vs 54% field;
  Argentina's last CONMEBOL referee was pre-1990.
- CONMEBOL-PEERS CHECK (2026-07-18): the UEFA tilt is NOT a South American
  constant. Since 1990: Argentina 74.1% UEFA referees — highest in CONMEBOL —
  vs Brazil 55.4%, Uruguay 62.1%, Colombia 66.7%, Chile 33.3%, Paraguay 28.6%,
  Ecuador 31.2% (field 42.5%). Brazil's similarly deep runs got 19 points fewer
  European referees. Partial innocent explanation: elite refs at elite stages;
  the size of the gap over peers is the strained part.
- Copa América control (Exhibit K): Argentina's penalty rate vs field in
  CONMEBOL competition = 1.10/0.00/0.70/1.17/1.07x (2015-2024, incl. both
  title runs) vs 4.80/4.69x at FIFA World Cups 2022/2026 — the anomaly follows
  the organizer, not the team.

## Referee-teams study (added 2026-07-17; crews for all 654 matches 1990-2026)
- Crew expansion: 3 officials/match (1990) → 4 (1998-2014) → 8 (2018-2022 VAR era)
  → 7 (2026, slimmed VAR); appointed pools 41 (1990) → 171 (2026).
- **Marciniak-Argentina is the most-repeated referee-team pairing in the whole
  1990-2026 dataset: 4 matches across 3 tournaments** (2018 opener, 2022 R16,
  2022 FINAL, 2026 opener), with the same VAR (Kwiatkowski) on the last three.
  No other pairing reaches 4. Argentina holds 3 of the 8 pairings with ≥3
  matches (Marciniak 4, Rizzoli 3 in 2014 alone, Irmatov 3).
- VAR repeats are NOT unique to Argentina (Irrati-France 4, Makkelie-England 4)
  — honest counterweight.
- Confederation mix: UEFA referees take 74.1% of Argentina matches vs 42.5%
  baseline (~54% after adjusting for the neutrality rule that bars CONMEBOL
  referees from Argentina matches — elevated, but knockout-stage elite-referee
  selection plausibly explains part of it).
- Full-history penalty ledger completed 1930-1986 (104 more source-verified
  penalties; all 13 converted-count anchors matched): Argentina 0.96× field
  1930-1986 — the pre-2022 ordinariness now spans 92 years.

## Referee forensics — four hard tests (added 2026-07-17; subreports/ for full methods)
1. WITHIN-REFEREE: no referee's card/penalty behavior detectably changes when
   Argentina plays (pooled contrast IRR 1.11, p=0.44; zero FDR survivors;
   Marciniak at his own baseline).
2. ASSIGNMENT MONTE CARLO (20k sims): a 4-match referee-team pair somewhere is
   expected (p=.43); the Argentina-specific Marciniak structure is ~1-in-10
   unusual (p=.06-.15), post hoc, one piece of evidence. Real-data finding:
   country neutrality is absolute (0 violations in 654 matches) but
   confederation neutrality is NOT actually practiced.
3. ELO RESIDUALS: Argentina did NOT overperform Elo post-2022 — **2022 is the
   only negative-residual championship since 1990 (-0.72)**; 2026-so-far +1.07
   is mid-pack among title runs. Under Marciniak Argentina UNDERperformed
   (p=0.90 in favoritism direction). No referee survives multiplicity.
4. HIERARCHICAL PAIR MODEL (1,025 pairs): pair variance ~0; Marciniak-Argentina
   ranks 1,001/1,025 on cards — neutral. No Argentina pair is an outlier.

SYNTHESIS UPDATE: the anomaly is NOT in results (Argentina won on merit, even
under-running their rating in 2022) and NOT in per-referee behavior. It is
confined to high-discretion DECISIONS (penalty awards 5x field, VAR 8-1) plus a
mildly unusual assignment pattern. Draw analysis (in progress): groups were
historically soft (no 2022 break); 2026 knockout path (mean opp Elo 1797) is
the softest deep-run path in the dataset vs rivals' 1882-1956.

## Supporting analyses
- **Poisson GLM** (match level, knockout + tournament FE, cluster SE): Argentina
  ×post-2022 interaction — opponents' yellows IRR 1.9, penalty goals IRR 6.0
  (both p<.001; CIs overconfident with 7 treated matches — the exact tests above
  are the defensible numbers).
- **Difference-in-differences** 1990-2018→2022: card differential +1.24/match
  (4th of 28 teams; the 3 above had ≤5 post matches), penalty net +0.31 (top-5).
- **Deep-run cohort 2022:** card differential NOT unique (England +1.40,
  Portugal +1.40 vs Argentina +1.29) — but penalties clearly are (0.71 awarded
  /match vs ≤0.40 for every other semifinal-caliber team).
- **Empirical-Bayes rankings 1990-2018:** Argentina 40/71 (cards), 52/71 (pens)
  — historically mid-table, no favoritism baseline.

## Evidence classes and caveats
- Cards/goals/pens 1990–2022: fjelstul/worldcup dataset (academic, complete).
- Pens awarded 1990–2010: per-incident compilation (RSSSF primary, cross-checked
  vs Linguasport + a third source; 101 pens; converted subset matches the
  academic dataset exactly). 2014–2026: FBref squad tables via archived
  snapshots; Argentina's rows cross-checked vs summed ESPN box scores (fouls
  and PK counts match exactly; two 1-2 card discrepancies documented).
- VAR incidents: journalistic compilation (REFSIX 2018, ESPN tracker 2022, ESPN
  commentary sweep 2026), 86 directional incidents; 27 ambiguous 2026 feed rows
  EXCLUDED — treat VAR findings as strong-but-softer evidence than penalties.
- Known gaps: 2014 per-team pens-conceded unpublished (Argentina assumed 0
  conceded-awarded; converted-against was 0); fouls unavailable pre-2014; 2026
  missing final + 3rd-place match; n=14 post-apex matches is small — the pen
  finding is significant DESPITE that, not immune to it.
- Confounder honestly stated: elite attacking teams draw more penalties. The
  cohort table addresses this — no other elite deep-run team in 2022/2026
  exceeds 0.40 awarded/match; Argentina is at 0.57 pooled.

## Context (allegations, cited as allegations)
The FBI is reportedly investigating the AFA for money laundering of 2022 prize
money and commercial funds through US shell companies (CBS Sports, Inc., La
Nación reporting, 2026); journalist Romain Molina alleges FIFA protected the
AFA. No charges have been filed; nothing here proves causation between the
financial allegations and the officiating pattern. The site must present these
as parallel, sourced observations — the statistics stand on their own.
