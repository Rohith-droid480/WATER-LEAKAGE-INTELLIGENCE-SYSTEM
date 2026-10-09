"""AquaSentinel — Real-Time Municipal Water Network Monitoring Console.

Deterministic Benchmark Replay & Statistical Leak Anomaly Detection Console.
"""

from __future__ import annotations

import pandas as pd
import streamlit as st

import evaluate
import interfaces
from replay_engine import (
    ReplaySession,
    create_replay_session,
    pause_session,
    play_session,
    reset_session,
    resume_session,
    step_session,
)

# Set page configuration
st.set_page_config(
    page_title="AquaSentinel — Water Network Monitoring",
    page_icon="💧",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom Styling for Premium Mission-Critical Dashboard Aesthetics
st.markdown(
    """
    <style>
    /* Metric Card Styling */
    .metric-card {
        background: linear-gradient(135deg, rgba(15, 23, 42, 0.85), rgba(30, 41, 59, 0.75));
        border: 1px solid rgba(56, 189, 248, 0.2);
        border-radius: 10px;
        padding: 14px 18px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.25);
    }
    .metric-title {
        font-size: 0.78rem;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: #94a3b8;
        margin-bottom: 4px;
    }
    .metric-value {
        font-size: 1.55rem;
        font-weight: 700;
        color: #f8fafc;
        line-height: 1.2;
    }
    .metric-sub {
        font-size: 0.76rem;
        color: #38bdf8;
        margin-top: 4px;
    }
    .banner-container {
        background: linear-gradient(90deg, #0369a1 0%, #0f172a 100%);
        border-left: 5px solid #38bdf8;
        padding: 12px 18px;
        border-radius: 6px;
        margin-bottom: 20px;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    .banner-text {
        font-weight: 600;
        font-size: 0.95rem;
        color: #e0f2fe;
        letter-spacing: 0.02em;
    }
    .banner-badge {
        background: rgba(56, 189, 248, 0.2);
        border: 1px solid #38bdf8;
        color: #bae6fd;
        padding: 3px 10px;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 600;
    }
    .incident-alert-card {
        background: linear-gradient(135deg, rgba(127, 29, 29, 0.85), rgba(69, 10, 10, 0.85));
        border: 1px solid #ef4444;
        border-radius: 8px;
        padding: 14px 18px;
        margin-bottom: 12px;
        color: #fee2e2;
    }
    .incident-clear-card {
        background: linear-gradient(135deg, rgba(6, 78, 59, 0.75), rgba(2, 44, 34, 0.75));
        border: 1px solid #10b981;
        border-radius: 8px;
        padding: 12px 16px;
        color: #d1fae5;
    }
    .eval-card {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.8), rgba(15, 23, 42, 0.8));
        border: 1px solid rgba(148, 163, 184, 0.2);
        border-radius: 8px;
        padding: 14px 18px;
        margin-bottom: 12px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Initialize Session State
if "session" not in st.session_state:
    st.session_state.session = create_replay_session(use_mock=False, max_steps=4032)

session: ReplaySession = st.session_state.session

# --- MANDATORY VISIBLE BENCHMARK BANNER ---
st.markdown(
    """
    <div class="banner-container">
        <div>
            <span style="font-size: 1.1rem; margin-right: 8px;">🛡️</span>
            <span class="banner-text">Benchmark Replay — simulated data, not live municipal telemetry.</span>
        </div>
        <span class="banner-badge">OFFLINE VERIFICATION</span>
    </div>
    """,
    unsafe_allow_html=True,
)

# Interface status badge
status_info = interfaces.get_interface_status()
if session.is_mock:
    st.warning(
        "⚠️ **MOCK HARNESS ACTIVE** — Using synthetic placeholder telemetry and mock detector. "
        "THIS IS NOT REAL BENCHMARK DETECTION."
    )
else:
    st.success(
        "✅ **REAL BATTLEDIM PIPELINE CONNECTED** — Historical 2018 diurnal baseline, "
        "one-sided CUSUM detector, and chronological 2019 replay actively bound."
    )

# --- SIDEBAR CONTROLS ---
with st.sidebar:
    st.title("🎛️ Replay Controller")
    st.caption("Deterministic Chronological Execution")

    # Mode Selector
    telemetry_mode = st.radio(
        "Dataset Source",
        options=["Real BattLeDIM (2019 Telemetry)", "Synthetic Mock Harness (Testing)"],
        index=1 if session.is_mock else 0,
        help="Select whether to replay real BattLeDIM 2019 benchmark data or synthetic testing harness.",
    )
    is_mock_selected = "Mock" in telemetry_mode
    if is_mock_selected != session.is_mock:
        st.session_state.session = create_replay_session(
            use_mock=is_mock_selected,
            max_steps=150 if is_mock_selected else 4032,
        )
        st.rerun()

    # Replay slice control for real dataset
    if not session.is_mock:
        dataset_slice = st.selectbox(
            "Replay Horizon",
            options=["14 Days (4,032 observations)", "1 Month (8,640 observations)", "Full Year (105,120 observations)"],
            index=0,
            help="Select replay window duration for the benchmark run.",
        )
        slice_map = {
            "14 Days (4,032 observations)": 4032,
            "1 Month (8,640 observations)": 8640,
            "Full Year (105,120 observations)": 105120,
        }
        target_steps = slice_map[dataset_slice]
        if session.total_observations != target_steps and session.is_ready:
            st.session_state.session = create_replay_session(use_mock=False, max_steps=target_steps)
            st.rerun()

    st.divider()

    # Playback Control Buttons
    c1, c2 = st.columns(2)
    with c1:
        if session.is_playing:
            if st.button("⏸ Pause", width="stretch"):
                pause_session(session)
                st.rerun()
        else:
            if session.is_paused:
                if st.button("▶ Resume", type="primary", width="stretch"):
                    resume_session(session)
                    st.rerun()
            elif not session.is_ended:
                if st.button("▶ Play", type="primary", width="stretch"):
                    play_session(session)
                    st.rerun()
            else:
                st.button("🏁 Ended", disabled=True, width="stretch")

    with c2:
        if st.button("🔄 Reset", width="stretch"):
            reset_session(session)
            st.rerun()

    # Step single row button
    if st.button("⏭ Step Single Row", disabled=session.is_playing or session.is_ended, width="stretch"):
        step_session(session, batch_size=1)
        st.rerun()

    st.divider()

    # Playback Configuration
    st.subheader("⚙️ Replay Settings")
    speed_batch = st.select_slider(
        "Replay Speed (Rows / Tick)",
        options=[1, 5, 10, 25, 50, 100],
        value=session.speed_batch_size if session.speed_batch_size in [1, 5, 10, 25, 50, 100] else 1,
        help="Number of sequential 5-minute observations processed per update tick.",
    )
    session.speed_batch_size = speed_batch

    auto_tick_rate = st.slider(
        "Tick Interval (seconds)",
        min_value=0.5,
        max_value=3.0,
        value=1.0,
        step=0.5,
        help="Time between automated playback ticks.",
    )

    chart_window_size = st.slider(
        "Bounded Chart History (Points)",
        min_value=30,
        max_value=300,
        value=session.chart_buffer_max_len,
        step=10,
        help="Bounded memory rolling window for snappy visualization.",
    )
    session.chart_buffer_max_len = chart_window_size

    st.divider()

    # Metadata & Session Status
    st.subheader("📊 Session Diagnostics")
    st.markdown(f"**Run ID:** `{session.run_id[:13]}...`")
    st.markdown(f"**Replay State:** `{session.status}`")
    st.markdown(f"**Last Processed Index:** `{session.last_processed_index}`")
    st.markdown(f"**Progress:** `{session.replay_index} / {session.total_observations}`")
    st.progress(session.progress_fraction)

    if session.is_ended:
        st.warning("Replay completed: End of dataset reached.")


# --- MAIN DASHBOARD SECTION ---

# Channel Selection
channels = list(session.channel_configs.keys())
selected_channel = st.selectbox(
    "Monitored Telemetry Channel",
    options=channels,
    index=0,
    help="Select network sensor channel for deep-dive residual and CUSUM analysis.",
)

# Replay Execution Fragment (handles periodic auto-advance when playing)
run_every_param = auto_tick_rate if session.is_playing and not session.is_ended else None


@st.fragment(run_every=run_every_param)
def render_live_monitoring_fragment():
    # If playing, step the session forward
    if session.is_playing and not session.is_ended:
        step_session(session, batch_size=session.speed_batch_size)

    # Get latest data point if available
    latest_record = session.chart_history[-1] if session.chart_history else None

    # --- TOP ROW: KPI METRIC CARDS ---
    m1, m2, m3, m4 = st.columns(4)

    with m1:
        current_time_str = latest_record["timestamp"] if latest_record else "Not Started"
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-title">Simulated Timestamp</div>
                <div class="metric-value">{current_time_str}</div>
                <div class="metric-sub">Index: {session.last_processed_index if session.last_processed_index >= 0 else 'None'}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with m2:
        obs_val = f"{latest_record[f'{selected_channel}_observed']:.2f}" if latest_record else "—"
        exp_val = f"{latest_record[f'{selected_channel}_expected']:.2f}" if latest_record else "—"
        unit = "m³/h" if "FLOW" in selected_channel.upper() or selected_channel.startswith("p") or selected_channel.startswith("PUMP") else "m"
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-title">Observed vs Expected ({unit})</div>
                <div class="metric-value">{obs_val} <span style="font-size: 0.95rem; color: #94a3b8; font-weight: 400;">/ {exp_val}</span></div>
                <div class="metric-sub">Historical Baseline Match</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with m3:
        residual_val = f"{latest_record[f'{selected_channel}_residual']:+.2f}" if latest_record else "—"
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-title">Instantaneous Residual</div>
                <div class="metric-value">{residual_val}</div>
                <div class="metric-sub">Deviation from Normal Baseline</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with m4:
        cusum_val = f"{latest_record[f'{selected_channel}_cusum']:.2f}" if latest_record else "0.00"
        thresh_val = f"{latest_record[f'{selected_channel}_threshold']:.1f}" if latest_record else "8.0"
        is_crossing = float(cusum_val) > float(thresh_val) if latest_record else False
        color_badge = "#ef4444" if is_crossing else "#10b981"
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-title">CUSUM Score vs Threshold</div>
                <div class="metric-value" style="color: {color_badge};">{cusum_val} <span style="font-size: 0.95rem; color: #94a3b8; font-weight: 400;">/ h={thresh_val}</span></div>
                <div class="metric-sub">{'THRESHOLD EXCEEDED' if is_crossing else 'Within Statistical Limits'}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.write("")

    # --- MIDDLE SECTION: TABS ---
    if session.chart_history:
        history_df = pd.DataFrame(session.chart_history)
        history_df["timestamp_dt"] = pd.to_datetime(history_df["timestamp"])

        tab_charts, tab_evidence, tab_logs, tab_eval = st.tabs(
            [
                "📈 Real-Time Telemetry & CUSUM Traces",
                "⚠️ Incident Evidence Log",
                "📋 Prediction Audit Log",
                "🎯 Ground-Truth Evaluation",
            ]
        )

        with tab_charts:
            # Chart 1: Observed vs Expected Readings
            st.markdown(f"##### 1. Observed vs Expected Baseline — `{selected_channel}`")
            chart_1_data = history_df.set_index("timestamp_dt")[
                [f"{selected_channel}_observed", f"{selected_channel}_expected"]
            ]
            chart_1_data.columns = ["Observed Reading", "Baseline Expected"]
            st.line_chart(chart_1_data, height=220)

            # Chart 2: Residuals
            st.markdown(f"##### 2. Baseline Residuals ($x_t - \\hat{{x}}_t$) — `{selected_channel}`")
            chart_2_data = history_df.set_index("timestamp_dt")[[f"{selected_channel}_residual"]]
            chart_2_data.columns = ["Residual Deviation"]
            st.line_chart(chart_2_data, height=180)

            # Chart 3: CUSUM Score & Threshold
            st.markdown(f"##### 3. CUSUM Accumulator Score ($S_t$) with Decision Interval ($h$) — `{selected_channel}`")
            chart_3_data = history_df.set_index("timestamp_dt")[
                [f"{selected_channel}_cusum", f"{selected_channel}_threshold"]
            ]
            chart_3_data.columns = ["CUSUM Score", "Alert Threshold (h)"]
            st.line_chart(chart_3_data, height=200)

        with tab_evidence:
            st.markdown("##### Suspected Leak Anomaly Incidents")
            st.caption(
                "A statistical anomaly crossing threshold $h$ constitutes suspected incident evidence. "
                "Per project governance, anomalies are NOT confirmed leaks until verified by utility operators."
            )

            if session.incident_log:
                for inc in reversed(session.incident_log[-10:]):
                    st.markdown(
                        f"""
                        <div class="incident-alert-card">
                            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                                <strong>🚨 Incident {inc.get('incident_id')}</strong>
                                <span style="background: rgba(239, 68, 68, 0.3); padding: 2px 8px; border-radius: 4px; font-size: 0.8rem; font-weight: 600;">
                                    {inc.get('status')}
                                </span>
                            </div>
                            <div style="font-size: 0.88rem; line-height: 1.5;">
                                <div>• <strong>Onset Index / Timestamp:</strong> {inc.get('onset_index')} ({inc.get('timestamp')})</div>
                                <div>• <strong>Contributing Channels:</strong> {', '.join(inc.get('contributing_channels', []))}</div>
                                <div>• <strong>Peak CUSUM Accumulator:</strong> {inc.get('max_cusum_score', '—')}</div>
                                <div style="margin-top: 6px; font-style: italic; color: #fca5a5;">
                                    ⚠️ {inc.get('evidence_note', 'Suspected statistical anomaly.')}
                                </div>
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
            else:
                st.markdown(
                    """
                    <div class="incident-clear-card">
                        ✅ <strong>Nominal Network Conditions:</strong> No persistent statistical threshold crossings detected.
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        with tab_logs:
            st.markdown("##### Complete Prediction Log (Audit Trail)")
            st.caption(
                f"Showing all {len(session.prediction_log)} sequentially processed predictions without data lookahead."
            )
            pred_df = pd.DataFrame(session.prediction_log)
            st.dataframe(
                pred_df,
                width="stretch",
                height=350,
            )

            # Export button
            csv_data = pred_df.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="📥 Download Complete Prediction Log (CSV)",
                data=csv_data,
                file_name=f"aquasentinel_predictions_{session.run_id[:8]}.csv",
                mime="text/csv",
            )

        with tab_eval:
            st.markdown("##### Post-Run Ground-Truth Evaluation (Beta)")
            st.caption(
                "Evaluation is strictly procedurally held-out: Ground-truth event metadata is accessed "
                "only AFTER predictions are generated, never during live replay."
            )

            if session.is_mock:
                st.info("ℹ️ Evaluation requires running against real BattLeDIM benchmark data. Switch Dataset Source to Real BattLeDIM in the sidebar.")
            else:
                # Load ground-truth events for the current year
                events_2019 = evaluate.load_event_metadata("data", year=2019)
                try:
                    summary = evaluate.evaluate_predictions(session.prediction_log, events_2019)

                    e1, e2, e3, e4 = st.columns(4)
                    with e1:
                        st.metric("Eligible Leak Events", summary.total_events_eligible)
                    with e2:
                        st.metric("Detected Events (Strict / Lenient)", f"{summary.events_detected_strict} / {summary.events_detected_lenient}")
                    with e3:
                        st.metric("Recall (Strict / Lenient)", f"{summary.recall_strict:.1%} / {summary.recall_lenient:.1%}")
                    with e4:
                        st.metric("Precision (Lenient)", f"{summary.precision_lenient:.1%}")

                    st.markdown("###### Detailed Evaluation Metrics")
                    m_c1, m_c2, m_c3 = st.columns(3)
                    with m_c1:
                        st.markdown(f"• **Missed Events:** {summary.events_missed}")
                        st.markdown(f"• **Total Alert Steps:** {summary.total_alerts_count}")
                    with m_c2:
                        st.markdown(f"• **Unmatched Episodes:** {summary.unmatched_alerts_count}")
                        st.markdown(f"• **Unmatched / Sim Month:** {summary.unmatched_alerts_per_simulated_month}")
                    with m_c3:
                        st.markdown(f"• **Evaluable Delays:** {summary.delays_evaluable_count}")
                        med_del = f"{summary.median_delay_hours}h" if summary.median_delay_hours is not None else "N/A"
                        st.markdown(f"• **Median Delay:** {med_del}")

                    st.markdown("###### Recall by Leak Size")
                    for size_lbl, stats in summary.recall_by_diameter.items():
                        st.write(f"- **{size_lbl}:** {stats['detected']} / {stats['eligible']} detected ({stats['recall']:.1%})")

                    st.markdown("###### Limitations & Truth Disclosures")
                    for lim in summary.limitations:
                        st.info(f"📌 {lim}")

                except Exception as ex:
                    st.warning(f"Evaluation pending: {ex}")

    else:
        st.info("Replay initialized in READY state. Click **▶ Play** or **⏭ Step Single Row** to begin sequential replay.")


# Render Fragment
render_live_monitoring_fragment()
