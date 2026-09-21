import json,datetime,re
t=open('build/t2.html').read()
model=open('model.json').read()
logo=open('logo_b64.txt').read().strip()
build="2026-09-21.1"
# The Squabbit read date comes off the raw pull file itself, so a rebuild that does not re-pull
# cannot quietly claim fresh form. Nothing to remember to update: the file's own timestamp is the
# only honest record of when the scoring history was actually read.
import os
try: pulled=datetime.date.fromtimestamp(os.path.getmtime('squabbit_pull.json')).isoformat()
except Exception: pulled=""
# A fingerprint of the form figures themselves, so a model change always invalidates saved state
# even if the build label is left alone by mistake.
import hashlib
modelv=hashlib.sha1(model.encode()).hexdigest()[:8]
# THE SAVED STATE HAS TO DIE WHEN THE MARKET LIST CHANGES, and until now it only died when the
# model or the hand-typed build string changed. Every novelty market is copied into localStorage
# under S.novelty, so editing DEF_NOV and forgetting to bump `build` left every phone that had
# already loaded that build on the OLD market list — a new market that never appears and a deleted
# one that stays bettable. That is exactly what nearly shipped today: the build string was set
# minutes before the market edits landed. Fold the definitions into the fingerprint so it cannot
# depend on anybody remembering.
_m0=t.index('const MARKETS=['); _m1=t.index('const MODEL_V=')
marketsv=hashlib.sha1(t[_m0:_m1].encode()).hexdigest()[:8]

t=t.replace('__MODEL__',model).replace('__PULLED__',pulled).replace('__MODELV__',modelv)
t=t.replace('__MARKETSV__',marketsv)
# The Form Book's two headline figures, counted rather than remembered. `n` is the number of
# 18-hole rounds behind each man after pairs formats, 9s and short courses are thrown out, and a
# man has a scoring record when he has any rounds at all and is not running on an assumed form.
_m=json.loads(model)
t=t.replace('__ROUNDS__',str(sum(p.get('n',0) for p in _m)))
t=t.replace('__WITHREC__',str(sum(1 for p in _m if p.get('n',0)>0 and not p.get('unknown'))))
t=t.replace('__LOGO__',logo).replace('__BUILD__',build)
open('index.html','w').write(t)

# The service worker's cache name carries the build, so a new release evicts the old shell
# instead of leaving twenty phones on last week's board.
sw=open('build/sw.js').read().replace('__BUILD__',build)
open('sw.js','w').write(sw)
print("built",build,"model",modelv,"markets",marketsv,"pulled",pulled,len(t),"sw",len(sw))
