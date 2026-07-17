# Use Case - Quantum Portfolio Optimizer
## Bob MODE: pre-sales-demo-mode-quantum.yaml

Why this is a strong test: Boards and CIOs are skeptical of quantum hype. This lab does the opposite of overselling — it puts a real quantum optimizer (QAOA) next to the exact classical answer on a synthetic portfolio, runs it on a local simulator for free, and (only on explicit approval) submits the same circuit to a real IBM Quantum QPU. It exercises the mode's four-step Qiskit pattern, the tri-mode execution axis (local-ideal → local-noisy → cloud-qpu), the classical-baseline honesty rule, and the paid-QPU cost gate.

Cluster: Quantum Optimization · Industry: Finance & Banking · Output shape: QAOA portfolio selection + optimization-landscape visual + quantum-vs-classical comparison + optional real-QPU run

### USE-CASE NARRATIVE

A portfolio manager must pick the best subset of assets to hold under a budget — maximize expected return, minimize risk (covariance). For N assets there are 2^N possible portfolios; this is the kind of combinatorial problem quantum optimization targets.

The demo formulates the selection as a QUBO, solves it three ways the audience can compare:
- the exact classical optimum (brute force, at the small demo size),
- QAOA on a local simulator (ideal and noisy),
- the same QAOA circuit on a real IBM Quantum computer (gated, opt-in).

The honest story: on today's NISQ hardware the classical answer still wins at this size — the value is the **trajectory** and a working small instance, not a production claim.

### PREPARATION
- IBM Bob access with `pre-sales-demo-mode-quantum.yaml` active
- Python 3.11+
- The `ibm-qiskit` skill available to Bob
- Optional (for the real-QPU run only): an IBM Quantum API key + instance CRN **from the same IBM Cloud account**

Environment variables:

QUANTUM_MODE=local
EXECUTION_TARGET=local-ideal
ALLOW_PAID_QPU=false
IBM_QUANTUM_CHANNEL=ibm_quantum_platform
IBM_QUANTUM_API_KEY= (optional, only for cloud-qpu)
IBM_QUANTUM_CRN= (optional, only for cloud-qpu)

### PROMPT 1 - Build the core app

```text
Create a serious quantum demo app called "Quantum Portfolio Optimizer".

The user should configure a small synthetic portfolio problem, for example:
"8 assets, budget = pick 4, maximize return minus risk" for a fictional fund.

Build it as the App-demo shape from the quantum mode:
- A FastAPI backend with a tri-mode quantum service (local-ideal default, local-noisy, cloud-qpu).
- A Carbon Design React frontend (g100 theme) with pages: Dashboard, Problem, Circuit, Run, Results, Architecture.

The quantum kernel is QAOA for portfolio selection:
- Map the portfolio (synthetic expected returns + covariance + budget penalty) to a QUBO / Ising cost Hamiltonian as a SparsePauliOp.
- Build a QAOA ansatz (cost + mixer layers, p=1..2) with the circuit library.
- Optimize: transpile to the selected backend's ISA.
- Execute with SamplerV2 (PUBs) — local by default.
- Post-process: most-probable bitstring = selected portfolio; show the measurement histogram.

ALWAYS pair the quantum result with the exact classical optimum (brute-force enumerate all 2^N subsets at this small size) so the audience sees an honest comparison.

Use the ibm-qiskit skill for all Qiskit / qiskit-aer / qiskit-ibm-runtime APIs — do not improvise them. Use V2 primitives only. Synthetic data only (Faker seed=42, fictional asset names, no real tickers). The app MUST run end-to-end on the local simulator with ZERO IBM Quantum account. Do not hardcode fake results.

The UI should look investment-grade: clean, dark, boardroom style. Include the synthetic-data disclaimer banner and a clear NISQ/"not a production claim" note on the Results page.
```

### PROMPT A - Build the core app

```text
Start the application for me on the local laptop, without containers, by using these credentials you can store in the .env file. Keep QUANTUM_MODE=local as the default so it runs for free; wire these so I can later flip a backend selector to run on my real IBM Quantum instance.

IBM_QUANTUM_CHANNEL=ibm_quantum_platform
IBM_QUANTUM_API_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
IBM_QUANTUM_CRN=crn:v1:bluemix:public:quantum-computing:us-east:a/wwwwwwwwwwwwwwwwwwwwwwwww:0ca9ddf2-d685-4647-a251-81da91c43163::
DEFAULT_SHOTS=4096

Verify the key and CRN belong to the same account and list my available QPUs (backends only — do NOT submit any paid job yet). Then run the QAOA portfolio optimization on the local-ideal simulator and show me the selected portfolio next to the brute-force classical optimum.
```

> Note: this is a live IBM Quantum API key + instance CRN — treat it as a secret. The QPUs on this instance are paid Heron r2 devices, so a real-QPU run bills QPU time per second. The mode keeps `ALLOW_PAID_QPU=false` and requires explicit confirmation before any hardware submission.

### PROMPT 2 - Add the real-QPU run and noise

```text
Enhance the Run page so the backend selector offers all three targets:
- local-ideal (default)
- local-noisy (AerSimulator.from_backend of a fake IBM device)
- cloud-qpu (my real instance)

For cloud-qpu, require an explicit "Run on real QPU (bills QPU time)" confirmation in the UI, set ALLOW_PAID_QPU only when I confirm, transpile the QAOA circuit to the chosen backend's ISA, run it once with SamplerV2, and show the job ID plus the histogram. Add error suppression/mitigation options (resilience level, dynamical decoupling) and explain each briefly.

On the Results page, compare all targets I have run: classical optimum vs local-ideal vs local-noisy vs cloud-qpu, and write an honest one-paragraph interpretation of what the noise shows.
```

### PROMPT B - Build the core app

```text
Start the application for me on the local laptop and test it. Run the QAOA on local-ideal and local-noisy, confirm the selected portfolio matches the brute-force optimum on local-ideal, and capture screenshots of the histogram and the quantum-vs-classical panel. Do NOT submit a paid QPU job unless I explicitly say so.
```

### PROMPT 3 - Executive polish

```text
Add an "Efficient frontier" view: sweep a risk-aversion parameter and plot return vs risk for the portfolios QAOA finds versus the classical frontier.

Add a collapsible "How this maps to quantum" panel showing the QUBO, the cost Hamiltonian (SparsePauliOp), and the transpiled ISA circuit depth/op-counts for the selected backend.

Finally, improve README.md with:
- setup instructions (local-first; how to enable the real QPU and the cost warning)
- required .env variables
- how to run the app
- a suggested 15-minute executive demo script
- 3 sample portfolio problems to test (different sizes)
- an honest "Maturity & Scope" section (NISQ, why classical still wins at this size, the path to advantage)
```

### EXPECTED OUTPUT
- Carbon React IBM-style quantum optimization app (g100 theme)
- QAOA portfolio kernel built with Qiskit (QUBO → cost Hamiltonian → ansatz → ISA → SamplerV2)
- Tri-mode execution: local-ideal, local-noisy, and the real IBM Quantum instance (gated)
- Exact classical baseline shown beside every quantum result
- Optimization-landscape / efficient-frontier visuals + measurement histogram + job ID for QPU runs
- Honest NISQ scope statement (no overselling)
- README, Architecture, PILOT Plan, and Demo Script
