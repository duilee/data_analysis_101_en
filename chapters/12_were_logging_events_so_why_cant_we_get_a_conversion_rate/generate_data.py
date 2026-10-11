"""We're Logging Events, So Why Can't We Get a Conversion Rate? — example data generator.

For a fictional content app (4-step onboarding → home → content detail → home banner → payment),
build two taxonomy documents (taxonomy_events.csv, taxonomy_properties.csv) and
30 days of event logs (event_log.csv, 2026-08-01 to 08-30). Seed is fixed.

Five incidents that silently break the logs are planted in the 3.5.0 release on 2026-08-25. All five are caught by the standard thresholds (±60%, at least 50 events).
  1 iOS   tap_content_card          event count -65%  (tap handler bug drops the event)        → caught (sharp drop)
  2 Android view_content_card       event count 2x    (impression event fires twice)           → caught (sharp rise)
  3 iOS   page_view_content_detail  content_id fill rate 100% → 30% (property missing)       → caught (null ratio)
  4 Android page_view_home          event count -70%  (home-entry event dropped)              → caught (sharp drop)
  5 system_subscription_renewed (server)  event count -100% (renewal batch stopped)           → caught (sharp drop, 0 events)
"""
import json, os
import numpy as np
import pandas as pd

SEED = 11
rng = np.random.default_rng(SEED)
HERE = os.path.dirname(os.path.abspath(__file__))
START = pd.Timestamp("2026-08-01")
DAYS = 30
RELEASE_DAY = 24                  # 3.5.0 from 2026-08-25 onward
N_USERS = 3000

# ---------- 1. Taxonomy document: events ----------
E = []
def ev(name, etype, screen, desc, source="Client", platform="iOS|Android", status="Live", lifetime="Permanent", ver="3.0.0"):
    E.append((name, etype, source, platform, screen, desc, status, lifetime, ver))
ev("system_first_launch", "System", "app", "First launch after install. Base event for every funnel")
ev("page_view_onboarding_step", "Page View", "onboarding", "Entered an onboarding step screen. The step property tells the steps apart")
ev("tap_onboarding_next", "Tap/Click", "onboarding", "Tapped the onboarding Next button")
ev("tap_onboarding_skip", "Tap/Click", "onboarding", "Tapped Skip in onboarding")
ev("system_permission_granted", "System", "onboarding", "Permission grant result. The permission property tells the kinds apart")
ev("page_view_home", "Page View", "home", "Entered the home screen")
ev("view_main_banner", "View", "home", "Top banner on home shown")
ev("tap_main_banner", "Tap/Click", "home", "Tapped the top banner on home")
ev("view_content_card", "View", "home", "Content card in the home feed shown")
ev("tap_content_card", "Tap/Click", "home", "Tapped a content card in the home feed")
ev("page_view_content_detail", "Page View", "content_detail", "Entered the content detail screen")
ev("tap_like_button", "Tap/Click", "content_detail", "Tapped Like on a content item")
ev("tap_share_button", "Tap/Click", "content_detail", "Tapped the Share button on a content item")
ev("page_view_search", "Page View", "search", "Entered the search screen")
ev("tap_search_result", "Tap/Click", "search", "Tapped a search result")
ev("page_view_paywall", "Page View", "paywall", "Entered the payment screen. The source property tells the entry paths apart")
ev("tap_purchase_button", "Tap/Click", "paywall", "Tapped the Purchase button")
ev("system_subscription_started", "System", "server", "Subscription started (server)", source="Server")
ev("system_subscription_renewed", "System", "server", "Subscription renewed (server daily batch)", source="Server")
ev("page_view_settings", "Page View", "settings", "Entered the settings screen")
ev("tap_theme_toggle", "Tap/Click", "settings", "Tapped the theme toggle")
ev("system_push_sent", "System", "server", "Push sent (server)", source="Server")
ev("tap_push_notification", "Tap/Click", "app", "Tapped a push notification")
ev("page_view_profile", "Page View", "profile", "Entered the profile screen")
events = pd.DataFrame(E, columns=["event_name","event_type","source","platform","screen_name","description","status","lifetime","version_added"])

# ---------- 2. Taxonomy document: properties ----------
P = [
 ("step","event","enum","1|2|3|4","Onboarding step number","page_view_onboarding_step|tap_onboarding_next|tap_onboarding_skip"),
 ("permission","event","enum","notification|camera|location","Kind of permission granted","system_permission_granted"),
 ("banner_id","event","string","","Banner identifier","view_main_banner|tap_main_banner"),
 ("content_id","event","string","","Content identifier","view_content_card|tap_content_card|page_view_content_detail|tap_like_button|tap_share_button"),
 ("content_type","event","enum","article|video","Kind of content","view_content_card|tap_content_card|page_view_content_detail"),
 ("position","event","int","","Position within the feed (0-based)","view_content_card|tap_content_card|tap_search_result"),
 ("channel","event","enum","kakao|instagram|link","Share channel","tap_share_button"),
 ("source","event","enum","home|content_detail|settings|push","Entry path to the payment screen","page_view_paywall"),
 ("plan","event","enum","monthly|yearly","Subscription plan","tap_purchase_button|system_subscription_started|system_subscription_renewed"),
 ("theme","event","enum","dark|light","Theme switched to","tap_theme_toggle"),
 ("push_type","event","enum","daily|content|promo","Kind of push","system_push_sent|tap_push_notification"),
 ("subscription_status","user","enum","free|trial|paid|churned","Subscription status",""),
 ("signup_date","user","date","","Signup date",""),
]
props = pd.DataFrame(P, columns=["property_name","scope","data_type","allowed_values","description","events"])

# ---------- 3. Event log ----------
rows = []
def log(t, uid, plat, ver, name, screen, **pr):
    rows.append((t.strftime("%Y-%m-%d %H:%M:%S"), uid, plat, ver, name, screen, json.dumps(pr, ensure_ascii=False)))

def version_for(day):      # assume 3.5.0 spreads quickly from release day
    if day < RELEASE_DAY: return rng.choice(["3.4.0","3.4.1"], p=[0.3,0.7])
    return rng.choice(["3.4.1","3.5.0"], p=[0.15,0.85])

for i in range(N_USERS):
    uid = f"u{i:05d}"
    plat = "iOS" if rng.random() < 0.55 else "Android"
    d0 = int(rng.integers(-20, DAYS))            # install day (some before the observation window)
    sub = bool(rng.random() < 0.30)
    if d0 >= 0:                                  # onboarding for users who installed inside the window
        t = START + pd.Timedelta(days=d0, minutes=int(rng.integers(0, 24*60)))
        ver = version_for(d0)
        log(t, uid, plat, ver, "system_first_launch", "app")
        for step in (1,2,3,4):
            t += pd.Timedelta(seconds=int(rng.integers(5, 60)))
            log(t, uid, plat, ver, "page_view_onboarding_step", "onboarding", step=step)
            if rng.random() < 0.06: log(t, uid, plat, ver, "tap_onboarding_skip", "onboarding", step=step); break
            if rng.random() < 0.10: break
            log(t, uid, plat, ver, "tap_onboarding_next", "onboarding", step=step)
        else:
            if rng.random() < 0.7: log(t, uid, plat, ver, "system_permission_granted", "onboarding", permission="notification")
    for day in range(max(d0, 0), DAYS):
        age = day - d0
        if rng.random() > 0.55 * 0.93 ** age + 0.10: continue
        t = START + pd.Timedelta(days=day, minutes=int(rng.integers(0, 24*60)))
        ver = version_for(day)
        broken = day >= RELEASE_DAY and ver == "3.5.0"
        if not (broken and plat == "Android" and rng.random() < 0.85):                                           # incident 4
            log(t, uid, plat, ver, "page_view_home", "home")
        if rng.random() < 0.6:
            bid = f"b{int(rng.integers(1,6))}"
            log(t, uid, plat, ver, "view_main_banner", "home", banner_id=bid)
            if rng.random() < 0.08: log(t, uid, plat, ver, "tap_main_banner", "home", banner_id=bid)
        for pos in range(int(rng.integers(2, 6))):
            cid = f"c{int(rng.integers(1, 400)):03d}"; ctype = rng.choice(["article","video"])
            log(t, uid, plat, ver, "view_content_card", "home", content_id=cid, content_type=ctype, position=pos)
            if broken and plat == "Android":                                                                     # incident 2
                log(t, uid, plat, ver, "view_content_card", "home", content_id=cid, content_type=ctype, position=pos)
            if rng.random() < 0.25:
                if not (broken and plat == "iOS" and rng.random() < 0.85):                                        # incident 1
                    log(t, uid, plat, ver, "tap_content_card", "home", content_id=cid, content_type=ctype, position=pos)
                detail = dict(content_id=cid, content_type=ctype)
                if broken and plat == "iOS" and rng.random() < 0.85: detail["content_id"] = None                  # incident 3
                log(t, uid, plat, ver, "page_view_content_detail", "content_detail", **detail)
                if rng.random() < 0.3: log(t, uid, plat, ver, "tap_like_button", "content_detail", content_id=cid)
                if rng.random() < 0.08: log(t, uid, plat, ver, "tap_share_button", "content_detail", content_id=cid, channel=rng.choice(["kakao","instagram","link"]))
        if rng.random() < 0.15:
            log(t, uid, plat, ver, "page_view_search", "search")
            if rng.random() < 0.5: log(t, uid, plat, ver, "tap_search_result", "search", position=int(rng.integers(0,5)))
        if rng.random() < 0.08:
            log(t, uid, plat, ver, "page_view_settings", "settings")
            if rng.random() < 0.3: log(t, uid, plat, ver, "tap_theme_toggle", "settings", theme=rng.choice(["dark","light"]))
        if not sub and rng.random() < 0.10:
            log(t, uid, plat, ver, "page_view_paywall", "paywall", source=rng.choice(["home","content_detail","settings"]))
            if rng.random() < 0.15:
                plan = rng.choice(["monthly","yearly"], p=[0.7,0.3])
                log(t, uid, plat, ver, "tap_purchase_button", "paywall", plan=plan)
                log(t, uid, plat, ver, "system_subscription_started", "server", plan=plan); sub = True
        if rng.random() < 0.04: log(t, uid, plat, ver, "page_view_profile", "profile")
    # server events: subscription renewal daily batch (incident 5: stops after the release), push
    if sub:
        for day in range(DAYS):
            if day >= RELEASE_DAY: break                                                                          # incident 5
            if rng.random() < 0.15: log(START + pd.Timedelta(days=day, hours=3), uid, plat, "server", "system_subscription_renewed", "server", plan="monthly")
    for day in range(max(d0, 0), DAYS):
        if rng.random() < 0.06:
            t = START + pd.Timedelta(days=day, hours=9)
            log(t, uid, plat, "server", "system_push_sent", "server", push_type="daily")
            if rng.random() < 0.2: log(t + pd.Timedelta(minutes=3), uid, plat, version_for(day), "tap_push_notification", "app", push_type="daily")

logdf = pd.DataFrame(rows, columns=["event_time","user_id","platform","app_version","event_name","screen_name","properties"]).sort_values("event_time")
os.makedirs(os.path.join(HERE, "data"), exist_ok=True)
events.to_csv(os.path.join(HERE, "data", "taxonomy_events.csv"), index=False)
props.to_csv(os.path.join(HERE, "data", "taxonomy_properties.csv"), index=False)
logdf.to_csv(os.path.join(HERE, "data", "event_log.csv"), index=False)
print(f"events {len(events)} / properties {len(props)} / log rows {len(logdf):,} / users {logdf.user_id.nunique():,} / days {logdf.event_time.str[:10].nunique()}")
