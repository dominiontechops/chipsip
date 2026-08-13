# Chip &amp; Sip 2026

Tote-pool betting board and form book for the Málaga golf trip, 24–27 September 2026.

One self-contained HTML file. No build step, no server, no dependencies. Open `index.html` in
any browser and it works, including offline on a plane.

## Live site

GitHub Pages serves `index.html` from the repository root. See **Deploying** below.

## What's in it

| Tab | What it does |
|---|---|
| **Pools** | Every market, collapsed until pressed. Captains and vice-captains are badged C and VC throughout. Ante-post and open stakes in whole pounds, implied odds against the model's fair price, and the edge between them |
| **Form Book** | All 20 players with handicap, form, volatility and sample size, plus the simulated prices |
| **Schedule** | Transfers, tee times and collections for all four days, and the four courses |
| **Rules** | How the pools settle. Read this before arguing |
| **Blue Room** | Encrypted. Opposition dossiers, handicap watchlist, captain's notes |
| **Admin** | Roster, handicaps, courses, payment link, ledger, handicap declaration |

## Passphrases

Both use the same scheme: AES-GCM, key derived from the passphrase via PBKDF2 at 250,000 iterations.
**Neither passphrase appears anywhere in the source.** Only ciphertext ships.

The Blue Room passphrase is set in `seal.py`; run it to re-seal after changing the payload, then
rebuild. The watchlist prose is generated from the same figures as the table beneath it, split by team,
so it can never again tell the captain to argue one of his own men's handicaps down.

- **Blue Room** encrypts *content*. Get the passphrase wrong and there is nothing to read, because the
  dossiers exist only as ciphertext. Red Team cannot get at them from View Source however hard they try.
- **Admin** encrypts a *verifier* — a small blob that simply fails to decrypt on the wrong passphrase.
  The panel it guards holds no secrets, only controls, so somebody handy with developer tools could
  unhide it without knowing the passphrase. That costs nothing: every control edits state living in
  that person's own browser. The real ledger and the live site are untouched.

**To change either passphrase, do not hand-edit anything.** Go to Admin → Change a passphrase, pick the
target, enter the new one, and paste the line it produces over the existing `const BLUE = {...}` or
`const ADMIN = {...}` declaration. Then commit and push. Editing ciphertext by hand makes it permanently
unreadable.

## The model

Prices come from a Monte Carlo of the full Ryder Cup, run in the browser. It simulates every match
hole by hole rather than comparing round totals, because three of the four days are pairs formats and
only Sunday's singles produces an individual score.

- **Foursomes** — averages the pair and adds an occasional extra shot, because one ball between two
  players means errors compound
- **Fourball** — better net ball of the two, 90% allowance
- **Scramble** — better of the two balls with a stochastic bonus, 35/15 allowance
- **Singles** — full difference

Pairings are redrawn every simulation, so prices average over who ends up with whom rather than
assuming a draw nobody has made yet.

Player form comes from 461 individual rounds pulled from Squabbit across everyone's full history.
Two things matter and should not be undone if anyone edits the data:

1. **Pairs rounds are excluded.** Identical hole-by-hole scores across a pairing tell you nothing
   about one player. Half the logged trip rounds were foursomes or scrambles.
2. **Small samples are shrunk.** A gap built on three rounds is mostly noise, so each player's figure
   is weighted `n/(n+12)` and pulled toward the field median by the remainder. Without this, a player
   with seven rounds priced as a 61% MVP favourite.

Four players have a handicap but no logged rounds. They are marked `form assumed` throughout and are
running on a prior, not a read.

## The three betting phases

A tote has no concept of taking a price — everyone in a pool gets identical terms whenever they bet.
Without an adjustment, betting early would simply be a worse bet: same return, less information. Hence
three phases, all feeding the same pool on each market.

1. **Ante-post** — now until the handicaps are declared on the first night. Prices rest on last
   season's numbers and assumptions, so you are betting partly blind. Stakes struck here count 1.25×
   when the pool divides.
2. **Open** — from declaration until the first tee shot, Thursday 13:50. Handicaps are known and the
   model has been re-run, so the prices are real. Ordinary share: you are paying for certainty.
3. **Closed** — ten minutes before the relevant ball is struck, not on it. Automatic, off the tee times,
   so nobody has to remember and the organiser cannot conveniently forget.

Tee times are stored with an explicit `+02:00`, which is Spain in late September. They are therefore
absolute instants: a phone left on UK time computes the same closing moment as one on Spanish time. Each
market shows its cutoff in both. Do not rewrite these as bare local date strings.

The phase changes your share of the pool, not what you are betting on, and none of it reaches the
organiser. Set the multiplier to 1 in Admin to switch the whole idea off.

Admin controls the transition: tick **Handicaps declared** once they are agreed in the bar, correct the
handicaps, then Apply and re-run. Every price moves. There is also a manual close and an override for
fixing a stake keyed into the wrong column.

## Saving state

There is deliberately no backend. Pools, handicaps and the ledger live in the browser's local
storage. Admin → Save your state copies everything out as JSON; paste it back to restore, or to move
the board to another device.

## Deploying

Push to GitHub, then Settings → Pages → source `main`, folder `/root`. Live in a few minutes at
`https://<user>.github.io/<repo>`.

For a custom domain, add a CNAME record pointing `chipsip` at `<user>.github.io`, then enter
`chipsip.dominiontechops.com` in that same Pages settings screen and commit the resulting `CNAME`
file.

The site is public, which costs nothing here: the only genuinely secret content is encrypted.

## Updating during the trip

Edit `index.html`, commit, push. Pages redeploys in about a minute. Every change is a commit you can
roll back from a phone if something breaks in a Spanish villa.

## Novelty pricing

The golf markets come from the simulation. The novelty markets cannot — nobody has ever logged an air
shot — so they are *shaped* rather than simulated: weight per player is `exp(a·h + b·v)`, where `h` is
handicap in field-spreads above the median and `v` is volatility against a typical five-shot spread.
Weights normalise to exactly 100%, same as everywhere else. It is deterministic, so every phone shows the
same price and nobody can refresh into a better one.

Three exceptions to the formula:

- **Fewest Putts** runs the coefficients negative. It is the one novelty a good player wins.
- **First to Get Sunburnt** is priced off rounds played, not handicap. Hours in the sun, not shots.
- **Most Likely to Have a Heated Discussion** uses a hand-set `wts` map, because no handicap will ever tell
  you who fell out with whom last year. It also carries `winners: 2.2` — a row takes two men and sometimes
  three, the dead-heat rule splits the pool between them, so the book adds to 220% and the fair prices are
  correspondingly shorter. That is not an overround; it is what a multi-winner tote pays.

An unwon pool (nobody scores zero, nobody goes four-from-four) is **not** the organiser's. It rolls into
the kitty for next year's trip, declared in the ledger, and any backer can ask for his stake back instead
at any point up to the flight home. That opt-out is what keeps it clean: nothing is deducted from anybody
without consent, and the organiser takes nothing either way.

Singles only. No doubles, trebles or accumulators — a multiple needs the prices fixed at the moment of
striking, and fixing prices is what makes a man a bookmaker.

Markets that name one man and settle on his own behaviour — the Yes/No ones — carry a `subject`. He is
barred from betting on them either way, enforced in `check_bet_integrity()` against `market_subjects`,
not just in the page.

## Theme

Light and dark, toggled in the header, chosen from the system preference on a first visit and remembered
after that. It is applied by an inline script in `<head>` so there is no flash. Every colour is a CSS
variable on `:root`; if you add a bare hex to the stylesheet it will not follow the theme.

## Numbers that must stay derived

Points on offer, the player count and the sample-size wording are computed from the roster
(`pointsOnOffer()`), not typed in. An earlier build hard-coded "25 points" in three places and went on
promising them after a player was removed, while the simulation quietly refused to price anything.
Market cutoffs come from `cutoffOf(ROUND_TEE[r])` everywhere, including the "When each market shuts"
table — that table used to print the raw tee time and contradict the market cards by ten minutes.
