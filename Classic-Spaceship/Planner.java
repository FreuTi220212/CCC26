import java.io.*;
import java.nio.file.*;
import java.util.*;
import java.util.concurrent.*;

/**
 * Level 7: exakte (gewichtete) A*-Suche ueber den vollen kinematischen Zustand beider Achsen.
 * Zustand = (x, y, Pace-Eintrag-Zustand X, Pace-Eintrag-Zustand Y); ein Tick = ein Schritt.
 * Aufruf: java Planner <input.txt> <output.txt> [gewicht] [threads]
 */
public class Planner {
    static final int NS = 31;
    static int MODE = Integer.getInteger("mode", 2); // Bit0: (A,A), Bit1: (B,B), Bit2: gemischte Ecken
    static final int[] Q = new int[NS], E = new int[NS], D = new int[NS], DA = new int[NS], DB = new int[NS], CONT = new int[NS];
    static final boolean[] END = new boolean[NS];
    static final int[][] NEXT = new int[NS][];
    static final int[] ORD = {0, 5, 4, 3, 2, 1};

    static {
        int idx = 0;
        Q[0] = 0; E[0] = 0; D[0] = 0;
        idx = 1;
        int[][] map = new int[2][];
        int[] start = new int[2 * 6 * 6];
        // Index je (d, q, e): d in {+1,-1}
        int[][][] id = new int[2][6][5];
        for (int di = 0; di < 2; di++) {
            for (int q = 5; q >= 1; q--) {
                for (int e = 0; e < q; e++) {
                    id[di][q][e] = idx;
                    Q[idx] = q; E[idx] = e; D[idx] = di == 0 ? 1 : -1;
                    idx++;
                }
            }
        }
        for (int s = 0; s < NS; s++) {
            DA[s] = Q[s] > 0 ? D[s] : 0;
            DB[s] = (Q[s] > 0 && E[s] == Q[s] - 1) ? D[s] : 0;
            END[s] = Q[s] == 0 || E[s] == Q[s] - 1;
            if (!END[s]) {
                int di = D[s] > 0 ? 0 : 1;
                CONT[s] = id[di][Q[s]][E[s] + 1];
            }
            // naechste Eintraege (Phase 0)
            List<Integer> nx = new ArrayList<>();
            if (Q[s] == 0) {
                nx.add(0); nx.add(id[0][5][0]); nx.add(id[1][5][0]);
            } else {
                int di = D[s] > 0 ? 0 : 1;
                int i = 0;
                for (int k = 0; k < ORD.length; k++) if (ORD[k] == Q[s]) i = k;
                for (int j = i - 1; j <= i + 1; j++) {
                    if (j < 0 || j >= ORD.length) continue;
                    if (ORD[j] == 0) nx.add(0); else nx.add(id[di][ORD[j]][0]);
                }
            }
            NEXT[s] = nx.stream().mapToInt(Integer::intValue).toArray();
        }
    }

    // ---------------- Fall ----------------
    static class Case {
        int tx, ty, limit;
        int[][] ast;
    }

    static String solveCase(Case c, double weight0) {
        if (c.tx == 0 && c.ty == 0) return "0\n0\n";
        // Gewichtetes A*: erst schnell (grosses Gewicht), bei Misserfolg/Zeitueberschreitung genauer
        for (double w : new double[]{weight0, 2.5, 4.0, 1.25, 1.0}) {
            for (int margin : new int[]{30, 70, 150}) {
                String r = search(c, w, margin);
                if (r != null) return r;
            }
        }
        return "0\n0\n";
    }

    static String search(Case c, double weight, int margin) {
        int xlo = Math.min(0, c.tx) - margin, xhi = Math.max(0, c.tx) + margin;
        int ylo = Math.min(0, c.ty) - margin, yhi = Math.max(0, c.ty) + margin;
        int W = xhi - xlo + 1, H = yhi - ylo + 1;
        boolean[] blocked = new boolean[W * H];
        final boolean cont = (MODE & 8) != 0;  // kontinuierliche Positionen (Bruchteile) zu den Tickzeitpunkten
        final int rad = cont ? 1 : 2;           // Karte fuer die BFS-Heuristik (im kontinuierlichen Modus entspannt)
        for (int[] a : c.ast) {
            for (int x = Math.max(a[0] - rad, xlo); x <= Math.min(a[0] + rad, xhi); x++)
                for (int y = Math.max(a[1] - rad, ylo); y <= Math.min(a[1] + rad, yhi); y++)
                    blocked[(x - xlo) * H + (y - ylo)] = true;
        }
        // Praefixsumme der Asteroiden (ungedehnt) fuer O(1)-Rechteckabfragen im kontinuierlichen Modus
        final int PX = xlo - 3, PY = ylo - 3, PW = W + 6, PH = H + 6;
        int[] pre = null;
        if (cont) {
            int[] occ = new int[PW * PH];
            for (int[] a : c.ast) {
                int ix = a[0] - PX, iy = a[1] - PY;
                if (ix >= 0 && ix < PW && iy >= 0 && iy < PH) occ[ix * PH + iy] = 1;
            }
            pre = new int[(PW + 1) * (PH + 1)];
            for (int i = 0; i < PW; i++)
                for (int j = 0; j < PH; j++)
                    pre[(i + 1) * (PH + 1) + (j + 1)] = occ[i * PH + j] + pre[i * (PH + 1) + (j + 1)] + pre[(i + 1) * (PH + 1) + j] - pre[i * (PH + 1) + j];
        }
        // Heuristik: Zugzahl bis zum Ziel auf freien Zellen (8 Nachbarn, Diagonale nur bei freien Ecken), vom Ziel aus per BFS
        int[] hd = new int[W * H];
        Arrays.fill(hd, -1);
        int[] queue = new int[W * H];
        int qh = 0, qt = 0;
        int tIdx = (c.tx - xlo) * H + (c.ty - ylo);
        if (blocked[tIdx] || blocked[(0 - xlo) * H + (0 - ylo)]) return null;
        hd[tIdx] = 0; queue[qt++] = tIdx;
        int[] ddx = {1, -1, 0, 0, 1, 1, -1, -1}, ddy = {0, 0, 1, -1, 1, -1, 1, -1};
        while (qh < qt) {
            int cur0 = queue[qh++];
            int cx = cur0 / H + xlo, cy = cur0 % H + ylo;
            for (int k = 0; k < 8; k++) {
                int nx = cx + ddx[k], ny = cy + ddy[k];
                if (nx < xlo || nx > xhi || ny < ylo || ny > yhi) continue;
                int ni = (nx - xlo) * H + (ny - ylo);
                if (blocked[ni] || hd[ni] >= 0) continue;
                // Diagonale ohne Eckenpruefung: im Sprung-am-Ende-Modell darf das Schiff diagonal springen (zulaessige Heuristik)
                hd[ni] = hd[cur0] + 1; queue[qt++] = ni;
            }
        }
        if (hd[(0 - xlo) * H + (0 - ylo)] < 0) return null;
        final int maxT = c.limit;
        // Zustandsschluessel: ((x*H + y)*NS + sx)*NS + sy  (x,y relativ zum Fenster)
        long cap = 1 << 20;
        long[] keys = new long[(int) cap];
        Arrays.fill(keys, -1L);
        int[] gArr = new int[(int) cap];
        int[] par = new int[(int) cap];
        long mask = cap - 1;
        int count = 0;

        // Heap (long-codiert): f in obere Bits
        long[] heap = new long[1 << 16];
        int hs = 0;

        long startKey = (((long) (0 - xlo) * H + (0 - ylo)) * NS + 0) * NS + 0;
        // Insert start
        int slot = (int) (hash(startKey) & mask);
        keys[slot] = startKey; gArr[slot] = 0; par[slot] = -1; count++;
        heap = push(heap, hs++, enc((int) Math.round(weight * hd[(0 - xlo) * H + (0 - ylo)]), 0, slot));
        int goalSlot = -1;
        long expanded = 0;
        int[] ox = new int[3], oy = new int[3];
        while (hs > 0) {
            long top = heap[0];
            hs = pop(heap, hs);
            int sl = decSlot(top), g = decG(top);
            if (gArr[sl] != g) continue;
            long key = keys[sl];
            int sy = (int) (key % NS); long r1 = key / NS; int sx = (int) (r1 % NS); long r2 = r1 / NS;
            int y = (int) (r2 % H) + ylo; int x = (int) (r2 / H) + xlo;
            if (x == c.tx && y == c.ty && sx == 0 && sy == 0) { goalSlot = sl; break; }
            if (g + 1 > maxT) continue;
            if (++expanded > 6_000_000L) break;
            // Nachfolger je Achse
            int xn = x + (END[sx] ? (Q[sx] > 0 ? D[sx] : 0) : 0);
            int yn = y + (END[sy] ? (Q[sy] > 0 ? D[sy] : 0) : 0);
            int[] nxs = END[sx] ? NEXT[sx] : new int[]{CONT[sx]};
            int[] nys = END[sy] ? NEXT[sy] : new int[]{CONT[sy]};
            for (int nsx : nxs) {
                int xa = xn + DA[nsx], xb = xn + DB[nsx];
                for (int nsy : nys) {
                    int ya = yn + DA[nsy], yb = yn + DB[nsy];
                    boolean bad = false;
                    if (cont) {
                        int xr = 60 * xn + (Q[nsx] > 0 ? D[nsx] * E[nsx] * (60 / Q[nsx]) : 0);
                        int yr = 60 * yn + (Q[nsy] > 0 ? D[nsy] * E[nsy] * (60 / Q[nsy]) : 0);
                        bad = fracHit(pre, PX, PY, PW, PH, xr, yr);
                    }
                    if (!cont && (MODE & 1) != 0 && hit(blocked, xa, ya, xlo, xhi, ylo, yhi, H)) bad = true;   // beide Achsen springen am Anfang
                    if (!cont && (MODE & 2) != 0 && hit(blocked, xb, yb, xlo, xhi, ylo, yhi, H)) bad = true;   // beide springen am Ende
                    if (!cont && (MODE & 4) != 0 && (hit(blocked, xa, yb, xlo, xhi, ylo, yhi, H) || hit(blocked, xb, ya, xlo, xhi, ylo, yhi, H))) bad = true;  // gemischt
                    if (bad) continue;
                    if (xn < xlo || xn > xhi || yn < ylo || yn > yhi) continue;
                    long nk = (((long) (xn - xlo) * H + (yn - ylo)) * NS + nsx) * NS + nsy;
                    int ng = g + 1;
                    int hv0 = hd[(xn - xlo) * H + (yn - ylo)];
                    if (hv0 < 0 || (!cont && ng + hv0 > maxT) || ng > maxT) continue;  // Zugzahl bis zum Ziel ist untere Schranke: Limit nicht mehr haltbar
                    int s2 = (int) (hash(nk) & mask);
                    while (keys[s2] != -1L && keys[s2] != nk) s2 = (int) ((s2 + 1) & mask);
                    if (keys[s2] == nk) {
                        if (gArr[s2] <= ng) continue;
                    } else {
                        keys[s2] = nk; count++;
                    }
                    gArr[s2] = ng; par[s2] = sl;
                    if (hs == heap.length) heap = Arrays.copyOf(heap, hs * 2);
                    heap = push(heap, hs++, enc(ng + (int) Math.round(weight * hv0), ng, s2));
                    if (count * 2L > cap) { // vergroessern
                        long ncap = cap * 2;
                        if (ncap > (1L << 24)) return null;
                        long[] nkeys = new long[(int) ncap]; Arrays.fill(nkeys, -1L);
                        int[] ng_ = new int[(int) ncap]; int[] np_ = new int[(int) ncap];
                        long nmask = ncap - 1;
                        int[] remap = new int[(int) cap];
                        for (int i = 0; i < cap; i++) {
                            if (keys[i] == -1L) continue;
                            int j = (int) (hash(keys[i]) & nmask);
                            while (nkeys[j] != -1L) j = (int) ((j + 1) & nmask);
                            nkeys[j] = keys[i]; ng_[j] = gArr[i]; np_[j] = par[i]; remap[i] = j;
                        }
                        for (int i = 0; i < ncap; i++) if (nkeys[i] != -1L && np_[i] >= 0) np_[i] = remap[np_[i]];
                        for (int i = 0; i < hs; i++) { long hv = heap[i]; heap[i] = enc(decF(hv), decG(hv), remap[decSlot(hv)]); }
                        if (goalSlot >= 0) goalSlot = remap[goalSlot];
                        keys = nkeys; gArr = ng_; par = np_; cap = ncap; mask = nmask;
                        sl = remap[sl];
                    }
                }
            }
        }
        if (goalSlot < 0) return null;
        // Rueckverfolgung: Zustaende je Tick
        ArrayList<int[]> st = new ArrayList<>();
        int cur = goalSlot;
        while (cur >= 0) {
            long key = keys[cur];
            int sy = (int) (key % NS); long r1 = key / NS; int sx = (int) (r1 % NS);
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

    /** Kollision eines Schiffs an der (mit 60 skalierten) Position (xr, yr): Asteroid mit |dx| < 3 und |dy| < 3 (offen). */
    static boolean fracHit(int[] pre, int PX, int PY, int PW, int PH, int xr, int yr) {
        int xl = Math.floorDiv(xr - 180, 60) + 1, xu = -Math.floorDiv(-(xr + 180), 60) - 1;
        int yl = Math.floorDiv(yr - 180, 60) + 1, yu = -Math.floorDiv(-(yr + 180), 60) - 1;
        int i1 = Math.max(xl - PX, 0), i2 = Math.min(xu - PX, PW - 1), j1 = Math.max(yl - PY, 0), j2 = Math.min(yu - PY, PH - 1);
        if (i1 > i2 || j1 > j2) return false;
        int q = PH + 1;
        return pre[(i2 + 1) * q + (j2 + 1)] - pre[i1 * q + (j2 + 1)] - pre[(i2 + 1) * q + j1] + pre[i1 * q + j1] > 0;
    }

    static boolean hit(boolean[] blocked, int x, int y, int xlo, int xhi, int ylo, int yhi, int H) {
        if (x < xlo || x > xhi || y < ylo || y > yhi) return true; // ausserhalb des Suchraums = gesperrt
        return blocked[(x - xlo) * H + (y - ylo)];
    }

    static int hf(int x, int y, Case c, int xlo, int ylo, double w) {
        int dx = Math.abs(c.tx - x), dy = Math.abs(c.ty - y);
        int h = Math.max(dx, dy);
        return (int) Math.round(w * h);
    }

    static long hash(long k) { k ^= k >>> 33; k *= 0xff51afd7ed558ccdL; k ^= k >>> 33; return k & Long.MAX_VALUE; }
    static long enc(int f, int g, int slot) { return ((long) f << 44) | ((long) g << 28) | slot; }
    static int decF(long v) { return (int) (v >>> 44); }
    static int decG(long v) { return (int) ((v >>> 28) & 0xFFFF); }
    static int decSlot(long v) { return (int) (v & 0xFFFFFFF); }

    static long[] push(long[] h, int n, long v) {
        int i = n;
        h[i] = v;
        while (i > 0) {
            int p = (i - 1) >> 1;
            if (h[p] <= h[i]) break;
            long t = h[p]; h[p] = h[i]; h[i] = t; i = p;
        }
        return h;
    }

    static int pop(long[] h, int n) {
        n--;
        h[0] = h[n];
        int i = 0;
        while (true) {
            int l = 2 * i + 1, r = l + 1, m = i;
            if (l < n && h[l] < h[m]) m = l;
            if (r < n && h[r] < h[m]) m = r;
            if (m == i) break;
            long t = h[m]; h[m] = h[i]; h[i] = t; i = m;
        }
        return n;
    }

    // ---------------- I/O ----------------
    public static void main(String[] args) throws Exception {
        List<String> lines = new ArrayList<>();
        for (String l : Files.readAllLines(Paths.get(args[0]))) if (!l.trim().isEmpty()) lines.add(l.trim());
        double weight = args.length > 2 ? Double.parseDouble(args[2]) : 1.0;
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
            c.ast = new int[k][2];
            for (int j = 0; j < k; j++) { String[] t = as[j].split(","); c.ast[j][0] = Integer.parseInt(t[0]); c.ast[j][1] = Integer.parseInt(t[1]); }
            cases[i] = c;
            p += 3;
        }
        String[] res = new String[n];
        ExecutorService ex = Executors.newFixedThreadPool(threads);
        List<Future<?>> fs = new ArrayList<>();
        for (int i = 0; i < n; i++) {
            final int ii = i;
            fs.add(ex.submit(() -> { res[ii] = solveCase(cases[ii], weight); }));
        }
        for (Future<?> f : fs) f.get();
        ex.shutdown();
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < n; i++) sb.append(res[i]).append("\n");
        Files.write(Paths.get(args[1]), sb.toString().getBytes("UTF-8"));
    }
}
