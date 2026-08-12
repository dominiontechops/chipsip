# Chip &amp; Sip 2026

Tote-pool betting board and form book for the Málaga golf trip, 24–27 September 2026.

One self-contained HTML file. No build step, no server, no dependencies. Open `index.html` in
any browser and it works, including offline on a plane.

## Live site

GitHub Pages serves `index.html` from the repository root. See **Deploying** below.

## What's in it

| Tab | What it does |
|---|---|
| **Pools** | Every market, ante-post and open stakes in whole pounds, implied odds against the model's fair price, and the edge between them |
| **Form Book** | All 20 players with handicap, form, volatility and sample size, plus the simulated prices |
| **Schedule** | Transfers, tee times and collections for all four days, and the four courses |
| **Rules** | How the pools settle. Read this before arguing |
| **Blue Room** | Encrypted. Opposition dossiers, handicap watchlist, captain's notes |
| **Admin** | Roster, handicaps, courses, payment link, ledger, handicap declaration |

## Passphrases

- **Admin** — set in the `ADMIN_PW` constant near the top of the `<script>` block. A soft gate, and
  that is all it needs to be: everything behind it lives in the visitor's own browser, so the worst a
  snooper can do is change numbers on their own screen.
- **Blue Room** — genuinely encrypted with AES-GCM, key derived from the passphrase via PBKDF2 at
  250,000 iterations. The passphrase is **not** in this file. Only ciphertext ships, so Red Team
  cannot read it from View Source no matter how hard they look.

**To change the Blue Room passphrase, do not hand-edit anything.** Unlock the Blue Room, go to
Admin → Re-seal, enter the new passphrase, and paste the line it gives you over the existing
`const BLUE = {...}` declaration. Editing the ciphertext by hand will make it permanently unreadable.

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

## Ante-post

A tote has no concept of taking a price — everyone in a pool gets the same terms whenever they bet.
Without an adjustment, betting early is simply a worse bet: same return, less information. The
ante-post multiplier fixes that by giving stakes struck before the handicaps are declared a larger
share of the same pool. It moves money between backers, never to the organiser, so there is still no
rake. Set it to 1 in Admin to switch the idea off.

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
