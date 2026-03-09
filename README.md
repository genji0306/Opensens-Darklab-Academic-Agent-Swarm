# Opensens-Darklab-Academic-Agent-Swarm
MnO₂ Electrochemical Sensor Research Swarm Protocol
Unified Multiscale Workflow & OpenCLAW Megaprompt — DARKLAB/Opensens
Version: 1.0
Date: 2026-03-09
Author: Steve Trinh / Opensens
System: DARKLAB (2× Mac Mini cluster via OpenClaw)
Target: Autonomous, iterative MnO₂ polymorph research pipeline

1. Executive Summary
This document synthesizes three independent research analyses (Perplexity prompt scaffold, Gemini multiscale workflow, Claude deep research report) into a single, operationalized protocol for an AI-driven research swarm. The protocol addresses:

Phase-aware characterization of α, γ, δ, and ε-MnO₂ polymorphs for electrochemical sensing
Multiscale simulation (DFT → MD/KMC → continuum/FEM) with explicit experimental data fusion
Autonomous agent orchestration via OpenCLAW YAML workflows and persistent memory
Publication-grade outputs (3 article concepts, reproducible code, structured data)

The critical design principle: every claimed "phase effect" must survive morphology/defect confound checks. Phase identity, defect density, microstructure, and test conditions are never conflated.

2. Polymorph Reference Architecture
Each MnO₂ phase is treated as a transport–reactivity architecture rather than a mere crystallographic label. The swarm agents must internalize these distinctions.
α-MnO₂ (Cryptomelane/Hollandite) — Stabilized 2×2 Tunnel Template

Structure: Tetragonal; 2×2 tunnels (~0.46 nm) hosting K⁺/Ba²⁺/NH₄⁺ stabilizer cations
Morphology: High-aspect-ratio nanowires/nanorods (L ≈ 2.4 μm, d ≈ 20–30 nm)
Key XRD: 2θ = 12.7°, 18.0°, 28.6°, 36.7°, 38.6°, 41.9°; d₁₁₀ ≈ 0.69–0.70 nm
Sensing: Highest H₂O₂ sensitivity (0.094 mA·μM⁻¹·cm⁻²); 138 F/g at 1 A/g
Simulation priority: Tunnel diffusion + vacancy-enhanced electron transfer on (110) facet

γ-MnO₂ (Ramsdellite/Pyrolusite Intergrowth) — Defect-Enabled Conductor–Reactor

Structure: Orthorhombic intergrowth of 1×1 pyrolusite + 1×2 ramsdellite; De Wolff defects + microtwinning
Morphology: Urchin-like architectures, nanofibrous networks (d ≈ 5 μm)
Key XRD: 2θ = 22.2°, 37.6°, 42.5°, 56.2°, 65.3° (broad peaks due to disorder)
Sensing: Lower sensitivity (0.030 mA·μM⁻¹·cm⁻²); 103 F/g; poor bulk conductivity
Simulation priority: Disorder is signal, not noise — intergrowth fraction controls transport

δ-MnO₂ (Birnessite) — Hydrated Layered Ion-Exchange Platform

Structure: Monoclinic/hexagonal; 2D edge-sharing MnO₆ layers with interlayer H₂O + alkali cations
Morphology: Ultra-thin nanosheets/nanoflakes (3–5 nm lateral)
Key XRD/SAED: d₀₀₁ ≈ 0.70 nm (interlayer); d₁₀₀ ≈ 0.24 nm; diffuse rings (poor crystallinity)
Sensing: High initial surface area but cycle-dependent degradation (restacking)
Simulation priority: Hydration/interlayer dynamics; operando structural evolution under cycling

ε-MnO₂ (Akhtenskite) — Nanocrystalline Vacancy-Rich MnO₂

Structure: Hexagonal defect-NiAs; randomized Mn⁴⁺ vacancies; extensive twinning
Key XRD: d ≈ 0.242, 0.213, 0.164 nm; broad peak at ~0.42 nm (synthesis-dependent)
Sensing: Moderate sensitivity (0.070 mA·μM⁻¹·cm⁻²); morphology-dependent performance
Simulation priority: High-energy active sites from domain boundaries; vacancy density quantification

Quick Reference Table
PhaseSystemArchitectureMorphologyKey d-spacings (nm)H₂O₂ SensitivityαTetragonal2×2 TunnelsNanowires/rods0.69–0.70 (110)0.094 mA·μM⁻¹·cm⁻²γOrthorhombicIntergrowthUrchin-like/fibers0.40, 0.24 (variable)0.030 mA·μM⁻¹·cm⁻²δMonoclinic2D LayeredNanosheets/flakes0.70 (001), 0.24 (100)Low / cycle-dependentεHexagonalDefective 1×1Nanoparticles0.242, 0.213, 0.1640.070 mA·μM⁻¹·cm⁻²

3. Experimental Data → Quantitative Descriptors
The swarm converts each characterization modality into a compact set of physically interpretable parameters. These become the single source of truth for all downstream modeling.
3.1 Data Schema (per sample)
python# mnox_schema.py — Canonical descriptor record for each MnO₂ specimen
from __future__ import annotations
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Literal, Optional, Dict
import json

Phase = Literal["alpha", "gamma", "delta", "epsilon"]

@dataclass(frozen=True)
class SampleMeta:
    sample_id: str
    phase: Phase
    synthesis_route: str
    calcination_temp_C: Optional[float]
    electrolyte: str
    reference_electrode: str
    working_electrode: str
    substrate: str
    loading_mg_cm2: Optional[float]
    geometric_area_cm2: Optional[float]
    notes: str = ""

@dataclass
class Descriptors:
    # === XRD / SAED ===
    lattice_params: Dict[str, float]       # {"a":..., "b":..., "c":..., "beta":...}
    crystallite_size_nm: Optional[float]
    microstrain: Optional[float]
    disorder_metric: Optional[float]       # γ intergrowth proxy, ε domain ordering, δ stacking
    phase_purity: Optional[float]          # Rietveld phase fraction (0–1)

    # === SEM / TEM ===
    feature_size_nm: Dict[str, float]      # {"rod_d":..., "rod_L":..., "sheet_t":...}
    porosity_proxy: Optional[float]
    roughness_factor: Optional[float]      # ECSA / geometric area

    # === XPS ===
    mn_aos: Optional[float]                # Average Mn oxidation state (Mn 3s splitting)
    mn3_fraction: Optional[float]          # Mn³⁺/(Mn³⁺+Mn⁴⁺) from 2p₃/₂ deconvolution
    mn2_fraction: Optional[float]          # Mn²⁺ fraction (extreme surface reduction)
    o1s_components: Dict[str, float]       # normalized: lattice_O, OH, adsorbed_H2O

    # === Electrochemistry ===
    rs_ohm: Optional[float]                # Solution resistance
    rct_ohm: Optional[float]               # Charge transfer resistance
    cdl_F: Optional[float]                 # Double-layer capacitance (or CPE Q + α)
    cpe_alpha: Optional[float]             # CPE exponent
    warburg_coeff: Optional[float]         # Warburg coefficient σ
    b_value_mean: Optional[float]          # CV scan-rate b-value (0.5=diffusion, 1.0=surface)

    # === Sensing Performance ===
    sensitivity_mA_uM_cm2: Optional[float]
    lod_uM: Optional[float]
    linear_range_uM: Optional[float]
    operational_potential_V: Optional[float]

def save_record(meta: SampleMeta, desc: Descriptors, outpath: Path) -> None:
    out = {"meta": asdict(meta), "descriptors": asdict(desc)}
    outpath.parent.mkdir(parents=True, exist_ok=True)
    outpath.write_text(json.dumps(out, indent=2))
3.2 Descriptor Extraction Protocols
Crystallography (XRD + SAED):

Phase fractions and amorphous content via Rietveld or whole-pattern fitting
Anisotropic crystallite size and microstrain (Williamson-Hall or WPPM)
Disorder metrics: γ intergrowth descriptors from peak-shape models; ε domain-ordering from broad-peak features; δ stacking fault indices
SAED cross-check: local d-spacings and zone-axis twinning/stacking evidence

Morphology (SEM/TEM):

Particle/feature size distributions (nanorod d/L; nanosheet t/area; aggregate size)
Porosity proxies from imaging (void fraction, tortuosity, connectivity)
Facet exposure from HRTEM (vacancy formation is facet-dependent)

Surface Chemistry (XPS):

Mn AOS via Mn 3s multiplet splitting + supportive Mn 2p/3p analysis
Mn 2p₃/₂ deconvolution: Mn²⁺ (~641.3 eV), Mn³⁺ (~642.5 eV), Mn⁴⁺ (~644.0 eV) using Shirley background + pseudo-Voigt
O 1s deconvolution: lattice O (~529.8 eV) vs defective/OH (~531.5 eV)
Mn³⁺/Mn⁴⁺ ratio = primary oxygen vacancy proxy

Electrochemistry (CV + EIS):

b-value analysis: log(i) vs log(v) to separate surface vs diffusion control
Dunn decomposition: i(V) = k₁v + k₂v^(1/2) for capacitive/diffusive fractions
EIS: Rₛ, R_ct, C_dl/CPE, Warburg via Randles-CPE baseline fit
Upgrade to transmission-line model when SEM/TEM indicates thick porous films

3.3 Cross-Modality Consistency Gates
These are hard gates — no comparative claims pass without them:

XRD crystallite size vs TEM domain size: order-of-magnitude agreement required
XPS AOS trends vs disorder/hydration: more defective/hydrated → more mixed valence expected
R_ct trends vs microstructure + surface chemistry: lower R_ct should co-occur with improved sensor response
Phase assignment for γ/ε: requires SAED/TEM confirmation before mechanistic claims (XRD alone ambiguous)
EIS fit uniqueness: if non-unique → run parameter identifiability and sensitivity analysis; no mechanism claims


4. Multiscale Simulation Architecture
The simulation stack consumes experimental descriptors and returns mechanistic, falsifiable conclusions. Models have explicit parameter handoffs — never monolithic.
4.1 Layer 1: Atomistic — DFT(+U) Surface Chemistry
Question answered: Which phase/defect/facet provides most favorable adsorption/reaction energetics?
Inputs from experiment:

XRD/SAED d-spacings → lattice parameters for slab construction
XPS Mn³⁺/Mn⁴⁺ ratio → oxygen vacancy concentration for supercell defect insertion

Computation:

DFT+U slab models for representative facets of α/γ/δ/ε (Hubbard U for Mn 3d localization)
Adsorption free energies (ΔG_ads) for H₂O₂ and intermediates on each surface
NEB transition state analysis → activation energy barrier (E_a)
Projected DOS around Fermi level → conductivity trends from vacancies/dopants

Key bridge equation (transition state theory → electrochemical kinetics):

k₀ = (k_B·T / h) · exp(−E_a / R·T)
j₀ = n·F·k₀·C_bulk (exchange current density)

Outputs passed down: site densities, adsorption rankings, k₀ priors, E_a values
4.2 Layer 2: Mesoscale — Ion/Water Transport
Question answered: How do tunnels/layers/hydration translate into effective ion mobility?
Approaches:

MD for hydrated layered MnO₂ (especially δ-birnessite): water layering, cation coordination
KMC or coarse-grained hopping for ion/proton diffusion in tunnel systems using DFT barriers
Microstructure-aware random-walk diffusion from SEM/TEM-derived pore statistics

Outputs passed down: D_eff, hydration-state dependence, time constants, accessibility factors
4.3 Layer 3: Continuum — Porous Electrode Digital Twin
Question answered: Given microstructure + kinetics + transport, what sensor response should we see?
Framework:

PNP + Butler-Volmer (or simplified Nernst diffusion + heterogeneous kinetics)
Transmission-line / porous electrode impedance when distributed resistances present
Implementation via PyBaMM or EchemFEM (Python ecosystem)

Calibration strategy:

Fit directly to EIS spectra (multi-frequency) and CV shapes (multi-scan-rate)
Not separate equivalent circuits without mechanistic linkage

Butler-Volmer core:
j_loc = j₀ · [exp(α_a·n·F·η / R·T) − exp(−α_c·n·F·η / R·T)]
I_total(t) = A_surf · j_faradaic(t) + A_surf · C_dl · (dE/dt)
4.4 Layer 4: Data Fusion — Physics-Informed Multimodal Regression
Purpose: Disentangle phase vs morphology vs defect contributions.
Approach: Bayesian hierarchical model predicting either sensor FoMs (sensitivity, LOD) or mechanistic intermediates (R_ct, j₀, D_eff) from compiled descriptors, with XPS/SEM-informed priors.
Strategic rule: Keep coupling conservative — DFT supplies relative trends and parameter bounds; CV/EIS provides final calibrated values.

5. Code Frameworks
5.1 EIS Fitting — Randles/CPE Baseline + TLM Upgrade
python# eis_fit.py — Baseline diagnostic; upgrade to TLM for porous films
import numpy as np
from dataclasses import dataclass
from scipy.optimize import least_squares

@dataclass
class RandlesCPEFit:
    Rs: float
    Rct: float
    Q: float       # CPE magnitude
    alpha: float   # CPE exponent
    sigma: float   # Warburg coefficient

def Z_cpe(omega, Q, alpha):
    return 1.0 / (Q * (1j * omega) ** alpha)

def Z_warburg(omega, sigma):
    return sigma / np.sqrt(1j * omega)

def Z_randles_cpe_w(omega, Rs, Rct, Q, alpha, sigma):
    Zw = Z_warburg(omega, sigma)
    Zc = Z_cpe(omega, Q, alpha)
    Zpar = 1.0 / (1.0 / (Rct + Zw) + 1.0 / Zc)
    return Rs + Zpar

def fit_randles(omega, Z_exp, p0):
    """Fit Randles-CPE-Warburg model to experimental EIS data."""
    def resid(p):
        Z_mod = Z_randles_cpe_w(omega, *p)
        return np.concatenate([(Z_mod.real - Z_exp.real), (Z_mod.imag - Z_exp.imag)])

    bounds = ([0, 0, 0, 0.2, 0], [np.inf, np.inf, np.inf, 1.0, np.inf])
    res = least_squares(resid, x0=np.array(p0, dtype=float), bounds=bounds, max_nfev=8000)
    Rs, Rct, Q, alpha, sigma = res.x
    return RandlesCPEFit(Rs=Rs, Rct=Rct, Q=Q, alpha=alpha, sigma=sigma), res
5.2 CV Scan-Rate Kinetics
python# cv_kinetics.py — b-value analysis and Dunn decomposition
import numpy as np

def b_value_at_potential(currents, scan_rates):
    """Fit log(i) = log(a) + b·log(v); b≈1 surface-controlled, b≈0.5 diffusion."""
    x = np.log(scan_rates)
    y = np.log(np.abs(currents) + 1e-30)
    b, _ = np.polyfit(x, y, deg=1)
    return float(b)

def dunn_decomposition(i_v, scan_rates):
    """i(V) = k₁·v + k₂·v^(1/2) at each potential; returns k₁(V), k₂(V)."""
    vs = scan_rates
    X = np.sqrt(vs)
    k1 = np.zeros(i_v.shape[0])
    k2 = np.zeros(i_v.shape[0])
    for j in range(i_v.shape[0]):
        y = i_v[j, :] / np.sqrt(vs)
        slope, intercept = np.polyfit(X, y, deg=1)
        k1[j] = slope
        k2[j] = intercept
    return k1, k2

def capacitive_fraction(i_v, scan_rate, k1, k2):
    """Compute capacitive fraction at a given scan rate."""
    i_cap = k1 * scan_rate
    i_diff = k2 * np.sqrt(scan_rate)
    frac = np.trapz(np.abs(i_cap), dx=1.0) / (np.trapz(np.abs(i_cap + i_diff), dx=1.0) + 1e-30)
    return float(frac), i_cap, i_diff
5.3 Multiscale CV Simulation (ODE Baseline)
python# multiscale_cv_sim.py — Butler-Volmer + DFT-parameterized kinetics
import numpy as np

class MultiscaleSensorSimulation:
    def __init__(self, atomistic_params, mesoscale_params, exp_params):
        # DFT-derived
        self.k_0 = atomistic_params.get('k_0', 1.2e-4)    # cm/s
        self.alpha = atomistic_params.get('alpha', 0.5)
        # MD-derived
        self.C_dl = mesoscale_params.get('C_dl', 20.0e-6)  # F/cm²
        self.D_O = mesoscale_params.get('D_O', 1.0e-5)     # cm²/s
        self.D_R = mesoscale_params.get('D_R', 1.0e-5)
        # Experimental
        self.F = 96485.33
        self.R_const = 8.314
        self.T = exp_params.get('temperature', 298.15)
        self.n = exp_params.get('electrons_transferred', 1)
        self.A_surf = exp_params.get('surface_area', 0.05)
        self.v = exp_params.get('scan_rate', 0.1)
        self.E_start = exp_params.get('E_start', 0.0)
        self.E_switch = exp_params.get('E_switch', 0.8)
        self.E_0 = exp_params.get('E_formal', 0.4)

    def butler_volmer_kinetics(self, E_applied, C_O_surf, C_R_surf):
        eta = E_applied - self.E_0
        k_f = self.k_0 * np.exp(-self.alpha * self.n * self.F * eta / (self.R_const * self.T))
        k_b = self.k_0 * np.exp((1 - self.alpha) * self.n * self.F * eta / (self.R_const * self.T))
        return self.n * self.F * (k_f * C_O_surf - k_b * C_R_surf)

    def potential_sweep_waveform(self, t):
        t_switch = (self.E_switch - self.E_start) / self.v
        if t <= t_switch:
            return self.E_start + self.v * t
        else:
            return self.E_switch - self.v * (t - t_switch)
5.4 Bayesian Calibration Pattern
python# bayes_calibrate.py — Physics-informed parameter inference with experimental priors
import numpy as np

def amperometric_forward(conc, k_eff, A_eff, n=2, F=96485.33):
    """Simplified: i = n·F·A_eff·k_eff·conc. Replace with mixed kinetic+diffusion model."""
    return n * F * A_eff * k_eff * conc

def bayesian_fit(conc, current, sigma_i, priors):
    """
    Implementation pattern for PyMC:
    Priors informed by:
      - EIS R_ct distributions → k_eff prior
      - SEM/TEM area estimates → A_eff prior
      - XPS Mn³⁺/vacancy proxies → k_eff prior shift
    
    with pm.Model() as m:
        k_eff ~ LogNormal(mu=priors['k_eff_mu'], sigma=priors['k_eff_sigma'])
        A_eff ~ LogNormal(mu=priors['A_eff_mu'], sigma=priors['A_eff_sigma'])
        i_hat = amperometric_forward(conc, k_eff, A_eff)
        current_obs ~ Normal(mu=i_hat, sigma=sigma_i)
        trace = pm.sample(2000, tune=1000)
    return trace
    """
    raise NotImplementedError("Implement with PyMC; priors from EIS/XPS/SEM")

6. Research Protocol — Stage-Gated Execution
Phase 1: Data Ingestion & Structural Mapping

Establish sample registry (immutable IDs, full metadata manifest)
Deconvolute XPS for Mn³⁺/Mn⁴⁺ ratios (oxygen vacancy proxy)
Index XRD/SAED to confirm polymorphic purity; extract d-spacings
Process SEM/TEM for geometric boundaries, aspect ratios, active surface area
Run hard QC gates: charge correction consistency, iR compensation, frequency range

Phase 2: Atomistic Parameterization (DFT)

Build periodic slab models from Phase 1 lattice parameters
Insert oxygen vacancies matching XPS-derived defect concentrations
Compute surface formation energies, DOS, binding energies (ΔG_ads)
Execute NEB for transition state → E_a → k₀ conversion

Phase 3: Mesoscale Transport (MD/KMC)

Initialize MD from SEM/TEM geometric constraints
Simulate electrode-electrolyte interface for D_eff at operating conditions
Calculate theoretical C_dl under varying surface charge
Ensure solvent/ion models match exact experimental electrolyte

Phase 4: Continuum Integration (FEM)

Feed DFT k₀ and MD D_eff/C_dl into PyBaMM or EchemFEM
Construct discretized cell geometry matching experimental setup
Execute simulated CV and EIS at experimental scan rates / frequency ranges
Generate theoretical Nyquist plots and voltammograms

Phase 5: Iterative Validation

Superimpose simulated vs experimental curves
Compute residual sum of squares; identify divergence points
If R_ct deviation > threshold → re-evaluate DFT defect models (loop to Phase 2)
If diffusion mismatch → revise MD solvation structures (loop to Phase 3)
Converge on dominant-limitation map per polymorph:

Charge transfer limited (high R_ct; surface chemistry sensitive)
Porous diffusion limited (Warburg/TLM signatures; microstructure sensitive)
Electronic percolation limited (scaffold integration needed)



Phase 6: Publication & Experiment Design

Generate iteration report with changelog of conclusions
Propose targeted experiments from model residuals
Draft manuscript sections with properly attributed claims


7. Journal Article Concepts
Article 1: Phase–Defect–Kinetics Causality (Comprehensive)
Title: Phase–Defect–Kinetics Coupling in α-, γ-, δ-, and ε-MnO₂ for Electrochemical Sensing: A Multimodal–Multiscale Digital Twin
Abstract: MnO₂ polymorphs exhibit distinct tunnel/layer architectures and defect chemistries that strongly modulate electrochemical sensing performance, yet comparative conclusions are often confounded by correlated morphology and surface state changes. We integrate XRD, SEM/TEM/SAED, XPS, CV, and EIS for α-, γ-, δ-, and ε-MnO₂ to compile a physically interpretable descriptor set spanning crystallographic disorder, microstructure, Mn oxidation state distribution, and interfacial charge-transfer characteristics. A multiscale digital twin links phase-specific surface chemistry to porous-electrode transport and impedance response, calibrated directly against EIS/CV datasets. The resulting model disentangles phase identity from defect density and microstructure, revealing the dominant limitation regime for each polymorph. This framework provides generalizable design rules for MnO₂ polymorph and processing window selection.
Sections: Introduction → Experimental dataset and descriptor extraction → Phase/disorder quantification (XRD/SAED) → Surface chemistry analysis (XPS) → Electrochemical kinetics and impedance → Multiscale model construction/calibration → Dominant-limitation maps → Conclusions
Article 2: δ/ε Hydration–Disorder Impedance Physics
Title: Hydration and Structural Disorder Control Distributed Charge Transfer in δ- and ε-MnO₂ Sensor Films: Evidence from SAED/XPS-Coupled Transmission-Line Modeling
Abstract: Layered δ-MnO₂ and defect-rich ε-MnO₂ frequently show broadened diffraction and non-ideal impedance suggestive of distributed transport. We quantify local disorder using SAED-supported crystallography and Mn oxidation states via XPS, then interpret EIS and scan-rate CV using porous-electrode TLM constrained by SEM/TEM microstructure. The calibrated model isolates how hydration/interlayer chemistry (δ) and vacancy/domain-boundary density (ε) reshape diffusion lengths, CPE behavior, and R_ct. Impedance dispersion correlates systematically with disorder metrics, enabling predictive mapping from microscopy to sensor kinetics.
Sections: Motivation → SAED-informed disorder descriptors → XPS oxidation/oxygen speciation → EIS/CV TLM modeling → Structure–impedance correlations → Sensing optimization implications
Article 3: Predictive Design Rules
Title: From Multimodal Descriptors to Design Rules: Predictive Optimization of MnO₂ Polymorph Microstructure for Electrochemical Sensors
Abstract: We compile a multi-technique dataset for α-, γ-, δ-, and ε-MnO₂ and develop a physics-informed regression model predicting kinetic parameters from crystallographic and surface descriptors, together with microstructure statistics. The model proposes targeted synthesis modifications (cation insertion, thermal treatments, scaffold integration) to shift each polymorph toward desired limitation regimes. Prospective validation experiments confirm predicted rate-limiting steps. The workflow enables continuous refinement and transferable design rules across analyte classes.
Sections: Dataset standardization → Descriptor engineering → Physics-informed learning → Experimental proposals → Generalized design rules

8. OpenCLAW Megaprompt — Director Agent
═══════════════════════════════════════════════════════════════════
SYSTEM INSTRUCTION: OPENCLAW MnO₂ RESEARCH DIRECTOR
═══════════════════════════════════════════════════════════════════

You are the primary orchestration agent (Director) operating within the DARKLAB
OpenCLAW execution framework (2× Mac Mini cluster). Your prime directive is to
autonomously manage a continuous, iterative research pipeline for multiscale
simulation and experimental integration of MnO₂ polymorphs (α, γ, δ, ε) for
electrochemical sensor development.

═══════════════════════════════════════════════════════════════════
1. OPERATING PRINCIPLES (NON-NEGOTIABLE)
═══════════════════════════════════════════════════════════════════

- Always separate: phase effects vs morphology vs surface chemistry vs test conditions
- Every factual claim requires a citable source OR traceable experimental data
  (sample_id + file + analysis code hash)
- Maintain reproducibility: version-controlled code, parameter files, run ledger
- Prefer mechanistic parameters (k₀, D_eff, R_ct, site density) over performance
  metrics alone (sensitivity/LOD), but report both
- Treat equivalent-circuit fits as provisional unless justified by morphology
  and validated by residual analysis
- Never fabricate or extrapolate data beyond physical reality
- If integration fails to converge, generate error card with exact divergence
  metrics and propose alternative atomistic hypothesis

═══════════════════════════════════════════════════════════════════
2. CORE OPERATING PARADIGM
═══════════════════════════════════════════════════════════════════

- Coordinate specialized worker agents via Lobster workflow shell (YAML)
- Communicate using validated JSON payloads via openclaw.invoke protocol
- Maintain context via HyperStack persistent memory (pgvector semantic search)
- Before any new hypothesis: query memory for existing cards tagged with
  [MnO2_Phase], [Simulation_Params], [Convergence_Report]

═══════════════════════════════════════════════════════════════════
3. INPUTS (EXPECTED)
═══════════════════════════════════════════════════════════════════

A. Experimental repository (read-only):
   /raw/XRD/         — diffractograms (.xy, .csv, .raw)
   /raw/SEM/         — micrographs
   /raw/TEM_SAED/    — TEM images + SAED patterns
   /raw/XPS/         — spectra (.vms, .csv)
   /raw/Electrochem/CV/  — cyclic voltammetry (.csv, .mpt)
   /raw/Electrochem/EIS/ — impedance spectra (.csv, .mpt, .DTA)

B. Sample registry:
   samples.csv (sample_id, phase, synthesis, substrate, loading, electrolyte,
                pH, reference, date, notes)

C. Research focus:
   analyte(s), sensing mode (amperometry/DPV/SWV/CV), operating potentials,
   matrix constraints

═══════════════════════════════════════════════════════════════════
4. AGENT SWARM ROLES
═══════════════════════════════════════════════════════════════════

Agent LIT (Literature)
  Task: Build living review on MnO₂ polymorphs for sensing.
  Methods: academic-research-hub + deep-research skills; OpenAlex, arXiv ingestion
  Extract: DFT adsorption energies, SAED d-spacings, XPS binding energies,
           Butler-Volmer parameters
  Output: annotated bibliography + consensus statements + disputed topics list

Agent DATA (Experimental Data Engineer)
  Task: Ingest raw files; enforce metadata; produce standardized cleaned datasets
  Methods: unit normalization, baseline correction, peak fitting, image
           segmentation, provenance tracking
  Output: /data/descriptors/sample_id.json (canonical schema)

Agent STRUC (Crystallography/Defects)
  Task: XRD + SAED analysis; quantify disorder
  Output: phase fractions, lattice params, crystallite size/strain, disorder indices

Agent SURF (Surface Chemistry)
  Task: Quantify Mn oxidation state and O speciation consistently
  Output: Mn AOS, Mn³⁺ fraction, O 1s ratios, uncertainty bounds

Agent ELEC (Electrochemistry)
  Task: Analyze CV and EIS; fit baseline circuits AND porous/TLM models
  Output: Rs, Rct, Cdl/CPE, diffusion params, b-values with caveats

Agent ATOM (Atomistic Modeling)
  Task: Build DFT(+U) models for representative facets/defects
  Output: adsorption rankings, defect formation energies, migration barriers

Agent MESO (Mesoscale Transport)
  Task: MD for hydration/interlayer/tunnel ion motion; KMC with DFT barriers
  Output: D_eff, hydration dependence, time constants

Agent TWIN (Digital Twin Integrator)
  Task: Couple atomistic/mesoscale with continuum porous electrode model;
        calibrate to EIS/CV; produce prediction intervals
  Output: calibrated parameter sets + sensitivity analyses + limitation maps

Agent EXP (Experiment Designer)
  Task: Propose experiments that maximally distinguish hypotheses
  Examples: electrolyte cation swap, controlled hydration, targeted annealing,
            scaffold integration, thickness series
  Output: ranked experiment queue with predicted outcomes + decision criteria

Agent WRIT (Manuscript Generator)
  Task: Convert validated conclusions into journal sections; enforce citations
  Output: /manuscript_drafts/ (LaTeX or docx)

═══════════════════════════════════════════════════════════════════
5. AUTONOMOUS ITERATION LOOP
═══════════════════════════════════════════════════════════════════

Step 1: OBSERVE — Retrieve latest data uploads from user directory
Step 2: RECALL — Pull previous iteration params from HyperStack memory
Step 3: PLAN — Identify deviations between simulated and empirical data;
        formulate parameter update plan
Step 4: DELEGATE — Execute Lobster YAML workflow assigning updates to
        appropriate specialist agents
Step 5: EVALUATE — Require human approval ONLY when deploying modified
        simulation scripts that alter core kinetic equations
Step 6: UPDATE LITERATURE — Check for new papers, contradictions
Step 7: REFIT — Refit electrochemical models; check identifiability
Step 8: RECALIBRATE — Update digital twin; generate predictions
Step 9: HYPOTHESIS TEST —
        If systematic mismatch → propose targeted experiment OR refine physics
        (never overfit)
Step 10: REPORT — Produce iteration_YYYYMMDD.md + changelog

═══════════════════════════════════════════════════════════════════
6. QUALITY GATES
═══════════════════════════════════════════════════════════════════

- No cross-sample comparison unless electrolyte, potential window, loading,
  and preprocessing are controlled or explicitly modeled
- Any "phase effect" claim must survive confound checks:
  (a) microstructure descriptors included
  (b) XPS oxidation state included
  (c) impedance-derived kinetics included
- Publishable claim requires ≥2 independent supports:
  e.g., (XPS Mn³⁺↑ + R_ct↓ + model-calibrated k₀↑) → improved sensing

═══════════════════════════════════════════════════════════════════
7. FAIL-SAFE RULES
═══════════════════════════════════════════════════════════════════

- Ambiguous phase assignment → require SAED/TEM before mechanistic claims
- Non-unique EIS fits → parameter identifiability + sensitivity analysis mandatory
- Divergence > tolerance → error card + alternative hypothesis (no fabrication)

═══════════════════════════════════════════════════════════════════
8. DELIVERABLE FORMATS
═══════════════════════════════════════════════════════════════════

/reports/iteration_YYYYMMDD.md
/data/descriptors/sample_id.json
/models/ (inputs + outputs + parameter files)
/figures/ (scripted generation, reproducible)
/manuscript_drafts/ (LaTeX or docx)

9. Lobster YAML Workflow Template
yamlname: mno2-multiscale-simulation-convergence-pipeline
description: >
  Automates literature parameter extraction, PyBaMM script generation,
  and residual data comparison for MnO₂ sensor optimization.

steps:
  # Step 1: Deep literature extraction for phase-specific parameters
  - id: extract_dft_data
    command: >
      deep-research execute
      --query "Extract exact DFT activation energy barriers (eV) and transition
      state geometries for H2O2 reduction on alpha-MnO2 (110) facet.
      Output as structured JSON."
      --json

  # Step 2: Push parameters into HyperStack persistent memory
  - id: update_memory
    command: hyperstack store --tag "alpha-MnO2_kinetics" --ttl 30d
    stdin: $extract_dft_data.stdout

  # Step 3: Update simulation script with new k₀ values
  - id: generate_simulation
    command: >
      llm-task --agent "coding-worker"
      --prompt "Update Butler-Volmer kinetic definitions and exchange current
      density variables in pybamm_cv_sim.py using the activation energies
      provided. Mass transport equations remain untouched."
      --json
    stdin: $extract_dft_data.stdout

  # Step 4: Execute simulation (REQUIRES HUMAN APPROVAL)
  - id: execute_script
    command: python pybamm_cv_sim.py --output "sim_results/alpha_cv_latest.json"
    approval: required

  # Step 5: Statistical comparison of simulated vs empirical CV
  - id: analyze_convergence
    command: >
      llm-task --agent "data-analyst"
      --prompt "Compare sim_results/alpha_cv_latest.json against
      empirical_data/raw_cv_alpha.csv. Calculate residual sum of squares.
      Suggest next iterative refinement for MD double-layer capacitance."

  # Step 6: Store analysis in memory graph
  - id: log_results
    command: hyperstack store --tag "simulation_convergence_report_alpha"
    stdin: $analyze_convergence.stdout

10. Model-Driven Experiment Proposals
When model residuals indicate specific gaps, the EXP agent generates targeted experiments:
Residual SignalHypothesisProposed ExperimentContinuum underpredicts low-conc currentAdsorption/coverage effectsConcentration-dependent EIS; potential-step chronoamperometryUnphysical diffusion lengths in fitMicrostructure misestimationCross-sectional SEM/TEM; thickness mappingδ-MnO₂ shows driftHydration/structural instabilityHumidity control; electrolyte cation swap (K⁺/Na⁺/Mg²⁺)R_ct much higher than DFT-predictedElectronic percolation limitScaffold integration (rGO, CNTs); conductivity measurementsγ/ε phase distinction unclearIntergrowth fraction ambiguityFocused SAED; Rietveld refinement with intergrowth model

11. Directory Structure
/MnO2_Sensor_Research/
├── raw/
│   ├── XRD/
│   ├── SEM/
│   ├── TEM_SAED/
│   ├── XPS/
│   └── Electrochem/
│       ├── CV/
│       └── EIS/
├── data/
│   ├── descriptors/           # sample_id.json (canonical schema)
│   └── cleaned/               # processed/normalized datasets
├── models/
│   ├── atomistic/             # DFT inputs/outputs
│   ├── mesoscale/             # MD/KMC results
│   └── continuum/             # PyBaMM/EchemFEM scripts + results
├── sim_results/               # simulation output JSONs
├── reports/
│   └── iteration_YYYYMMDD.md  # iteration changelogs
├── figures/                   # scripted, reproducible
├── manuscript_drafts/         # LaTeX or docx
├── code/
│   ├── mnox_schema.py
│   ├── eis_fit.py
│   ├── cv_kinetics.py
│   ├── multiscale_cv_sim.py
│   └── bayes_calibrate.py
├── workflows/
│   └── convergence_pipeline.yaml
├── samples.csv                # master sample registry
└── README.md

12. Key References (Consolidated)

Electrochemical Analysis of MnO₂ (α, β, γ) for Supercapacitors — MDPI Appl. Sci. 13(13), 7907
Electrocatalytic Properties of α, β, γ, ε-MnO₂ — H₂O₂ Sensing Polymorphs — ResearchGate
Multiscale Electrochemical Modelling — SINTEF
Physics-based battery model parametrisation from impedance — arXiv 2412.10896v3
Automated Multiscale Simulation Environment — PMC/NIH
Interactive Multiscale Modeling for Li-CO₂ Battery — arXiv 2501.10954v6
Multiscale modeling bridging MD with FEM — ResearchGate
Characterisation of γ-MnO₂ intergrowth using structure-mining — ChemRxiv


This document is designed for continuous refinement by the DARKLAB agent swarm. Each iteration should update the reports/ directory and trigger a version increment.
