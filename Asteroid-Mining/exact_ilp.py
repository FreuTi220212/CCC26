import sys
import numpy as np
from scipy.optimize import LinearConstraint, milp, Bounds


def exact(w, h, sc):
    cells = [(r, c) for r in range(1, h + 1) for c in range(1, w + 1)]
    idx = {p: i for i, p in enumerate(cells)}
    n = len(cells)
    S = (0, sc)
    edges = []  # gerichtete Kanten zwischen minierbaren Zellen + Start -> (1, sc)
    for (r, c) in cells:
        for nb in ((r + 1, c), (r - 1, c), (r, c + 1), (r, c - 1)):
            if nb in idx:
                edges.append((idx[(r, c)], idx[nb]))
    start_edge = idx[(1, sc)]
    ne = len(edges)
    nv = n + ne + 1  # x_v, f_e, f_start
    A, lo, hi = [], [], []
    # Dominanz
    for (r, c) in cells:
        row = np.zeros(nv)
        row[idx[(r, c)]] = 1
        for nb in ((r + 1, c), (r - 1, c), (r, c + 1), (r, c - 1)):
            if nb in idx:
                row[idx[nb]] = 1
        A.append(row); lo.append(1); hi.append(np.inf)
    M = n
    # Fluss <= M*x_ziel
    for e, (u, v) in enumerate(edges):
        row = np.zeros(nv); row[n + e] = 1; row[v] = -M
        A.append(row); lo.append(-np.inf); hi.append(0)
    row = np.zeros(nv); row[n + ne] = 1; row[start_edge] = -M
    A.append(row); lo.append(-np.inf); hi.append(0)
    # Flusserhaltung: eingehend - ausgehend = x_v (jeder Tunnel verbraucht 1)
    for v in range(n):
        row = np.zeros(nv)
        for e, (a, b) in enumerate(edges):
            if b == v:
                row[n + e] += 1
            if a == v:
                row[n + e] -= 1
        if v == start_edge:
            row[n + ne] += 1
        row[v] -= 1
        A.append(row); lo.append(0); hi.append(0)
    cobj = np.zeros(nv); cobj[:n] = 1
    integ = np.zeros(nv); integ[:n] = 1
    ub = np.full(nv, np.inf); ub[:n] = 1
    res = milp(cobj, constraints=LinearConstraint(np.array(A), lo, hi), integrality=integ, bounds=Bounds(0, ub))
    x = np.rint(res.x[:n]).astype(int)
    return int(x.sum()), {p for p, i in idx.items() if x[i]}


if __name__ == "__main__":
    w, h, sc = map(int, sys.argv[1:4])
    cost, cells = exact(w, h, sc)
    print(cost)
    for r in range(h + 2):
        print("".join("S" if (r, c) == (0, sc) else "#" if r in (0, h + 1) or c in (0, w + 1) else "X" if (r, c) in cells else ":" for c in range(w + 2)))
