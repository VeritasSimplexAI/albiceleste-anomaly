# Within-referee bias analysis: does the same referee treat Argentina differently?

Script: `analysis/within_referee.py` · Output table: `data/processed/within_referee_results.csv`
Compiled 2026-07-17.

## Question

Cross-referee comparisons ("Argentina wins more with referee X") are confounded by each
referee's personal style — some officials simply show more cards than others, and FIFA does
not assign referees to matches at random. The fix here: use **each referee as his own
control**. For every referee we compare how he officiated *Argentina's matches* against how
he officiated *his other World Cup matches*. Personal style cancels out by construction.

## Data and join

- **Officiating crews:** `data/referee-teams/match_officials_1990_2010.csv` +
  `match_officials_2014_2026.csv` (main `referee` column only).
- **Per-team-per-match outcomes:** `data/processed/match_team_level.csv` (fjelstul academic
  dataset): yellow cards received (`yellows`) and converted penalties scored (`pen_goals`).
- **Join:** match_date + sorted normalized team pair, with the same small team-name ALIAS
  dict used in `analysis/referee_comparison.py`.
- **Join rate: 552/552 matches (100%) for 1990–2022.** 1,104 team-match rows, 192 distinct
  referees, 47 Argentina team-rows (Argentina played 47 matches 1990–2022).
- **Scope: 1990–2022 only.** Per-match cards for non-Argentina 2026 matches are not
  available locally, so 2026 cannot enter a within-referee model (no control group). It is a
  descriptive appendix below.

## Method

### 1. Pooled within-referee Poisson model

One row per team per match; outcome = yellow cards that team received (then repeated for
converted penalties it scored):

```
yellows ~ C(referee) + is_arg + is_arg_opponent + knockout + C(year)
```

Referee fixed effects make `is_arg` (Argentina's own rows) and `is_arg_opponent` (rows of
teams playing *against* Argentina) **within-referee** estimates. Year fixed effects absorb
era-wide card inflation; `knockout` absorbs stage intensity. Standard errors are
cluster-robust by match (each match contributes two correlated rows; 552 clusters). Design
matrix is full rank (203/203 — identifiable because 53 referees span 2+ tournaments). For
the penalties model, the 100 referees with zero converted penalties in *all* their matches
are dropped (standard fixed-effects Poisson practice; those groups carry no information).

### 2. Per-referee table

For every referee with **≥2 Argentina matches and ≥4 total matches** (6 qualify): his
card/penalty rate in Argentina matches (both directions — cards *to* Argentina and cards
*to Argentina's opponents*) vs his rate per team-match in his other matches. Significance
via **exact conditional Poisson tests** (binomial conditioning on the summed count), then
**Benjamini–Hochberg FDR across referees** within each test family. No referee is labeled
"biased" — we report effect sizes and p/q-values and let FDR speak.

## Results — pooled model

**Yellow cards** (n = 1,104 rows, 552 match clusters):

| term | IRR | 95% CI | p |
|---|---|---|---|
| `is_arg` (cards to Argentina) | 1.186 | [0.947, 1.485] | 0.138 |
| `is_arg_opponent` (cards to ARG's opponents) | **1.311** | [1.076, 1.597] | **0.007** |
| `knockout` | 1.172 | [1.058, 1.298] | 0.002 |
| contrast: opponent − Argentina | 1.106 | [0.855, 1.430] | 0.443 |

Reading: with the *same referee*, in the *same tournament*, at the *same stage*, teams
playing against Argentina pick up **~31% more yellow cards** than teams in that referee's
other matches (p = 0.007). But Argentina itself also picks up ~19% more (p = 0.138), and the
**directly bias-relevant contrast — opponents vs Argentina — is only IRR 1.11, p = 0.44,
not significant.** The defensible summary is that *Argentina's matches are cardier for
everyone on the pitch, slightly more so for the opponent*. That pattern is at least as
consistent with Argentina matches being higher-intensity/higher-stakes (and with
Argentina's possession style drawing fouls) as with referees favoring Argentina.

**Converted penalties** (n = 634 rows after dropping 100 zero-penalty referees):

| term | IRR | 95% CI | p |
|---|---|---|---|
| `is_arg` | 1.254 | [0.582, 2.701] | 0.564 |
| `is_arg_opponent` | 1.097 | [0.412, 2.924] | 0.853 |
| contrast: opponent − Argentina | 0.875 | [0.334, 2.290] | 0.786 |

No evidence either way — and honestly, this model cannot detect anything but an enormous
effect: only 131 converted penalties exist in 1990–2022, Argentina scored a handful. The
point estimate (Argentina converting ~25% more penalties per match under a given referee
than his other teams) has a CI spanning "half as many" to "nearly triple". Treat as
uninformative, not as exoneration.

## Results — per-referee (6 referees qualify: ≥2 ARG matches, ≥4 total)

Cards (rates per match; "other" = per team-match in his non-Argentina matches):

| Referee | Years | ARG m. | Other m. | Cards to ARG | Cards to opp | Other rate | IRR (ARG) | p | IRR (opp) | p |
|---|---|---|---|---|---|---|---|---|---|---|
| Nicola Rizzoli | 2014 | 3 | 1 | 1.00 | 2.00 | 2.00 | 0.50 | 0.45 | 1.00 | 1.00 |
| Ravshan Irmatov | 2010–2018 | 3 | 8 | 2.00 | 2.00 | 1.94 | 1.03 | 1.00 | 1.03 | 1.00 |
| Szymon Marciniak | 2018–2022 | 3 | 2 | 1.67 | 1.67 | 1.75 | 0.95 | 1.00 | 0.95 | 1.00 |
| Cüneyt Çakır | 2014–2018 | 2 | 4 | 2.00 | 2.00 | 2.00 | 1.00 | 1.00 | 1.00 | 1.00 |
| Frank De Bleeckere | 2006–2010 | 2 | 5 | 3.00 | 2.00 | 2.50 | 1.20 | 0.63 | 0.80 | 1.00 |
| Roberto Rosetti | 2006–2010 | 2 | 4 | 0.50 | 2.00 | 1.88 | 0.27 | 0.22 | 1.07 | 1.00 |

Converted penalties: Marciniak's Argentina matches contained 1 converted penalty *by*
Argentina (Messi, 2022 final) and 2 *against* (both Mbappé, 2022 final) vs zero in his
other matches (p = 0.43 and 0.18 respectively, q = 1.0 / 0.6). All other qualifying
referees: 0 penalties either way in their Argentina matches.

**After Benjamini–Hochberg FDR across referees: nothing survives in any test family
(all q ≥ 0.45).** The headline names behave almost identically with and without Argentina:

- **Marciniak** (ARG matches: Iceland '18, Australia '22, France '22 final): 1.67
  cards/match to Argentina and 1.67 to opponents, vs 1.75 per team-match in his other
  matches — IRR 0.95 both directions, p = 1.0. His penalty numbers are entirely the 2022
  final, where he gave more (2 v 1 converted) *against* Argentina than for them.
- **Irmatov** (11 matches, most of any qualifier): 2.00 vs 1.94 — IRR 1.03, p = 1.0.
- **Rizzoli** carded Argentina *half* as often as his baseline (IRR 0.50) but that is 3
  cards vs a 1-match control, p = 0.45.
- **Çakır**: exactly at his own baseline (IRR 1.00).

## Appendix — Argentina 2026 (descriptive only)

Per-match cards for other 2026 matches are unavailable, so there is no within-referee
control; these are raw facts, not evidence:

| Date | Opponent | Referee | Cards ARG | Cards opp | Fouls | Pens awarded |
|---|---|---|---|---|---|---|
| Jun 16 | Algeria | Szymon Marciniak | 0Y | 0Y | 13–8 | 0–0 |
| Jun 22 | Austria | Amin Omar | 2Y | 2Y | 13–13 | 1–0 |
| Jun 27 | Jordan | István Kovács | 0Y | 3Y | 7–13 | 1–0 |
| Jul 3 | Cape Verde | Drew Fischer | 1Y | 1Y | 13–12 | 0–0 |
| Jul 7 | Egypt | François Letexier | 0Y | 4Y | 13–11 | 1–0 |
| Jul 11 | Switzerland | João Pinheiro | 3Y | 1Y+1R | 14–18 | 0–0 |
| Jul 15 | England | Ismail Elfath | 3Y | 1Y | 15–11 | 0–0 |

Argentina: 9 yellows received, 12Y+1R for opponents, 3 penalties awarded for / 0 against
across 7 matches. Marciniak's Algeria match (0 cards total, vs his 1.70 cards/team-match
1990–2022 baseline) and Elfath's England match sit within their historical ranges given
single-match noise.

## Honest caveats

1. **Tiny n.** Argentina played 47 matches in 1990–2022 under 36 distinct referees; only 6
   referees have even 2+ Argentina matches, and the biggest control group is Irmatov's 8
   matches. Per-referee tests are severely underpowered — a real 2× effect would usually
   not reach significance here. Absence of evidence ≠ evidence of absence.
2. **Uncalled-incident selection bias.** Cards measure *called* fouls, penalties measure
   *awarded* incidents. A referee who favors a team by *not* calling incidents (waving off a
   penalty appeal, not showing a deserved second yellow) is invisible in this data. Concrete
   example of the sibling problem: `pen_goals` counts only *converted* penalties — Messi's
   missed penalty vs Iceland (2018, Marciniak) does not appear anywhere in the model.
3. **Non-random assignment.** FIFA assigns referees deliberately (confederation rules,
   perceived big-match competence). Referee FE handles level differences, but if a referee
   is *specifically* given Argentina's hardest matches, his "other matches" are not a
   perfect counterfactual. Year and knockout controls mitigate, not eliminate, this.
4. **Opponent mix and outlier matches.** `is_arg_opponent` pools all of Argentina's
   opponents; a single explosive match (the 2022 Netherlands quarter-final under Lahoz:
   8 yellows to *each* side — Lahoz has only 1 ARG match so is not in the per-referee
   table but is in the pooled model) pushes both coefficients up without saying anything
   about how referees treat *Argentina* specifically.
5. **Two rows per match are correlated** (a fiery match yields cards for both sides) —
   handled with cluster-robust SEs by match, but the point estimates still reflect
   match-level intensity, which is why the opponent-vs-Argentina *contrast* (p = 0.44) is
   the right headline number, not the raw opponent coefficient (p = 0.007).
6. **Penalties-awarded incident data** (`data/penalties-historical/`) covers 1930–2010 only
   and was not merged into the per-referee table to keep one consistent outcome definition
   (converted pens, 1990–2022) across all referees.

## Bottom line

Within-referee, the same officials who worked Argentina's matches showed **no detectable
tilt toward Argentina**: the Argentina-vs-opponent card contrast is small and insignificant
(IRR 1.11, p = 0.44), the penalty model is uninformative, and **no individual referee —
including Marciniak, Irmatov, Rizzoli and Çakır — survives FDR correction**; their
within-referee card rates in Argentina matches are all within ±7% of their own baselines
except in trivially small samples. What the data does show is that Argentina's matches
produce more cards overall — a match-intensity story, not a referee-bias story.
