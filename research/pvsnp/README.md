# P vs NP research workspace

Status: **unresolved**. See `NOTES.md` for every claim, proof, adversarial check and obstruction.

- `NOTES.md`: research log, proved lemmas, obstructions, dependency graph, open questions
- `tools/mincircuit.py`: exact minimum B2 circuit size via SAT (certified by UNSAT at s-1)
- `tools/check_finite.py`: exhaustive checks of the finite statements used in the notes
- `experiments/e1_geometry.py`: solution-space geometry, 3-XOR-SAT vs 3-SAT (n=20, exhaustive)
- `experiments/e2_width.py`: resolution width of PHP, Tseitin, random 3-CNF; GF(2) elimination
- `experiments/e3_npn4.py`: exact circuit size of all 4-input functions (222 NPN classes)
- `experiments/e4_gate_elim.py`: how much one-variable restrictions lower circuit size, n=4
- `results/`: raw outputs

Requirements: `pip install python-sat numpy`. Lean 4 was unavailable in this environment, so nothing is machine-checked.
