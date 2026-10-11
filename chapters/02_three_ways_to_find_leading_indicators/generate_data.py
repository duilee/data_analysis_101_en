"""Example data generator for the leading-indicator practice.

Simulates each new user's install (D0) session as an *ordered event flow* and writes a single raw
event log to data/event_log.csv. This one log is the input to all three practice sections.

  - 2.5.2 (EDA)   : label users as D7 retained / churned, then compare share and average count of D0~D1 behaviors
  - 2.5.3 (SHAP)  : predict D7 retention from per-user behavior features and decompose the contributions
  - 2.5.4 (Sankey): draw the install-session event sequence as a flow, colored by D7 retention per transition

The key idea is the "planted truth". Every user gets a latent quality value q, and q drives both
(a) which behaviors they perform and (b) whether they are retained on D7. On top of that, the retention
probability (logit) is built directly as a *function of the behavior features and flow branches*, so all
three methods recover the same leading indicators (tutorial completion, content views, likes, etc.) in
their own way. The data is synthetic, but the point of the practice is that the results trace back to the truth.

Planted relationships (should show up consistently across the three practice sections):
  - tap_tutorial_complete / system_push_permission_granted : share is much higher among retained users
  - page_view_content_detail count          : more views -> higher retention (monotonic increase)
  - tap_like_button                   : retention kinks upward again at 3 or more likes (threshold / aha moment)
  - session_duration_sec           : retention kinks upward at roughly 150 seconds or more (threshold / aha moment)
  - tap_search_button                    : low share, but users who search do it several times (higher average count)
  - view_error_popup                    : more popups -> lower retention (negative contribution)
  - flow branches                       : skipping the tutorial / detouring home -> profile/settings lowers retention,
                                      home -> content view -> like raises it
"""

import os
import sys

import numpy as np
import pandas as pd

# Keep stdout UTF-8 when it is captured through a pipe (no effect on direct console output)
sys.stdout.reconfigure(encoding="utf-8")

SEED = 314
N_USERS = 12_000
INSTALL_DAYS = 7                       # Spread install dates evenly over this window (so D7 is observable)
BASE_DATE = pd.Timestamp("2026-01-01")  # First possible install date

# Event metadata: event_name -> (screen_name, description)
EVENT_META = {
    "system_app_install":        ("app",            "App installed"),
    "page_view_onboarding_step":  ("onboarding",     "Onboarding step viewed"),
    "tap_tutorial_complete":          ("onboarding",     "Tutorial completed"),
    "system_push_permission_granted":                 ("permission",     "Push notification permission granted"),
    "page_view_home":             ("home",           "Home screen viewed"),
    "page_view_content_detail":               ("content_detail", "Content detail viewed"),
    "tap_like_button":               ("content_detail", "Content liked"),
    "tap_share_button":              ("content_detail", "Content shared"),
    "tap_search_button":                ("search",         "Search used"),
    "page_view_profile":          ("profile",        "Profile viewed"),
    "page_view_settings":              ("settings",       "Settings opened"),
    "view_error_popup":                ("error",          "Error popup shown"),
}


def sigmoid(x):
    return 1.0 / (1.0 + np.exp(-x))


def simulate_user(uid, q, install_dt, rng, rows):
    """Simulate one user's install session (D0) in order and append the events to rows.

    Returns: (d7_retained, d1_retained, session_duration_sec) -- used to stamp the return activity afterwards.
    """
    # Relative clock (seconds) running inside the session. Each event lingers a few to several dozen seconds.
    clock = {"t": 0}

    def emit(event_name, dt_base, count=1, gap=(3, 40)):
        clock["t"] += int(rng.integers(gap[0], gap[1] + 1))
        ts = dt_base + pd.Timedelta(seconds=clock["t"])
        screen, desc = EVENT_META[event_name]
        rows.append((ts, ts.date(), uid, event_name, screen, count, desc))

    # --- D0 install session: a branching flow ----------------------------------
    emit("system_app_install", install_dt, gap=(0, 1))
    emit("page_view_onboarding_step", install_dt, gap=(2, 8))

    # Branch 1) complete the tutorial vs skip it (higher q -> more likely to complete)
    tutorial = rng.random() < sigmoid(0.9 * q + 0.4)
    if tutorial:
        emit("tap_tutorial_complete", install_dt, gap=(5, 30))

    # Push permission granted
    push = rng.random() < sigmoid(0.7 * q + 0.0)
    if push:
        emit("system_push_permission_granted", install_dt, gap=(2, 10))

    emit("page_view_home", install_dt, gap=(3, 15))

    # Branch 2) from home, view content vs detour to profile/settings
    went_content = rng.random() < sigmoid(1.0 * q + 0.3 + (0.4 if tutorial else 0.0))
    content_cnt = like_cnt = search_cnt = share_cnt = profile_cnt = settings_cnt = 0

    if went_content:
        n_content = 1 + int(rng.poisson(max(0.2, np.exp(0.2 + 0.5 * q))))
        n_content = min(n_content, 8)
        for _ in range(n_content):
            emit("page_view_content_detail", install_dt, count=int(rng.integers(1, 4)), gap=(8, 60))
            content_cnt += 1
            # Branch 3) like the content after viewing it (higher q -> more likely)
            if rng.random() < sigmoid(0.8 * q + 0.0):
                emit("tap_like_button", install_dt, gap=(2, 8))
                like_cnt += 1
            if rng.random() < sigmoid(-1.2 + 0.4 * q):
                emit("tap_share_button", install_dt, gap=(3, 12))
                share_cnt += 1

        # Search: low share (rare), but a user who searches once searches several times -> higher average count
        if rng.random() < sigmoid(-1.4 + 0.8 * q):
            n_search = min(1 + int(rng.poisson(max(0.1, np.exp(0.3 + 0.7 * q)))), 6)
            for _ in range(n_search):
                emit("tap_search_button", install_dt, count=int(rng.integers(1, 3)), gap=(5, 30))
                search_cnt += 1
    else:
        if rng.random() < 0.5:
            emit("page_view_profile", install_dt, gap=(3, 15))
            profile_cnt += 1
        else:
            emit("page_view_settings", install_dt, gap=(3, 15))
            settings_cnt += 1

    # Error popups: more frequent for low q
    n_err = min(int(rng.poisson(max(0.02, np.exp(-0.5 - 0.7 * q)))), 3)
    for _ in range(n_err):
        emit("view_error_popup", install_dt, gap=(5, 40))

    session_duration = clock["t"]  # The first event starts at t>0, so this is effectively the session length

    # --- Retention probability: built directly from behavior features and flow branches (planted truth) ----
    detoured = (profile_cnt + settings_cnt) > 0
    logit = (
        -1.7
        + 0.6 * q
        + 0.9 * tutorial
        + 0.5 * push
        + 0.18 * min(content_cnt, 8)
        + 0.6 * (session_duration >= 150)     # threshold effect
        + 0.5 * (like_cnt >= 3)               # threshold effect
        + 0.35 * went_content
        - 0.45 * detoured
        - 0.5 * n_err
        + 0.15 * search_cnt
    )
    p7 = sigmoid(logit)
    d7_retained = rng.random() < p7
    # D1 retention is more lenient than D7 (anyone retained on D7 is treated as retained on D1 too)
    d1_retained = bool(d7_retained or (rng.random() < sigmoid(logit + 1.2)))

    # --- Stamp the return activity (the D7 labeling in 2.5.2 detects retention from activity) ---------
    if d1_retained:
        d1_dt = pd.Timestamp(install_dt.date()) + pd.Timedelta(days=1, hours=int(rng.integers(8, 22)))
        clock["t"] = 0
        emit("page_view_home", d1_dt, gap=(2, 10))
        for _ in range(1 + int(rng.poisson(0.8))):
            emit("page_view_content_detail", d1_dt, count=int(rng.integers(1, 4)), gap=(8, 50))

    if d7_retained:
        d7_dt = pd.Timestamp(install_dt.date()) + pd.Timedelta(days=7, hours=int(rng.integers(8, 22)))
        clock["t"] = 0
        emit("page_view_home", d7_dt, gap=(2, 10))
        emit("page_view_content_detail", d7_dt, count=int(rng.integers(1, 4)), gap=(8, 50))

    return d7_retained, d1_retained, session_duration


def main():
    rng = np.random.default_rng(SEED)

    # Per-user latent quality value and install time
    qs = rng.normal(0.0, 1.0, size=N_USERS)
    install_day_offsets = rng.integers(0, INSTALL_DAYS, size=N_USERS)

    rows = []
    n_d7 = 0
    for uid in range(N_USERS):
        install_dt = (
            BASE_DATE
            + pd.Timedelta(days=int(install_day_offsets[uid]))
            + pd.Timedelta(seconds=int(rng.integers(0, 6 * 3600)))  # install time of day (morning to midday)
        )
        d7, _d1, _dur = simulate_user(f"u{uid:06d}", qs[uid], install_dt, rng, rows)
        n_d7 += int(d7)

    df = pd.DataFrame(
        rows,
        columns=[
            "event_timestamp",
            "event_date",
            "user_id",
            "event_name",
            "screen_name",
            "event_count",
            "description",
        ],
    )
    df = df.sort_values(["user_id", "event_timestamp"]).reset_index(drop=True)

    out_dir = os.path.join(os.path.dirname(__file__), "data")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "event_log.csv")
    df.to_csv(out_path, index=False)

    print(f"Done: {out_path}")
    print(f"  users          = {N_USERS:,}")
    print(f"  event rows     = {len(df):,}")
    print(f"  D7 retention   = {n_d7 / N_USERS:.1%}")


if __name__ == "__main__":
    main()
