"""python run.py N  -> Beispiel pruefen, dann alle Inputs von levelN verarbeiten und zippen."""
import glob
import os
import subprocess
import sys
import time

n = sys.argv[1]
base = os.path.dirname(os.path.abspath(__file__))
d = os.path.join(base, f"level{n}")
sol = os.path.join(base, f"level{n}.py")
env = dict(os.environ, PYTHONUTF8="1")


def run(path):
    t = time.time()
    with open(path, "rb") as f:
        p = subprocess.run([sys.executable, sol], stdin=f, capture_output=True, env=env, timeout=120)
    if p.returncode:
        print(p.stderr.decode(errors="replace")[-1500:])
        sys.exit(f"FEHLER bei {os.path.basename(path)}")
    return p.stdout.replace(b"\r\n", b"\n"), time.time() - t


import importlib.util
spec = importlib.util.spec_from_file_location("sol", sol)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
validate = getattr(mod, "validate", None)  # Level mit mehreren richtigen Loesungen

ins = sorted(glob.glob(os.path.join(d, "in_*.txt")))
examples = [p for p in ins if "example" in p]
for p in examples:
    out, _ = run(p)
    if validate:
        err = validate(open(p).read(), out.decode())
        if err:
            sys.exit(f"BEISPIEL FALSCH (validate): {err}")
        print("Beispiel OK (validate):", os.path.basename(p))
        continue
    exp = open(os.path.join(d, "out_" + os.path.basename(p)[3:]), "rb").read().replace(b"\r\n", b"\n")
    if out != exp:
        o, e = out.decode().split("\n"), exp.decode().split("\n")
        for i in range(max(len(o), len(e))):
            a, b = (o[i] if i < len(o) else "<fehlt>"), (e[i] if i < len(e) else "<fehlt>")
            if a != b:
                print(f"{os.path.basename(p)} Zeile {i + 1}: erwartet {b!r}, bekommen {a!r}")
                break
        sys.exit("BEISPIEL FALSCH")
    print("Beispiel OK:", os.path.basename(p))

outdir = os.path.join(d, "output")
os.makedirs(outdir, exist_ok=True)
files = []
for p in ins:
    if p in examples:
        continue
    out, sec = run(p)
    if validate:
        err = validate(open(p).read(), out.decode())
        if err:
            sys.exit(f"{os.path.basename(p)}: {err}")
    target = os.path.join(outdir, "out_" + os.path.basename(p)[3:])
    open(target, "wb").write(out)
    files.append(target)
    print(f"{os.path.basename(p)}: {sec:.2f}s")
print(f"{len(files)} Outputs in {outdir}")
