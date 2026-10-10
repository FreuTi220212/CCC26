import sys

BEDROCK, MINABLE = "#", ":"


def parse(data):
    t = data.split()
    n = int(t[0])
    return [(int(t[1 + 2 * i]), int(t[2 + 2 * i])) for i in range(n)]


def render(width, height):
    """Asteroid: minierbares Rechteck width x height, ringsum eine Schicht Grundgestein."""
    border = BEDROCK * (width + 2)
    row = BEDROCK + MINABLE * width + BEDROCK
    return [border] + [row] * height + [border]


def solve(data):
    # Beispiel-Output: nach JEDEM Asteroiden eine Leerzeile (auch nach dem letzten)
    return "".join("\n".join(render(w, h)) + "\n\n" for w, h in parse(data))


if __name__ == "__main__":
    sys.stdout.write(solve(sys.stdin.read()))
