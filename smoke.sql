-- CHIP & SIP SMOKE TEST. Run in the Supabase SQL editor before launch day and after any change
-- to triggers, policies or the ledger. Everything is inside a transaction that rolls back, so it
-- writes nothing. Every line should say what it says it should say.
create or replace function pg_temp.try_bet(p_stake int, p_phase text) returns text
language plpgsql as $$
begin
  insert into public.bets(bettor,market,outcome,stake,phase)
  values (public.my_name(),'nov_air','Rob Parfitt',p_stake,p_phase);
  return 'accepted';
exception when others then return 'refused: '||sqlerrm;
end $$;

create or replace function pg_temp.try_over_limit() returns text language plpgsql as $$
begin
  insert into public.bets(bettor,market,outcome,stake,phase)
  select public.my_name(),'nov_air','Rob Parfitt',10,'antepost' from generate_series(1,6);
  return 'accepted - WRONG, the £50 limit did not fire';
exception when others then return 'refused: '||sqlerrm;
end $$;

begin;
  -- act as a real claimed punter
  select set_config('request.jwt.claims',
    json_build_object('sub', p.id::text, 'role','authenticated')::text, true)
  from public.profiles p where p.name='Jack Mulroy' limit 1;
  set local role authenticated;

  select public.my_name()                       as acting_as;
  select pg_temp.try_bet(1,'antepost')          as a_normal_bet;        -- expect: accepted
  select pg_temp.try_bet(20,'antepost')         as over_ten_pounds;     -- expect: refused, £10 max
  select pg_temp.try_over_limit()               as past_fifty_unpaid;   -- expect: refused, £50 limit
  select public.board_version()                 as version_moved;       -- expect: higher than before
rollback;

-- and the board itself, as a phone that is not signed in
begin;
  set local role anon;
  select jsonb_array_length(s->'mine')     as must_be_zero_mine,
         jsonb_array_length(s->'detail')   as must_be_zero_detail,
         jsonb_array_length(s->'myledger') as must_be_zero_ledger,
         jsonb_array_length(s->'totals')   as pool_rows,
         jsonb_array_length(s->'roster')   as roster_rows
  from (select public.board_state() as s) q;
rollback;
