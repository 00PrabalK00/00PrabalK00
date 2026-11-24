"""Exhaustive checks of the finite statements used in NOTES.md.
These check finitely many cases only; they are not proofs of general claims."""
import itertools, math


def check_xor3_encoding():
    for parity in (0, 1):
        clauses = []
        for b in itertools.product([0, 1], repeat=3):
            if sum(b) % 2 != parity:
                clauses.append([(i, 1 - bi) for i, bi in enumerate(b)])  # literal true iff x_i == 1-b_i
        assert len(clauses) == 4
        for x in itertools.product([0, 1], repeat=3):
            sat = all(any(x[i] == want for i, want in c) for c in clauses)
            assert sat == (sum(x) % 2 == parity)
    return 'Lemma 1.2 base case: 3-XOR == its 4 clauses on all 8 assignments, both parities: OK'


def check_xor_chain(maxw=8):
    # x1+..+xw = b  <=>  exists unique y-chain satisfying 3-variable parities
    for w in range(3, maxw + 1):
        for b in (0, 1):
            for x in itertools.product([0, 1], repeat=w):
                ys = []
                y = x[0] ^ x[1]
                for j in range(2, w - 1):
                    ys.append(y)
                    y = y ^ x[j]
                last_ok = (y ^ x[w - 1]) == b
                assert last_ok == (sum(x) % 2 == b)
    return f'Lemma 1.2 chain: verified for all w <= {maxw}: OK'


def check_counting():
    out = []
    for n in range(6, 31):
        s = 2 ** n // (4 * n)
        lhs = s * math.log2(16 * (n + s) ** 2)
        out.append((n, lhs < 2 ** n))
    first = min(n for n, ok in out if all(o for m, o in out if m >= n))
    return f'Lemma 4.1 inequality s*log2(16(n+s)^2) < 2^n with s=2^n/(4n): holds for all checked n in [{first},30]'


if __name__ == '__main__':
    for f in (check_xor3_encoding, check_xor_chain, check_counting):
        print(f())
