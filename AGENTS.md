# AGENTS.md
# MnO₂ Electrochemical Sensor Research — Autonomous Swarm Protocol
# Target runtime: OpenAI Codex / Claude Code / OpenCLAW agents
# Infrastructure: DARKLAB (2× Mac Mini M4, macOS, OpenClaw orchestration)

---

## Project Identity

This is a **computational electrochemistry research project** investigating four
MnO₂ polymorphs (alpha, gamma, delta, epsilon) for electrochemical sensor
applications. The codebase integrates multimodal experimental data (XRD, SEM,
TEM, SAED, XPS, CV, EIS) with multiscale simulations (DFT → MD → continuum FEM)
to produce mechanistic conclusions and publication-ready manuscripts.

The canonical research protocol lives in `MnO2_Research_Swarm_Protocol.md` at the
project root. That document is the single source of truth for scientific methods,
polymorph properties, simulation architecture, and publication targets.
**Read it before executing any research task.**

---

## Directory Layout

```
.
├── AGENTS.md                          # THIS FILE — agent instructions
├── MnO2_Research_Swarm_Protocol.md    # Full research protocol (read-only reference)
├── samples.csv                        # Master sample registry (immutable IDs)
├── raw/                               # Experimental data (READ-ONLY — never modify)
│   ├── XRD/                           #   diffractograms (.xy, .csv, .raw)
│   ├── SEM/                           #   micrographs (.tif, .png)
│   ├── TEM_SAED/                      #   TEM images + SAED patterns
│   ├── XPS/                           #   spectra (.vms, .csv, .txt)
│   └── Electrochem/
│       ├── CV/                        #   cyclic voltammetry (.csv, .mpt)
│       └── EIS/                       #   impedance spectra (.csv, .mpt, .DTA)
├── data/
│   ├── descriptors/                   #   sample_id.json — canonical descriptor records
│   └── cleaned/                       #   processed/normalized intermediate datasets
├── models/
│   ├── atomistic/                     #   DFT input/output files
│   ├── mesoscale/                     #   MD/KMC results
│   └── continuum/                     #   PyBaMM/EchemFEM scripts + simulation outputs
├── sim_results/                       #   simulation output JSONs (timestamped)
├── reports/
│   └── iteration_YYYYMMDD.md          #   iteration changelogs
├── figures/                           #   scripted figure generation (reproducible)
├── manuscript_drafts/                 #   LaTeX or .docx article drafts
├── code/                              #   All Python source modules
│   ├── mnox_schema.py                 #   Canonical data schema + I/O
│   ├── data_ingest.py                 #   Raw file parsers → descriptor JSON
│   ├── eis_fit.py                     #   EIS equivalent circuit fitting
│   ├── cv_kinetics.py                 #   CV scan-rate analysis (b-values, Dunn)
│   ├── multiscale_cv_sim.py           #   Butler-Volmer + DFT-parameterized CV sim
│   ├── bayes_calibrate.py             #   Bayesian parameter inference (PyMC)
│   ├── cross_validate.py              #   Cross-modality consistency checks
│   ├── plotting.py                    #   Standardized figure generation
│   └── utils.py                       #   Shared helpers (file I/O, unit conversion)
├── tests/                             #   pytest test suite
│   ├── test_schema.py
│   ├── test_eis_fit.py
│   ├── test_cv_kinetics.py
│   ├── test_ingest.py
│   └── conftest.py                    #   shared fixtures (synthetic test data)
└── workflows/
    └── convergence_pipeline.yaml      #   OpenCLAW Lobster YAML workflow
```

### Critical path rules

- `raw/` is **read-only**. Never write, rename, or delete files there.
- `samples.csv` is the registry of truth. Every sample_id used anywhere must
  exist in this file. Never invent sample IDs.
- `data/descriptors/*.json` follows the schema in `code/mnox_schema.py` exactly.
  No ad-hoc JSON shapes.
- `reports/` uses filenames like `iteration_20260310.md`. Always include the date.
- `figures/` must contain only script-generated outputs. No manual image drops.

---

## Environment & Dependencies

**Runtime:** Python 3.11+ on macOS (Apple Silicon / M4)

**Core dependencies** (install via pip):

```
numpy>=1.26
scipy>=1.12
matplotlib>=3.8
pandas>=2.1
lmfit>=1.3
```

**Extended dependencies** (install when needed by specific agents):

```
# EIS / electrochemistry
impedance>=1.7           # alternative EIS fitting library
pyeis>=1.0               # Boukamp KK validation + CNLS

# Simulation
pybamm>=24.1             # continuum electrode modeling
# Note: PyBaMM requires additional solvers — run `pybamm.install_idas_solver()`

# Bayesian inference
pymc>=5.10
arviz>=0.17

# Image analysis (SEM/TEM)
scikit-image>=0.22
opencv-python>=4.9

# XRD analysis
pymatgen>=2024.1         # crystal structure + diffraction tools

# Data handling
jsonschema>=4.21
```

**Install pattern:**

```bash
cd /path/to/MnO2_Sensor_Research
python -m venv .venv
source .venv/bin/activate
pip install numpy scipy matplotlib pandas lmfit pytest
```

**Never install globally.** Always use the project venv.

---

## Coding Standards

### Language and style

- Python 3.11+. Type hints on all function signatures.
- Use `dataclasses` for structured data, not raw dicts.
- `pathlib.Path` for all file paths, never string concatenation.
- Docstrings: Google style. Every public function gets one.
- No notebooks (.ipynb) in the repo. All analysis must be runnable as scripts.

### Naming conventions

```
code/module_name.py          # snake_case modules
code/mnox_schema.py          # domain prefix when relevant
tests/test_module_name.py    # mirror code/ structure
data/descriptors/alpha_01.json   # sample_id as filename
figures/alpha_01_eis_nyquist.png # sample_id + plot_type
reports/iteration_20260310.md    # date-stamped
```

### Import order

```python
# 1. stdlib
from __future__ import annotations
from pathlib import Path
from typing import Optional, Dict, Literal
import json

# 2. third-party
import numpy as np
from scipy.optimize import least_squares
import matplotlib.pyplot as plt

# 3. project
from code.mnox_schema import SampleMeta, Descriptors, save_record
```

### Error handling

- File I/O: always catch `FileNotFoundError` with a message naming the expected
  path and the sample_id context.
- Fitting routines: if `least_squares` does not converge (cost > threshold or
  `res.success is False`), log a warning with residual metrics and return `None`.
  Never silently return bad fits.
- Schema validation: use `jsonschema` to validate descriptor JSONs on write
  AND on read. Fail loud if a field is missing.

### Numerical discipline

- All energies in eV. All potentials in V vs stated reference. All lengths in nm
  for crystallography, cm for electrochemistry. All currents in A, capacitance
  in F. Document units in docstrings and JSON schema.
- Never mix unit systems silently. `utils.py` must provide explicit conversion
  functions: `ev_to_kj()`, `nm_to_angstrom()`, `mA_to_A()`, etc.
- Floating point comparisons: use `np.isclose()` with stated tolerances.

---

## Agent Roles & Task Routing

When you receive a task, identify which agent role it falls under. Each role
has defined inputs, outputs, allowed files, and quality gates.

### DIRECTOR — Orchestration & Planning

**You act as DIRECTOR when the task involves:**
- Planning multi-step research workflows
- Deciding which agent to invoke next
- Reviewing iteration reports
- Resolving conflicts between agent outputs

**Rules:**
- Always check `samples.csv` before referencing any sample.
- Before starting a new analysis cycle, read the latest `reports/iteration_*.md`.
- Never execute DFT or MD directly — produce input files in `models/` and
  flag for external HPC execution.
- Human approval required for: new simulation scripts that change kinetic
  equations, publication-bound claims, experiment proposals.

---

### Agent DATA — Experimental Data Ingestion

**You act as DATA when the task involves:**
- Parsing raw experimental files into standardized formats
- Producing `data/descriptors/sample_id.json` records
- Cleaning, normalizing, or baseline-correcting datasets

**Inputs:** Files in `raw/`, `samples.csv`
**Outputs:** `data/descriptors/*.json`, `data/cleaned/*`
**Primary code:** `code/data_ingest.py`, `code/mnox_schema.py`

**Execution pattern:**

```bash
python -m code.data_ingest --sample alpha_01 --all
# Reads raw/XRD/alpha_01.*, raw/XPS/alpha_01.*, raw/Electrochem/*/alpha_01.*
# Produces data/descriptors/alpha_01.json
```

**Parser requirements by file type:**

| Source | Formats | Key extraction |
|--------|---------|----------------|
| XRD | .xy, .csv, .raw | 2θ vs intensity; peak positions; d-spacings |
| SEM | .tif, .png | Feature size distribution (rod d/L, sheet t) |
| TEM/SAED | .tif, .dm3, .png | d-spacings from ring/spot patterns |
| XPS | .vms, .csv, .txt | Binding energy vs intensity; peak fitting |
| CV | .csv, .mpt | Potential vs current at multiple scan rates |
| EIS | .csv, .mpt, .DTA | Frequency, Z_real, Z_imag |

**Quality gates for DATA agent:**
1. Every output JSON must validate against the schema in `mnox_schema.py`.
2. If a raw file is missing for a sample, set the corresponding descriptor
   fields to `null` — never fabricate values.
3. Log which raw files were consumed in a `data/cleaned/ingest_log.json`.
4. XPS peak fitting must use Shirley background + pseudo-Voigt line shapes.
   Document the fitting window and constraints used.

**Bio-Rad / EC-Lab .mpt parser notes:**
- `.mpt` files have a header section (lines starting with metadata) and a
  data section (tab-separated). Skip header lines until the column-name row.
- Column names vary by technique. For EIS: `freq/Hz`, `Re(Z)/Ohm`, `-Im(Z)/Ohm`.
- For CV: `Ewe/V`, `<I>/mA` (or `I/mA`).
- Always check the `Ns` column for cycle number if present.

---

### Agent STRUC — Crystallography & Defect Analysis

**You act as STRUC when the task involves:**
- XRD pattern indexing, Rietveld refinement, phase identification
- SAED pattern analysis (d-spacing measurement, zone axis ID)
- Crystallite size / microstrain extraction (Williamson-Hall, WPPM)
- Disorder quantification (γ intergrowth fraction, ε domain ordering)

**Inputs:** `raw/XRD/`, `raw/TEM_SAED/`, `data/descriptors/*.json`
**Outputs:** Updated descriptor JSONs (crystallography fields), analysis reports
**Tools:** `pymatgen`, custom peak-fitting code

**Critical domain knowledge:**
- α-MnO₂: sharp peaks at 2θ = 12.7°, 18.0°, 28.6°, 36.7°, 38.6°, 41.9°
- γ-MnO₂: broad peaks at 22.2°, 37.6°, 42.5°, 56.2°, 65.3° — breadth is DATA
- δ-MnO₂: d₀₀₁ ≈ 0.70 nm; diffuse SAED rings; often poorly crystalline
- ε-MnO₂: very broad; d ≈ 0.242, 0.213, 0.164 nm; peak at ~0.42 nm

**Fail-safe:** If XRD alone cannot distinguish γ from ε, flag the sample as
`phase_ambiguous: true` in the descriptor and require SAED/TEM confirmation
before any mechanistic claims proceed.

---

### Agent SURF — XPS Surface Chemistry

**You act as SURF when the task involves:**
- XPS peak fitting (Mn 2p, Mn 3s, O 1s regions)
- Mn average oxidation state (AOS) calculation
- Mn³⁺/Mn⁴⁺ ratio extraction (oxygen vacancy proxy)
- O 1s deconvolution (lattice O vs hydroxyl/defective O)

**Inputs:** `raw/XPS/`, `data/descriptors/*.json`
**Outputs:** Updated descriptor JSONs (XPS fields)

**Fitting protocol (non-negotiable):**

```
Mn 2p₃/₂ deconvolution:
  Background: Shirley
  Line shape: pseudo-Voigt (or Gaussian-Lorentzian product)
  Components:
    Mn²⁺ ≈ 641.3 eV  (extreme surface reduction)
    Mn³⁺ ≈ 642.5 eV  (oxygen vacancy indicator)
    Mn⁴⁺ ≈ 644.0 eV  (stoichiometric bulk)
  Spin-orbit doublet: Mn 2p₁/₂ at ~653.8 eV confirms structural integrity

O 1s deconvolution:
  Lattice O (Mn-O-Mn) ≈ 529.8 eV
  Defective/OH (Mn-O-H) ≈ 531.5 eV

Mn AOS crosscheck: Mn 3s multiplet splitting (ΔE_3s)
  AOS ≈ 8.95 − 1.13 × ΔE_3s (empirical correlation)
```

**Quality gates:**
- Charge correction must be consistent across all samples (state method used).
- Report uncertainty bounds on Mn³⁺ fraction (±spread from fit parameter covariance).
- If fitting window or constraints change between samples, document why.

---

### Agent ELEC — Electrochemical Analysis

**You act as ELEC when the task involves:**
- EIS equivalent circuit fitting (Randles-CPE baseline; TLM upgrade)
- CV scan-rate analysis (b-values, Dunn decomposition)
- Extracting R_s, R_ct, C_dl/CPE, Warburg parameters
- Amperometric sensitivity, LOD, linear range calculation

**Inputs:** `raw/Electrochem/`, `data/descriptors/*.json`
**Outputs:** Updated descriptor JSONs (electrochem fields), fit reports, figures
**Primary code:** `code/eis_fit.py`, `code/cv_kinetics.py`

**EIS fitting workflow:**

```python
# 1. Parse raw EIS data
omega, Z_exp = parse_eis("raw/Electrochem/EIS/alpha_01.mpt")

# 2. Baseline Randles-CPE-Warburg fit
from code.eis_fit import fit_randles
fit, result = fit_randles(omega, Z_exp, p0=(10, 500, 1e-5, 0.85, 50))

# 3. Evaluate fit quality
if result.cost > COST_THRESHOLD or not result.success:
    log_warning(f"Poor EIS fit for {sample_id}: cost={result.cost}")
    # Flag for TLM upgrade if porous microstructure indicated by SEM

# 4. Write to descriptor
descriptors.rs_ohm = fit.Rs
descriptors.rct_ohm = fit.Rct
descriptors.cdl_F = fit.Q  # Note: CPE, not true C; record alpha too
descriptors.cpe_alpha = fit.alpha
descriptors.warburg_coeff = fit.sigma
```

**CV analysis workflow:**

```python
from code.cv_kinetics import b_value_at_potential, dunn_decomposition

# b-value at peak potential across scan rates
b = b_value_at_potential(peak_currents, scan_rates)
# b ≈ 1.0 → surface-controlled; b ≈ 0.5 → diffusion-controlled

# Dunn decomposition for capacitive/diffusive separation
k1, k2 = dunn_decomposition(current_matrix, scan_rates)
cap_frac, i_cap, i_diff = capacitive_fraction(current_matrix, target_rate, k1, k2)
```

**Upgrade trigger for TLM:**
If BOTH conditions are true:
1. SEM/TEM indicates thick porous film (thickness > 500 nm)
2. Nyquist shows distributed arcs OR strong low-frequency dispersion

Then implement transmission-line model instead of Randles. Document the switch.

**Quality gates:**
- All comparative EIS must use identical: electrolyte, frequency range,
  AC amplitude, steady-state criteria, iR compensation method.
- b-values are comparative descriptors only — do not claim mechanism from
  b-value alone without corroborating EIS and microstructure.
- Non-unique fits → run parameter identifiability analysis. Report it.

---

### Agent ATOM — Atomistic Modeling (DFT)

**You act as ATOM when the task involves:**
- Building DFT(+U) slab models from experimental lattice parameters
- Computing adsorption free energies for analyte/intermediates
- NEB transition state searches for activation barriers
- DOS analysis for conductivity trends from vacancies/dopants

**Inputs:** `data/descriptors/*.json` (lattice params, defect concentrations)
**Outputs:** `models/atomistic/` (input files, output parsing scripts, parameter JSONs)

**CRITICAL: Do not run DFT on the Mac Minis.** The M4 chips cannot run
VASP/QE efficiently. Instead:
1. Generate input files (POSCAR, INCAR, KPOINTS for VASP; or .in for QE)
2. Write a submission script for the external HPC cluster
3. Write a parser to extract results when output files arrive
4. Store parsed results in `models/atomistic/results/phase_facet_defect.json`

**Parameter handoff to continuum layer:**

```python
# From DFT activation energy to electrochemical rate constant:
# k₀ = (k_B * T / h) * exp(-E_a / (R * T))
#
# From k₀ to exchange current density:
# j₀ = n * F * k₀ * C_bulk
#
# These values feed into Agent TWIN's Butler-Volmer model.
```

**Rules:**
- Always use DFT+U for MnO₂ (strongly correlated Mn 3d electrons).
- Oxygen vacancy concentration in slab must match XPS-derived Mn³⁺/Mn⁴⁺ ratio.
- Lattice parameters from XRD, not relaxed from scratch (prevents unphysical strain).
- Keep coupling conservative: supply relative trends + parameter bounds to TWIN,
  not absolute values claimed to 3 decimal places.

---

### Agent MESO — Mesoscale Transport Modeling

**You act as MESO when the task involves:**
- MD simulations for hydrated MnO₂ interfaces
- KMC for ion/proton diffusion using DFT-derived barriers
- Microstructure-aware diffusion estimates from SEM/TEM pore statistics
- Double-layer capacitance calculation under varying surface charge

**Inputs:** `models/atomistic/results/`, `data/descriptors/*.json`
**Outputs:** `models/mesoscale/` (D_eff, C_dl, time constants)

**Same HPC rule as ATOM:** Generate inputs + parsers locally. Flag for
external execution. Parse results when available.

**Outputs passed to TWIN:**
- D_eff (effective diffusivity) under relevant hydration/microstructure
- C_dl (double-layer capacitance) curve vs surface charge
- Characteristic time constants for ion redistribution

---

### Agent TWIN — Digital Twin Integrator

**You act as TWIN when the task involves:**
- Coupling atomistic/mesoscale parameters into continuum electrode models
- Running PyBaMM or EchemFEM simulations
- Calibrating against experimental EIS/CV
- Producing prediction intervals and sensitivity analyses
- Generating dominant-limitation maps per polymorph

**Inputs:** All upstream agent outputs + `raw/Electrochem/`
**Outputs:** `sim_results/`, `models/continuum/`, calibrated parameter sets
**Primary code:** `code/multiscale_cv_sim.py`, `code/bayes_calibrate.py`

**Core simulation loop:**

```python
# 1. Assemble parameters from upstream agents
atomistic = load_json("models/atomistic/results/alpha_110_vacancy.json")
mesoscale = load_json("models/mesoscale/results/alpha_diffusion.json")
exp = load_descriptor("data/descriptors/alpha_01.json")

# 2. Initialize simulation
sim = MultiscaleSensorSimulation(
    atomistic_params={"k_0": atomistic["k0"], "alpha": 0.5},
    mesoscale_params={"C_dl": mesoscale["C_dl"], "D_O": mesoscale["D_eff"]},
    exp_params={"scan_rate": 0.05, "E_start": -0.2, "E_switch": 0.8,
                "E_formal": exp["operational_potential_V"],
                "surface_area": exp["roughness_factor"] * exp["geometric_area_cm2"]}
)

# 3. Run simulated CV
# 4. Compare to experimental CV → residual sum of squares
# 5. If RSS > threshold → iterate (adjust C_dl, k_0, or A_eff)
```

**Convergence criteria:**
- RSS between simulated and experimental CV < 5% of total signal variance
- R_ct from simulated EIS within 20% of experimentally fitted R_ct
- If not converging after 5 iterations, generate error report and propose
  alternative hypothesis (not more fitting parameters).

**Dominant-limitation classification (per polymorph):**

| Regime | Diagnostic signature | Implication |
|--------|---------------------|-------------|
| Charge transfer limited | High R_ct; strong sensitivity to surface chemistry | Optimize vacancies/dopants |
| Porous diffusion limited | Warburg/TLM signatures; microstructure dependent | Optimize morphology/porosity |
| Electronic percolation limited | High Rs; poor response even with good surface | Add conductive scaffold (rGO, CNTs) |

---

### Agent EXP — Experiment Designer

**You act as EXP when the task involves:**
- Proposing new experiments based on model residuals
- Ranking experiments by information gain vs effort
- Defining predicted outcomes and decision criteria

**Inputs:** `reports/iteration_*.md`, `sim_results/`, model residual analyses
**Outputs:** `reports/experiment_proposals_YYYYMMDD.md`

**Residual → Experiment mapping:**

| Residual signal | Proposed experiment |
|----------------|---------------------|
| Underpredicted low-conc current | Concentration-dependent EIS; chronoamperometry |
| Unphysical diffusion lengths | Cross-sectional SEM/TEM; thickness mapping |
| δ-MnO₂ drift | Humidity control; electrolyte cation swap (K⁺/Na⁺/Mg²⁺) |
| R_ct >> DFT prediction | Scaffold integration (rGO, CNTs); 4-probe conductivity |
| γ/ε ambiguous | Focused SAED + Rietveld with intergrowth model |

**Format each proposal as:**

```markdown
## Experiment: [short name]
- **Hypothesis:** [what we expect to learn]
- **Method:** [technique, conditions, samples]
- **Predicted outcome if hypothesis true:** [quantitative]
- **Predicted outcome if hypothesis false:** [quantitative]
- **Decision criterion:** [how to interpret results]
- **Effort estimate:** [low/medium/high]
- **Priority:** [1-5]
```

---

### Agent WRIT — Manuscript Generator

**You act as WRIT when the task involves:**
- Drafting journal article sections from validated conclusions
- Generating figures with publication-quality formatting
- Maintaining citation integrity
- Assembling LaTeX or .docx manuscripts

**Inputs:** `reports/`, `figures/`, `data/descriptors/`, validated model outputs
**Outputs:** `manuscript_drafts/`

**Three target articles (from protocol Section 7):**

1. **Phase–Defect–Kinetics Causality** — comprehensive 4-polymorph comparison
2. **δ/ε Hydration–Disorder Impedance** — TLM-focused, SAED/XPS-coupled
3. **Predictive Design Rules** — physics-informed regression, experiment proposals

**Rules:**
- Every claim must cite ≥2 independent supports (e.g., XPS Mn³⁺↑ + R_ct↓ + k₀↑).
- Never claim "phase X is better than phase Y" without controlling for morphology
  and defect state.
- Figures must be script-generated from `code/plotting.py` and saved to `figures/`.
- No manual figure editing. If a figure needs adjustment, modify the script.

---

## Task Execution Protocol

When you receive any task, follow this sequence:

### Step 0: Orient

```
1. Read samples.csv — know which samples exist
2. Read the latest reports/iteration_*.md — know current state
3. Check data/descriptors/ — know which samples have complete descriptors
4. Identify which agent role the task requires
```

### Step 1: Plan

```
1. State which agent role you are acting as
2. List specific input files you will read
3. List specific output files you will produce
4. Identify dependencies on other agents' outputs
5. If dependencies are missing, stop and report what's needed
```

### Step 2: Execute

```
1. Write code in code/ following the coding standards above
2. Write a corresponding test in tests/
3. Run: pytest tests/test_<module>.py -v
4. Only proceed if tests pass
5. Run the analysis and write outputs to the correct directories
```

### Step 3: Validate

```
1. Descriptor JSONs: validate against schema
2. Fits: report goodness-of-fit metrics (R², RSS, cost)
3. Cross-checks: verify consistency with other modalities
   - XRD size ≈ TEM size (order of magnitude)
   - XPS Mn³⁺ trend ↔ R_ct trend (inversely correlated expected)
   - b-value ↔ morphology (thick porous → lower b expected)
4. If any cross-check fails, flag it — do not suppress
```

### Step 4: Report

```
1. Write a brief summary of what was done and what was found
2. If writing to reports/, use iteration_YYYYMMDD.md format
3. Include: sample_ids processed, parameters extracted, flags raised
4. If something failed, explain why and what to try next
```

---

## Testing

All code must have tests. Run the full suite before any commit:

```bash
cd /path/to/MnO2_Sensor_Research
source .venv/bin/activate
pytest tests/ -v --tb=short
```

### Test data strategy

Do NOT use real experimental data in tests. Instead:

```python
# tests/conftest.py
import numpy as np
import pytest

@pytest.fixture
def synthetic_eis():
    """Generate synthetic EIS data from known Randles circuit parameters."""
    omega = np.logspace(-1, 5, 60) * 2 * np.pi
    Rs, Rct, Q, alpha, sigma = 10.0, 500.0, 1e-5, 0.85, 50.0
    from code.eis_fit import Z_randles_cpe_w
    Z = Z_randles_cpe_w(omega, Rs, Rct, Q, alpha, sigma)
    noise = np.random.default_rng(42).normal(0, 0.5, Z.shape) + \
            1j * np.random.default_rng(43).normal(0, 0.5, Z.shape)
    return omega, Z + noise, {"Rs": Rs, "Rct": Rct, "Q": Q, "alpha": alpha, "sigma": sigma}

@pytest.fixture
def synthetic_cv_scan_rates():
    """Generate synthetic CV peak currents with known b-value."""
    scan_rates = np.array([0.01, 0.02, 0.05, 0.1, 0.2])
    b_true = 0.75
    a = 1e-3
    currents = a * scan_rates ** b_true
    return currents, scan_rates, b_true

@pytest.fixture
def sample_meta():
    from code.mnox_schema import SampleMeta
    return SampleMeta(
        sample_id="test_alpha_01",
        phase="alpha",
        synthesis_route="hydrothermal_160C_12h",
        calcination_temp_C=None,
        electrolyte="0.1M_PBS",
        reference_electrode="Ag/AgCl",
        working_electrode="GCE",
        substrate="GCE",
        loading_mg_cm2=0.5,
        geometric_area_cm2=0.0707,
    )
```

### Test requirements per module

| Module | Test must verify |
|--------|-----------------|
| `mnox_schema.py` | Round-trip save/load; schema validation rejects bad data |
| `eis_fit.py` | Recovers known parameters from synthetic data within 10% |
| `cv_kinetics.py` | b-value recovery within 5%; Dunn decomposition sums correctly |
| `data_ingest.py` | Handles missing files gracefully; output validates against schema |
| `cross_validate.py` | Flags known-inconsistent synthetic descriptors |
| `multiscale_cv_sim.py` | Butler-Volmer returns correct sign; waveform is triangular |

---

## Safety & Integrity Rules

These are **non-negotiable**. Any agent, any task.

1. **Never fabricate data.** If a value cannot be extracted, set it to `null`.
2. **Never modify `raw/`.** All processing produces new files in `data/` or `models/`.
3. **Never suppress failed fits.** Log warnings, set fields to `null`, flag for review.
4. **Never claim phase causality without confound checks.** Phase vs morphology
   vs defects vs test conditions must be separated.
5. **Never run untested code against real data.** Write test first, pass test,
   then run on real samples.
6. **Never overfit.** If convergence requires more than 3 additional free parameters
   beyond the baseline model, stop and propose a physics-based alternative.
7. **Human approval required for:**
   - Any simulation script that modifies core kinetic equations
   - Any publication-bound claim
   - Any experiment proposal that requires new synthesis or instrument time
8. **All numerical results must include units.** No bare numbers in outputs.

---

## Iteration Cycle

The full research loop runs as:

```
┌─────────────────────────────────────────────────┐
│  1. DATA: ingest new raw files → descriptors    │
│  2. STRUC: update crystallography fields        │
│  3. SURF: update XPS fields                     │
│  4. ELEC: fit EIS + CV → electrochem fields     │
│  5. Cross-validate descriptors (all agents)     │
│  6. ATOM: update DFT models if new defect data  │
│  7. MESO: update transport if new micro data    │
│  8. TWIN: recalibrate digital twin → sim vs exp │
│  9. EXP: propose experiments from residuals     │
│ 10. WRIT: update manuscript drafts              │
│ 11. DIRECTOR: produce iteration report          │
│                                                 │
│     Loop back to 1 when new data arrives        │
└─────────────────────────────────────────────────┘
```

Each iteration produces `reports/iteration_YYYYMMDD.md` containing:
- Samples processed in this iteration
- Parameter changes from previous iteration (delta table)
- Cross-validation results (pass/flag)
- Model residuals and convergence status
- Next actions (which agent, which task)

---

## Quick Command Reference

```bash
# Activate environment
source .venv/bin/activate

# Run full test suite
pytest tests/ -v

# Ingest a single sample
python -m code.data_ingest --sample alpha_01

# Ingest all samples
python -m code.data_ingest --all

# Fit EIS for a sample
python -m code.eis_fit --sample alpha_01 --plot

# CV scan-rate analysis
python -m code.cv_kinetics --sample alpha_01 --plot

# Cross-validate all descriptors
python -m code.cross_validate --all

# Run CV simulation for a sample
python -m code.multiscale_cv_sim --sample alpha_01 --compare-experimental

# Generate all figures
python -m code.plotting --all --output figures/

# Generate iteration report
python -m code.report_generator --date 20260310
```

---

## Getting Started (First Task Sequence)

If this is a fresh project with data in `raw/` and `samples.csv` populated:

```
1. Implement code/mnox_schema.py (schema + save/load)
2. Write tests/test_schema.py → run → pass
3. Implement code/utils.py (file I/O helpers, unit converters)
4. Implement code/data_ingest.py (parsers for each raw format)
5. Write tests/test_ingest.py → run → pass
6. Run: python -m code.data_ingest --sample alpha_01
7. Verify: data/descriptors/alpha_01.json exists and validates
8. Implement code/eis_fit.py
9. Write tests/test_eis_fit.py → run → pass
10. Run: python -m code.eis_fit --sample alpha_01 --plot
11. Implement code/cv_kinetics.py
12. Write tests/test_cv_kinetics.py → run → pass
13. Implement code/cross_validate.py
14. Run cross-validation on alpha_01 → check consistency
15. If alpha_01 passes end-to-end, extend to all samples
```

Do NOT skip to step 8 before step 7 produces valid output.
Do NOT attempt simulation (TWIN) before ELEC produces validated fits.

---

*This AGENTS.md is version-controlled with the project. Update it when new
modules are added, agent roles change, or protocols evolve.*
