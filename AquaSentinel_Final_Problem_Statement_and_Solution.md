# AquaSentinel — Final Problem Statement and Solution

**Project domain:** AI for Sustainability  
**Subdomain:** Sustainable Urban Water Infrastructure  
**Solution status:** Concept locked; model performance must be validated before claims are made.

---

## 1. Final Problem Statement

Municipal water-utility operators struggle to identify developing leaks early because normal changes in water demand, sensor errors, and genuine leak events can produce similar pressure and flow patterns. Fixed thresholds may generate too many alerts, while waiting for stronger evidence can delay investigation. Operators need an explainable, continuous monitoring system that identifies suspicious persistent changes and helps them decide when a network zone should be investigated.

## 2. The Problem in Simple Words

Cities move drinking water through large networks of pipes. Sensors measure variables such as flow and pressure, helping utility operators understand how the network is behaving.

When a pipe leaks, its pressure or flow pattern may change. But a change in the readings does not automatically mean there is a leak. Morning demand peaks, pump or valve operations, missing readings, and sensor faults can also produce unusual patterns.

A simple fixed threshold has two common risks:

- If the threshold is too sensitive, the system may generate too many false alarms.
- If the threshold is too loose, a developing leak may not trigger an alert until the signal becomes large.

The core problem is therefore not just finding unusual readings. It is identifying **persistent readings that are suspicious enough to warrant investigation, while being transparent about uncertainty**.

## 3. Final Solution Statement

**AquaSentinel is an explainable water-network monitoring platform that processes incoming pressure and flow readings sequentially, compares them with historical operating patterns, detects sustained deviations using statistical change detection, and presents evidence-backed suspected-leak alerts with performance measurements.**

AquaSentinel will first be validated using a public water-network benchmark. Its purpose is to help an operator decide whether a suspicious event deserves investigation. It will not automatically declare a leak confirmed or dispatch a repair crew.

## 4. Target User and Job to Be Done

**Primary user:** Municipal water-utility control-room operator or network engineer.

**Decision to improve:** Does the incoming sensor evidence provide enough reason to raise a suspected-leak alert for investigation, or is the evidence insufficient or potentially explained by another cause?

**Expected value:** Give the operator earlier, more explainable indications of suspicious persistent changes, while measuring the detector’s false alarms and missed events rather than relying on an unverified claim of accuracy.

## 5. Locked Technical Direction

### Primary candidate

Use a **time-of-day/day-of-week flow baseline followed by a one-sided CUSUM change detector**.

1. Establish an expected flow pattern using historical readings.
2. Compare each new reading with the expected value.
3. Normalize the difference using variability estimated from historical data.
4. Accumulate evidence of a sustained shift with CUSUM.
5. Raise a suspected-anomaly alert if the calibrated decision threshold is crossed.
6. Group repeated alerts associated with the same continuing event and provide the measured evidence to the operator.

The baseline and detector must be fitted and tuned using historical/training and validation data only. During evaluation and replay, each prediction may use only information that would have been available at that timestamp.

### Alternatives and extensions

- **Comparison baselines:** Fixed thresholds and a simpler baseline-only detector.
- **SPRT:** An alternative challenger that may be tested fairly against CUSUM; it is not assumed to be superior in advance.
- **Pressure corroboration:** A small, optional supporting-evidence layer. Add it only if tests show that it improves detection at an acceptable false-alarm rate.
- **Deferred:** Hydraulic digital twin (WNTR/EPANET), HGNN or other graph neural networks, exact pipe-level localization, and autonomous dispatch.

### Important limitations of statistical detection

CUSUM can detect persistent deviations, but it cannot by itself prove that the cause is a physical leak. A sustained sensor offset or legitimate sustained demand change can also trigger it. Pressure evidence may provide useful context, but it does not guarantee the physical cause can be distinguished. The system must use language such as **“suspected leak/anomaly”** and clearly display its evidence and uncertainty.

## 6. Minimum Viable Product (MVP)

The MVP consists of four connected components.

### A. Data ingestion and baseline

- Load the required public benchmark readings and leakage-related labels.
- Verify actual column names, timestamp formats, units, missing values, sensor mapping, and label semantics before use.
- Create a historical time-of-day/day-of-week flow baseline.

### B. Statistical detector

- Calculate baseline residuals.
- Apply a one-sided CUSUM detector.
- Tune the threshold and reference parameter using training/validation data.
- Handle gaps conservatively, group repeated alerts, and define an acknowledge/reset/re-baseline policy.

### C. Explainable monitoring dashboard

- Display incoming data in timestamp order.
- Show observed flow, expected baseline, residual, detector state, and the time an alert was raised.
- Show the evidence behind every alert.
- Clearly label the demo as **Benchmark Replay — not live municipal telemetry**.

### D. Evaluation panel

Compare AquaSentinel with simpler baselines using the same held-out data. Show measured outcomes, limitations, and missed events—not only successful examples.

## 7. Data and Validation Plan

**Primary candidate dataset:** BattLeDIM L-Town benchmark, publicly listed on Zenodo: https://zenodo.org/records/4017659  
**Official challenge information:** https://battledim.ucy.ac.cy/  
**Potential hydraulic-tool reference for future work:** https://github.com/USEPA/WNTR

The BattLeDIM L-Town benchmark uses simulated telemetry based on a water-distribution network. It is appropriate for a reproducible benchmark prototype, but it is not a live municipal sensor feed. The relevant files and their schema must be inspected before implementation assumptions are treated as facts.

### First-hour feasibility gate

Before investing the remaining build time:

1. Obtain the necessary flow and leakage-related files, and pressure files if corroboration is to be tested.
2. Verify the timestamps, units, sensor channels, and exact meaning of the leakage labels.
3. Plot a documented event window alongside normal observations.
4. Measure the flow change relative to normal residual variability.
5. Confirm that an event can be evaluated without future-information leakage.

**Go:** The data is usable, labels align, and the relevant signal is measurable. Proceed with the baseline and CUSUM.

**Conditional path:** If flow-only detection misses smaller events, test pressure corroboration or narrow the claim to the event types/sizes the evidence supports.

**Fallback:** If continuous/daytime detection produces unacceptable false alarms, test a simpler CUSUM restricted to a defensible night-flow window. If the data or labels cannot be aligned, do not claim measured detection performance.

## 8. Evaluation Criteria

Use a chronological evaluation design where supported by the dataset. Fit and tune on the designated historical/validation periods, freeze the method, and evaluate on a held-out period such as the separate evaluation year. Do not tune parameters using the final evaluation outcomes.

Primary metrics:

- **Event-level recall:** Fraction of documented leak events detected.
- **Precision:** Fraction of event alerts matched to documented events under a clearly defined matching rule.
- **False alarms per unit of network time:** For example, per simulated network month.
- **Detection delay:** Time from documented event onset to first qualifying alert, if the source labels genuinely provide onset time.
- **Baseline comparison:** Compare methods at a comparable false-alarm rate.

Do not rely on overall row-level accuracy alone because leak periods can be rare and adjacent time-series readings are correlated. Before calculating event recall or delay, verify the actual semantics of the benchmark's event labels. If the available file provides repair time but not onset time, do not infer an exact onset from the repair time alone; inspect the separate leakage time series/configuration as appropriate.

Optional impact metric: **simulated leak volume before alert**, only if the leakage time series and label alignment support a valid calculation. This is a benchmark-derived proxy, not proof of real-world water saved.

## 9. Judge-Facing “Wow Factor”

AquaSentinel should look like a professional infrastructure-intelligence product without hiding a weak detector behind a polished interface.

### A. Live-style monitoring console

Replay readings sequentially with controllable playback speed. Display current readings, the expected baseline, residual, and detector state. Make the replay label visible.

### B. Explainable incident cards

For each alert, show the relevant channel, timestamp, deviation size, persistence, any supporting pressure evidence, and what remains uncertain. Never label an event “confirmed” without independent confirmation.

### C. Benchmark performance comparison

Show static-threshold versus AquaSentinel results on the same held-out period, including event recall, false alarms, and detection delay. The results must be generated by the actual evaluation code.

### D. Network-zone context

Show only verified channel-to-zone relationships available from the benchmark documentation. Do not imply exact pipe localization from a zone-level flow sensor.

### E. Impact timeline (optional)

Where the benchmark labels support it, show the documented/simulated leak interval and when the detector first alerted. If calculated, report simulated leakage volume before the alert with the assumptions and calculation disclosed. Do not label it “water saved.”

## 10. Real-World Impact and Deployment Path

The real-world goal is to help utilities notice suspicious leakage earlier and direct human investigation more efficiently. Whether AquaSentinel actually reduces leak duration or water losses must be established through field validation.

A credible path toward deployment is:

1. Evaluate the detector on the public benchmark and report the results honestly.
2. Test it on authorized, real utility telemetry with verified event and repair records.
3. Run a read-only shadow pilot where alerts do not control operations.
4. Compare alerts with confirmed field events and existing utility practice.
5. Measure false alarms, detection delays, operator acceptance, and whether investigated events are repaired earlier.
6. Calibrate the method for the actual network, sensor arrangement, demand patterns, and supply regime.

An especially important limitation for an India-focused deployment is intermittent water supply. A model tested on continuous-flow benchmark data must not be assumed to work during network filling, pressurization, and draining. Such operating conditions require separate data and validation.

## 11. Out of Scope for the Hackathon MVP

- HGNN or other deep graph-model training.
- A calibrated hydraulic digital twin.
- Exact pipe-level or GPS-level leak localization.
- Connection to live municipal SCADA systems.
- Automatic crew dispatch or work-order creation.
- Unverified water-volume, financial-savings, or carbon-reduction claims.
- Claiming that every anomaly is a leak or that small background leaks are reliably detectable without evidence.

## 12. Solution-Lock Record

**Project name:** AquaSentinel — Real-Time Water Leak Intelligence  
**Problem:** Identify suspicious persistent changes in water-network telemetry early enough to support investigation.  
**Primary solution:** Time-of-day/day-of-week flow baseline + one-sided CUSUM, with evidence-backed suspected-anomaly alerts.  
**Primary validation:** Held-out chronological benchmark replay with event-level metrics and comparison to simple baselines.  
**Conditional extension:** Pressure corroboration if measured value is demonstrated.  
**Fallback:** Simpler or night-window detector if daytime false alarms remain unacceptable.  
**Core promise:** Explainable suspected-leak detection on benchmark data, with a measurable and honest path toward real-world testing.  
**Not promised:** Live utility deployment, exact pipe localization, confirmed leak diagnosis, or proven water savings.

### Final Recommendation

Proceed with AquaSentinel as the selected concept. Prioritize a working data-to-alert-to-evaluation loop. Make the demonstration impressive through real evidence, sequential replay, clear explanations, and a professional incident dashboard—not through unvalidated complexity.
