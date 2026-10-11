"""Appendix: taxonomy document rule checks + document-vs-log comparison (book section 12.6.1). Run from inside extra/: python taxonomy_check.py"""
import re, json, pandas as pd, duckdb
pd.set_option("display.width", 200); pd.set_option("display.max_colwidth", 60)
events = pd.read_csv("../data/taxonomy_events.csv").fillna("")
props  = pd.read_csv("../data/taxonomy_properties.csv").fillna("")
log    = pd.read_csv("../data/event_log.csv")
def show(title, df): print(f"\n### {title}\n"); print(df.to_markdown(index=False))

show("0. taxonomy_events (head)", events.head(6))
show("0. taxonomy_properties (head)", props.head(5)[["property_name","scope","data_type","allowed_values","description"]])
show("0. event_log (head)", log.head(4))

# ---------- 1. Name and type rule checks ----------
PREFIXES = ("page_view_", "tap_", "view_", "system_")
PAST_TENSE = re.compile(r"_(started|renewed|cancelled|granted|sent|completed|failed)$")
def event_issues(r):
    n = r.event_name; out = []
    if not (n.startswith(PREFIXES) or PAST_TENSE.search(n)): out.append("no prefix")
    if n != n.lower() or not re.fullmatch(r"[a-z0-9_]+", n): out.append("not snake_case")
    if r.description.strip() == "": out.append("no description")
    return out
ev_v = events.assign(issues=events.apply(event_issues, axis=1)).query("issues.str.len() > 0")
ev_v = ev_v.assign(issues=ev_v.issues.str.join(", "))[["event_name","event_type","platform","issues"]]
show("1a. Event naming rule violations", ev_v)

def prop_issues(r):
    out = []
    if r.data_type == "enum" and r.allowed_values == "": out.append("enum without allowed values")
    n_ev = len([e for e in r.events.split("|") if e])
    if r.scope == "event" and n_ev >= 0.8 * len(events): out.append(f"attached to {n_ev} events → user property candidate")
    return out
pr_v = props.assign(issues=props.apply(prop_issues, axis=1)).query("issues.str.len() > 0")
pr_v = pr_v.assign(issues=pr_v.issues.str.join(", "))[["property_name","scope","data_type","issues"]]
show("1b. Property rule violations", pr_v)

def event_kind(n):
    for p, k in zip(PREFIXES, ("page view","tap/click","impression","system")):
        if n.startswith(p): return k
    return "system" if PAST_TENSE.search(n) else "unclassified"
kinds = events.assign(kind=events.event_name.map(event_kind)).groupby("kind").size().rename("events").reset_index()
show("1c. Event count by type inferred from prefix", kinds.sort_values("events", ascending=False))

# ---------- 2. Question coverage check ----------
NEEDS = {
  "4-step onboarding conversion rate": [("system_first_launch", None), ("page_view_onboarding_step", "step"), ("system_permission_granted", "permission")],
  "Home banner click-through rate":   [("view_main_banner", "banner_id"), ("tap_main_banner", "banner_id")],
  "Content card click-through rate":  [("view_content_card", "position"), ("tap_content_card", "position")],
  "Paywall conversion by entry path": [("page_view_paywall", "source"), ("tap_purchase_button", "plan"), ("system_subscription_started", "plan")],
}
live = set(events.query("status == 'Live'").event_name)
prop_of = {r.property_name: set(r.events.split("|")) for r in props.itertuples()}
rows = []
for q, needs in NEEDS.items():
    for ev, pr in needs:
        ok_ev = ev in live; ok_pr = (pr is None) or (ev in prop_of.get(pr, set()))
        rows.append((q, ev, pr or "—", "O" if ok_ev else "X", "O" if ok_pr else "X"))
cov = pd.DataFrame(rows, columns=["question","event","property","event_exists","property_attached"])
show("2. Question coverage", cov)
verdict = cov.groupby("question").apply(lambda g: "answerable" if (g["event_exists"].eq("O") & g["property_attached"].eq("O")).all() else "not answerable").rename("verdict").reset_index()
show("2b. Verdict per question", verdict)

# ---------- 3. Document vs log comparison (DuckDB) ----------
con = duckdb.connect()
con.execute("CREATE TABLE taxonomy_events AS SELECT * FROM read_csv_auto('../data/taxonomy_events.csv')")
con.execute("CREATE TABLE taxonomy_properties AS SELECT * FROM read_csv_auto('../data/taxonomy_properties.csv', all_varchar=true)")
con.execute("CREATE TABLE event_log AS SELECT * FROM read_csv_auto('../data/event_log.csv')")
con.execute("UPDATE taxonomy_properties SET allowed_values = coalesce(allowed_values, ''), events = coalesce(events, '')")
results = {}
for name in ["undocumented_events", "dead_events", "enum_drift", "platform_asymmetry"]:
    results[name] = con.execute(open(f"sql/{name}.sql").read()).df()
    show(f"3. {name}", results[name])

# ---------- 4. Draft change request ----------
req = []
for r in ev_v.itertuples():
    req.append(("Modify", r.event_name, f"naming rule: {r.issues}"))
for r in pr_v.itertuples():
    req.append(("Modify", r.property_name, r.issues))
for r in cov.query("event_exists == 'X'").itertuples():
    req.append(("Add", r.event, f"event needed for '{r.question}' is missing"))
for r in results["undocumented_events"].itertuples():
    req.append(("Add", r.event_name, f"exists only in the log ({r.events:,} events) — document it or remove it"))
for r in results["dead_events"].itertuples():
    req.append(("Deprecate", r.event_name, "documented as Live, 0 events in the log"))
for r in results["enum_drift"].itertuples():
    req.append(("Modify", f"{r.property_name}={r.value}", f"value outside the allowed set ({r.platform} {r.app_version}, {r.events:,} events)"))
for r in results["platform_asymmetry"].itertuples():
    req.append(("Modify", r.event_name, f"platform asymmetry (iOS {r.ios_users}, Android {r.android_users})"))
request = pd.DataFrame(req, columns=["change_type","target","reason"]).drop_duplicates("target")
show("4. Draft change request", request)
print("\nRequest rows:", len(request), "| by type:", request["change_type"].value_counts().to_dict())
