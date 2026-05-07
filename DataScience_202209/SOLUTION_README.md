# Marketing Mix Model (MMM) — HAMS Data Science Challenge

## Objective
Quantify the contribution of 7 marketing channels to weekly revenue 
using a Bayesian Marketing Mix Model (PyMC), and estimate ROI per channel.

## Approach
- Built a full Bayesian MMM using PyMC with NUTS sampling
- Modelled adstock (carry-over) effects with learned decay rates per channel
- Added trend and Fourier seasonality terms to capture yearly patterns
- Evaluated model using MAPE, MAE and R²
- Calculated ROI per channel from posterior estimates

## Key Findings
| Channel | ROI | Verdict |
|---------|-----|---------|
| Channel 2 | 14.05 | 🟢 Massively underinvested |
| Channel 5 | 1.53 | 🟢 Profitable |
| Channel 1 | 0.89 | 🔴 Below break-even |
| Channel 4 | 0.79 | 🔴 Unprofitable |
| Channel 6 | 0.59 | 🔴 Unprofitable |
| Channel 3 | 0.57 | 🔴 High spend, poor return |
| Channel 7 | 0.32 | 🔴 Worst ROI, highest spend |

**Recommendation:** Reallocate budget from Channel 7 & 3 → Channel 2 & 5.

> **Note:** Channel 2's ROI of 14x is notably high and likely reflects 
> data sparsity — it has the lowest total spend (€35k) of all channels, 
> which can amplify uncertainty in the estimate. This warrants further 
> investigation with more spend data before acting on it.

## Model Performance
- MAPE (Mean Absolute Percentage Error): 19.63%
- MAE (Mean Absolute Error): €26,577
- R² (R-Squared): 0.449
- R-hat (Convergence Diagnostic): 1.00 across all parameters ✅

## Environment
- Python 3.13.3 (installed via uv)
- All dependencies managed with uv

## How to Run

```bash
# Install uv if you don't have it
pip install uv

# Install Python 3.13 via uv
uv python install 3.13

# Create and activate virtual environment
uv venv --python 3.13
source venv/bin/activate

# Install dependencies
uv pip install -r requirements.txt

# Launch Jupyter
jupyter lab
```
Then open `mmm_analysis.ipynb` and run all cells top to bottom.

## Stack
- Python 3.13.3
- PyMC 5.28.5 — Bayesian modeling & NUTS sampling
- ArviZ 0.23.4 — MCMC diagnostics & visualization
- NumPy 2.4.4 — numerical computing
- Pandas 3.0.2 — data processing
- Matplotlib 3.10.9 / Seaborn 0.13.2 — visualization
- Scikit-learn 1.8.0 — model evaluation metrics
- JupyterLab 4.5.7 — interactive notebook environment

## Project Structure
```
├── mmm_analysis.ipynb   — full analysis notebook
├── MMM_test_data.csv    — dataset
├── requirements.txt     — all dependencies
└── README.md            — this file
```