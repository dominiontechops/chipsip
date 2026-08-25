"""
Rebuilds last year's day guides for 2026.

WHAT IS REAL AND WHAT IS NOT
Every number on these pages comes off the Squabbit scorecard for the tee we are actually playing:
par, stroke index and yardage. The tactical notes are DERIVED from those numbers — which nine is
longer, where the stroke holes fall, whether the par 3s and 5s sit on odd or even tees. Nothing
here is local knowledge invented about a course nobody has walked. Last year's guides carried the
club's own hole descriptions and yardage-book artwork; those pages go in when Dom supplies them,
and the layout leaves the slot for them.
"""
import json, pathlib
D = pathlib.Path(__file__).parent
d = json.load(open(D/"data.json"))
M = d["meta"]

def ordinal(h):
    return f"{h}{'th' if 11<=h%100<=13 else {1:'st',2:'nd',3:'rd'}.get(h%10,'th')}"

def notes(day):
    """Tactical notes that follow from the card, one per line. No invention."""
    p, si, y = day["pars"], day["si"], day["yds"]
    fp, bp = sum(p[:9]), sum(p[9:])
    par3 = [i+1 for i in range(18) if p[i]==3]
    par5 = [i+1 for i in range(18) if p[i]==5]
    odd  = [i for i in range(18) if (i+1)%2==1]
    even = [i for i in range(18) if (i+1)%2==0]
    so, se = sum(si[i] for i in odd), sum(si[i] for i in even)
    h1, h2 = si.index(1)+1, si.index(2)+1
    easiest = si.index(18)+1
    out=[]
    out.append(("The card", 
        f"Par {day['par']} off the {day['teeName']} tees, {day['yards']:,} yards, "
        f"slope {day['slope']} and rating {day['rating']}. Out in {fp}, back in {bp}. "
        f"{len(par3)} par 3s ({', '.join(ordinal(x) for x in par3)}) and "
        f"{len(par5)} par 5s ({', '.join(ordinal(x) for x in par5)})."))
    out.append(("Where the shots go",
        f"Stroke index 1 is the {ordinal(h1)} and index 2 the {ordinal(h2)} — everyone playing off "
        f"a handicap gets a shot there first. The {ordinal(easiest)} is index 18 and is where a shot "
        f"is worth least, so it is the one to give away if you are choosing your fights."))
    # Matched on "Foursome"/"Fourball" until the group asked for the plain-English names.
    # The test follows data.json, or the day loses its format advice without saying so.
    if day["format"].startswith("Alternate Shot"):
        harder, easier = ("even","odd") if se<so else ("odd","even")
        out.append(("Who tees where",
            f"This is the decision that actually wins alternate shot. The {harder}-numbered tees are "
            f"collectively the harder set here (stroke indexes adding to {min(so,se)} against "
            f"{max(so,se)}), and they include index 1, the {ordinal(h1)}. Put your straighter driver on "
            f"the {harder} tees and accept he will not hit the pretty ones."))
        p3odd = [x for x in par3 if x%2==1]
        out.append(("Irons off the tee",
            f"{len(p3odd)} of the {len(par3)} par 3 tee shots fall on odd holes "
            f"({', '.join(ordinal(x) for x in p3odd) or 'none'}). Whoever takes the odd tees is hitting "
            f"more irons at flags and fewer drivers, which suits the better iron player."))
    if day["format"].startswith("Best Ball"):
        out.append(("Where a best ball is won",
            f"Two balls means somebody can attack. The sensible split is the higher handicapper going at "
            f"the stroke holes where his shot is worth most — the {ordinal(h1)} and the {ordinal(h2)} — "
            f"while the low man keeps a score on the card. Do not both play safe on the same hole."))
        out.append(("The bonus is thin here",
            f"There are only {len(par3)} par 3s on this course ({', '.join(ordinal(x) for x in par3)}), "
            f"so the par 3 bonus point turns on {len(par3)*10} scores across the whole team. One "
            f"disaster on a short hole decides it."))
    if day["format"].startswith("2 man Scramble"):
        out.append(("Order of play",
            "In a scramble the second man plays knowing what the first has done. Send the wilder hitter "
            "first on the tee, so the safe player can respond to a bad one, and reverse it on the greens: "
            "the better putter goes last having watched the line."))
        out.append(("The bonus lives on the par 5s",
            f"{len(par5)} par 5s ({', '.join(ordinal(x) for x in par5)}), and the {ordinal(h1)} is index 1 "
            f"as well as a par 5. Two decent drives there and the bonus point is genuinely in play, which "
            f"is the one place it is worth taking on the hero shot."))
    if day["format"].startswith("Singles"):
        out.append(("An unusual card",
            f"Out in {fp} and back in {bp}. The front nine carries "
            f"{len([x for x in par5 if x<=9])} of the {len(par5)} par 5s and is "
            f"{sum(v for v in y[:9] if v):,} yards; the back is shorter and tighter. Bank your points "
            f"early — the closing stretch does not give them away."))
        out.append(("The streak bonus",
            "Net par or better in a row. Because it is a streak rather than a total, one blow-up ends it, "
            "so on a hole where you have a shot and the trouble is real, take the safe line and keep it alive."))
    verdict = ("the stiffest test of the week, so shots given and received are worth more here than anywhere else we play"
               if day['slope']>=137 else
               "the gentlest of the week, so shots given and received are worth less here than anywhere else we play"
               if day['slope']<=127 else
               "middling for the week, so shots are worth about what you would expect")
    out.append(("Slope, in English",
        f"Slope {day['slope']} says how much harder this plays for a mid handicapper than for a scratch "
        f"golfer. That makes it {verdict}."))
    return out

CSS = """
@page { size: A4 landscape; margin: 14mm 16mm; }
* { box-sizing: border-box; }
body { font-family: Georgia, 'Times New Roman', serif; color: #1c2b33; margin:0; font-size: 11.2pt; }
h1 { font-family: Helvetica, Arial, sans-serif; color:#0f5e73; font-size: 21pt; letter-spacing:.3px;
     margin: 0 0 4px; font-weight: 600; }
.sub { font-family: Helvetica, Arial, sans-serif; color:#6b7d86; font-size: 9.5pt;
       letter-spacing:.6px; text-transform: uppercase; margin-bottom: 14px; }
p { margin: 0 0 9px; line-height: 1.45; }
b, strong { color:#12333f; }
.lbl { font-family: Helvetica, Arial, sans-serif; font-weight:700; }
h2 { font-family: Helvetica, Arial, sans-serif; color:#0f5e73; font-size: 12pt; margin: 16px 0 7px; }
.page { page-break-after: always; }
.page:last-child { page-break-after: auto; }
table.card { border-collapse: collapse; width: 100%; font-family: Helvetica, Arial, sans-serif;
             font-size: 9.4pt; margin-top: 4px; }
table.card th, table.card td { border: 1px solid #cfdce1; padding: 4px 3px; text-align: center; }
table.card th { background:#eef5f7; color:#0f5e73; font-weight:700; }
table.card td.rowlbl, table.card th.rowlbl { text-align:left; background:#f7fbfc; font-weight:700;
             color:#12333f; white-space:nowrap; padding-left:7px; }
table.card td.tot { background:#eef5f7; font-weight:700; }
td.si1 { background:#fde8e8; font-weight:700; }
td.si18 { background:#e8f6ec; }
.note { font-size: 9.6pt; color:#6b7d86; font-family: Helvetica, Arial, sans-serif; margin-top:8px; }
.tips p { margin: 0 0 8px; }
.tips .lbl { color:#0f5e73; }
.pill { display:inline-block; font-family:Helvetica,Arial,sans-serif; font-size:9pt; color:#0f5e73;
        border:1px solid #9ec6d1; border-radius:99px; padding:2px 9px; margin-right:6px; }
.mapslot { border:1.5px dashed #b9cdd4; border-radius:6px; height: 118mm; display:flex;
           align-items:center; justify-content:center; color:#9db3bb;
           font-family:Helvetica,Arial,sans-serif; font-size:10pt; text-align:center; }
.two { display:flex; gap: 16px; }
.two > div { flex: 1 1 0; min-width:0; }
"""

def cardtable(day):
    p,si,y = day["pars"], day["si"], day["yds"]
    def half(a,b,label):
        hs=range(a,b)
        rows=[]
        rows.append("<tr><th class='rowlbl'>HOLE</th>"+"".join(f"<th>{h+1}</th>" for h in hs)+f"<th class='tot'>{label}</th></tr>")
        rows.append("<tr><td class='rowlbl'>PAR</td>"+"".join(f"<td>{p[h]}</td>" for h in hs)+f"<td class='tot'>{sum(p[a:b])}</td></tr>")
        rows.append("<tr><td class='rowlbl'>S.I.</td>"+"".join(
            f"<td class='{'si1' if si[h]<=2 else 'si18' if si[h]>=17 else ''}'>{si[h]}</td>" for h in hs)+"<td class='tot'></td></tr>")
        yy=[y[h] for h in hs]
        tot=sum(v for v in yy if v)
        rows.append("<tr><td class='rowlbl'>YARDS</td>"+"".join(
            f"<td>{y[h] if y[h] else '&mdash;'}</td>" for h in hs)+f"<td class='tot'>{tot if tot else '&mdash;'}</td></tr>")
        return "".join(rows)
    return (f"<table class='card'>{half(0,9,'OUT')}</table>"
            f"<table class='card' style='margin-top:9px'>{half(9,18,'IN')}</table>")

def page1(day):
    return f"""<div class="page">
  <h1>DAY {day['n']} &ndash; {day['course']}</h1>
  <div class="sub">{day['date']} &middot; first tee {day['tee']} &middot; {day['teeName']} tees &middot;
    par {day['par']} &middot; {day['yards']:,} yards &middot; slope {day['slope']} &middot; rating {day['rating']}</div>
  <p><span class="lbl">{day['format']} :</span> {day['formatLine']}</p>
  <p>{day['basis']} &nbsp;|&nbsp; {day['points']}</p>
  <p><span class="lbl">Bonus point :</span> {day['bonus']}</p>
  <h2>Course tips</h2>
  <div class="tips">
  {''.join(f"<p><span class='lbl'>{t}.</span> {b}</p>" for t,b in notes(day))}
  </div>
</div>"""

def page2(day):
    p,si,y=day["pars"],day["si"],day["yds"]
    miss = [i+1 for i in range(18) if y[i] is None]
    return f"""<div class="page">
  <h1>DAY {day['n']} &ndash; THE CARD</h1>
  <div class="sub">{day['course']} &middot; {day['teeName']} tees</div>
  {cardtable(day)}
  <p class="note">Stroke index 1 and 2 are shaded red, 17 and 18 green. Every figure is taken from the
  club scorecard for the tees we are playing.{(' Back nine yardages are not on the card we have &mdash; '
  'holes ' + ', '.join(str(h) for h in miss) + ' show par and stroke index only.') if miss else ''}</p>
  <h2>Reading it before you play</h2>
  <div class="tips">
    <p><span class="lbl">Your shots.</span> Count your course handicap, then find that many holes starting
    at stroke index 1 and working up. Those are the holes where a bogey is still a half.</p>
    <p><span class="lbl">Their shots.</span> Do the same for the man you are playing. Knowing where he gets
    one and you do not is worth more than any swing thought.</p>
    <p><span class="lbl">The bonus point.</span> {day['bonus']}</p>
  </div>
</div>"""

def maps_placeholder(day):
    out=[]
    for h in range(18):
        out.append(f"""<div class="page">
  <div class="two">
    <div><div class="mapslot">Hole {h+1} map<br><span style="font-size:8.5pt">yardage-book artwork to be dropped in</span></div></div>
    <div>
      <h1 style="font-size:30pt;margin-bottom:2px">{h+1}</h1>
      <p style="margin:0"><span class="lbl">Par:</span> {day['pars'][h]}</p>
      <p style="margin:0 0 10px"><span class="lbl">Stroke index:</span> {day['si'][h]}</p>
      <p><span class="pill">{day['teeName']} tees</span>
         <span class="pill">{str(day['yds'][h]) + ' yds' if day['yds'][h] else 'yardage to come'}</span></p>
      <h2>Playing it</h2>
      <p class="note" style="margin-top:0">Club notes go here once the yardage book is in.</p>
    </div>
  </div>
</div>""")
    return "".join(out)

for day in d["days"]:
    html=f"""<!doctype html><html><head><meta charset="utf-8"><style>{CSS}</style></head><body>
{page1(day)}{page2(day)}{maps_placeholder(day)}
</body></html>"""
    (D/f"day{day['n']}.html").write_text(html)
    print("wrote", f"day{day['n']}.html")
