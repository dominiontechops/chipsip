import json, statistics as st
# SUPERSEDED BY refit.py, 25 Aug 2026. players.txt now carries the live Squabbit handicap for
# every man including Theo and Josh, so there is no second list to keep in step. Kept only because
# squabbit_report.py imports STATED to label the two marks that are the group's word rather than
# Squabbit's. Do not run this script: it would write back the marks below, which are now stale.
PROFILE={
 "Alex Mulvin":13.2,"Ben West":20.6,"Chris Best":24.0,"Dave Huddleston":19.4,
 "Dom Mills":26.0,"Dong Ming Lau":19.1,"Eamonn Brady":16.4,"Gabe Hills":17.5,
 "Jack Mulroy":21.2,"Jay France":9.5,"Josh Menzies":13.7,"Luke Holland":13.4,
 "Luke Usher":13.8,"Matt Holland":22.4,"Rob Parfitt":21.5,"Tom Bucknall":25.3,
 "Theo Sims-Harris":18.3,"Josh Evans":12.0}
# Josh's Squabbit profile reads 0.9 off four rounds, one of which is a 3-over that the model drops
# as an outlier anyway. 12.0 is the group's mark and the one the board runs on.
STATED={"Matt Petty":18.0,"Mark Sturgess":20.0,"Josh Evans":12.0,"Theo Sims-Harris":15.0}

M=json.load(open('model.json'))
old={p['name']:p['hcp'] for p in M}

# rawForm is measured scoring, independent of handicap - it does not move.
# Only the gap moves, so recompute gaps against the new marks and re-shrink.
K=12.0
known=[p for p in M if not p.get('unknown')]
for p in known:
    p['hcp']=PROFILE[p['name']]
    p['rawGap']=round(p['rawForm']-p['hcp'],2)
medgap=st.median([p['rawGap'] for p in known])
meansd=st.mean([p['sd'] for p in known])
for p in known:
    w=p['n']/(p['n']+K)
    p['gap']=round(w*p['rawGap']+(1-w)*medgap,2)
    p['form']=round(p['hcp']+p['gap'],2)
for p in M:
    if p.get('unknown'):
        p['hcp']=STATED[p['name']]
        p['gap']=round(medgap,2); p['form']=round(p['hcp']+medgap,2); p['sd']=round(meansd,2)
M.sort(key=lambda p:(p['team'],p['gap']))
json.dump(M,open('model.json','w'),indent=1)

print(f"{'Player':18s} {'was':>6s} {'profile':>8s} {'move':>6s} {'form':>6s} {'newgap':>7s}")
for p in sorted(M,key=lambda x:-abs(x['hcp']-old[x['name']])):
    d=p['hcp']-old[p['name']]
    tag='' if p.get('unknown') else ('   <-- big move' if abs(d)>=2 else '')
    src='stated' if p.get('unknown') else f"{p['hcp']:.1f}"
    print(f"{p['name']:18s} {old[p['name']]:6.1f} {src:>8s} {d:+6.1f} {p['form']:6.1f} {p['gap']:+7.2f}{tag}")
print(f"\nfield median raw gap now {medgap:+.2f}")
