# Compares a Squabbit pull against what the board is currently running on.
# Written to be re-run: drop a new pull into squabbit_pull.json and run it again.
import json, datetime, sys

PULL=json.load(open('squabbit_pull.json'))
M={p['name']:p for p in json.load(open('model.json'))}
STATED={"Matt Petty":18.0,"Mark Sturgess":20.0,"Josh Evans":12.0,"Theo Sims-Harris":15.0}
today=datetime.date.today().isoformat()

L=[f"# Squabbit refresh — {today}\n"]
L.append("Pulled from app.squabbitgolf.com against the accounts the board is actually using. "
         "Accounts are matched by the courses they play, not by name: several of these names have "
         "half a dozen namesakes on Squabbit and picking the wrong one has already nearly happened once.\n")

moves,newrec,samples=[],[],[]
for r in sorted(PULL,key=lambda x:x['n']):
    n=r['n']; p=M.get(n)
    if not p: continue
    stored=p['hcp']; live=r['hcp']
    if live is not None and abs(live-stored)>=0.05:
        moves.append((n,stored,live,live-stored))
    if p.get('unknown'):
        newrec.append((n,STATED.get(n),live,r['n18'],r['ovpL20']))
    else:
        samples.append((n,p['n'],r['n18'],r['since2026']))

L.append("## Handicaps\n")
if moves:
    L.append("| Player | Board | Squabbit | Move |")
    L.append("|---|---:|---:|---:|")
    for n,a,b,d in moves: L.append(f"| {n} | {a} | {b} | {d:+.1f} |")
else:
    L.append("**No handicap has moved.** Every mark the board is running matches the Squabbit profile.")
L.append("")
L.append("Josh Evans is the one deliberate disagreement. His Squabbit profile reads 0.9, computed off "
         "four rounds of 23, 3, 17 and 14 over par. One good card out of four is not a scratch golfer, "
         "so the board runs the group's mark of 12.0 and prices him off the scoring instead.")
L.append("")

L.append("## Players who now have a scoring record\n")
if newrec:
    L.append("These are priced as *form assumed* on the board — a field-median guess. Squabbit now has "
             "real rounds for them, so the guess can be replaced with a read.\n")
    L.append("| Player | Board assumes | Squabbit says | Rounds | Recent scoring |")
    L.append("|---|---:|---:|---:|---:|")
    for n,st,live,cnt,ovp in newrec:
        L.append(f"| {n} | {st} (stated) | {live if live is not None else '—'} | {cnt} | {ovp:+.1f} over par |")
else:
    L.append("None outstanding. Theo Sims-Harris and Josh Evans were the last two priced on a guess, "
             "and both now have a real record behind them: they are matched by Squabbit document id "
             "rather than by name, because neither account is under the name the board uses.")
L.append("")

L.append("## New rounds logged\n")
L.append("The board's count is individual rounds after pairs formats are stripped out, so it is always "
         "lower than the raw total. What matters is the direction.\n")
L.append("| Player | On the board | On Squabbit now | Logged in 2026 |")
L.append("|---|---:|---:|---:|")
for n,a,b,c in sorted(samples,key=lambda x:-(x[2]-x[1])):
    L.append(f"| {n} | {a} | {b} | {c} |")
L.append("")

L.append("## Scoring, all on one scale\n")
L.append("Strokes over par, which is the one measure available for every round. It is not a WHS "
         "differential — the course table is not readable from the app — so treat it as a trend, not "
         "a handicap.\n")
L.append("| Player | Hcp | Source | Rounds | All time | Last 20 | Last 10 | Spread |")
L.append("|---|---:|---|---:|---:|---:|---:|---:|")
for r in sorted(PULL,key=lambda x:(x['ovpL20'] if x['ovpL20'] is not None else 99)):
    L.append(f"| {r['n']} | {r['hcp']} | {r['src']} | {r['n18']} | {r['ovpAll']:+.1f} | "
             f"{r['ovpL20']:+.1f} | {r['ovpL10']:+.1f} | {r['sd']} |")
L.append("")

L.append("## Trending\n")
hot=[r for r in PULL if r['ovpL10'] is not None and r['ovpL20'] is not None and r['n18']>=12
     and r['ovpL10']-r['ovpL20']<=-1.0]
cold=[r for r in PULL if r['ovpL10'] is not None and r['ovpL20'] is not None and r['n18']>=12
      and r['ovpL10']-r['ovpL20']>=1.0]
if hot: L.append("**Improving** (last 10 better than last 20): "
                 +", ".join(f"{r['n']} ({r['ovpL10']-r['ovpL20']:+.1f})" for r in sorted(hot,key=lambda x:x['ovpL10']-x['ovpL20'])))
if cold: L.append("\n**Slipping**: "
                 +", ".join(f"{r['n']} ({r['ovpL10']-r['ovpL20']:+.1f})" for r in sorted(cold,key=lambda x:-(x['ovpL10']-x['ovpL20']))))
if not hot and not cold: L.append("Nobody has moved enough to call.")
L.append("")

stale=[r for r in PULL if r['last'] and r['last']<"2026-06-01"]
if stale:
    L.append("## Gone quiet\n")
    L.append(", ".join(f"{r['n']} (last logged {r['last']})" for r in sorted(stale,key=lambda x:x['last'])))
    L.append("")
open('squabbit-report.md','w').write("\n".join(L))
print("\n".join(L))
