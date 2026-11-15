-- Ask Hot Potato (PLAN D6) limit counters in Supabase, Eleonora's choice of 2026-11-15 (replaces the Redis store,
-- d6-store (a), which needed a paid store). Holds only counters: questions per hashed visitor per UTC day and
-- the app's spend per day. No question text, no IP addresses.
-- Access: the table sits in a private schema with RLS on and no policies; the two functions are SECURITY DEFINER
-- and only service_role (the server's secret key, set in Vercel) may call them. anon/authenticated cannot read,
-- write or call anything here, so a visitor cannot reset or inflate the counters.

create schema if not exists ask_private;
revoke all on schema ask_private from public;

create table if not exists ask_private.counters (
  key        text primary key check (key like 'ask:%' and length(key) <= 200),
  value      numeric not null default 0,
  expires_at timestamptz not null
);
alter table ask_private.counters enable row level security;
revoke all on ask_private.counters from public;

create or replace function public.ask_limit_add(p_key text, p_by numeric, p_ttl_seconds integer)
returns numeric
language plpgsql
security definer
set search_path = ''
as $$
declare v numeric;
begin
  if p_key is null or p_key not like 'ask:%' or length(p_key) > 200 then raise exception 'bad key'; end if;
  if p_by is null or p_by < 0 or p_by > 100 then raise exception 'bad increment'; end if;
  if p_ttl_seconds is null or p_ttl_seconds < 1 or p_ttl_seconds > 7 * 86400 then raise exception 'bad ttl'; end if;
  delete from ask_private.counters where expires_at < now() - interval '1 day';  -- housekeeping
  insert into ask_private.counters as c (key, value, expires_at)
  values (p_key, p_by, now() + make_interval(secs => p_ttl_seconds))
  on conflict (key) do update
    set value = case when c.expires_at < now() then excluded.value else c.value + excluded.value end,
        expires_at = excluded.expires_at
  returning c.value into v;
  return v;
end $$;

create or replace function public.ask_limit_get(p_key text)
returns numeric
language sql
stable
security definer
set search_path = ''
as $$
  select coalesce((select value from ask_private.counters where key = p_key and expires_at >= now()), 0)
$$;

revoke all on function public.ask_limit_add(text, numeric, integer) from public, anon, authenticated;
revoke all on function public.ask_limit_get(text) from public, anon, authenticated;
do $$ begin
  if exists (select 1 from pg_roles where rolname = 'service_role') then
    execute 'grant usage on schema ask_private to service_role';
    execute 'grant execute on function public.ask_limit_add(text, numeric, integer) to service_role';
    execute 'grant execute on function public.ask_limit_get(text) to service_role';
  end if;
end $$;
