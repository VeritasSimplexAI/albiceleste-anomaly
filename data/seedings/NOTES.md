# Draw Seedings & Pre-Tournament FIFA Rankings — Sources and Notes

Compiled 2026-07-17. Covers FIFA Men's World Cups 1990–2026.

## Files

- `draw_pots.csv` — one row per team per tournament: official final-draw pot, and whether the
  team was officially seeded (Pot 1 / "top-seeded" pot). 320 rows (24+24+32×7+48).
- `fifa_rankings_pre.csv` — one row per participating team per tournament 1994–2026: the team's
  position in the **last FIFA World Ranking published before the tournament's opening match**.
  296 rows (24+32×7+48).

## Pot-number mapping convention

`pot` is always an integer with **pot 1 = the officially seeded pot** (hosts/holders/top seeds).
Where a tournament's own labels differ, the mapping is documented per tournament below.
`seeded = yes` exactly for pot-1 rows.

## Team-name convention

Names match the project convention (fjelstul `teams.csv` / `worldcup-2026` files):
"West Germany" (1990), "United States", "South Korea", "Republic of Ireland", "Ivory Coast",
"Turkey", "Cape Verde", "Curaçao", "DR Congo", "Czech Republic".
"FR Yugoslavia" (1998 on Wikipedia) is recorded as "Yugoslavia"; "Ireland" (1994 draw table) as
"Republic of Ireland"; "Côte d'Ivoire" as "Ivory Coast"; "Türkiye"/"Cabo Verde"/"Congo DR"
(FIFA 2026 spellings) as "Turkey"/"Cape Verde"/"DR Congo".

## Per-tournament seeding structure

**1990 (draw 9 Dec 1989, Rome).** Six seeded teams chosen by the FIFA Organising Committee from
1986 (double weight) and 1982 World Cup results: Italy (host), Argentina (holders), Brazil,
West Germany, Belgium, England. Remaining 18 in three geographic pots — mapping used here:
pot 2 = Wikipedia's "Pot 1" (CAF/AFC/CONCACAF), pot 3 = "Pot 2" (CONMEBOL + second-tier UEFA),
pot 4 = "Pot 3" (best unseeded UEFA). Argentina: **seeded (pot 1)**.

**1994 (draw 19 Dec 1993, Las Vegas).** Six seeds = host USA + holders Germany + top 4 by results
in the last three World Cups (Argentina, Italy, Brazil, Belgium); the new FIFA ranking was
deliberately NOT used. Pot 2 = Africa & Americas, pot 3 = best unseeded UEFA, pot 4 = AFC +
lowest-ranked UEFA. Argentina: **seeded (pot 1)**.

**1998 (draw 4 Dec 1997, Marseille).** 8 seeds (Pot A) = holders Brazil + host France + top 6 of a
formula (last three World Cups 60%, FIFA rankings Dec 1995/Dec 1996/Nov 1997 40%):
Germany, Italy, Spain, Argentina, Romania, Netherlands. Pot B = UEFA (9 teams — the ninth was
drawn into a group headed by a South American seed), Pot C = AFC+CONMEBOL (7), Pot D =
CAF+CONCACAF (8). Pots A–D mapped to 1–4. Argentina: **seeded (pot 1)**.

**2002 (draw 1 Dec 2001, Busan).** 8 seeds = holders France + co-hosts South Korea & Japan + top 5
of the World Cup-performance/FIFA-ranking formula (Brazil, Argentina, Italy, Germany, Spain).
Mexico (7th) and England (8th) in the formula table were NOT seeded. Pot 2 = UEFA (11 — three
were drawn as third UEFA-slot fillers into groups with non-UEFA seeds), pot 3 = AFC+CONMEBOL (5),
pot 4 = CAF+CONCACAF (8). Argentina: **seeded (pot 1)**.

**2006 (draw 9 Dec 2005, Leipzig).** 8 seeds (Pot A) by formula (WC 1998/2002 + FIFA rankings
2003–05): Germany (host), Brazil, England, Spain, Mexico, France, Italy, Argentina. Pot B =
CONMEBOL/CAF/OFC (8), Pot C = UEFA (8), Pot D = CONCACAF/AFC (7). Serbia and Montenegro (lowest-
ranked UEFA qualifier) went into a **special pot** — recorded here as pot 5 — and were drawn into
a group headed by a non-European seed (they landed with Argentina in Group C).
Pots A–D mapped to 1–4. Argentina: **seeded (pot 1)**.

**2010 (draw 4 Dec 2009, Cape Town).** 8 seeds = host South Africa + top 7 of the **October 2009**
FIFA ranking (Brazil, Spain, Netherlands, Italy, Germany, Argentina, England). Pot 2 =
AFC/CONCACAF/OFC, pot 3 = CAF/CONMEBOL, pot 4 = UEFA. Argentina: **seeded (pot 1)**.

**2014 (draw 6 Dec 2013, Costa do Sauípe).** 8 seeds = host Brazil + top 7 of the **October 2013**
FIFA ranking (Argentina, Colombia, Uruguay, Belgium, Germany, Spain, Switzerland). Pot 2 =
CAF+CONMEBOL (7), pot 3 = AFC+CONCACAF (8), pot 4 = UEFA (9). To even the pots, one Pot-4 team
was drawn out at the ceremony and moved to Pot 2 — it was **Italy**, recorded here as pot 2
(officially pre-allocated to Pot 4). Argentina: **seeded (pot 1)**.

**2018 (draw 1 Dec 2017, Moscow).** First draw with ALL pots by ranking (October 2017 edition):
Pot 1 = host Russia + top 7 (Germany, Brazil, Portugal, Argentina, Belgium, Poland, France);
pots 2–4 = next 8, next 8, last 8 regardless of confederation. Argentina: **seeded (pot 1)**.

**2022 (draw 1 Apr 2022, Doha).** Pots by the **31 March 2022** FIFA ranking: Pot 1 = host Qatar +
top 7 (Brazil, Belgium, France, Argentina, England, Spain, Portugal). Pot 4 contained three
placeholders decided in June 2022; they were won by **Wales** (UEFA Path A), **Costa Rica**
(CONCACAF–OFC play-off) and **Australia** (AFC–CONMEBOL play-off) — these three are recorded as
pot 4. Argentina: **seeded (pot 1)**.

**2026 (draw 5 Dec 2025, Washington D.C.).** Four pots of 12 by the **19 November 2025** FIFA
ranking: Pot 1 = co-hosts Mexico, Canada, United States + top 9 qualified (Spain, Argentina,
France, England, Brazil, Portugal, Netherlands, Belgium, Germany). Pot 4 included six
placeholders decided in March 2026, won by **Bosnia and Herzegovina** (UEFA Path A — beat Italy
in the final), **Czech Republic**, **Sweden**, **Turkey** (other UEFA paths) and **DR Congo**,
**Iraq** (inter-confederation play-offs); all six recorded as pot 4.
Argentina: **seeded (pot 1)**.

**Argentina summary: officially seeded / Pot 1 in every World Cup 1990 through 2026.**

## Ranking editions used in `fifa_rankings_pre.csv`

The FIFA World Ranking was introduced in December 1992/August 1993 — **there is no ranking for
1990** (tournament omitted from the rankings file by design).

| Tournament | Opening match | Ranking edition used (last published before opening) |
|---|---|---|
| 1994 | 17 Jun 1994 | 14 Jun 1994 |
| 1998 | 10 Jun 1998 | 20 May 1998 |
| 2002 | 31 May 2002 | 15 May 2002 |
| 2006 | 9 Jun 2006 | 17 May 2006 |
| 2010 | 11 Jun 2010 | 26 May 2010 |
| 2014 | 12 Jun 2014 | 5 Jun 2014 |
| 2018 | 14 Jun 2018 | 7 Jun 2018 (last edition of the pre-Elo formula) |
| 2022 | 20 Nov 2022 | 6 Oct 2022 |
| 2026 | 11 Jun 2026 | 11 Jun 2026 (released hours before the opening match) |

Notes on rankings:
- Ranks are NOT the ranks used for draw seeding (those came months earlier — e.g. Oct 2009 for
  the 2010 seeds, Oct 2013 for 2014, Oct 2017 for 2018, 31 Mar 2022 for 2022, 19 Nov 2025 for
  2026). This file records tournament-start strength; `draw_pots.csv` records draw treatment.
- The pre-2006 ranking formula produced **ties**: in the 17 May 2006 edition Spain and United
  States are both 5, Croatia and Iran both 23, Poland and South Korea both 29; in the 7 Jun 2018
  edition Denmark and England are both 12 ("joint 12" per source). These duplicates are genuine.
- 1998: Nigeria's rank of 74 is correct per the 20 May 1998 edition (verified verbatim in the
  source table), despite Nigeria being a strong side at that tournament.
- 2026: the 11 June 2026 edition (Argentina 1, Spain 2, France 3) was published on the day of,
  but hours before, the opening match; the April 1, 2026 edition (France 1) was the previous one.
  Values taken from the Wikipedia 2026 article's qualified-teams table, which cites the FIFA
  ranking archived 12 June 2026; top-10 cross-checked against Goal.com's 11 June 2026 report.

## Sources

Primary (pots and rankings; all extracted from raw article wikitext, not rendered summaries):
- https://en.wikipedia.org/wiki/1990_FIFA_World_Cup (Seedings section; pots cited there to
  The Times, 9 Dec 1989; seeds to The New York Times, 8 Dec 1989)
- https://en.wikipedia.org/wiki/1994_FIFA_World_Cup (Group-stage draw section)
- https://en.wikipedia.org/wiki/1998_FIFA_World_Cup (Draw section; rankings cite FIFA 20 May 1998)
- https://en.wikipedia.org/wiki/2002_FIFA_World_Cup (Draw section; rankings cite FIFA 15 May 2002)
- https://en.wikipedia.org/wiki/2006_FIFA_World_Cup (Seeding section; rankings cite FIFA 17 May 2006)
- https://en.wikipedia.org/wiki/2010_FIFA_World_Cup (Seeding section; rankings "May 2010" edition,
  released 26 May 2010)
- https://en.wikipedia.org/wiki/2014_FIFA_World_Cup_seeding and
  https://en.wikipedia.org/wiki/2014_FIFA_World_Cup (rankings cite FIFA 5 Jun 2014)
- https://en.wikipedia.org/wiki/2018_FIFA_World_Cup_seeding and
  https://en.wikipedia.org/wiki/2018_FIFA_World_Cup (June 2018 ranks; edition date 7 Jun 2018
  confirmed via soccerphile.com/football-rankings.info)
- https://en.wikipedia.org/wiki/2022_FIFA_World_Cup_seeding and
  https://en.wikipedia.org/wiki/2022_FIFA_World_Cup (rankings cite FIFA 6 Oct 2022)
- https://en.wikipedia.org/wiki/2026_FIFA_World_Cup_draw and
  https://en.wikipedia.org/wiki/2026_FIFA_World_Cup

Cross-checks (second sources):
- **Argentina's seeded status 1990–2014**: FIFA fact sheet "FIFA World Cup seeded teams since
  1930" (digitalhub.fifa.com, archived; lists seeds per tournament — Argentina appears as a seed
  in 1990, 1994, 1998, 2002, 2006, 2010 and 2014). PDF:
  https://web.archive.org/web/20220322012822/https://digitalhub.fifa.com/m/79d9ab359eab12f3/original/g6sxbyxsmoqdxz3firrz-pdf.pdf
- **2018 Pot 1** (incl. Argentina): Sports Illustrated / Goal.com draw-pot articles
  (https://www.si.com/soccer/2017/11/28/fifa-world-cup-draw-russia-rules-pots-teams-groups-schedule).
- **2022 pots** (all four, incl. Argentina Pot 1): Al Jazeera
  (https://www.aljazeera.com/news/2022/4/1/qatar-2022-world-cupdrawexplained) and Sports
  Illustrated (https://www.si.com/soccer/2022/03/30/world-cup-2022-draw-pots-qualifying-fifa-ranking)
  — identical to the Wikipedia seeding page.
- **2026 pots** (all four, incl. Argentina Pot 1): Al Jazeera
  (https://www.aljazeera.com/sports/2025/12/2/fifa-world-cup-2026-draw-teams-pots-how-to-watch-and-all-to-know)
  and FIFA.com draw-procedures pages — identical to the Wikipedia draw page.
- **2026 rankings**: Goal.com, "Argentina reclaim top spot in FIFA Men's World Rankings as 2026
  World Cup kicks off" (11 Jun 2026).

## Gaps / caveats

- **1990 FIFA rankings: none exist** (rankings began after 1990); no 1990 rows in
  `fifa_rankings_pre.csv`.
- Exact 1994 pot-2/3/4 memberships are from the Wikipedia 1994 draw table (sourced to the
  televised draw and FIFA fact sheets); RSSSF was not separately consulted.
- 2006 Pot B/C/D memberships: structure and Pot C verified verbatim from Wikipedia; Pot B
  membership additionally matches a Soccer America draw report; Pot D is the remaining seven
  CONCACAF/AFC qualifiers (deterministic given the structure).
- `pot 5` appears only once (Serbia and Montenegro, 2006 special pot).
- 2014 Italy recorded as pot 2 (drawn from Pot 2 after ceremony relocation from Pot 4).
- 2018/2022/2026 pot ranks in the sources refer to the seeding editions (Oct 2017 / Mar 2022 /
  Nov 2025), which differ from the tournament-start ranks in `fifa_rankings_pre.csv`.
