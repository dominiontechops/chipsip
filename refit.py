# Refit the model from a fresh players.txt WITHOUT losing the things players.txt does not carry:
# team, role, and the display name the board uses. The scoring maths below is gen.py's, unchanged —
# recency-weighted mean of the cleaned rounds, then shrink each man's gap and spread toward the
# field. Everything else is a straight recompute so a rerun is always reproducible.
import json, statistics as st

LAST = {}    # date of the most recent round, straight off the pull
for r in json.load(open('squabbit_pull.json')):
    LAST[r['n'].lower()] = r['last']

# TREND: the last 10 rounds against the ones BEFORE them.
#
# It used to be the last 10 against the whole record — but the whole record contains the last 10,
# so a man with 10 rounds or fewer was being compared against himself and came out at exactly
# 0.0 every time. Four men sat on the Form Book reading "steady at his usual level, 6th of 20"
# purely because the arithmetic could not return anything else. That is a claim the data cannot
# support dressed up as a measurement.
#
# Two disjoint sets fixes it: recent golf on one side, earlier golf on the other. It is undefined
# when there is nothing on the earlier side, which is the honest answer, and it needs at least 5
# rounds back there before it will say anything — 10 against 1 is a rounding error with an opinion.
# Everyone who had a trend before keeps the same direction; the figures are simply bigger, because
# the baseline is no longer diluted by the very rounds being tested against it.
TREND_MIN_EARLIER = 5
def trend_of(clean):
    earlier = clean[:-10]
    if len(earlier) < TREND_MIN_EARLIER: return None
    return round(st.mean(clean[-10:]) - st.mean(earlier), 1)

rows = []
for line in open('players.txt'):
    line = line.strip()
    if not line: continue
    p = line.split('|'); d = dict(kv.split('=', 1) for kv in p[1:])
    rows.append(dict(name=p[0], hcp=float(d['hcp']), n=int(d['n']),
                     sd=float(d['sd']),
                     diffs=[float(x) for x in d['diffs'].split(',')],
                     mix=[float(x) for x in d['mix'].split('/')]))

out = []
for r in rows:
    ds = r['diffs']; med = st.median(ds)
    clean = [x for x in ds if x >= med - 12 and x > 0]      # 9-hole / scramble artefacts
    dropped = len(ds) - len(clean)
    if len(clean) < 3: clean = [x for x in ds if x > 0]
    w = [0.92 ** (len(clean) - 1 - i) for i in range(len(clean))]   # most recent last
    form = sum(x * wi for x, wi in zip(clean, w)) / sum(w)
    sd = st.pstdev(clean) if len(clean) > 2 else r['sd']
    sd = max(2.8, min(9.0, sd))
    tot = sum(r['mix'])
    probs = [m / tot for m in r['mix']] if tot > 0 else [0, .03, .25, .4, .2, .12]
    out.append(dict(name=r['name'], hcp=r['hcp'], n=r['n'], form=round(form, 2),
                    sd=round(sd, 2), gap=round(form - r['hcp'], 2),
                    probs=[round(x, 4) for x in probs],
                    trend=trend_of(clean),
                    dropped=dropped, lowSample=r['n'] < 10))

K = 12.0
medgap = st.median([p['gap'] for p in out])
meansd = st.mean([p['sd'] for p in out])
for p in out:
    w = p['n'] / (p['n'] + K)
    p['rawGap'] = p['gap']; p['rawForm'] = p['form']; p['w'] = round(w, 3)
    p['gap'] = round(w * p['rawGap'] + (1 - w) * medgap, 2)
    p['form'] = round(p['hcp'] + p['gap'], 2)
    p['sd'] = round(w * p['sd'] + (1 - w) * meansd, 2)
    p['avg'] = round(72 + p['form'])
    p['last'] = LAST.get(p['name'].lower())
    p['unknown'] = False

# team and role live only in model.json — carry them across
OLD = {p['name'].lower(): p for p in json.load(open('model_prev.json'))}
for p in out:
    o = OLD.get(p['name'].lower(), {})
    p['team'] = o.get('team'); p['role'] = o.get('role')
    if p['team'] is None: raise SystemExit("no team for " + p['name'])

out.sort(key=lambda p: (p['team'], p['gap']))
json.dump(out, open('model.json', 'w'), indent=1)

print(f"{'Player':18s}{'hcp':>6}{'was':>7}{'now':>7}{'move':>7}{'avg':>5}{'trend':>7}{'n':>5}")
for p in sorted(out, key=lambda x: -abs(x['form'] - OLD[x['name'].lower()]['form'])):
    o = OLD[p['name'].lower()]
    d = p['form'] - o['form']
    tag = '   <-- big move' if abs(d) >= 1.0 else ''
    print(f"{p['name']:18s}{p['hcp']:6}{o['form']:7.2f}{p['form']:7.2f}{d:+7.2f}"
          f"{p['avg']:5d}{str(p['trend']):>7}{p['n']:5d}{tag}")
print(f"\nfield median raw gap {medgap:+.2f}   mean spread {meansd:.2f}")
