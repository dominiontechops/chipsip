# Squabbit refresh — 2026-09-11

Second read in 4 days, taken at 15:40 UK. Accounts are matched by the courses they play rather than by name, and three men are pinned by Squabbit document id because neither of their accounts is under the name the board uses.

## Handicaps

| Player | Board before | Squabbit now | Board now | Move |
|---|---:|---:|---:|---:|
| Dave Huddleston | 19.4 | 20.4 | 20.4 | +1.0 |
| Matt Petty | 16.3 | 15.7 | 15.7 | -0.6 |
| Josh Evans | 12.0 | 0.9 | 12.0 | +0.0 |

Josh Evans is the one deliberate disagreement and it has not changed: his Squabbit profile still reads 0.9 off 4 rounds of 23, 3, 17 and 14 over par, so the board keeps the group's mark of 12.0 and prices him off the scoring instead.

Matt Petty has cut his own Squabbit figure from 16.3 to 15.7 and Dave Huddleston's has gone up from 19.4 to 20.4. Both were being tracked straight off Squabbit, so both are adopted.

## New rounds

| Player | Rounds before | Rounds now | Last logged | Form before | Form now | Move |
|---|---:|---:|---|---:|---:|---:|
| Dave Huddleston | 8 | 10 | 2026-09-11 | 26.84 | 28.55 | +1.71 |
| Matt Petty | 13 | 14 | 2026-09-09 | 21.62 | 20.63 | -0.99 |
| Chris Best | 7 | 8 | 2026-09-11 | 29.90 | 30.48 | +0.58 |
| Josh Menzies | 26 | 27 | 2026-09-11 | 19.78 | 19.54 | -0.24 |
| Jack Mulroy | 85 | 86 | 2026-09-09 | 27.79 | 27.94 | +0.15 |

The other 14 are unchanged to the penny. Every man's scoring record was checksummed against what the board already held before anything was written, so an unchanged line here means the record is provably identical rather than merely similar.

## A sorting fault worth recording

Ben West, Rob Parfitt and Eamonn Brady each came back with a different fingerprint and no new golf. In all 3 cases two rounds played on the SAME DAY had swapped places: same scores, same sum, same hole distribution. The puller sorted on the date string alone, which is not a total order, so Firestore returned same-day rounds in whatever order it liked and the recency weighting — 0.92 to the power of position — moved their form for no reason. The puller now sorts on date and then on score, so a rerun is reproducible. Their held order was kept for this refresh rather than letting a tie-break wobble 3 men's figures.

## Trending

**Improving** (last 10 better than the rounds before them): Rob Parfitt (-3.5), Ben West (-2.0), Luke Holland (-1.2)

**Slipping**: Gabe Hills (+3.9), Tom Bucknall (+3.7), Jay France (+3.4), Josh Menzies (+2.4), Dong Ming Lau (+1.8), Jack Mulroy (+1.7), Eamonn Brady (+1.5), Luke Usher (+1.1)

## Gone quiet

Josh Evans (last logged 2026-05-23), Matt Holland (last logged 2026-05-30)

