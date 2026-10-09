---
trigger: model_decision
description: "Load when touching BattLeDIM files, sensor mappings, event metadata, baselines, CUSUM parameters, replay chronology, label parsing, or evaluation metrics."
---

- Do not hardcode channel IDs from reports; inspect actual headers and verify mapping.
- Do not assume file schema or YAML keys. Print actual headers and inspect configuration before parsing.
- Do not treat repair time as leak onset or per-link leakage rate as aggregate flow residual.
- Do not allow the 2019 label parser into the prediction path. Only post-run evaluation may read 2019 labels.
- Do not tune baseline/channel/threshold/matching on 2019 results.
- Do not fit baselines on known leak-active 2018 rows where reliable event metadata identifies them.
- Do not report delay when onset is unknown or event already active at series start.
- Do not claim per-pipe attribution from aggregate flow sensors or report simulated volume as actual water saved.
- Do not conceal overlap ambiguity; use predeclared strict/lenient matching or disclose that the result is ambiguous.
