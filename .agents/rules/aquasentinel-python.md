---
trigger: glob
description: "Use these constraints when editing Python files in AquaSentinel."
globs: "*.py"
---

- Do not mix Streamlit rendering into baseline, detector, or evaluation calculations.
- Do not process replay rows out of timestamp order or let a row update state more than once.
- Do not use zero to replace missing measurements.
- Do not divide by zero/near-zero scale; use the documented pooled robust scale or mark the profile unavailable.
- Do not catch broad exceptions and silently continue with fabricated defaults.
- Do not add a package or change the run environment without Human approval.
- Do not create a second detector implementation in `app.py`; call the pure function in `detector.py`.
- Do not state that a test passed unless the exact test ran and its output was inspected.
