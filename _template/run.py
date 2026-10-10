#!/usr/bin/env python3
"""CCC-Runner (nur Standardbibliothek, Windows-tauglich).

  python run.py setup N <zip>   Zip nach levelN/ entpacken (flach), levelN.py anlegen (Kopie von level(N-1).py oder
                                Template), PDF-Seiten als PNG nach levelN/pages/ (wenn pymupdf da ist), Input-Groessen zeigen
  python run.py info N          Input-Groessen/Kopfzeilen von levelN zeigen
  python run.py N [Optionen]    Beispiel pruefen, dann alle Inputs loesen und Outputs schreiben
      --timeout S   Timeout je Datei (Standard 60)      --slow S    Warnung ab S Sekunden (Standard 10)
      --zip         zusaetzlich levelN/output.zip       --loose     Zeilenende-Leerzeichen/Leerzeilen am Ende ignorieren
      --no-validate validate() aus levelN.py nicht fuer die grossen Inputs benutzen

Dateien: levelN/in_level-N_X-name.txt (Input), out_level-N_X-name.txt (Output). Beispiel = Name enthaelt 'example'.
Hat levelN.py eine Funktion validate(input_text, output_text) -> None | Fehlertext, wird sie statt des exakten
Vergleichs benutzt (noetig bei Aufgaben mit mehreren gueltigen Loesungen).
"""
import importlib.util
import os
import shutil
import subprocess
import sys
import time
import zipfile

ROOT = os.path.dirname(os.path.abspath(__file__))
TEMPLATE = os.path.join(ROOT, "level_template.py")
MAX_DIFFS = 10


def ldir(n):
    return os.path.join(ROOT, f"level{n}")


def sol(n):
    return os.path.join(ROOT, f"level{n}.py")


def rel(p):
    return os.path.relpath(p, ROOT).replace("\\", "/")


def size(n):
    return f"{n} B" if n < 1024 else f"{n / 1024:.0f} KB" if n < 1024 ** 2 else f"{n / 1024 ** 2:.1f} MB"


def norm(b):
    return b.decode("utf-8", "replace").replace("\r\n", "\n").replace("\r", "\n")


def key(s):
    import re
    return [int(t) if t.isdigit() else t for t in re.split(r"(\d+)", s)]


def input_files(n):
    d = ldir(n)
    ins = sorted((f for f in os.listdir(d) if f.startswith("in_") and f.endswith(".txt")), key=key)
    ex = [f for f in ins if "example" in f.lower()]
    return ex, [f for f in ins if f not in ex]


def out_name(f):
    return "out_" + f[3:]


# ------------------------------------------------------------------ setup / info
def info(n):
    d = ldir(n)
    ex, rest = input_files(n)
    print(f"{rel(d)}: {len(ex)} Beispiel(e), {len(rest)} weitere Inputs")
    for f in ex + rest:
        p = os.path.join(d, f)
        with open(p, "r", encoding="utf-8", errors="replace") as fh:
            lines = fh.read().splitlines()
        head = " | ".join(x[:30] for x in lines[:3])
        print(f"  {f:34} {size(os.path.getsize(p)):>8}  {len(lines):>7} Zeilen  {head}")


def setup(n, zip_path):
    if not os.path.isfile(zip_path):
        sys.exit(f"Zip nicht gefunden: {zip_path}")
    dest = ldir(n)
    os.makedirs(dest, exist_ok=True)
    with zipfile.ZipFile(zip_path) as zf:
        for info_ in zf.infolist():
            name = info_.filename.replace("\\", "/").split("/")[-1]
            if info_.is_dir() or not name or name.startswith(".") or "__MACOSX" in info_.filename:
                continue
            with zf.open(info_) as src, open(os.path.join(dest, name), "wb") as dst:
                shutil.copyfileobj(src, dst)
    print(f"entpackt nach {rel(dest)}/")
    if not os.path.exists(sol(n)):
        prev = sol(n - 1)
        shutil.copyfile(prev if os.path.isfile(prev) else TEMPLATE, sol(n))
        print(f"{rel(sol(n))} angelegt ({'Kopie von ' + rel(prev) if os.path.isfile(prev) else 'Template'})")
    pdfs = [f for f in os.listdir(dest) if f.lower().endswith(".pdf")]
    if pdfs:
        try:
            import pymupdf
            doc = pymupdf.open(os.path.join(dest, pdfs[0]))
            pdir = os.path.join(dest, "pages")
            os.makedirs(pdir, exist_ok=True)
            for i, page in enumerate(doc):
                page.get_pixmap(dpi=70).save(os.path.join(pdir, f"p{i + 1}.png"))
            print(f"{len(doc)} PDF-Seiten als PNG nach {rel(pdir)}/ (ansehen! pdftotext verpasst Bilder/Regeln)")
        except ImportError:
            print("pymupdf fehlt (pip install pymupdf) -> PDF-Seiten nicht gerendert")
        except Exception as e:  # kaputte/ungewoehnliche PDF
            print(f"PDF konnte nicht gerendert werden: {e}")
    info(n)


# ------------------------------------------------------------------ run
def load_validate(n):
    spec = importlib.util.spec_from_file_location(f"level{n}", sol(n))
    mod = importlib.util.module_from_spec(spec)
    sys.path.insert(0, ROOT)
    spec.loader.exec_module(mod)  # levelN.py muss unter __main__ geschuetzt sein
    return getattr(mod, "validate", None)


def run_one(n, path, timeout):
    """-> (status, stdout_bytes, sekunden, stderr_text); status ok|timeout|error"""
    env = dict(os.environ, PYTHONUTF8="1", PYTHONIOENCODING="utf-8")
    with open(path, "rb") as f:
        data = f.read()
    t0 = time.perf_counter()
    try:
        p = subprocess.run([sys.executable, sol(n)], input=data, capture_output=True, timeout=timeout, env=env, cwd=ROOT)
    except subprocess.TimeoutExpired:
        return "timeout", b"", time.perf_counter() - t0, ""
    st = "ok" if p.returncode == 0 else "error"
    return st, p.stdout, time.perf_counter() - t0, p.stderr.decode("utf-8", "replace")


def diff_lines(exp, got, loose):
    e, g = exp.split("\n"), got.split("\n")
    if loose:
        e, g = [x.rstrip() for x in e], [x.rstrip() for x in g]
        while e and e[-1] == "":
            e.pop()
        while g and g[-1] == "":
            g.pop()
    out = []
    for i in range(max(len(e), len(g))):
        a = e[i] if i < len(e) else "<fehlt>"
        b = g[i] if i < len(g) else "<fehlt>"
        if a != b:
            out.append((i + 1, a, b))
    return out


def fail_exit(msg, ok, total):
    print(msg)
    print(f"Beispiele {ok}/{total} OK - abgebrochen")
    sys.exit(1)


def show_err(err):
    lines = err.strip().splitlines()
    print("\n".join("    " + l for l in lines[-15:]))


def run_level(n, timeout, slow, make_zip, loose, use_validate):
    if not os.path.isfile(sol(n)) or not os.path.isdir(ldir(n)):
        sys.exit(f"{rel(sol(n))} oder {rel(ldir(n))}/ fehlt (python run.py setup {n} <zip>)")
    validate = load_validate(n)
    ex, rest = input_files(n)
    if not ex:
        print("WARNUNG: kein Beispiel gefunden")
    ok = 0
    for f in ex:
        p = os.path.join(ldir(n), f)
        st, out, sec, err = run_one(n, p, timeout)
        head = f"[Beispiel] {f} ({size(os.path.getsize(p))}, {sec:.2f}s)"
        if st == "timeout":
            fail_exit(f"{head} TIMEOUT nach {timeout:g}s", ok, len(ex))
        if st == "error":
            print(f"{head} EXCEPTION")
            show_err(err)
            fail_exit("", ok, len(ex))
        got = norm(out)
        if validate:
            with open(p, "r", encoding="utf-8") as fh:
                msg = validate(fh.read(), got)
            if msg:
                fail_exit(f"{head} VALIDATOR: {msg}", ok, len(ex))
        else:
            exp_path = os.path.join(ldir(n), out_name(f))
            with open(exp_path, "rb") as fh:
                exp = norm(fh.read())
            diffs = diff_lines(exp, got, loose)
            if diffs:
                print(f"{head} FALSCH ({len(diffs)} Zeilen)")
                for line, a, b in diffs[:MAX_DIFFS]:
                    print(f"    Zeile {line}: erwartet {a!r} | bekommen {b!r}")
                if not loose and not diff_lines(exp, got, True):
                    print("    Hinweis: nur Leerzeichen/Leerzeilen am Ende anders (--loose) - Beispiel-Output mit `od -c` ansehen!")
                fail_exit("", ok, len(ex))
        print(f"{head} OK" + (" (Validator)" if validate else ""))
        ok += 1

    odir = os.path.join(ldir(n), "output")
    shutil.rmtree(odir, ignore_errors=True)
    os.makedirs(odir)
    written, failed, slow_files = [], 0, []
    for f in rest:
        p = os.path.join(ldir(n), f)
        st, out, sec, err = run_one(n, p, timeout)
        head = f"[Input]    {f} ({size(os.path.getsize(p))}, {sec:.2f}s)"
        if st != "ok":
            print(f"{head} {'TIMEOUT nach %gs' % timeout if st == 'timeout' else 'EXCEPTION'}")
            if err:
                show_err(err)
            failed += 1
            continue
        got = norm(out)
        if validate and use_validate:
            with open(p, "r", encoding="utf-8") as fh:
                msg = validate(fh.read(), got)
            if msg:
                print(f"{head} VALIDATOR: {msg}")
                failed += 1
                continue
        with open(os.path.join(odir, out_name(f)), "wb") as fh:
            fh.write(got.encode("utf-8"))
        written.append(os.path.join(odir, out_name(f)))
        warn = f"  <-- LANGSAM (> {slow:g}s): Algorithmus pruefen" if sec > slow else ""
        if warn:
            slow_files.append(f)
        print(f"{head} OK{warn}")
    if make_zip and written and not failed:
        zp = os.path.join(ldir(n), "output.zip")
        with zipfile.ZipFile(zp, "w", zipfile.ZIP_DEFLATED) as z:
            for w in written:
                z.write(w, os.path.basename(w))
    tail = f" - {rel(odir)}/" + (f" + output.zip" if make_zip and not failed else "")
    print(f"Beispiele {ok}/{len(ex)} OK - {len(written)} Outputs{tail}" + (f" - {failed} FEHLGESCHLAGEN" if failed else ""))
    if slow_files:
        print(f"WARNUNG langsam: {', '.join(slow_files)}")
    sys.exit(1 if failed else 0)


def main(argv):
    for s in (sys.stdout, sys.stderr):
        try:
            s.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass
    if len(argv) >= 2 and argv[1] == "setup" and len(argv) == 4 and argv[2].isdigit():
        return setup(int(argv[2]), argv[3])
    if len(argv) == 3 and argv[1] == "info" and argv[2].isdigit():
        return info(int(argv[2]))
    if len(argv) < 2 or not argv[1].isdigit():
        sys.exit(__doc__)
    n, timeout, slow, make_zip, loose, uv = int(argv[1]), 60.0, 10.0, False, False, True
    rest, i = argv[2:], 0
    while i < len(rest):
        a = rest[i]
        if a == "--timeout" and i + 1 < len(rest):
            timeout, i = float(rest[i + 1]), i + 2
        elif a == "--slow" and i + 1 < len(rest):
            slow, i = float(rest[i + 1]), i + 2
        elif a == "--zip":
            make_zip, i = True, i + 1
        elif a == "--loose":
            loose, i = True, i + 1
        elif a == "--no-validate":
            uv, i = False, i + 1
        else:
            sys.exit(__doc__)
    run_level(n, timeout, slow, make_zip, loose, uv)


if __name__ == "__main__":
    main(sys.argv)
