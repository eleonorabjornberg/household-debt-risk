-- Who Holds the Debt? — core schema.
-- raw  : append-only observations, every vintage kept (Z.1 revises history each quarter)
-- core : dimensions + latest-vintage quarterly facts
-- mart : analysis-ready tables consumed by Tableau and the website (rebuilt by the pipeline)

create schema if not exists raw;
create schema if not exists core;
create schema if not exists mart;

-- ---------------------------------------------------------------- raw
create table raw.observations (
  source     text        not null check (source in ('z1','fred','nyfed')),
  series_id  text        not null,
  date       date        not null,
  value      numeric     not null,
  vintage    date        not null,           -- release date of the source file
  loaded_at  timestamptz not null default now(),
  primary key (series_id, date, vintage)
);

-- ---------------------------------------------------------------- core
create table core.dim_series (
  series_id        text primary key,
  source           text not null,
  role             text not null,
  description      text not null,
  debt_type        text,                    -- mortgage | consumer_credit
  risk_bucket      text,
  collateral_class text,
  unit             text not null default 'USD millions'
);

create table core.dim_risk_bucket (
  risk_bucket text primary key,
  label       text not null,
  is_public   boolean not null,
  sort_order  int not null
);

create table core.dim_crisis (
  crisis_id  text primary key,              -- e.g. 'gfc_2007'
  name       text not null,
  kind       text not null check (kind in ('nber_recession','policy_shock')),
  start_q    date not null,                 -- quarter-end date of NBER peak quarter / shock quarter
  end_q      date,                          -- quarter-end of NBER trough quarter (null for shocks)
  notes      text
);

-- Latest vintage only, quarter-end dates, USD millions (or native unit for context series).
create table core.fact_quarterly (
  series_id text not null references core.dim_series,
  date      date not null,
  value     numeric not null,
  vintage   date not null,
  primary key (series_id, date)
);

-- ---------------------------------------------------------------- mart
-- One row per quarter x risk bucket x debt type. Mortgage holder amounts are apportioned
-- to the household liability (holder share of all 1-4 family mortgages x FL153165105).
create table mart.debt_by_risk_holder (
  date            date    not null,
  risk_bucket     text    not null references core.dim_risk_bucket,
  debt_type       text    not null check (debt_type in ('mortgage','consumer_credit')),
  nominal_musd    numeric not null,
  real_musd       numeric,                  -- constant dollars of the latest CPI quarter
  share_of_total  numeric not null,         -- of scope total (mortgages + consumer credit), 0-1
  pct_of_dpi      numeric,                  -- of disposable personal income (SAAR), 0-1; null pre-1959
  primary key (date, risk_bucket, debt_type)
);

-- One row per quarter: headline series for the ratchet chart.
create table mart.public_share (
  date                   date primary key,
  scope_total_musd       numeric not null,
  public_musd            numeric not null,  -- federal_direct + gse_agency + state_local
  public_share           numeric not null,
  public_share_mortgage  numeric not null,
  public_share_cc        numeric not null,
  fed_mbs_musd           numeric,           -- QE overlay (WSHOMCB quarter-end), null pre-2009
  fed_mbs_share_of_scope numeric
);

create table mart.collateral_coverage (
  date                 date    not null,
  collateral_class     text    not null check (collateral_class in
                         ('home_backed','vehicle_backed','uncollateralized','other_nonrevolving')),
  debt_musd            numeric not null,
  collateral_value_musd numeric,            -- null where no collateral
  coverage_ratio       numeric,             -- collateral / debt; null where no collateral
  share_of_debt        numeric not null,    -- of scope total, 0-1
  is_estimated         boolean not null default false,  -- true where type split is imputed (early years)
  primary key (date, collateral_class)
);

-- Long format, so Tableau can small-multiple any metric across crises.
-- metric examples: 'public_share', 'share:gse_agency', 'share:uncollateralized', 'coverage:home_backed'
create table mart.crisis_event_window (
  crisis_id     text    not null references core.dim_crisis,
  metric        text    not null,
  q_offset      int     not null check (q_offset between -8 and 16),
  date          date    not null,
  value         numeric not null,
  value_at_t0   numeric not null,
  delta_from_t0 numeric not null,           -- value - value_at_t0 (percentage points for shares)
  primary key (crisis_id, metric, q_offset)
);

-- NY Fed CCP (2003+): balances and transitions into serious delinquency by loan type.
create table mart.nyfed_by_type (
  date                      date    not null,
  loan_type                 text    not null check (loan_type in
                              ('mortgage','heloc','auto','credit_card','student','other')),
  balance_busd              numeric,        -- USD billions as published
  transition_serious_pct    numeric,        -- % of balance transitioning into 90+ days delinquent (annualized, as published)
  primary key (date, loan_type)
);

-- ---------------------------------------------------------------- roles & access
-- Tableau: read-only, mart + core dims only.
do $$ begin
  if not exists (select 1 from pg_roles where rolname = 'tableau_reader') then
    create role tableau_reader login noinherit;  -- password set out-of-band: alter role tableau_reader password '...';
  end if;
end $$;
grant usage on schema mart, core to tableau_reader;
grant select on all tables in schema mart to tableau_reader;
grant select on core.dim_crisis, core.dim_risk_bucket, core.dim_series to tableau_reader;
alter default privileges in schema mart grant select on tables to tableau_reader;

-- Website: anon reads mart through PostgREST. Expose 'mart' in API settings (Exposed schemas).
grant usage on schema mart to anon, authenticated;
grant select on all tables in schema mart to anon, authenticated;
alter default privileges in schema mart grant select on tables to anon, authenticated;

alter table mart.debt_by_risk_holder enable row level security;
alter table mart.public_share        enable row level security;
alter table mart.collateral_coverage enable row level security;
alter table mart.crisis_event_window enable row level security;
alter table mart.nyfed_by_type       enable row level security;
create policy public_read on mart.debt_by_risk_holder for select to anon, authenticated, tableau_reader using (true);
create policy public_read on mart.public_share        for select to anon, authenticated, tableau_reader using (true);
create policy public_read on mart.collateral_coverage for select to anon, authenticated, tableau_reader using (true);
create policy public_read on mart.crisis_event_window for select to anon, authenticated, tableau_reader using (true);
create policy public_read on mart.nyfed_by_type       for select to anon, authenticated, tableau_reader using (true);

-- raw/core stay private (no grants to anon); enable RLS defensively.
alter table raw.observations    enable row level security;
alter table core.fact_quarterly enable row level security;
