# Player-level defensive & discipline stats (tackle-vs-foul study)

**File:** `player_defense.csv` — one row per player per tournament, all players of all teams.
**Tournaments:** FIFA World Cup 2018, 2022, 2026 (through the semifinals) and Copa América 2019, 2021, 2024.
**Rows:** 3,119 total — WC 2018: 604 · WC 2022: 680 · WC 2026: 1,035 (48-team format) · Copa 2019: 228 · Copa 2021: 233 · Copa 2024: 339.
**Built:** 2026-07-17. All data parsed programmatically from Wayback Machine snapshots of FBref pages (live FBref returns 403; several pages were freshly captured with Save Page Now on 2026-07-17). FBref tables that sit inside HTML comments were un-commented before parsing; cells were read by their `data-stat` attributes.

## Definitions (Opta, as used by FBref)

- **Tackles (Tkl):** attempts to dispossess an opponent by tackling the ball-carrier — includes both won and lost tackles.
- **Tackles won (TklW):** tackles in which the tackler's team ended with possession of the ball.
- **Challenges Att:** number of times the player contested an opposing dribbler (dribbles challenged).
- **Challenges Lost:** challenges where the dribbler got past the challenger (unsuccessful attempts to challenge a dribbling player).
- **Fouls (Fls) / Fouled (Fld):** fouls committed / fouls drawn. **CrdY / CrdR:** yellow / red cards (CrdY does not double-count second yellows; a second yellow appears as a red).
- 2018-era FBref data was originally StatsBomb; FBref has since replaced historical international-tournament data with a basic feed (see coverage gaps below).

## Sources (Wayback snapshots)

| Tournament | Page | Snapshot (capture date) |
|---|---|---|
| WC 2018 | standard | https://web.archive.org/web/20250519020101/https://fbref.com/en/comps/1/2018/stats/2018-FIFA-World-Cup-Stats (2025-05-19) |
| WC 2018 | defense | https://web.archive.org/web/20260606150656/https://fbref.com/en/comps/1/2018/defense/2018-FIFA-World-Cup-Stats (2026-06-06) |
| WC 2018 | misc | https://web.archive.org/web/20260716203607/https://fbref.com/en/comps/1/2018/misc/2018-FIFA-World-Cup-Stats (2026-07-16) |
| WC 2022 | standard | https://web.archive.org/web/20260716203513/https://fbref.com/en/comps/1/2022/stats/2022-FIFA-World-Cup-Stats (2026-07-16) |
| WC 2022 | defense | https://web.archive.org/web/20241213210916/https://fbref.com/en/comps/1/defense/World-Cup-Stats (2024-12-13; final 2022 data with FULL Opta detail — see gaps) |
| WC 2022 | misc | https://web.archive.org/web/20260716203158/https://fbref.com/en/comps/1/2022/misc/2022-FIFA-World-Cup-Stats (2026-07-16) |
| WC 2026 | standard | https://web.archive.org/web/20260717104029/https://fbref.com/en/comps/1/2026/stats/2026-FIFA-World-Cup-Stats (2026-07-17, SPN) |
| WC 2026 | defense | https://web.archive.org/web/20260717103842/https://fbref.com/en/comps/1/2026/defense/2026-FIFA-World-Cup-Stats (2026-07-17, SPN) |
| WC 2026 | misc | https://web.archive.org/web/20260716203655/https://fbref.com/en/comps/1/2026/misc/2026-FIFA-World-Cup-Stats (2026-07-16) |
| Copa 2019 | standard | https://web.archive.org/web/20200918142521/https://fbref.com/en/comps/685/10343/stats/2019-Copa-America-Stats (2020-09-18) |
| Copa 2019 | defense | https://web.archive.org/web/20260717104245/https://fbref.com/en/comps/685/2019/defense/2019-Copa-America-Stats (2026-07-17, SPN) |
| Copa 2019 | misc | https://web.archive.org/web/20200928140837/https://fbref.com/en/comps/685/10343/misc/2019-Copa-America-Stats (2020-09-28) |
| Copa 2019 | misc (cross-check) | https://web.archive.org/web/20260717115232/https://fbref.com/en/comps/685/2019/misc/2019-Copa-America-Stats (2026-07-17, SPN) |
| Copa 2021 | standard | https://web.archive.org/web/20221128020519/https://fbref.com/en/comps/685/stats/Copa-America-Stats (2022-11-28) |
| Copa 2021 | defense | https://web.archive.org/web/20260717104544/https://fbref.com/en/comps/685/2021/defense/2021-Copa-America-Stats (2026-07-17, SPN) |
| Copa 2021 | misc | https://web.archive.org/web/20260717104620/https://fbref.com/en/comps/685/2021/misc/2021-Copa-America-Stats (2026-07-17, SPN) |
| Copa 2024 | standard | https://web.archive.org/web/20241211180007/https://fbref.com/en/comps/685/stats/Copa-America-Stats (2024-12-11) |
| Copa 2024 | defense | https://web.archive.org/web/20250714170127/https://fbref.com/en/comps/685/defense/Copa-America-Stats (2025-07-14) |
| Copa 2024 | misc | https://web.archive.org/web/20250714165820/https://fbref.com/en/comps/685/misc/Copa-America-Stats (2025-07-14) |

The `source_url` column in the CSV carries the tournament's **defense-page** snapshot; minutes/position come from the standard page and fouls/cards from the misc page listed above.

### 2026 cutoff
All three 2026 pages were captured **after the semifinals** (SF played 2026-07-14/15; misc captured 2026-07-16, stats & defense 2026-07-17), i.e. through 102 matches. Third-place match and final are NOT included.

## Join method

- Each FBref page carries its player table inside an HTML comment; comments were stripped and tables located by id (`stats_standard`, `stats_defense`, `stats_misc`), cells read via `data-stat` attributes (handles both the old-era names `dribbles_vs`/`dribbled_past` and the current `challenges`/`challenges_lost`).
- The three tables were joined per tournament on (accent-stripped lower-cased player name, team). Because snapshots span FBref eras, 20 player-name spelling variants (e.g. "Idrissa Gueye" ↔ "Idrissa Gana Gueye", "Ederson" ↔ "Ederson Moraes", "Jhon Durán" ↔ "Jáder Durán") were aliased after verifying each pair co-occurs on the same team with complementary columns. After aliasing, **every row has all three sources joined (0 unmatched rows in all six tournaments)**.
- FBref team names were mapped to the names used elsewhere in this repo: IR Iran→Iran, Korea Republic→South Korea, Czechia→Czech Republic, Türkiye→Turkey, Cabo Verde→Cape Verde, Côte d'Ivoire→Ivory Coast, Congo DR→DR Congo, Bosnia–Herz→Bosnia and Herzegovina.
- `position` is FBref's Pos column verbatim (GK/DF/MF/FW combos such as "FW,MF").

## Quality checks

**(a) Player-sum fouls vs squad-level fouls** (`data/processed/squad_discipline_clean.csv` for WC, `data/copa-america/copa_squad_discipline.csv` for Copa):

| Tournament | Exact match | Notes |
|---|---|---|
| WC 2018 | 7/32 | Deltas 0–4 fouls; 31/32 teams within ±3. Verified FBref-internal: the squads table and the sum of player rows disagree **on the same FBref page** for 25/32 teams (basic-feed bookkeeping quirk). Yellows match 32/32 exactly. |
| WC 2022 | 31/32 | Only France off (players 68 vs squad 69), again FBref-internal on the same page. |
| WC 2026 | 48/48 | Perfect. |
| Copa 2019 | 12/12 | Perfect. |
| Copa 2021 | n/a | Squad file has no fouls for 2021 (its snapshot lacked them). Player-level fouls are newly provided here; yellow cards match the squad file 10/10 exactly. |
| Copa 2024 | 16/16 | Perfect. |

Yellow-card cross-check: 2018 32/32, 2026 48/48, Copa 2021 10/10, Copa 2024 16/16 exact. WC 2022: 29/32 — Argentina (players 17 vs squad 19), Serbia (11 v 12), South Korea (6 v 7); FBref's squad CrdY totals include cards not attributed to any player row (bench/staff cards), visible on FBref's own page.

**(b) Argentina roster:** Messi present in all six tournaments. Argentina 2026 player sums (fouls 88, yellows 9, reds 0) match `data/worldcup-2026/argentina_matches_cards_2026.csv` match-by-match totals exactly.

**(c) Row counts:** WC 604/680/1,035 (2026 is a 48-team tournament, hence above the ~600–750 range of 32-team editions), Copa 228/233/339 — all in expected ranges.

**Cross-era validation (Copa 2019):** player-level fouls/CrdY/CrdR from the 2020-era snapshot agree 100% (228/228 players, zero diffs) with a freshly captured 2026-era page — strong evidence the player-level data is stable and correct.

## Known gaps & caveats

1. **Total tackles and challenges are only available for WC 2022 and Copa 2024.** FBref has replaced its historical advanced data for international tournaments with a basic feed: the current defense pages for WC 2018, Copa 2019, Copa 2021 and WC 2026 carry **only TklW (tackles won)** (plus interceptions). For those four tournaments `tackles`, `challenges_att`, `challenges_lost` are empty and `tackles_won` is the usable tackle measure. Exhaustive Wayback searches (year-form, season-id-form, current-form URLs, and de/es/fr/it/pt language mirrors) found **no archived full-data versions** — the WC 2022 full table survives only in the 2024-12-13 current-URL snapshot used here, and even the live 2022 year-form page has since been degraded to TklW-only (verified via a fresh 2026-07-17 capture).
2. **Consequence for the study:** a like-for-like "tackles vs fouls" comparison across all six tournaments must use `tackles_won` (available everywhere); `tackles`/`challenges` support a deeper 2022-vs-2024 analysis only.
3. **`copa_squad_discipline.csv` 2019 yellow_cards look wrong.** Its values (e.g. Argentina 2) come from the old FBref squads table, which is internally inconsistent with FBref's own player rows (sum 19; identical in both 2020-era and 2026-era pages). Its Argentina 2019 red_cards=0 also contradicts Messi's red card (present here). Player-level values in this file should be preferred for 2019 cards.
4. Minutes for WC 2026 reflect the 2026-07-17 stats snapshot (through the semifinals); they will not include the third-place match/final.
5. Squad-level totals used in check (a) for WC 2018/2022/2026 come from the same FBref snapshots as the squad files' `source_url`s, so mismatches there are FBref-internal, not snapshot-era artifacts.
