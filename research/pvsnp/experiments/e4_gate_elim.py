"""E4: gate-elimination profile on all 4-input functions.
For f on 4 vars define drop(f,i,c) = C(f) - C(f|x_i=c) (restricted function on 3 vars).
A gate-elimination lower-bound proof proceeds by restricting a variable and
charging the drop.  min_{i,c} drop(f,i,c) is what an adversarially-chosen hard
function guarantees an elimination step *must* settle for if the prover cannot
choose; max_{i,c} drop is the best a prover can extract from f in one step.
Finite data, n=4 only.
"""
import itertools, json, sys
import numpy as np
sys.path.insert(0, __file__.rsplit('/', 2)[0] + '/tools')
from mincircuit import min_circuit

T = 16
cls = json.load(open(sys.argv[1]))['class_sizes']
cls = {int(k, 16): v for k, v in cls.items()}

F = np.arange(1 << T, dtype=np.int64)
bits = (F[:, None] >> np.arange(T)) & 1
w = (1 << np.arange(T)).astype(np.int64)
best = F.copy()
for p in itertools.permutations(range(4)):
    for ng in itertools.product([0, 1], repeat=4):
        idx = [sum(1 << p[j] for j in range(4) if ((t >> j) & 1) ^ ng[j]) for t in range(T)]
        g = bits[:, idx] @ w
        best = np.minimum(best, np.minimum(g, (1 << T) - 1 - g))
C4 = np.array([cls[int(c)] for c in best])

C3 = {}
for g in range(256):
    C3[g] = min_circuit(3, [(g >> t) & 1 for t in range(8)], smax=8)[0]


def restrict(f, i, c):
    g, k = 0, 0
    for t in range(16):
        if ((t >> i) & 1) == c:
            # index among remaining 3 vars
            rest = [(t >> j) & 1 for j in range(4) if j != i]
            r = sum(b << q for q, b in enumerate(rest))
            g |= ((f >> t) & 1) << r
    return g


prof = {}
worst_min = {}
for f in range(1 << T):
    drops = [int(C4[f]) - C3[restrict(f, i, c)] for i in range(4) for c in (0, 1)]
    key = (int(C4[f]), min(drops), max(drops))
    prof[key] = prof.get(key, 0) + 1
print('(C(f), min drop, max drop) -> #functions')
for k in sorted(prof):
    print(k, prof[k])
print('max C3 over 3-var functions:', max(C3.values()))
json.dump({str(k): v for k, v in prof.items()}, open(sys.argv[2], 'w'), indent=1)
