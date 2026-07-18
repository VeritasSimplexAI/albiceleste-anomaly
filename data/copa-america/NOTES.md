# Copa América data — sources and coverage notes

Compiled 2026-07-17. All data collected from the public sources listed below; nothing is estimated or fabricated. Blank cells mean the source does not publish that value (details per deliverable below).

## Argentina title count (verified against multiple sources)

**Argentina have 16 Copa América titles — the outright record** (one more than Uruguay's 15):
1921, 1925, 1927, 1929, 1937, 1941, 1945, 1946, 1947, 1955, 1957, 1959 (Argentina edition), 1991, 1993, 2021, 2024.

Verified against:
- [Argentina at the Copa América (Wikipedia)](https://en.wikipedia.org/wiki/Argentina_at_the_Copa_Am%C3%A9rica) — full edition-by-edition record.
- [Copa América (Wikipedia)](https://en.wikipedia.org/wiki/Copa_Am%C3%A9rica) — "Argentina have the most championships in the tournament's history, with 16 cups."
- News confirmation of the 16th title after the 2024 final: [Al Jazeera](https://www.aljazeera.com/news/2024/7/15/argentina-win-record-16th-copa-america-in-match-marred-by-crowd-chaos), [VOA](https://www.voanews.com/a/argentina-wins-record-16th-copa-america-title-beats-colombia-1-0/7698354.html).
- Note: RSSSF's overview page ([rsssf.org](https://www.rsssf.org/tabless/sachampfull.html)) is only updated through 2007 (it says 14 titles each for Argentina and Uruguay as of then); it agrees with the pre-2021 count but is not current.

## Deliverable 1 — copa_record.csv (48 rows, complete)

- One row per edition, 1916–2024. 1959 appears twice (two official editions that year: Argentina and Ecuador). Total editions: 48.
- Argentina entered every edition except: **1939 (withdrew), 1949 (withdrew), 1953 (did not enter), 2001 (withdrew days before kickoff over security/terrorism concerns)** — those rows have blank match stats.
- 1975, 1979, 1983 had no host country (played home-and-away throughout the year); host is recorded as "None (home-and-away basis)".
- Primary source: [Argentina at the Copa América (Wikipedia)](https://en.wikipedia.org/wiki/Argentina_at_the_Copa_Am%C3%A9rica). Host countries were cross-checked against the [main Copa América article](https://en.wikipedia.org/wiki/Copa_Am%C3%A9rica) (the initial extraction had host errors for 1925, 1926, 1939, 1946 — corrected to Argentina, Chile, Peru, Argentina respectively).
- Spot-check: the 1989 row (7 matches, W2 D3 L2, GF2 GA4, third place) was verified for internal consistency against the [1989 edition article](https://en.wikipedia.org/wiki/1989_Copa_Am%C3%A9rica) and [RSSSF 1989](https://www.rsssf.org/tables/89sa.html).

## Deliverable 2 — copa_squad_discipline.csv (66 rows)

Per-team, per-edition squad discipline from FBref (Squad Miscellaneous Stats + Squad Standard Stats). Live fbref.com returns HTTP 403 to non-browser clients, so all data was taken from **Wayback Machine snapshots** of FBref pages (snapshot URLs are in each row's `source_url`; the paired snapshots are listed below).

| Edition | Teams | Fouls | Cards | PK won/conceded | PK attempted | Snapshots used |
|---|---|---|---|---|---|---|
| 2015 | 12 | yes | yes | yes | yes | [misc](https://web.archive.org/web/20200914233006/https://fbref.com/en/comps/685/10341/misc/2015-Copa-America-Stats), [standard](https://web.archive.org/web/20200920130909/https://fbref.com/en/comps/685/10341/stats/2015-Copa-America-Stats) |
| 2016 | 16 | yes | yes | blank (see below) | yes | [misc (German-language mirror)](https://web.archive.org/web/20200903013137/https://fbref.com/de/comps/685/10342/misc/2016-Copa-America-Centenario-Stats), [standard](https://web.archive.org/web/20200819080112/https://fbref.com/en/comps/685/10342/stats/2016-Copa-America-Centenario-Stats) |
| 2019 | 12 | yes | yes | blank (FBref leaves the cells empty) | yes | [misc](https://web.archive.org/web/20200928140837/https://fbref.com/en/comps/685/10343/misc/2019-Copa-America-Stats), [standard](https://web.archive.org/web/20200918142521/https://fbref.com/en/comps/685/10343/stats/2019-Copa-America-Stats) |
| 2021 | 10 | blank (see below) | yes | blank (see below) | yes | [standard, complete, captured Nov 2022](https://web.archive.org/web/20221128020519/https://fbref.com/en/comps/685/stats/Copa-America-Stats) |
| 2024 | 16 | yes | yes | yes | yes | [misc](https://web.archive.org/web/20250714165820/https://fbref.com/en/comps/685/misc/Copa-America-Stats), [standard](https://web.archive.org/web/20250714163610/https://fbref.com/en/comps/685/stats/Copa-America-Stats) |

Known gaps and caveats:
- **2021 fouls/penalties-won**: the only archived snapshot of the 2021 misc page was captured mid-tournament ([2021-07-03](https://web.archive.org/web/20210703064843/https://fbref.com/en/comps/685/misc/Copa-America-Stats)) and covers the **group stage only** (4 matches per team). Rather than mix 4-match foul counts with 7-match totals, those cells are blank in the CSV. Group-stage-only values from that snapshot, if you want them: Argentina Fls 43 / Fld 69 / PKwon 1 / PKcon 1; Bolivia 36/36/0/1; Brazil 45/59/1/0; Chile 54/48/1/1; Colombia 61/52/1/0; Ecuador 62/42/0/0; Paraguay 65/39/1/2; Peru 52/58/0/1; Uruguay 52/47/1/0; Venezuela 52/47/0/1. 2021 matches_played, cards, and PKatt come from the complete post-tournament standard-stats snapshot.
- **2016 penalties won/conceded**: FBref displays 0 for every team, which contradicts its own PKatt column (Chile 1, Colombia 1, USA 1, Venezuela 2). Treated as not published; left blank.
- **Card/foul totals for 2015 and 2016 look undercounted vs official CONMEBOL records** (e.g., FBref credits Argentina with 1 yellow across the whole 2016 tournament, and Paraguay with 1 yellow in 2015). FBref's pre-2018 tournament event data has partial coverage. The values in the CSV are exactly what FBref publishes — use with caution for cross-era comparisons; 2019/2021/2024 look complete.
- Red cards (`CrdR`) follow FBref's convention and include second-yellow dismissals.
- FBref has no squad-stats pages for Copa América editions before 2015.

## Deliverable 3 — copa_referees_finals.csv (21 rows)

- Final referees for the last 10 editions (1999–2024), from each edition's Wikipedia article or dedicated final article.
- Argentina's per-match referees for all of 2021 (7 matches) and 2024 (6 matches). These were extracted directly from the raw HTML of the Wikipedia group/knockout-stage pages (`Referee:` line in each match box) rather than summarized, so they are exact. Note: an initial automated read misattributed the Bolivia 1–4 Argentina (2021) referee as Diego Haro; direct extraction shows it was **Andrés Rojas (Colombia)** (Haro refereed Paraguay–Bolivia).
- The 2021 and 2024 finals are Argentina matches and appear once each (in the finals block).

## VAR in the Copa América

- **VAR was used at the Copa América for the first time at the 2019 edition in Brazil.** CONMEBOL had earlier introduced VAR in its club competitions (Copa Libertadores/Sudamericana, 2018 — [Football Legal](https://www.football-legal.com/content/conmebol-has-implemented-the-video-assistant-referee-var-during-copa-libertadores-2018-and-copa-sudamericana-2018)), but 2019 was the first national-team Copa with it ([referee appointments with VAR roles, 2019](http://refereeingworld.blogspot.com/2019/03/conmebol-copa-america-2019.html)).
- Editions in this dataset with VAR: 2019, 2021, 2024. Without: 2015, 2016 and everything earlier.

## Officiating controversies involving Argentina (2021 / 2024)

- **2024 — Chile's formal complaint over the Argentina match**: after group-stage elimination, Chile's federation asked CONMEBOL to suspend officials for "gross errors", explicitly including Uruguayan referee Andrés Matonte's performance in Chile 0–1 Argentina (and Wilmar Roldán in Chile–Canada). Covered by [ESPN](https://www.espn.com/soccer/story/_/id/40470611/chile-copa-america-ref-suspended-errors).
- **2021 — no significant officiating controversy involving Argentina** was found in major-press coverage; the final (Ostojich) was widely regarded as well-officiated. Related context from the previous edition: after the 2019 semi-final loss to Brazil, Messi publicly alleged refereeing "corruption" and was suspended by CONMEBOL — see [OCCRP summary](https://www.occrp.org/en/news/lionel-messi-alleges-corruption-in-copa-america). That incident belongs to 2019, not 2021.
- The 2024 final's chaotic delayed kickoff in Miami was a crowd-control/security failure, not an officiating issue ([Al Jazeera](https://www.aljazeera.com/news/2024/7/15/argentina-win-record-16th-copa-america-in-match-marred-by-crowd-chaos)).

## File inventory

| File | Rows (excl. header) | Coverage |
|---|---|---|
| copa_record.csv | 48 | every edition 1916–2024 |
| copa_squad_discipline.csv | 66 | all teams, 2015/2016/2019/2021/2024 |
| copa_referees_finals.csv | 21 | finals 1999–2024 + all Argentina matches 2021 & 2024 |
