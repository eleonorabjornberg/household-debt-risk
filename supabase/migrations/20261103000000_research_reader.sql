-- research_reader: the project's one read-only login role (MCP server, evals, the site's Q&A, validation).
-- Replaces tableau_reader, which this migration removes.
--
-- Rights: SELECT on mart (tables and views) and on the three core dimension tables. Nothing in raw,
-- nothing in core.fact_quarterly, no writes anywhere. Sessions are read-only and time-limited by default.
-- The password is set out-of-band by the project owner in the Supabase SQL editor:
--   alter role research_reader password '<choose one>';

do $$ begin
  if not exists (select 1 from pg_roles where rolname = 'research_reader') then
    create role research_reader login noinherit;
  end if;
end $$;

alter role research_reader set default_transaction_read_only = on;
alter role research_reader set statement_timeout = '15s';
alter role research_reader set idle_in_transaction_session_timeout = '60s';

grant usage on schema mart, core to research_reader;
grant select on all tables in schema mart to research_reader;   -- includes the mart.dim_* views
grant select on core.dim_crisis, core.dim_risk_bucket, core.dim_series to research_reader;
alter default privileges in schema mart grant select on tables to research_reader;

drop policy if exists research_read on mart.debt_by_risk_holder;
create policy research_read on mart.debt_by_risk_holder for select to research_reader using (true);
drop policy if exists research_read on mart.public_share;
create policy research_read on mart.public_share        for select to research_reader using (true);
drop policy if exists research_read on mart.collateral_coverage;
create policy research_read on mart.collateral_coverage for select to research_reader using (true);
drop policy if exists research_read on mart.crisis_event_window;
create policy research_read on mart.crisis_event_window for select to research_reader using (true);
drop policy if exists research_read on mart.nyfed_by_type;
create policy research_read on mart.nyfed_by_type       for select to research_reader using (true);

-- ------------------------------------------------------------------ remove tableau_reader
do $$ begin
  if exists (select 1 from pg_roles where rolname = 'tableau_reader') then
    alter policy public_read on mart.debt_by_risk_holder to anon, authenticated;
    alter policy public_read on mart.public_share        to anon, authenticated;
    alter policy public_read on mart.collateral_coverage to anon, authenticated;
    alter policy public_read on mart.crisis_event_window to anon, authenticated;
    alter policy public_read on mart.nyfed_by_type       to anon, authenticated;
    alter default privileges in schema mart revoke select on tables from tableau_reader;
    revoke all on all tables in schema mart from tableau_reader;
    revoke all on core.dim_crisis, core.dim_risk_bucket, core.dim_series from tableau_reader;
    revoke usage on schema mart, core from tableau_reader;
    drop role tableau_reader;
  end if;
end $$;
