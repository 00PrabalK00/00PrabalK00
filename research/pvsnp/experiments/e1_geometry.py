"""E1: Is hardness a function of solution-space geometry?

Hypothesis H1 (statistical-mechanics route to P != NP):
  'If the solution space of a CNF family is shattered into exponentially many
   well-separated clusters with frozen variables, no poly-time algorithm
   decides the family.'

Adversarial test: random 3-XOR-SAT written as a 3-CNF (each XOR clause = 4
CNF clauses). It is decidable by Gaussian elimination, yet its solution
geometry is compared here with random 3-SAT at the same n.
Exhaustive enumeration over {0,1}^n, n=20.  Finite data only.
"""
import numpy as np, random, json, sys

n = 20
N = 1 << n
X = ((np.arange(N)[:, None] >> np.arange(n)) & 1).astype(np.uint8)


def sat_mask(clauses):
    m = np.ones(N, dtype=bool)
    for c in clauses:
        cm = np.zeros(N, dtype=bool)
        for l in c:
            v = abs(l) - 1
            cm |= (X[:, v] == (1 if l > 0 else 0))
        m &= cm
    return m


def xor_to_cnf(vs, parity):
    out = []
    for bits in range(8):
        b = [(bits >> i) & 1 for i in range(3)]
        if sum(b) % 2 != parity:  # forbid assignment b
            out.append([-(vs[i] + 1) if b[i] else (vs[i] + 1) for i in range(3)])
    return out


def clusters(mask):
    """components under single-bit-flip adjacency; frozen var fraction per cluster"""
    sols = np.flatnonzero(mask)
    S = set(sols.tolist())
    seen, comps = set(), []
    for s in sols.tolist():
        if s in seen:
            continue
        stack, comp = [s], []
        seen.add(s)
        while stack:
            u = stack.pop(); comp.append(u)
            for j in range(n):
                w = u ^ (1 << j)
                if w in S and w not in seen:
                    seen.add(w); stack.append(w)
        comps.append(comp)
    frozen = []
    for c in comps:
        a = np.array(c)
        bits = (a[:, None] >> np.arange(n)) & 1
        frozen.append(float(np.mean((bits.min(0) == bits.max(0)))))
    return len(sols), len(comps), (float(np.mean(frozen)) if frozen else None)


def main(seed=0):
    rng = random.Random(seed)
    res = {}
    for alpha in [0.5, 0.7, 0.85]:
        m = int(alpha * n)
        cl = []
        for _ in range(m):
            vs = rng.sample(range(n), 3)
            cl += xor_to_cnf(vs, rng.randint(0, 1))
        r = clusters(sat_mask(cl))
        res[f'3XOR m/n={alpha}'] = r
    for alpha in [3.5, 4.0, 4.2]:
        m = int(alpha * n)
        cl = [[(v + 1) * rng.choice([1, -1]) for v in rng.sample(range(n), 3)] for _ in range(m)]
        res[f'3SAT m/n={alpha}'] = clusters(sat_mask(cl))
    for k, v in res.items():
        print(f'{k:18s} #sol={v[0]:7d} #clusters={v[1]:7d} mean_frozen={v[2]}')
    return res


if __name__ == '__main__':
    out = {s: main(s) for s in range(3)}
    json.dump(out, open(sys.argv[1] if len(sys.argv) > 1 else '/dev/null', 'w'), indent=1)
