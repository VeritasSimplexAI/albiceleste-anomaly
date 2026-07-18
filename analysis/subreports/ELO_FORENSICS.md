# Elo forensics: referee residuals and the hierarchical referee×team card model

Script: `analysis/elo_forensics.py` · Output tables: `data/processed/elo_residuals_by_referee.csv`,
`data/processed/hierarchical_pairs.csv`
Compiled 2026-07-17. Fully reproducible: fixed seed (20260717), deterministic model starting values.

## Questions

1. **Step 3 (Elo residuals):** Once you account for team strength via Elo ratings, did Argentina
   win more than expected under specific referees — Szymon Marciniak in particular? And did
   Argentina's post-2022 overperformance exceed what other champions showed in their title runs?
2. **Step 4 (hierarchical card model):** After shrinking every referee×team pair against all
   1,025 pairs in the data, is any Argentina–referee pair an outlier in yellow cards received?

## Data and conventions

- **Elo:** `data/elo/elo_pre_tournament.csv` — pre-tournament Elo for all 320 team-tournament
  pairs 1990–2026, from eloratings.net (verified against archived snapshots; see
  `data/elo/NOTES.md`). Ratings are *frozen at tournament start*: within-tournament form is
  deliberately not credited, so a team that "catches fire" mid-tournament shows up as positive
  residuals rather than a moving rating.
- **Results:** `data/worldcup-1930-2022/matches.csv` (552 matches 1990–2022) +
  `data/worldcup-2026/matches_2026.csv` (102 matches through the 2026 semi-finals). 654 total.
- **Referees:** `data/referee-teams/match_officials_*.csv`, joined on match_date + sorted
  normalized team pair (same ALIAS dict as `analysis/referee_comparison.py`); **654/654 joined**.
- **Expected score:** for team A vs B, `E_A = 1 / (1 + 10^(−(R_A − R_B)/400))`.
  All venues treated as neutral **except host nations, which get +100 Elo** (the standard
  eloratings.net home-advantage convention). Hosts: Italy 1990, USA 1994, France 1998,
  South Korea + Japan 2002, Germany 2006, South Africa 2010, Brazil 2014, Russia 2018,
  Qatar 2022, USA + Canada + Mexico 2026.
- **Actual score, primary convention (Elo methodology):** result at end of play (after extra
  time): win = 1, draw = 0.5, loss = 0. **A penalty shootout counts as a 0.5–0.5 draw** —
  this is how eloratings.net itself scores shootouts.
- **Secondary sensitivity ("shootout-as-win"):** shootout winner credited with a full win.
  Reported alongside because the project's `match_team_level.csv` codes shootout winners as
  `win = 1`.
- **Residual:** actual − expected, from Argentina's (or the named team's) perspective.
  A team's residual per tournament sums its per-match residuals.

## Step 3 results

### 3a. Era residuals: Argentina vs other elite teams

Total (and per-match) residual, shootout = 0.5 draw:

| Team | 1990–2018 (n) | 2022 (n) | 2026 so far (n) |
|---|---|---|---|
| **Argentina** | **+1.59** (40) · +0.040/m | **−0.72** (7) · −0.103/m | **+1.07** (7) · +0.153/m |
| Brazil | +0.50 (47) · +0.011/m | −0.82 (5) · −0.163/m | −0.15 (5) |
| England | −3.10 (35) · −0.089/m | +0.31 (5) | +0.56 (7) |
| France | +1.36 (32) · +0.042/m | +0.79 (7) · +0.113/m | +0.77 (7) · +0.110/m |
| Germany* | +3.28 (48) · +0.068/m | −0.39 (3) | −0.37 (4) |
| Spain | −1.91 (35) · −0.055/m | −1.13 (4) | +0.70 (7) |

*Germany includes West Germany 1990.

### 3b. Champion title runs (the direct comparison)

| Year | Champion | Residual (shootout=draw) | Residual (shootout=win) |
|---|---|---|---|
| 1990 | West Germany | +1.18 | +1.68 |
| 1994 | Brazil | +1.63 | +2.13 |
| 1998 | France | +0.98 | +1.48 |
| 2002 | Brazil | +2.85 | +2.85 |
| 2006 | Italy | +1.72 | +2.22 |
| 2010 | Spain | +0.45 | +0.45 |
| 2014 | Germany | +1.63 | +1.63 |
| 2018 | France | +2.03 | +2.03 |
| **2022** | **Argentina** | **−0.72** | **+0.28** |
| 2026 | Argentina (finalist; final not yet played) | +1.07 | +1.07 |

**Verdict: no, Argentina did not overperform Elo post-2022 more than other champions did.**
Argentina's 2022 title run is the **only negative-residual championship since 1990** under the
standard Elo convention (they entered as the world's top-rated team, lost to Saudi Arabia, and
won two knockout games on penalties, which Elo scores as draws). Even under the
shootout-as-win convention (+0.28) it is the *weakest* title-run overperformance of the ten.
Argentina's 2026 run so far (+1.07 through the semi-final) sits mid-pack — below Brazil 2002
(+2.85), France 2018 (+2.03), Italy 2006, Brazil 1994 and Germany 2014 (+1.6–1.7), and near
France 1998 (+0.98). France, for comparison, has out-run its Elo in *both* 2022 (+0.79) and
2026 (+0.77) without winning either... (2026 pending).

### 3c. Per-referee Argentina residuals + permutation test

**Permutation design:** null hypothesis = referee assignments are exchangeable within each
tournament × stage stratum (stages: group, round of 32, round of 16, quarter-finals,
semi-finals, third place, final). 10,000 stratified permutations; permutations **respect the
same-country constraint** (a referee is never assigned a match involving his own country;
0 repairs failed; the observed data also contains 0 such conflicts). For each permutation,
every referee's Argentina residual is rebuilt; p-values are Monte Carlo with the +1
correction. Two p-values are reported: one-sided positive (favoritism direction,
`P(T_perm ≥ T_obs)`) and two-sided centered on the null mean.

All referees with ≥2 Argentina matches (full table incl. one-match referees and per-match
detail in `elo_residuals_by_referee.csv`):

| Referee | n | Residual (pens=draw) | Residual (pens=win) | Null mean ± sd | p (one-sided pos) | p (two-sided) |
|---|---|---|---|---|---|---|
| **Szymon Marciniak** | 4 | **−0.27** | +0.23 | −0.22 ± 0.21 | **0.90** | **0.35** |
| Nicola Rizzoli | 3 | +0.01 | +0.01 | −0.30 ± 0.14 | 0.032 | 0.032 |
| Ravshan Irmatov | 3 | −0.87 | −0.87 | +0.03 ± 0.31 | 0.994 | 0.007 |
| Roberto Rosetti | 2 | +0.80 | +0.80 | +0.19 ± 0.25 | 0.032 | 0.032 |
| Frank De Bleeckere | 2 | +0.58 | +0.58 | +0.21 ± 0.25 | 0.073 | 0.073 |
| Daniele Orsato | 2 | +0.35 | +0.35 | +0.08 ± 0.23 | 0.047 | 0.094 |
| Cüneyt Çakır | 2 | +0.10 | +0.60 | −0.04 ± 0.16 | 0.150 | 0.231 |
| Michel Vautrot | 2 | −0.39 | +0.11 | +0.17 ± 0.29 | 0.970 | 0.085 |

**Marciniak spotlight.** His four Argentina matches: 2018 group vs Iceland (1–1; expected
0.78 → **−0.28**), 2022 R16 vs Australia (win; expected 0.92 → +0.08), **2022 final vs France
(3–3, won on penalties; end-of-play score 0.5 vs expected 0.69 → −0.19)**, 2026 group vs
Algeria (win; expected 0.88 → +0.12). Net: **−0.27** — Argentina *under*-performed its Elo in
Marciniak's matches under the standard convention; one-sided p = 0.90 is about as far from
"suspicious favoritism" as the statistic can get. Under shootout-as-win his total flips to
+0.23, still unremarkable (Argentina was the Elo favourite in all four matches; winning them
all would sum to only +0.63).

**On the three nominal p < 0.05 values.** Eight referees were tested with no multiplicity
correction; the smallest one-sided p (0.032) would need ≤ 0.006 to survive Bonferroni. Rizzoli
and Rosetti are also *pre-2014* referees, irrelevant to a post-2022 favoritism story, and
Rizzoli's p is a stratification artifact worth spelling out: finals are single-match strata, so
his 2014 final (Argentina lost to Germany, residual −0.42) is pinned in every permutation; his
"significant" p only says Argentina beat expectation in his two *movable* 2014 matches (wins
over Nigeria and Belgium). Irmatov shows the mirror image (p = 0.007 two-sided for
*under*-performance). Scattered small p-values in both directions across 42 referees are
exactly what noise looks like.

## Step 4 results: hierarchical referee×team model of yellow cards

### Model

- **Data:** 1,104 team-match rows, 1990–2022 (2026 is excluded — per-match card data for
  non-Argentina 2026 matches does not exist locally). 192 referees, 74 teams, **1,025
  referee×team pairs** (96% of pairs occur in only 1–2 matches; the maximum is 3).
- **Outcome:** yellow cards received per team-match (`match_team_level.csv`).
- **Fixed effects:** standardized team Elo, standardized opponent Elo, knockout flag,
  tournament year (categorical).
- **Random effects:** referee intercept, **team intercept**, referee×team interaction.
  The task specified referee + referee×team; the team intercept was added so a team's
  general card-proneness is not misattributed to all of its referee pairs. The exact 2-component
  spec model was also fitted as a sensitivity check (same verdict, smaller pair variance).
- **Implementation:** `statsmodels 0.14.6 PoissonBayesMixedGLM` fitted by variational Bayes
  (`fit_vb`). The default BFGS optimizer with random starts did **not** converge; refitting with
  L-BFGS-B and deterministic starting values (mean 0, sd 0.5) converges cleanly in ~5 s with no
  warnings, which is what the script uses. The two-stage empirical-Bayes fallback was therefore
  not needed (it remains in the script, documented, for robustness).

### Variance components (posterior)

| Component | sd | variance |
|---|---|---|
| referee | 0.161 | 0.0258 |
| team | 0.107 | 0.0115 |
| **referee×team pair** | **0.039** | **0.0015** |

(2-component spec model: referee sd 0.172, pair sd 0.017.) Fixed effects behave sensibly:
higher own Elo → fewer yellows (−0.096), stronger opponent → more (+0.090), knockout +0.157,
and the 2006 card spike (+0.47) and lenient 2014 (−0.15) show up as year effects.

**The referee×team variance is essentially zero** — about 6% of the referee variance and 13%
of the team variance. With at most 3 matches per pair, the data contain almost no evidence of
pair-specific behavior, and the model shrinks all 1,025 pair effects into the ±0.008 log-rate
band (rate ratios 0.995–1.009).

### Top-10 most extreme shrunk pairs (any team)

| Pair | n | Yellows | Expected* | Raw O/E | Shrunk rate ratio | Rank |
|---|---|---|---|---|---|---|
| Howard Webb · Netherlands | 1 | 9 | 3.35 | 2.69 | 1.008 | 1 |
| Antonio López Nieto · Germany | 1 | 8 | 2.50 | 3.20 | 1.008 | 2 |
| **Antonio Mateu Lahoz · Argentina** | 1 | 8 | 2.52 | 3.17 | 1.008 | 3 |
| Valentin Ivanov · Portugal | 1 | 9 | 3.78 | 2.38 | 1.008 | 4 |
| Antonio López Nieto · Cameroon | 1 | 8 | 2.84 | 2.81 | 1.008 | 5 |
| Antonio Mateu Lahoz · Netherlands | 1 | 8 | 2.97 | 2.69 | 1.008 | 6 |
| Fernando Rapallini · Serbia | 1 | 7 | 2.02 | 3.47 | 1.007 | 7 |
| Jan Wegereef · Senegal | 1 | 7 | 2.66 | 2.63 | 1.007 | 8 |
| Carlos Simon · Italy | 2 | 8 | 3.82 | 2.10 | 1.006 | 9 |
| Ben Williams · Costa Rica | 1 | 6 | 1.96 | 3.05 | 1.006 | 10 |

*Expected = model prediction from fixed effects + referee + team components, excluding the pair effect.

The list is a catalogue of famous single-match card explosions (Webb's 2010 final; Mateu
Lahoz's Argentina–Netherlands 2022 quarter-final appears **twice**, once from each team's side).

### Where the Argentina pairs land

All 36 Argentina pairs are in `hierarchical_pairs.csv`. Highlights:

- **Mateu Lahoz · Argentina** is the most extreme Argentina pair: rank **3 of 1,025**, raw
  O/E = 3.17 (8 yellows vs 2.5 expected, the 2022 QF vs Netherlands) — but the shrunk rate
  ratio is **1.008**, statistically indistinguishable from 1 (z ≈ 0.21). One match cannot
  establish a pair effect.
- **Marciniak · Argentina**: 3 matches (1990–2022 window), 5 yellows vs 4.96 expected,
  raw O/E = **1.01**, rank **1,001 of 1,025** — as close to perfectly neutral as the data allow.
- Other multi-match Argentina pairs (Irmatov O/E 0.96, Rizzoli 0.65, Orsato 0.86, Çakır 1.17,
  De Bleeckere 1.36, Rosetti 0.24, Vautrot 1.77) scatter both sides of 1.

**Verdict: after shrinkage against all pairs, no Argentina–referee pair is an outlier.** The
only Argentina pair with an extreme *raw* signal is a single match (Mateu Lahoz 2022), which
the model — correctly — refuses to treat as evidence of a pair-level pattern.

## Honest caveats

1. **Power is very low everywhere.** Referees see at most 4 Argentina matches (Marciniak);
   96% of referee×team pairs are 1–2 matches. Neither analysis can detect anything but an
   enormous effect. Null results here mean "no evidence", not "proof of innocence".
2. **Elo residuals measure results, not officiating.** A referee can shape a match (a soft
   penalty, an uncalled red) without flipping the result — and Elo residuals also absorb pure
   form/luck (injuries, in-tournament improvement, shootout variance). Conversely,
   **uncalled incidents are invisible** in the card model: a referee who favors a team by
   *not* carding it or *not* penalizing its opponents' complaints leaves no trace in yellows
   received. These analyses test result- and card-level anomalies only.
3. **Revised-Elo caveat** (from `data/elo/NOTES.md`): eloratings.net has retroactively revised
   historical ratings; contemporary 2010/2014 snapshots run ~20–30 points below today's values.
   The CSV deliberately uses the current revised series for internal consistency. A 25-point
   shift in one team's rating moves a single-match expected score by ~0.036 — small, and it
   cannot manufacture referee-specific patterns, but pre-2018 residuals are not exactly what
   contemporaries would have computed.
4. **Finals are pinned.** Tournament×stage strata make finals single-match strata, so final
   assignments never vary under the null. Marciniak's 2022 final and Rizzoli's 2014 final
   residuals are constants in their null distributions (this is why null means are non-zero and
   why the two-sided p is centered).
5. **Referee assignment is not random.** FIFA weighs confederation balance, experience and
   perceived form. The permutation respects the same-country constraint but not confederation
   conventions; "significant" deviations could reflect assignment policy (better referees get
   bigger matches) rather than bias.
6. **2026 is incomplete**: results through the semi-finals (2026-07-15); the final had not been
   played at data-fetch time. Argentina's 2026 residual (+1.07) will move with the final.
   Multiple testing: 42 referees have ≥1 Argentina match; no correction is applied to the
   tabulated p-values.
7. **VB approximation.** Mean-field variational Bayes is known to underestimate posterior
   uncertainty; the pair-variance posterior sd (log-sd ±0.02) is likely optimistic. The
   qualitative conclusion (pair variance an order of magnitude below referee/team variance)
   is robust across the 2- and 3-component fits, but exact posterior sds should not be
   over-read.
8. **Host bump is a convention.** +100 for hosts is the standard eloratings.net figure, not
   estimated from these data. Argentina played a host exactly twice in-window (1990 SF vs
   Italy, 2006 QF vs Germany — both shootouts, scored 0.5 each way). The bump lowers
   Argentina's expected score in those two matches and therefore *raises* its measured
   residual there; dropping the convention would shave a little off Argentina's 1990–2018
   aggregate. No 2022/2026 Argentina match involved a host, so the headline eras are
   untouched.

## Bottom line

- Argentina's 2022 title run *under*-performed its pre-tournament Elo (−0.72; the only
  negative champion run since 1990), and its 2026 run so far (+1.07) is mid-pack among
  champions' runs. The "post-2022 Argentina outruns its rating" premise is not supported —
  France has overrun its Elo by more in the same window without winning.
- No referee shows a significant positive Argentina residual once stratified permutation and
  multiplicity are taken seriously. Marciniak's is *negative* (−0.27, p₊ = 0.90).
- The hierarchical card model finds essentially zero referee×team variance; no Argentina pair
  is an outlier after shrinkage. The loudest raw signal (Mateu Lahoz, 8 yellows, 2022 QF) is a
  single match and shrinks to a rate ratio of 1.008.
