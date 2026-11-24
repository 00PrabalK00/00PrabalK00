"""Exact minimum circuit size over the full binary basis B2 via SAT.

Encoding (standard, cf. Kojevnikov-Kulikov-Yaroslavtsev style):
  nodes 0..n-1 are inputs, nodes n..n+s-1 are gates.
  gate i: selector vars sel[i][j][k] (j<k<i) picking its two predecessors,
          4 truth-table bits op[i][ab] (output when (in_j,in_k)=(a,b)),
          value vars val[i][t] for each input assignment t.
  output: the LAST gate must equal f (or its negation is not needed since B2 closed).
Returns (s, circuit) for minimal s; UNSAT at s-1 certifies a lower bound
for that n *and only that n*.  This is a finite computation, never a proof
about asymptotic circuit size.
"""
import itertools, sys
from pysat.solvers import Cadical153
from pysat.card import CardEnc, EncType
from pysat.formula import IDPool


def encode(n, s, truth, pool):
    T = 1 << n
    cl = []
    val = {}
    for t in range(T):
        for j in range(n):
            v = pool.id(('x', j, t))
            val[(j, t)] = v
            cl.append([v] if (t >> j) & 1 else [-v])
    sel = {}
    op = {}
    for g in range(n, n + s):
        pairs = [(j, k) for j in range(g) for k in range(j + 1, g)]
        lits = []
        for (j, k) in pairs:
            sel[(g, j, k)] = pool.id(('sel', g, j, k))
            lits.append(sel[(g, j, k)])
        cl.append(lits)
        cl += CardEnc.atmost(lits, 1, vpool=pool, encoding=EncType.seqcounter).clauses
        for ab in range(4):
            op[(g, ab)] = pool.id(('op', g, ab))
        # symmetry breaking: gate is non-degenerate (depends on both inputs)
        o = [op[(g, ab)] for ab in range(4)]
        # forbid constant and projections: op not in {0000,1111,0011,0101,1100,1010}
        for bad in [(0,0,0,0),(1,1,1,1),(0,0,1,1),(0,1,0,1),(1,1,0,0),(1,0,1,0)]:
            cl.append([-o[i] if bad[i] else o[i] for i in range(4)])
        for t in range(T):
            val[(g, t)] = pool.id(('v', g, t))
        for (j, k) in pairs:
            sv = sel[(g, j, k)]
            for t in range(T):
                for a in (0, 1):
                    for b in (0, 1):
                        ab = 2 * a + b
                        la = -val[(j, t)] if a else val[(j, t)]
                        lb = -val[(k, t)] if b else val[(k, t)]
                        # sel & in=(a,b) -> v == op[ab]
                        cl.append([-sv, la, lb, -op[(g, ab)], val[(g, t)]])
                        cl.append([-sv, la, lb, op[(g, ab)], -val[(g, t)]])
    out = n + s - 1
    for t in range(T):
        cl.append([val[(out, t)]] if truth[t] else [-val[(out, t)]])
    # every gate except output is used by some later gate (no dead gates)
    for g in range(n, n + s - 1):
        users = [sel[(h, j, k)] for (h, j, k) in sel if h > g and (j == g or k == g)]
        cl.append(users)
    return cl, sel, op


def min_circuit(n, truth, smax=12, verbose=False):
    truth = list(truth)
    T = 1 << n
    if all(truth[t] == truth[0] for t in range(T)):
        return 0, 'const'
    for j in range(n):
        if all(truth[t] == ((t >> j) & 1) for t in range(T)) or \
           all(truth[t] != ((t >> j) & 1) for t in range(T)):
            return 0, f'literal x{j}'  # negation free in B2 counting convention
    for s in range(1, smax + 1):
        pool = IDPool()
        cl, sel, op = encode(n, s, truth, pool)
        with Cadical153(bootstrap_with=cl) as S:
            if S.solve():
                m = set(l for l in S.get_model() if l > 0)
                desc = []
                for g in range(n, n + s):
                    for (h, j, k), v in sel.items():
                        if h == g and v in m:
                            tt = ''.join('1' if op[(g, ab)] in m else '0' for ab in range(4))
                            desc.append(f'g{g}=op{tt}({j},{k})')
                return s, desc
            elif verbose:
                print(f'  size {s}: UNSAT', file=sys.stderr)
    return None, None


def tt(n, f):
    return [int(bool(f([(t >> j) & 1 for j in range(n)]))) for t in range(1 << n)]


if __name__ == '__main__':
    for n in range(2, 6):
        print('XOR', n, min_circuit(n, tt(n, lambda x: sum(x) % 2))[0])
    for n in range(3, 6):
        print('MAJ', n, min_circuit(n, tt(n, lambda x: sum(x) > n // 2))[0])
