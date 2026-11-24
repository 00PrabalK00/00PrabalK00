"""E2: Candidate P=NP algorithm A_k = saturate all resolvents of width <= k.
A_k runs in time n^{O(k)}.  If some fixed k refuted every unsatisfiable CNF,
UNSAT (hence SAT) would be in P.  We measure w(F) = least k for which A_k
derives the empty clause, on PHP^{m+1}_m, Tseitin(K_{m}) odd charge, and random
unsat 3-CNF.  Also: GF(2) Gaussian elimination as second component.
Finite data only.
"""
import itertools, random, sys, json
import numpy as np


def width_closure_refutes(clauses, k, cap=60000):
    S = set(frozenset(c) for c in clauses if len(c) <= k)
    big = [frozenset(c) for c in clauses if len(c) > k]
    # standard trick: initial clauses wider than k are allowed as premises
    allc = set(S) | set(big)
    frontier = list(allc)
    while frontier:
        new = []
        cur = list(allc)
        for a in frontier:
            for b in cur:
                for l in a:
                    if -l in b:
                        r = (a - {l}) | (b - {-l})
                        if any(-x in r for x in r):
                            continue
                        if len(r) <= k and r not in allc:
                            if len(r) == 0:
                                return True
                            allc.add(r); new.append(r)
                        break
        if len(allc) > cap:
            return None
        frontier = new
    return False


def min_width(clauses, kmax=8):
    for k in range(1, kmax + 1):
        r = width_closure_refutes(clauses, k)
        if r is None:
            return f'>{k-1}(cap)'
        if r:
            return k
    return f'>{kmax}'


def php(m):  # m+1 pigeons, m holes; var p(i,j)
    v = lambda i, j: i * m + j + 1
    cl = [[v(i, j) for j in range(m)] for i in range(m + 1)]
    for j in range(m):
        for i1 in range(m + 1):
            for i2 in range(i1 + 1, m + 1):
                cl.append([-v(i1, j), -v(i2, j)])
    return cl


def tseitin(edges, charge):
    nv = len(edges)
    inc = {}
    for e, (a, b) in enumerate(edges):
        inc.setdefault(a, []).append(e + 1); inc.setdefault(b, []).append(e + 1)
    cl, xors = [], []
    for u, es in inc.items():
        c = charge.get(u, 0)
        xors.append((es, c))
        for bits in itertools.product([0, 1], repeat=len(es)):
            if sum(bits) % 2 != c:
                cl.append([-e if b else e for e, b in zip(es, bits)])
    return cl, xors, nv


def gf2_unsat(xors, nv):
    A = np.zeros((len(xors), nv + 1), dtype=np.uint8)
    for r, (es, c) in enumerate(xors):
        for e in es: A[r, e - 1] ^= 1
        A[r, nv] = c
    r = 0
    for col in range(nv):
        piv = next((i for i in range(r, len(A)) if A[i, col]), None)
        if piv is None: continue
        A[[r, piv]] = A[[piv, r]]
        for i in range(len(A)):
            if i != r and A[i, col]: A[i] ^= A[r]
        r += 1
    return any(A[i, :nv].sum() == 0 and A[i, nv] for i in range(len(A)))


def rand3(n, m, rng):
    return [[(v + 1) * rng.choice([1, -1]) for v in rng.sample(range(n), 3)] for _ in range(m)]


def is_unsat(cl, n):
    from pysat.solvers import Cadical153
    with Cadical153(bootstrap_with=cl) as S:
        return not S.solve()


if __name__ == '__main__':
    out = {}
    for m in range(1, 4):  # m=4 exceeds closure budget here
        out[f'PHP^{m+1}_{m}'] = min_width(php(m), kmax=2 * m + 2)
        print(f'PHP^{m+1}_{m}', out[f'PHP^{m+1}_{m}'], flush=True)
    for m in [4, 5, 6]:
        edges = [(a, b) for a in range(m) for b in range(a + 1, m)]
        cl, xors, nv = tseitin(edges, {0: 1})
        out[f'Tseitin K{m}'] = (min_width(cl, kmax=m + 2), 'GF2 refutes:', bool(gf2_unsat(xors, nv)))
        print(f'Tseitin K{m}', out[f'Tseitin K{m}'], flush=True)
    rng = random.Random(1)
    for n in [8, 12, 16, 20]:
        ws = []
        while len(ws) < 3:
            cl = rand3(n, int(5.5 * n), rng)
            if is_unsat(cl, n):
                ws.append(min_width(cl, kmax=n))
        out[f'rand3 n={n}'] = ws
        print(f'rand3 n={n}', ws, flush=True)
    json.dump(out, open(sys.argv[1], 'w'), indent=1, default=str)
