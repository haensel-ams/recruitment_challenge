# Data Engineer Challenge — Dynamic Pricing (State & Data Structures)

**Objective.** Build a simple pricing bot for the **Duopoly** track of the [Dynamic Pricing Competition (DPC)](https://www.dynamic-pricing-competition.com).  
We don’t care about fancy ML — we care about **how you smartly structure and manage data and its information over time**.

---

## What you’ll do

Implement a pricing function `p(...)` (see DPC site) that is called once per **selling period**.  
Each call returns a price and may pass along a compact **state object** (`information_dump`) for the next call.

Focus on:
- Designing **lightweight, bounded** data structures (e.g., ring buffers) for streaming history.
- **Online / incremental** stats (O(1) updates) instead of re-fitting models every call.
- Clean handling of cold starts, edge cases, and sensible price bounds.

---

## Constraints (must follow)

- **Environment:** Your code runs in a DPC container (Python 3.9; 1 CPU; 512 MB RAM).
- **Timing:** Average response ≤ **0.2 s** per period; any single call ≤ **5 s**; ≥ **99%** valid responses.
- **Files & I/O:** Do **not** write custom logs or files.  
  The only cross-competition persistence allowed is **`duopoly_feedback.data`** (see DPC site).
- **File name:** Your main algorithm file **must** be named **`duopoly.py`**.
- **Libraries:** Python stdlib + **NumPy**, **pandas**, **xgboost**, **statsmodels** and **scikit-learn** only.  
  ❌ No torch/RL/optimizers/etc.


---

## Deliverables

Please submit a small repo or zip file containing:

- **duopoly.py** — your pricing function and compact helpers.
- **PDF summary** (≤ 2 page) — explain (include brief pseudocode and a short rationale for each structure):
  - your data structures (what/why/size),
  - your online update equations,  
  - cold-start & edge-case handling,
  - the chosen policy and trade-offs.
- **tests.py** — a couple of tiny unit tests (e.g., ring buffer rollover; running covariance update).
- **(Optional) simulate_local.py** — a toy simulator calling your p(...) to show state evolution.

Timebox yourself to ~4 hours of implementation. 
