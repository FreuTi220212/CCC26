import java.nio.file.*;
import java.util.*;
import java.util.concurrent.*;

/**
 * Level 8: bewegte Asteroiden (konstante Pace je Achse). Zeitexpandiertes gewichtetes A* ueber
 * (Tick, x, y, Pace-Eintrag-Zustand X, Pace-Eintrag-Zustand Y).
 * Konvention (an den Beispielen verifiziert): Schiff UND Asteroiden aendern die Position erst am ENDE der Pace-Dauer:
 *   Asteroid zum Tick t: x0 + sign * floor((t + 1) / |pace|).
 * Aufruf: java Planner8 <input.txt> <output.txt> [gewicht] [threads]
 */
public class Planner8 {
    static final int NS = 31;
    static final int[] Q = new int[NS], E = new int[NS], D = new int[NS], DB = new int[NS], CONT = new int[NS];
    static final boolean[] END = new boolean[NS];
    static final int[][] NEXT = new int[NS][];
    static final int[] ORD = {0, 5, 4, 3, 2, 1};

    static {
        int idx = 1;
        int[][][] id = new int[2][6][5];
        for (int di = 0; di < 2; di++)
            for (int q = 5; q >= 1; q--)
                for (int e = 0; e < q; e++) { id[di][q][e] = idx; Q[idx] = q; E[idx] = e; D[idx] = di == 0 ? 1 : -1; idx++; }
        for (int s = 0; s < NS; s++) {
            DB[s] = (Q[s] > 0 && E[s] == Q[s] - 1) ? D[s] : 0;
            END[s] = Q[s] == 0 || E[s] == Q[s] - 1;
            if (!END[s]) CONT[s] = id[D[s] > 0 ? 0 : 1][Q[s]][E[s] + 1];
            List<Integer> nx = new ArrayList<>();
            if (Q[s] == 0) { nx.add(0); nx.add(id[0][5][0]); nx.add(id[1][5][0]); }
            else {
                int di = D[s] > 0 ? 0 : 1, i = 0;
                for (int k = 0; k < ORD.length; k++) if (ORD[k] == Q[s]) i = k;
                for (int j = i - 1; j <= i + 1; j++) {
                    if (j < 0 || j >= ORD.length) continue;
                    nx.add(ORD[j] == 0 ? 0 : id[di][ORD[j]][0]);
                }
            }
            NEXT[s] = nx.stream().mapToInt(Integer::intValue).toArray();
        }
    }

    static class Case { int tx, ty, limit; int[][] ast; }

    static String solveCase(Case c, double weight0) {
        if (c.tx == 0 && c.ty == 0) return "0\n0\n";
        for (double w : new double[]{weight0, 2.5, 4.0, 1.25, 1.0}) {
            for (int margin : new int[]{20, 45}) {
                String r = search(c, w, margin);
                if (r != null) return r;
            }
        }
        return "0\n0\n";
    }

    static int astPos(int x0, int p, int t) {
        if (p == 0) return x0;
        int q = Math.abs(p);
        return x0 + (p > 0 ? 1 : -1) * ((t + 1) / q);
    }

    static String search(Case c, double weight, int margin) {
        int xlo = Math.min(0, c.tx) - margin, xhi = Math.max(0, c.tx) + margin;
        int ylo = Math.min(0, c.ty) - margin, yhi = Math.max(0, c.ty) + margin;
        int W = xhi - xlo + 1, H = yhi - ylo + 1;
        int tmax = c.limit;                       // Ticks 0..tmax-1
        int words = (W * H + 63) >> 6;
        long[][] blocked = new long[tmax][words];
        for (int t = 0; t < tmax; t++) {
            long[] bt = blocked[t];
            for (int[] a : c.ast) {
                int ax = astPos(a[0], a[2], t), ay = astPos(a[1], a[3], t);
                if (ax < xlo - 2 || ax > xhi + 2 || ay < ylo - 2 || ay > yhi + 2) continue;
                for (int x = Math.max(ax - 2, xlo); x <= Math.min(ax + 2, xhi); x++) {
                    int base = (x - xlo) * H - ylo;
                    for (int y = Math.max(ay - 2, ylo); y <= Math.min(ay + 2, yhi); y++) {
                        int i = base + y;
                        bt[i >> 6] |= 1L << (i & 63);
                    }
                }
            }
        }
        if (isBlocked(blocked, 0, 0, 0, xlo, ylo, H)) return null;

        long cap = 1 << 20;
        long[] keys = new long[(int) cap];
        Arrays.fill(keys, -1L);
        int[] par = new int[(int) cap];
        long mask = cap - 1;
        int count = 0;
        long[] heap = new long[1 << 16];
        int hs = 0;

        long startKey = key(0, 0 - xlo, 0 - ylo, 0, 0, W, H);
        int slot = (int) (hash(startKey) & mask);
        keys[slot] = startKey; par[slot] = -1; count++;
        heap[hs++] = enc((int) Math.round(weight * Math.max(Math.abs(c.tx), Math.abs(c.ty))), slot);
        int goalSlot = -1;
        long expanded = 0;
        while (hs > 0) {
            long top = heap[0];
            hs = pop(heap, hs);
            int sl = decSlot(top);
            long k = keys[sl];
            // Schluessel zerlegen
            int sy = (int) (k % NS); long r1 = k / NS; int sx = (int) (r1 % NS); long r2 = r1 / NS;
            int y = (int) (r2 % H); long r3 = r2 / H; int x = (int) (r3 % W); int t = (int) (r3 / W);
            int ax = x + xlo, ay = y + ylo;
            if (ax == c.tx && ay == c.ty && sx == 0 && sy == 0) { goalSlot = sl; break; }
            if (t + 2 > tmax) continue;           // Nachfolger braucht Tick t+1 <= tmax-1
            if (++expanded > 4_000_000L) break;
            int nt = t + 1;
            int xn = ax + (END[sx] ? (Q[sx] > 0 ? D[sx] : 0) : 0);
            int yn = ay + (END[sy] ? (Q[sy] > 0 ? D[sy] : 0) : 0);
            if (xn < xlo || xn > xhi || yn < ylo || yn > yhi) continue;
            int[] nxs = END[sx] ? NEXT[sx] : new int[]{CONT[sx]};
            int[] nys = END[sy] ? NEXT[sy] : new int[]{CONT[sy]};
            for (int nsx : nxs) {
                int xb = xn + DB[nsx];
                for (int nsy : nys) {
                    int yb = yn + DB[nsy];
                    if (isBlocked(blocked, nt, xb, yb, xlo, ylo, H, xhi, yhi)) continue;
                    int hh = Math.max(Math.abs(c.tx - xn), Math.abs(c.ty - yn));
                    if (nt + hh > tmax - 1) continue;
                    long nk = key(nt, xn - xlo, yn - ylo, nsx, nsy, W, H);
                    int s2 = (int) (hash(nk) & mask);
                    while (keys[s2] != -1L && keys[s2] != nk) s2 = (int) ((s2 + 1) & mask);
                    if (keys[s2] == nk) continue;
                    keys[s2] = nk; par[s2] = sl; count++;
                    if (hs == heap.length) heap = Arrays.copyOf(heap, hs * 2);
                    heap = push(heap, hs++, enc(nt + (int) Math.round(weight * hh), s2));
                    if (count * 2L > cap) {
                        long ncap = cap * 2;
                        if (ncap > (1L << 23)) return null;
                        long[] nkeys = new long[(int) ncap]; Arrays.fill(nkeys, -1L);
                        int[] np = new int[(int) ncap];
                        long nmask = ncap - 1;
                        int[] remap = new int[(int) cap];
                        for (int i = 0; i < cap; i++) {
                            if (keys[i] == -1L) continue;
                            int j = (int) (hash(keys[i]) & nmask);
                            while (nkeys[j] != -1L) j = (int) ((j + 1) & nmask);
                            nkeys[j] = keys[i]; np[j] = par[i]; remap[i] = j;
                        }
                        for (int i = 0; i < ncap; i++) if (nkeys[i] != -1L && np[i] >= 0) np[i] = remap[np[i]];
                        for (int i = 0; i < hs; i++) heap[i] = enc(decF(heap[i]), remap[decSlot(heap[i])]);
                        keys = nkeys; par = np; cap = ncap; mask = nmask;
                        sl = remap[sl];
                    }
                }
            }
        }
        if (goalSlot < 0) return null;
        ArrayList<int[]> st = new ArrayList<>();
        int cur = goalSlot;
        while (cur >= 0) {
            long k = keys[cur];
            int sy = (int) (k % NS); long r1 = k / NS; int sx = (int) (r1 % NS);
            st.add(new int[]{sx, sy});
            cur = par[cur];
        }
        Collections.reverse(st);
        StringBuilder bx = new StringBuilder(), by = new StringBuilder();
        for (int[] s : st) {
            if (E[s[0]] == 0) { if (bx.length() > 0) bx.append(' '); bx.append(D[s[0]] * Q[s[0]]); }
            if (E[s[1]] == 0) { if (by.length() > 0) by.append(' '); by.append(D[s[1]] * Q[s[1]]); }
        }
        return bx + "\n" + by + "\n";
    }

    static boolean isBlocked(long[][] b, int t, int x, int y, int xlo, int ylo, int H) {
        int i = (x - xlo) * H + (y - ylo);
        return (b[t][i >> 6] >>> (i & 63) & 1L) != 0;
    }

    static boolean isBlocked(long[][] b, int t, int x, int y, int xlo, int ylo, int H, int xhi, int yhi) {
        if (x < xlo || x > xhi || y < ylo || y > yhi) return true;
        return isBlocked(b, t, x, y, xlo, ylo, H);
    }

    static long key(int t, int x, int y, int sx, int sy, int W, int H) {
        return ((((long) t * W + x) * H + y) * NS + sx) * NS + sy;
    }

    static long hash(long k) { k ^= k >>> 33; k *= 0xff51afd7ed558ccdL; k ^= k >>> 33; return k & Long.MAX_VALUE; }
    static long enc(int f, int slot) { return ((long) f << 28) | slot; }
    static int decF(long v) { return (int) (v >>> 28); }
    static int decSlot(long v) { return (int) (v & 0xFFFFFFF); }

    static long[] push(long[] h, int n, long v) {
        int i = n; h[i] = v;
        while (i > 0) { int p = (i - 1) >> 1; if (h[p] <= h[i]) break; long t = h[p]; h[p] = h[i]; h[i] = t; i = p; }
        return h;
    }

    static int pop(long[] h, int n) {
        n--; h[0] = h[n]; int i = 0;
        while (true) {
            int l = 2 * i + 1, r = l + 1, m = i;
            if (l < n && h[l] < h[m]) m = l;
            if (r < n && h[r] < h[m]) m = r;
            if (m == i) break;
            long t = h[m]; h[m] = h[i]; h[i] = t; i = m;
        }
        return n;
    }

    public static void main(String[] args) throws Exception {
        List<String> lines = new ArrayList<>();
        for (String l : Files.readAllLines(Paths.get(args[0]))) if (!l.trim().isEmpty()) lines.add(l.trim());
        double weight = args.length > 2 ? Double.parseDouble(args[2]) : 1.5;
        int threads = args.length > 3 ? Integer.parseInt(args[3]) : Math.max(1, Runtime.getRuntime().availableProcessors() / 2);
        int n = Integer.parseInt(lines.get(0));
        Case[] cases = new Case[n];
        int p = 1;
        for (int i = 0; i < n; i++) {
            Case c = new Case();
            String[] a = lines.get(p).split(" ");
            String[] xy = a[0].split(",");
            c.tx = Integer.parseInt(xy[0]); c.ty = Integer.parseInt(xy[1]); c.limit = Integer.parseInt(a[1]);
            int k = Integer.parseInt(lines.get(p + 1));
            String[] as = lines.get(p + 2).split(" ");
            c.ast = new int[k][4];
            for (int j = 0; j < k; j++) { String[] t = as[j].split(","); for (int m = 0; m < 4; m++) c.ast[j][m] = Integer.parseInt(t[m]); }
            cases[i] = c;
            p += 3;
        }
        String[] res = new String[n];
        ExecutorService ex = Executors.newFixedThreadPool(threads);
        List<Future<?>> fs = new ArrayList<>();
        for (int i = 0; i < n; i++) { final int ii = i; fs.add(ex.submit(() -> { res[ii] = solveCase(cases[ii], weight); })); }
        for (Future<?> f : fs) f.get();
        ex.shutdown();
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < n; i++) sb.append(res[i]).append("\n");
        Files.write(Paths.get(args[1]), sb.toString().getBytes("UTF-8"));
    }
}
