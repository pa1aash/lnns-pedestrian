# Seeds

Every random number in the simulations comes from numpy's PCG64 generator.

- **Run seed.** A whole run started from scratch takes one integer seed. It sets the spawn positions and agent attributes (`code/sim/core/spawn.py:38`, `code/sim/core/agent.py:87`) and the simulation's own generator, which draws the per-step velocity noise (`code/sim/core/simulation.py:70`, `np.random.Generator(np.random.PCG64(seed))`). The same seed in two cells therefore gives the same crowd at the start.
- **Noise seed.** A restart from a frozen snapshot rebuilds the simulation with `seed = noise_seed` (`experiments/lib/w2lib.py:80`; `seed = 0` when the restart has no noise). The snapshot fixes the positions, so this seed only drives the noise.
- **Perturbation seed.** The deterministic restarts are run once unperturbed and five times with 1e-9 m Gaussian position perturbations drawn from `np.random.default_rng(perturb)` (`experiments/lib/runlib.py:91`).
- **Snapshots.** A snapshot is named after the run seed that produced it, so `E1b_seed52` is the deadlock of E1b run seed 52.

Ranges are written inclusive (`range(42, 67)` in Python is seeds 42-66).

## Simulations

| Step | What is seeded | Seeds | Source |
|---|---|---|---|
| E1a, E1b | whole runs, room bottleneck, both modes | run seeds 42-241 (200 per mode) | `experiments/E1/e1_library.py:5`, `:153` |
| E2 | which snapshots | 60 E1b snapshots: the 34 lone-keystone ones and 26 drawn from the second-trap snapshots with `Generator(PCG64(2026)).choice` | `experiments/selection.py:3-7`, `:33`, `:41` |
| E2 | deterministic restarts | perturbation seeds 900-904 (plus one unperturbed run) | `experiments/E2/e2_quench.py:44` |
| E2 | noise restarts | noise seed 7000 + 100 k + rep, k = snapshot index in selection order (0-59), rep 0-4; the same seeds at every sigma | `experiments/E2/e2_quench.py:66` |
| BAR | none (deterministic string method) | the 60 E2 snapshots | `experiments/BAR/bar.py:1`, `experiments/selection.py:8-12` |
| E3 | which snapshots | 20 of the 60, evenly spaced ranks in full-condition Delta U (deterministic) | `experiments/selection.py:13-15` |
| E3 | noise restarts | noise seed 51000 + 1000 k + 10 round(1000 dt) + rep (+500 for `dt_scaled`), k = index in the E3 list (0-19), rep 0-19, dt in {0.005, 0.01, 0.02} s | `experiments/E3/e3_dt.py:74-75`, `:32-34` |
| E3 (variance check) | noise runs | noise seed 31000 + k | `experiments/E3/t3_variance.py:75` |
| E4 | which snapshots | 10 of the 60, evenly spaced ranks in full-condition Delta U (deterministic) | `experiments/selection.py:16-17` |
| E4 | noise restarts | noise seed 11000 + 1000 k + 100 level + rep, k = index in the E4 list (0-9), level 0-2 (beta 1.5, 2.5, 3.5), rep 0-19 (no condition was extended beyond 20; `data/E4/e4_extension.json`) | `experiments/E4/e4_escape.py:80`, `:37-38` |
| E5a, E5b | whole runs with noise | run seeds 42-141 at every sigma; sigma = 0 reuses E1a / E1b seeds 42-141 | `experiments/E5/e5_sweep.py:19`, `:4` |
| E6a, E6b | whole runs, matched completion | run seeds 242-427 (186), the same seeds in both | `experiments/E6/e6.py:29` |
| E6p | whole runs, published reproduction, published ORCA | run seeds 428-477 (50) | `experiments/E6/e6.py:29` |
| E6 keystone tests | rebuilt final states | the run's own seed | `experiments/E6/keystone_e6.py:45` |
| E7 | whole runs, wall-model cells | run seeds 42-141 in every cell | `experiments/E7/e7_cells.py:21` |
| E7b library | whole runs, pair standoffs | run seeds from 242 upward in batches of 40, cap 641; seeds 242-561 were run (320), of which 46 qualify | `experiments/E7b/e7b_lib.py:33`, `data/E7b/e7b_lib.jsonl` |
| E7b static | none (deterministic relaxation) | the 46 qualifying snapshots | `experiments/E7b/e7b_static.py:82` |
| E7b barrier | none; which snapshots | 12 of the 46 at evenly spaced ranks of the softest Hessian eigenvalue mu1 (data key `lambda1`; deterministic) | `experiments/E7b/e7b_barrier.py:38`, `:76` |
| E7b quench | deterministic restarts | perturbation seeds 900-904 (plus one unperturbed run) | `experiments/E7b/e7b_quench.py:50` |
| E7b quench | noise restarts | noise seed 20000 + 100 k + rep, k = snapshot index in library order (0-45), rep 0-4; the same seeds at every sigma | `experiments/E7b/e7b_quench.py:111` |
| E7b matched b | deterministic restarts | perturbation seeds 900-904, as E7b quench | `experiments/E7b/matched_b.py:28`, `:69` |
| E8 | whole runs, open corridor | run seeds 42-66 for every condition and length; the second stream uses seed + 1000 for its spawn | `experiments/E8/e8_counterflow.py:29`, `experiments/lib/opengeo.py:39-40` |
| E9 | whole runs, open crossing | run seeds 42-66 for every condition and length; the second stream uses seed + 2000 for its spawn | `experiments/E9/e9_crossing.py:26`, `experiments/lib/opengeo.py:69-70` |
| E10 | whole runs, CroMa geometry | run seeds 42-66 in every cell; CroMa run type `RUNS[(seed - 42) % 5]` (5 seeds per run type) | `experiments/E10/e10_croma.py:56`, `:96` |
| E11 | whole runs, overlap | run seeds 42-66 in every cell | `experiments/E11/e11_overlap.py:30` |
| arch | whole runs, high drive | run seeds 42-66 (25) | `experiments/arch/arch.py:124` |

At the time of writing, E6p, E8 and E9 are queued and have no results in `data/` yet.

## Analysis resampling

Bootstrap and permutation intervals use one fixed generator per script.

| Script | Generator | Source |
|---|---|---|
| E1 analysis and chain | `PCG64(12345)` | `experiments/E1/e1_analyze.py:30`, `experiments/E1/chain.py:35` |
| E2, E3, E4, E7b analysis, Table 3 | seed 12345 | `experiments/E2/analyze.py:36`, `experiments/E3/analyze.py:42`, `experiments/E4/analyze.py:43`, `experiments/E7b/analyze.py:65`, `experiments/tables/make_table3.py:34` |
| E8, E9 (shared statistics), E11 | `PCG64(12345)` | `experiments/lib/openstats.py:39`, `experiments/E11/analyze.py:52` |
| E6, E10 analysis | `default_rng(2026)` | `experiments/E6/analyze.py:52`, `experiments/E10/analyze.py:45` |
| E7 analysis | `default_rng(7)` | `experiments/E7/analyze.py:144` |
