-- =================================================================================================
-- CHIP & SIP 2026 — CLEAR THE BOOK FOR LAUNCH
--
-- Run this ONCE, immediately before the link goes to the group. It takes the board back to zero
-- money and zero results, and leaves the twelve weeks of setup standing.
--
-- THERE IS NOW A BUTTON FOR THIS. Admin -> Tools -> Clear the book for launch does exactly what
-- this script does, in one transaction, behind a phrase you have to type out in full. Use that.
-- This file is the fallback: if the page will not load on the day, or you want to read the
-- figures yourself before committing to anything, everything below still works.
--
-- HOW TO RUN IT
--   1. Open the Supabase SQL editor for project nqewsjczuqnkqehcayzq.
--   2. Run PART 1 on its own. It writes nothing. Read what it says is about to go.
--   3. If those numbers are what you expect, run PART 2. It ends in COMMIT.
--      If anything looks wrong, do not run PART 2 — nothing has changed yet.
--   4. Run PART 3 to check it landed.
--
-- WHAT GOES
--   bets            every stake struck in testing, voided ones included
--   payments        every recorded payment, so nobody starts the week with a phantom balance
--   payouts         every recorded hand-over
--   payment_claims  every "I have sent it" note
--   results         every settled market
--   client_errors   anything phones reported while you were building it
--   matches         results, margins and pairings cleared — the 25 slots themselves stay
--   settings        the withdrawn-market list and the closed flag, plus the side-game score
--
-- WHAT STAYS
--   roster          the 20 players, their teams and the captaincy
--   profiles        the men who have already claimed their name. They stay signed in, and your
--                   own owner access keeps working. Everybody else claims as he arrives.
--   owners          who gets Admin without the passphrase
--   admin_secret    the passphrase
--   settings        the declared handicaps, the published model prices, the payment link, the
--                   ante-post multiplier, the blind scale and the stake limits
--   market_subjects which market is about whom, so nobody can back a market about himself
--   backups         the snapshot history, including the one this script takes first
--
-- LAUNCH DAY, IN ORDER
--   1. Deploy the current build first (git push, then wait for GitHub Pages to go green). The
--      clear-out stamps a moment that only the current build knows how to read.
--   2. Run PART 1 here and read it.
--   3. Run PART 2. Every phone picks the change up within 45 seconds, throws away any half-built
--      slip left over from testing, and shows an empty board.
--   4. Run PART 3 and check every line says true.
--   5. Open the board on your own phone, put £1 on something, check it appears in My Bets and on
--      the Money tab, then void it. Then send the link.
--
-- IT IS RECOVERABLE. Step 1 of Part 2 snapshots everything the script can delete — bets,
-- payments, payouts, results, roster, matches, profiles, claims, owners, subjects and settings —
-- into the backups table, where it shows up in Admin under Backups.
-- =================================================================================================


-- =================================================================================================
-- PART 1 — WHAT IS ABOUT TO GO. Read only. Run this first and read it.
-- =================================================================================================

select 'ABOUT TO BE CLEARED' as section, 'bets (live)'      as what,
       count(*)::text || ' bets, £' || coalesce(sum(stake),0)::text as amount
  from public.bets where voided = false
union all select 'ABOUT TO BE CLEARED', 'bets (already voided)',
       count(*)::text || ' bets, £' || coalesce(sum(stake),0)::text
  from public.bets where voided
union all select 'ABOUT TO BE CLEARED', 'payments',
       count(*)::text || ' payments, £' || coalesce(sum(amount),0)::text
  from public.payments
union all select 'ABOUT TO BE CLEARED', 'payouts',
       count(*)::text || ' payouts, £' || coalesce(sum(amount),0)::text
  from public.payouts
union all select 'ABOUT TO BE CLEARED', 'payment claims', count(*)::text
  from public.payment_claims
union all select 'ABOUT TO BE CLEARED', 'settled markets', count(*)::text
  from public.results
union all select 'ABOUT TO BE CLEARED', 'client errors', count(*)::text
  from public.client_errors
union all select 'ABOUT TO BE CLEARED', 'match results', count(*)::text
  from public.matches where result is not null
union all select 'ABOUT TO BE CLEARED', 'match pairings', count(*)::text
  from public.matches where blue is not null and array_length(blue,1) > 0
union all select 'STAYS', 'roster',
       count(*) filter (where playing)::text || ' playing, '
       || count(*) filter (where not playing)::text || ' not'
  from public.roster
union all select 'STAYS', 'name claims',
       coalesce(string_agg(name, ', ' order by claimed_at), 'none')
  from public.profiles
union all select 'STAYS', 'admin without the passphrase',
       coalesce(string_agg(name, ', ' order by name), 'none')
  from public.owners
union all select 'STAYS', 'declared handicaps',
       case when (select data ? 'hcp' from public.settings where id=1)
            then 'yes, ' || (select jsonb_array_length(data->'hcp') from public.settings where id=1)::text || ' players'
            else 'none published' end
union all select 'STAYS', 'published model prices',
       coalesce((select (data->'prices'->>'n') || ' simulations, published '
                        || to_char(to_timestamp((data->'prices'->>'at')::bigint/1000),
                                   'DD Mon HH24:MI')
                 from public.settings where id=1),
                'none published')
union all select 'STAYS', 'payment link',
       coalesce((select nullif(data->>'payLink','') from public.settings where id=1), 'not set')
union all select 'STAYS', 'match slots', count(*)::text || ' waiting for the draw'
  from public.matches
union all select 'CHECK THIS', 'roster entries not playing',
       coalesce(string_agg(name, ', ' order by name), 'none')
  from public.roster where not playing;

-- Anybody who would be left out of pocket or in credit if you cleared without reading this.
select 'these balances are about to be wiped' as note, bettor, staked, paid, balance
from public.ledger order by balance desc;


-- =================================================================================================
-- PART 2 — THE CLEAR-OUT. This one writes. It ends in COMMIT.
-- =================================================================================================

begin;

-- 1. Snapshot first. Carries everything below and shows up in Admin under Backups.
select public.take_backup('cleared the book for launch') as snapshot_id;

-- 2. The money and the results.
delete from public.payment_claims;
delete from public.payouts;
delete from public.payments;
delete from public.results;
delete from public.bets;

-- 3. Anything phones reported while you were building it.
delete from public.client_errors;

-- 4. The card. The 25 slots stay; what was written on them goes, so the Score tab opens at 0–0
--    with nothing played and no pairings showing.
update public.matches
   set result = null, margin = null, ended = null, blue = '{}', red = '{}';

-- 5. Settings. Only the things that are state rather than setup:
--    suspended  markets withdrawn during testing go back on the board
--    closed     betting is open
--    bonusB/R   any side-game points typed in while testing
--    Everything else — the handicaps, the published prices, the payment link, the multipliers —
--    is deliberately left alone.
--    cleared    stamps the moment the book emptied. Every phone reads this on its next poll and
--               throws away its own half-built slip and any "I have sent it" note left over from
--               testing. Nobody has to clear a browser.
update public.settings
   set data = (data - 'suspended' - 'bonusB' - 'bonusR')
              || jsonb_build_object('closed', false,
                                    'cleared', (extract(epoch from now())*1000)::bigint),
       updated_at = now()
 where id = 1;

-- 6. Read it back BEFORE committing. Every number here should be zero except the ones that stay.
select 'after the clear-out' as section,
       (select count(*) from public.bets)                                as bets,
       (select count(*) from public.payments)                            as payments,
       (select count(*) from public.payouts)                             as payouts,
       (select count(*) from public.payment_claims)                      as claims,
       (select count(*) from public.results)                             as settled_markets,
       (select count(*) from public.client_errors)                       as client_errors,
       (select count(*) from public.matches where result is not null)    as match_results,
       (select count(*) from public.ledger)                              as ledger_rows,
       (select count(*) from public.pool_totals)                         as pools;

select 'still standing' as section,
       (select count(*) from public.roster where playing)                as players,
       (select count(*) from public.profiles)                            as name_claims,
       (select count(*) from public.owners)                              as admins,
       (select count(*) from public.matches)                             as match_slots,
       (select count(*) from public.backups)                             as snapshots,
       (select (data->'prices'->>'n') from public.settings where id=1)   as prices_published,
       (select jsonb_array_length(data->'hcp') from public.settings where id=1) as handicaps;

commit;
-- rollback;   -- swap for the COMMIT above if either summary looks wrong


-- =================================================================================================
-- PART 3 — PROVE IT IS CLEAN. Read only. Run after Part 2.
-- =================================================================================================

-- Every one of these must be true.
select 'no money anywhere'      as check,
       (select count(*) from public.bets) = 0
   and (select count(*) from public.payments) = 0
   and (select count(*) from public.payouts) = 0                          as pass
union all
select 'nothing settled',
       (select count(*) from public.results) = 0
   and (select count(*) from public.matches where result is not null) = 0
union all
select 'nobody owes and nobody is owed',
       (select count(*) from public.ledger) = 0
union all
select 'every market back on the board',
       not coalesce((select data ? 'suspended' from public.settings where id=1), false)
union all
select 'betting is open',
       coalesce((select not (data->>'closed')::boolean from public.settings where id=1), true)
union all
select 'the 20 are still there',
       (select count(*) from public.roster where playing) = 20
union all
select 'the prices survived',
       coalesce((select data ? 'prices' from public.settings where id=1), false)
union all
select 'the handicaps survived',
       coalesce((select data ? 'hcp' from public.settings where id=1), false)
union all
select 'you still have admin',
       (select count(*) from public.owners) > 0
union all
select 'the snapshot is there',
       exists (select 1 from public.backups where reason = 'cleared the book for launch')
union all
select 'phones will clear their own slips',
       coalesce((select data ? 'cleared' from public.settings where id=1), false);

-- And a real bet still goes on. Rolled back, so it clears nothing and leaves nothing behind.
create or replace function pg_temp.launch_smoke() returns text language plpgsql as $$
begin
  insert into public.bets(bettor,market,outcome,stake,phase)
  values (public.my_name(),'nov_air','Rob Parfitt',1,'antepost');
  return 'a £1 bet goes on: PASS';
exception when others then return 'a £1 bet FAILED: '||sqlerrm;
end $$;

begin;
  select set_config('request.jwt.claims',
    json_build_object('sub', p.id::text, 'role','authenticated')::text, true)
  from public.profiles p where p.name is not null limit 1;
  set local role authenticated;
  select pg_temp.launch_smoke() as final_check;
rollback;
