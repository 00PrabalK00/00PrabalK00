"""E3: exact B2 circuit size of every 4-input Boolean function (via NPN classes).
Purpose: (a) validate the oracle against the known value max C(f)=7 for n=4
(Knuth, TAOCP 4A sec. 7.1.2 reports all 4-variable functions need <= 7 steps
in the full binary basis -- treated here as a check, not as an assumption);
(b) give exact data for the counting / natural-proofs analysis in NOTES.md.
"""
import itertools, sys, json
from multiprocessing import Pool
sys.path.insert(0, __file__.rsplit('/', 2)[0] + '/tools')
from mincircuit import min_circuit

n = 4
T = 16


def transform(f, perm, neg, oneg):
    g = 0
    for t in range(T):
        bits = [(t >> j) & 1 for j in range(n)]
        src = 0
        for j in range(n):
            if bits[j] ^ neg[j]:
                src |= 1 << perm[j]
        if ((f >> src) & 1) ^ oneg:
            g |= 1 << t
    return g


def canon(f):
    return min(transform(f, p, ng, o) for p in itertools.permutations(range(n))
               for ng in itertools.product([0, 1], repeat=n) for o in (0, 1))


def size(f):
    truth = [(f >> t) & 1 for t in range(T)]
    s, _ = min_circuit(n, truth, smax=9)
    return f, s


if __name__ == '__main__':
    import numpy as np
    F = np.arange(1 << T, dtype=np.int64)
    bits = (F[:, None] >> np.arange(T)) & 1
    w = (1 << np.arange(T)).astype(np.int64)
    best = F.copy()
    for p in itertools.permutations(range(n)):
        for ng in itertools.product([0, 1], repeat=n):
            idx = []
            for t in range(T):
                b = [(t >> j) & 1 for j in range(n)]
                idx.append(sum(1 << p[j] for j in range(n) if b[j] ^ ng[j]))
            g = bits[:, idx] @ w
            best = np.minimum(best, np.minimum(g, (1 << T) - 1 - g))
    reps = {}
    for c in best.tolist():
        reps[c] = reps.get(c, 0) + 1
    print('NPN classes:', len(reps), flush=True)
    with Pool(3) as P:
        sizes = dict(P.map(size, sorted(reps)))
    dist = {}
    for c, cnt in reps.items():
        dist[sizes[c]] = dist.get(sizes[c], 0) + cnt
    print('functions by exact circuit size:', dict(sorted(dist.items())))
    json.dump({'classes': len(reps), 'dist_functions': dist,
               'class_sizes': {hex(c): sizes[c] for c in reps}},
              open(sys.argv[1], 'w'), indent=1)
