/* =================================================================================================
   SQUABBIT PULLER — paste this whole file into the console on https://app.squabbitgolf.com
   while signed in as Dom, or run it through Claude in Chrome's javascript_tool.

   Returns the array that squabbit_report.py expects, ready to save as squabbit_pull.json.

   WHY IT WORKS THE WAY IT DOES
   ----------------------------
   Squabbit is a Flutter/CanvasKit app, so there is no DOM to scrape — but it leaves the Firebase
   modular SDK on `window`, and the signed-in user's own credentials are already attached. Only
   two collections are readable: `users` and `rounds`. Everything else is permission-denied.

   FINDING THE RIGHT PEOPLE is the part that has nearly gone wrong before. Several of these names
   have half a dozen namesakes on Squabbit — there is a second Luke Usher with a full scoring
   record who plays entirely different courses. So this does NOT search by name. It reads Dom's
   own tournament list, finds every round played in those tournaments, and takes the user IDs off
   those rounds. Somebody who has actually played in a Chip & Sip tournament is the right man by
   construction. Names are only used to label what comes back.

   NOTE: users/{authUid} is NOT the user document. The auth uid lives in a field called `authId`
   on the users doc, and rounds join on the DOCUMENT id. Getting that backwards returns silence
   rather than an error, which is how it wasted twenty minutes the first time.
   ================================================================================================= */
(async () => {
  const C = window.firebase_core, A = window.firebase_auth, F = window.firebase_firestore;
  if (!C || !F) throw new Error("Firebase not on window — is this app.squabbitgolf.com, fully loaded?");
  const app = C.getApps()[0], db = F.getFirestore(app);
  const auth = A.getAuth(app);
  if (!auth.currentUser) throw new Error("Not signed in to Squabbit.");

  const norm = s => String(s || "").toLowerCase().replace(/[^a-z]/g, "");

  /* 1. Dom's own users document, via authId. */
  const meQ = await F.getDocs(F.query(F.collection(db, "users"),
                F.where("authId", "==", auth.currentUser.uid), F.limit(1)));
  if (meQ.empty) throw new Error("No users doc for the signed-in account.");
  const meId = meQ.docs[0].id;
  const tids = meQ.docs[0].data().tournamentIdsV2 || [];

  /* 2. Everybody who has played in one of his tournaments. */
  const ids = new Set([meId]);
  for (const t of tids) {
    try {
      const rs = await F.getDocs(F.query(F.collection(db, "rounds"),
                   F.where("tournamentId", "==", t), F.limit(1500)));
      rs.docs.forEach(x => { const u = x.data().userId; if (u) ids.add(u); });
    } catch (e) { /* a tournament we cannot read is not worth stopping for */ }
  }

  /* 3. Name -> {id, profile}. First writer wins, and since these all come from real tournament
        rounds there is no namesake to disambiguate. */
  const map = {};
  for (const id of ids) {
    try { const u = await F.getDoc(F.doc(db, "users", id));
          if (u.exists()) { const k = norm(u.data().name); if (!map[k]) map[k] = { id, d: u.data() }; }
    } catch (e) {}
  }

  /* 4. The squad the board actually runs on. Anyone not here is somebody else's mate. */
  const WANT = ["Luke Usher","Dom Mills","Josh Menzies","Tom Bucknall","Alex Mulvin","Matt Petty",
    "Ben West","Matt Holland","Mark Sturgess","Rob Parfitt","Eamonn Brady","Gabe Hills",
    "dong ming lau","Luke Holland","Jay France","Chris Best","Dave Huddleston","Jack Mulroy",
    /* Both of these are pinned by document id below — neither matches on name. */
    "Theo Sims-Harris","Josh Evans"];

  /* A man's Squabbit account is not always under the name the board calls him. Theo signed up as
     "Theo Harris" and the board calls him Theo Sims-Harris, so for a fortnight he matched nothing
     and was priced on an assumed handicap while 14 real rounds sat there unread. Confirmed by Dom
     AND by the card: 9 rounds at Weybrook Park and one each at Morgado and Salgados, which are
     the 2024 Portugal courses.
     PINNED BY DOCUMENT ID, not by the other name. Name matching is what caused this in the first
     place, and "Theo Harris" is common enough that a namesake could walk into one of Dom's other
     tournaments and quietly take his place in the model. An id cannot be mistaken for anybody. */
  /* Matt Petty joined this list on 3 Sep 2026. Between 27 Aug and 3 Sep he dropped out of every
     one of Dom's tournaments, so the tournament-based match found nothing and a 20-man model
     would have quietly become 19 with Blue a man short. TWO accounts carry his name — one with a
     single round from July 2025 — and Dom confirmed which is his.
     The wider lesson: the tournament list is no longer only Chip & Sip. It now pulls 129 people
     from open events, so "the right man by construction" is weaker than it was. A pinned id is
     the only thing that cannot drift. */
  const SQUABBIT_ID = { "Theo Sims-Harris": "HERfU5b3UqXWr29TcGgK",
                       "Matt Petty":        "WR2TRZD2QNowFmvOcIXI",
                       /* Josh has THREE accounts under his name on Squabbit: one plays in Virginia,
                          one has 2 rounds off 28, and this one is his. Confirmed by Dom. Note the
                          profile handicap on it reads 0.9, which his own cards do not support — see
                          squabbit-report.md. Pinned by id so the record is read; the 0.9 is not adopted. */
                       "Josh Evans":       "tXunHSphT0q5WO77NPup" };

  const mean = a => a.length ? a.reduce((x, y) => x + y, 0) / a.length : null;
  const r1 = v => v == null ? null : Math.round(v * 10) / 10;
  const out = [], missing = [];

  for (const nm of WANT) {
    /* Pin first, name second. The other way round, a namesake who wanders into one of Dom's open
       events would beat the pin and never be noticed. */
    let e = SQUABBIT_ID[nm] ? null : map[norm(nm)];
    if (!e && SQUABBIT_ID[nm]) {
      try { const u = await F.getDoc(F.doc(db, "users", SQUABBIT_ID[nm]));
            if (u.exists()) e = { id: SQUABBIT_ID[nm], d: u.data() }; } catch (err) {}
    }
    if (!e) e = map[norm(nm)];              /* pin missed — fall back to the name */
    if (!e) { missing.push(nm); continue; }
    let docs = [];
    try {
      const rs = await F.getDocs(F.query(F.collection(db, "rounds"),
                   F.where("userId", "==", e.id), F.orderBy("date", "desc"), F.limit(500)));
      docs = rs.docs.map(x => x.data());
    } catch (err) { out.push({ n: nm, err: String(err.code || err.message) }); continue; }

    const rounds = [];
    let pairs = 0, sim = 0, short = 0, nines = 0, dupes = 0;
    /* DEDUPE. Reading `rounds` by userId is a single source — a round played inside a tournament
       is the SAME document whether you reach it from the tournament page or the man's profile, so
       there is no double-count by construction. What DOES happen is a man entering the same round
       twice on Squabbit: Alex Mulvin has two documents for 10 May 2025, both 93 off 18 holes. Left
       alone that round carries twice the weight in his average. Keyed on date + gross + holes
       played, which cannot collide for one man on one day. */
    const seenRound = new Set();
    for (const r of docs) {
      /* Simulator rounds are not golf. */
      if (r.isSimRound) { sim++; continue; }
      /* Pairs formats are excluded throughout: two men sharing a ball say nothing about either. */
      if (r.holesPartner && Object.keys(r.holesPartner).length) { pairs++; continue; }
      const pars = r.courseHolesPars || [];
      /* WHICH holes he actually played. This is the bit that used to throw away every nine:
         numHoles was tested against 18 and a twilight nine was binned. Worse, a 9-hole card still
         carries all 18 pars on the document, so subtracting the full par turns a decent nine into
         minus twenty-one. Sum the pars of the scored holes only. */
      const sc = r.holeScoresV2 ? Object.entries(r.holeScoresV2).filter(e2 => +e2[1] > 0) : [];
      const holes = sc.map(e2 => +e2[0]);
      if (holes.length < 9) { short++; continue; }          /* abandoned or barely started */
      const parPlayed = holes.reduce((a, h) => a + (+pars[h - 1] || 0), 0);
      const g = sc.reduce((a, e2) => a + (+e2[1]), 0);
      if (!(parPlayed > 25) || !(g > 25) || g > 200) { short++; continue; }
      const half = holes.length < 14;
      if (half) nines++;
      const d = r.date && r.date.toDate ? r.date.toDate().toISOString().slice(0, 10) : null;
      const dk = d + "|" + g + "|" + holes.length;
      if (seenRound.has(dk)) { dupes++; continue; }
      seenRound.add(dk);
      const sl = r.tee && +r.tee.slope, ra = r.tee && +r.tee.rating;
      /* Everything is expressed PER 18 HOLES, so nines and full rounds sit on one scale.
         Differentials come from full rounds only: a nine sometimes carries the 18-hole course
         rating on the document and sometimes the 9-hole one, with no reliable way to tell which,
         and doubling the wrong one produced a best-8 of minus six. Over-par is safe; this is not. */
      rounds.push({ d, half,
        ovp: (g - parPlayed) * (half ? 2 : 1),
        diff: (!half && sl > 0 && ra > 60) ? (113 / sl) * (g - ra) : null });
    }
    rounds.sort((a, b) => String(b.d).localeCompare(String(a.d)));

    const ov = rounds.map(r => r.ovp);
    const m = mean(ov);
    const sd = ov.length > 1 ? Math.sqrt(ov.reduce((a, v) => a + (v - m) * (v - m), 0) / (ov.length - 1)) : null;
    /* The WHS shape: best 8 differentials of the last 20. Tee rating and slope ARE on the round
       document, which they were not thought to be first time round — so this is a real figure,
       not a proxy. It still has no adjusted-gross cap, so treat it as indicative. */
    const df = rounds.filter(r => r.diff != null).map(r => r.diff);
    const best8 = df.slice(0, 20).sort((a, b) => a - b).slice(0, 8);

    out.push({
      n: nm, hcp: e.d.handicap, src: e.d.handicapSource || null,
      n18: rounds.length, nines, pairsSkipped: pairs, simSkipped: sim, shortSkipped: short,
      dupesSkipped: dupes,
      ovpAll: r1(m), ovpL20: r1(mean(ov.slice(0, 20))), ovpL10: r1(mean(ov.slice(0, 10))),
      sd: r1(sd),
      since2026: rounds.filter(r => r.d && r.d >= "2026-01-01").length,
      last: rounds.length ? rounds[0].d : null,
      whs8of20: best8.length ? r1(mean(best8)) : null
    });
  }
  console.log("MISSING (no Squabbit account found in Dom's tournaments):", missing.join(", ") || "none");
  return JSON.stringify(out);
})()
