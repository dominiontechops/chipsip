-- N2 LOAD TEST. Run this in the Supabase SQL editor. It only reads.
--
-- What it measures: the work the DATABASE does. It does not measure the network, and that is the
-- point — the old road paid for 7 to 10 separate HTTP round trips per phone per poll, and the
-- new road pays for one. The figures below are the floor under that, not the whole cost.
--
-- 20 phones polling every 45 seconds:
--   old road   20 x 10 queries / 45s = 267 queries a minute, every minute, whatever is happening
--   new road   20 x  1 query   / 45s =  27 queries a minute on a quiet board,
--              plus one full read per phone only when the book has actually moved
create or replace function pg_temp.bench(n int)
returns table(road text, total_ms numeric, each_ms numeric)
language plpgsql as $$
declare i int; t0 timestamptz; j jsonb; b bigint;
begin
  t0 := clock_timestamp();
  for i in 1..n loop
    perform data from public.settings where id=1;
    perform * from public.pool_totals;
    perform name,team,playing,role from public.roster order by name;
    perform name from public.claimed_names;
    perform market,outcomes,void,note,settled_at from public.results;
    perform session,slot,blue,red,result,margin,ended from public.matches order by session,slot;
    perform * from public.standings;
  end loop;
  road:='old: 7 reads a poll'; total_ms:=round(extract(epoch from clock_timestamp()-t0)*1000,1);
  each_ms:=round(total_ms/n,3); return next;

  t0 := clock_timestamp();
  for i in 1..n loop b := public.board_version(); end loop;
  road:='new: board_version()'; total_ms:=round(extract(epoch from clock_timestamp()-t0)*1000,1);
  each_ms:=round(total_ms/n,3); return next;

  t0 := clock_timestamp();
  for i in 1..n loop j := public.board_state(); end loop;
  road:='new: board_state() full read'; total_ms:=round(extract(epoch from clock_timestamp()-t0)*1000,1);
  each_ms:=round(total_ms/n,3); return next;
end $$;

-- 200 = 20 phones x 10 polls
select * from pg_temp.bench(200);

-- Payload the phone actually pulls on a full read
select pg_column_size(public.board_state()) as bytes, length(public.board_state()::text) as chars;
