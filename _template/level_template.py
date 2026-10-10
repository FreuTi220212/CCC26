import sys
import threading

sys.setrecursionlimit(1_000_000)


def solve(data):
    # TODO
    return ""


# Nur bei Aufgaben mit mehreren gueltigen Loesungen: Pruefung per Simulation statt exaktem Vergleich.
# run.py benutzt validate(), sobald es existiert. Rueckgabe: None wenn ok, sonst Fehlertext.
# def validate(inp, out):
#     return None


def main():
    result = solve(sys.stdin.read())
    if result is None:
        return
    result = str(result)
    sys.stdout.write(result if result == "" or result.endswith("\n") else result + "\n")


if __name__ == "__main__":
    threading.stack_size(256 * 1024 * 1024)  # tiefe Rekursion moeglich (besser: iterativ)
    t = threading.Thread(target=main)
    t.start()
    t.join()
