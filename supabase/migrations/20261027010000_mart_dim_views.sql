-- Expose the two small reference dims to the website through the mart schema.
-- security_invoker: the view runs with the caller's rights, so anon needs SELECT on the base tables.
-- core is not an exposed API schema, so this grants nothing beyond these two dims.
grant usage on schema core to anon, authenticated;
grant select on core.dim_crisis, core.dim_risk_bucket to anon, authenticated;

create or replace view mart.dim_crisis with (security_invoker = true) as
  select * from core.dim_crisis;
create or replace view mart.dim_risk_bucket with (security_invoker = true) as
  select * from core.dim_risk_bucket;

grant select on mart.dim_crisis, mart.dim_risk_bucket to anon, authenticated, tableau_reader;
