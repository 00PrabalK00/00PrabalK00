# P vs NP — research log

**Status: unresolved.** Nothing here proves P = NP or P ≠ NP. This file records
precise claims, complete proofs of the lemmas that were actually proved, the
adversarial analysis of each strategy, and the exact obstruction each one hit.

Conventions. Σ = {0,1}. C(f) = size of the smallest fan-in-2 circuit over the
full binary basis B₂ computing f (inputs and negations free). H(p) is binary
entropy. "Verified" means a complete proof appears below. "Computed" means a
finite computation whose script is in `experiments/` and whose output is in
`results/`; computations are never used as proofs of asymptotic statements.

Formal verification: Lean 4 could not be installed in this environment
(toolchain download refused by network policy, HTTP 403). No Lean
artefacts exist; no statement below is claimed to be machine-checked.

---

## Direction 1 — statistical mechanics: does solution-space geometry imply hardness?

**Hypothesis H1.** There are ε, δ, φ > 0 such that: if a family of CNFs Fₙ on N
variables has (a) ≥ 2^{εN} solution clusters, (b) pairwise inter-cluster Hamming
distance ≥ δN, (c) ≥ φN frozen variables in each cluster, then SAT restricted to
(the promise class of) such formulas is not in P.

If H1 held for random 3-SAT near threshold, it would be a route to P ≠ NP.

**Computed (E1, n = 20, exhaustive).** Random 3-XOR-SAT written as 3-CNF shows
cluster counts and frozen fractions comparable to or exceeding random 3-SAT at
m/n ∈ {3.5, 4.0, 4.2} (`results/e1_geometry.json`). Suggests H1 is false.

**Lemma 1.1 (Gilbert–Varshamov, proved).** For 0 < δ < 1/2 and k < (1 − H(δ))n
there is H ∈ F₂^{(n−k)×n} with ker H of dimension ≥ k and minimum weight ≥ δn.

*Proof.* Pick H uniformly. For fixed x ≠ 0, Hx is uniform on F₂^{n−k}, so
Pr[Hx = 0] = 2^{−(n−k)}. The number of nonzero x with |x| < δn is
≤ Σ_{i<δn} C(n,i) ≤ 2^{H(δ)n} (standard entropy bound for δ ≤ 1/2). Union bound:
Pr[∃ x ≠ 0, |x| < δn, Hx = 0] ≤ 2^{H(δ)n − (n−k)} < 1. Fix such an H;
dim ker H ≥ n − rank H ≥ k. ∎

**Lemma 1.2 (XOR to 3-CNF, proved).** A parity constraint x_{i1} ⊕ … ⊕ x_{iw} = b
(w ≥ 3) is equivalent, after adding w − 3 fresh variables y_j defined by
y₁ = x_{i1} ⊕ x_{i2}, y_{j+1} = y_j ⊕ x_{i(j+2)}, to w − 2 three-variable parity
constraints, each expressible as exactly 4 clauses of width 3. Every solution
of the original constraint extends uniquely to the new variables.

*Proof.* Each y_j is a fixed affine function of the x's, so extension is unique;
the chain ends with y_{w−3} ⊕ x_{i(w−1)} ⊕ x_{iw} = b, which is the original
constraint after substitution. A 3-variable parity constraint forbids exactly
the 4 assignments of the wrong parity, each excluded by one width-3 clause. ∎
(Exhaustive check of the 3-variable case: `tools/check_finite.py`.)

**Theorem 1.3 (H1 is false, proved).** Fix δ ∈ (0, 1/2), R ∈ (0, 1 − H(δ)).
There is an infinite family of 3-CNFs Φₙ on N ≤ 2n² + n variables, solvable
in polynomial time (Gaussian elimination over F₂), such that Sol(Φₙ) has
2^{Rn} = 2^{Ω(√N)} points with pairwise Hamming distance ≥ δn² ≥ (δ/3)N.
So every cluster (for any adjacency radius < (δ/3)N) is a single point,
and all N variables are frozen in every cluster.

*Proof.* Take H from Lemma 1.1 with k = ⌈Rn⌉. Encode Hx = 0 via Lemma 1.2,
using at most n(n−k) ≤ n² auxiliary variables. Add n−1 replicas x_i^{(r)} of
each x_i with 2-clauses x_i ↔ x_i^{(r)}. Solutions are in bijection with ker H.
Two distinct codewords differ in ≥ δn original coordinates, hence in ≥ δn·n
replica-or-original coordinates. N ≤ n² + n² + n. Satisfiability of any
system of F₂-linear equations is decided in O(N³) by Gaussian elimination, and
the clauses of Φₙ are recognisably grouped parity constraints. ∎

Scope, stated adversarially: the self-contained version gives 2^{Ω(√N)} clusters,
so it refutes H1 with (a) weakened to "superpolynomially many clusters". H1
exactly as stated, with 2^{εN}, is refuted by the version below. A 2^{Ω(N)} version holds if one uses expander codes (Sipser–Spielman), whose
parity checks have constant weight so no replication is needed. That relies on
a cited theorem and is **not** re-proved here.

**Obstruction O1.** Theorem 1.3 refutes every hardness criterion that depends
only on the metric geometry of the solution set (cluster count, separation,
freezing, entropy). Hardness depends on the *non-affine algebraic structure*
of the constraints, not on the shape of the set of solutions.

**Next direction from O1.** Use an algebraic invariant of the constraint
language. That invariant exists and is complete for CSPs: by the
Bulatov–Zhuk dichotomy theorem (2017), CSP(Γ) is in P when Γ has a Taylor
(equivalently, weak near-unanimity) polymorphism, and is NP-complete
otherwise. **Obstruction O1′:** the dichotomy classifies CSPs only *up to
polynomial-time reduction*. Every non-Taylor template is NP-complete, so the
invariant reduces P ≠ NP back to P ≠ NP for one template. Any invariant that
is preserved under polynomial-time reductions inherits exactly this collapse.

---

## Direction 2 — algorithms: bounded-width reasoning as a P = NP candidate

**Candidate A_k.** Saturate all resolution derivations with derived clauses of
width ≤ k (equivalently, k-consistency). Runs in N^{O(k)} time. If one fixed k
refuted every unsatisfiable 3-CNF, then P = NP.

**Computed (E2).** Measured minimum refutation widths; see
`results/e2_width.json`. Tseitin formulas are refuted instantly by F₂ elimination
but need growing width; random unsat 3-CNFs need growing width.

**Lemma 2.1 (certification transfer, proved).** Let 𝒫 be a Cook–Reckhow proof
system and A a deterministic algorithm that rejects only unsatisfiable inputs,
and from whose rejecting run on F a 𝒫-refutation of F can be produced in time
polynomial in the run length T_A(F). If a family Fₙ requires 𝒫-refutations of
size s(n), then T_A(Fₙ) ≥ s(n)^{Ω(1)}.

*Proof.* The refutation is produced in time poly(T_A(F)), so its size is at
most poly(T_A(F)). Hence poly(T_A(Fₙ)) ≥ s(n). ∎

**Consequences (using cited theorems, not re-proved).** CDCL and DPLL runs
convert to resolution proofs, so Haken's theorem (1985, the pigeonhole
principle needs exponential-size resolution proofs) gives exponential running
time for all of them. A_k is width-certifying, and Ben-Sasson–Wigderson (2001)
width lower bounds give A_k superpolynomial time for every fixed k.

**Lemma 2.2 (the target must be p-bounded, proved).** If P = NP there is a
polynomially bounded Cook–Reckhow proof system for UNSAT.

*Proof.* Let M decide UNSAT in polynomial time. Define the proof system
V(F, π) = 1 iff π is the empty string and M(F) = 1. It is sound and complete,
V runs in polynomial time, and every unsatisfiable F has a proof of length 0. ∎

**Obstruction O2.** By 2.1 and 2.2, a P = NP algorithm must induce a proof
system that is not p-simulated by any system with known superpolynomial lower
bounds (resolution, cutting planes, polynomial calculus, bounded-depth Frege,
and others). No superpolynomial lower bounds are known for Frege or Extended
Frege. So proof complexity neither confirms nor excludes this route. Proving
superpolynomial lower bounds for *every* proof system is equivalent to
NP ≠ coNP, which is at least as hard as P ≠ NP.

**Next direction from O2.** Add F₂-linear reasoning to A_k, since Gaussian
elimination kills Tseitin. The induced system is resolution over parities,
Res(⊕). As far as I know, superpolynomial lower bounds for unrestricted
(dag-like) Res(⊕) are open. I am deliberately not citing specific recent
partial results, because I cannot verify them here. Hybrid algorithms of this
kind are therefore not excluded by any lower bound I can establish. But they
are also not shown to work: PHP has no useful linear structure, so GF(2)
reasoning adds nothing on PHP, and this hybrid remains width-bounded on it.

---

## Direction 3 — information theory: query lower bounds and relativization

**Claim attempt.** "Finding a witness requires extracting n bits of information;
each poly-time step extracts O(log n) bits; therefore SAT ∉ P."

**Lemma 3.1 (black-box search, proved).** Any deterministic algorithm with
query access to an oracle X: {0,1}^n → {0,1} that decides ∃y X(y) = 1 must
make 2^n queries in the worst case.

*Proof.* Adversary: answer 0 to every query. If the algorithm halts after
< 2^n queries, some y₀ is unqueried; the oracles X ≡ 0 and X = 1_{y₀} give
identical transcripts but different answers. ∎

**Lemma 3.2 (oracle collapse, proved).** Let A = TQBF. Then P^A = NP^A.

*Proof.* NP^A ⊆ NPSPACE^A. Each oracle query is to a PSPACE language, so the
whole machine runs in nondeterministic polynomial space; by Savitch,
NPSPACE = PSPACE, so NP^A ⊆ PSPACE. Since TQBF is PSPACE-complete under
polynomial-time reductions, PSPACE ⊆ P^A. And P^A ⊆ NP^A trivially. ∎

**Obstruction O3.** The information-extraction argument uses the instance only
through membership queries, so it holds relative to every oracle. Lemma 3.2
exhibits an oracle where its conclusion is false. Hence any valid
P ≠ NP proof must use the explicit syntactic structure of the input formula,
in a way that fails relative to TQBF. Lemma 3.1 is exactly the oracle that
gives P^B ≠ NP^B. Information-theoretic counting alone cannot distinguish the
two worlds.

---

## Direction 4 — circuit complexity: counting, exact small-n data, and constructivity

**Lemma 4.1 (Shannon counting, proved).** The number of B₂ circuits with s
gates on n inputs is at most (16(n+s)²)^s. Hence if (16(n+s)²)^s < 2^{2^n}
some function on n inputs has C(f) > s; for s = 2^n/(4n) and large n this
holds, so most functions need ≥ 2^n/(4n) gates.

*Proof.* Each gate picks two predecessors among ≤ n + s nodes ((n+s)² ways)
and one of 16 binary operations; the output is the last gate. Taking logs:
s·log(16(n+s)²) ≤ (2^n/(4n))·(4 + 2·log(2^{n+1})) < 2^n for large n. ∎

**Computed (E3).** Exact C(f) for every 4-input function via the SAT-based
oracle `tools/mincircuit.py`; see `results/e3_npn4.json`. Sanity checks:
C(XOR_n) = n − 1 for n ≤ 5 (matches Schnorr's tight bound) and C(MAJ₃) = 4.

**Obstruction O4 (precise form).** Lemma 4.1 is non-constructive. To turn it
into a lower bound for an explicit NP function, one needs a property 𝒞 of
truth tables that is (i) satisfied by some explicit f ∈ NP and (ii) violated
by every function with poly-size circuits. Razborov–Rudich: if 𝒞 is also
*large* and decidable in time 2^{O(n)} from the truth table, then 𝒞 yields a
distinguisher against every pseudorandom function family in P/poly. Note
the barrier is **conditional**: it shows such a proof would refute the
existence of strong PRFs. It does not make natural proofs inconsistent. A
natural proof would therefore be a surprise in cryptography as well, which is
why nobody expects one. Separately: even a proof that NP ⊄ P/poly is strictly
stronger than P ≠ NP. Circuit lower bounds are sufficient but not necessary.

---

## Direction 5 — logic: universal search makes "P = NP" a statement about one program

**Lemma 5.1 (Levin-style universal search, proved).** There is an explicit
algorithm U that decides SAT correctly on all inputs and halts within
2^{O(n)} steps, and such that if P = NP then U runs in polynomial time on all
satisfiable inputs.

*Proof.* On input F with n variables, U runs two processes interleaved step by
step. Process 1 is brute force, finishing in 2^{O(n)}. Process 2, in phase
t = 1, 2, …, runs each machine M_1, …, M_t for t steps as a candidate decider
for SAT and uses it to self-reduce. It fixes x₁ = 0 if M_i says F[x₁=0] is
satisfiable, otherwise x₁ = 1, continues through all variables, and checks the
resulting assignment. U accepts as soon as any process finds a satisfying
assignment, and rejects only when brute force finishes without one. Soundness
is immediate since every acceptance is checked. If SAT is decided by some M_c
in time n^d, then in phase t = max(c, (2n)^{d+1}) machine M_c's self-reduction
finds an assignment for satisfiable F. The total work up to that phase is
poly(n) for fixed c and d. ∎

**Obstruction O5.** Lemma 5.1 turns "P = NP" into a statement about the
running time of one explicit program. But proving U is polynomial requires
exhibiting M_c, which is exactly the problem. On unsatisfiable inputs the
self-reduction cannot certify a "no" answer. Closing that gap needs short
refutations, which is Direction 2 / O2. Nothing new is gained.

---

## Direction 6 — topology: Betti-number lower bounds

**Observation.** Ben-Or's theorem gives depth Ω(log #connected components) for
algebraic decision trees over ℝ. Boolean analogue (proved, trivial): a
decision tree deciding membership in S ⊆ {0,1}^n has depth ≥ log₂ of its
number of leaves needed to separate the points of S from its complement.
That never exceeds n.

**Obstruction O6.** Component-counting bounds give at most linear or
logarithmic lower bounds, and only in tree-like models without fan-out reuse.
General polynomial-time computation (uniform circuits with fan-out) is not a
decision tree. Theorem 1.3 already shows connected-component and cluster counts
do not track hardness.

---

## Dependency graph

```
Lemma 1.1 (GV) ──┐
Lemma 1.2 (XOR→3CNF) ──┴─> Theorem 1.3 ──> O1 (geometry ≠ hardness) ──> O1′ (dichotomy collapse)
Lemma 2.1 (certification transfer) ─┐
[cited: Haken; Ben-Sasson–Wigderson] ─┴─> O2 (algorithms ↔ proof systems)
Lemma 2.2 (P=NP ⇒ p-bounded system) ──────> O2
Lemma 3.1 (black-box search) ──┐
Lemma 3.2 (P^TQBF = NP^TQBF) ──┴─> O3 (relativization)
Lemma 4.1 (counting) ──> O4 (constructivity; natural proofs, conditional)
Lemma 5.1 (universal search) ──> O5
```

Proved here: 1.1, 1.2, 1.3, 2.1, 2.2, 3.1, 3.2, 4.1, 5.1.
Cited, not re-proved: Haken; Ben-Sasson–Wigderson; Bulatov–Zhuk; Sipser–Spielman;
Razborov–Rudich; Savitch; Schnorr (used only as a sanity check).
Conjectures and assumptions used in any result above: **none**.

## Open questions this log leaves

1. Superpolynomial lower bounds for dag-like Res(⊕), the system induced by the
   first algorithm family not killed by Direction 2. (Open as far as I know.)
2. A property of truth tables that is useful against P/poly but is either not
   large or not constructive, and that some explicit NP function satisfies.
   This is the shape any circuit-based proof must take, by O4.
3. A non-relativizing use of the explicit formula structure (O3) that also
   avoids O4. Williams' algorithmic method is the only known template
   meeting both. Extending it from NEXP vs ACC⁰ to NP vs P/poly is open.

## Final status

**P vs NP: unresolved by this work.** No step above proves either direction.
