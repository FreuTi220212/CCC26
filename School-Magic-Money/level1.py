import sys


def parse(data):
    t = data.split()
    n, c = int(t[0]), int(t[1])
    return [[int(x) for x in t[2 + i * c:2 + (i + 1) * c]] for i in range(n)]


def smallest_not_single_coin(coins):
    have = set(coins)
    x = 1
    while x in have:
        x += 1
    return x


def solve(data):
    return "\n".join(str(smallest_not_single_coin(cur)) for cur in parse(data))


if __name__ == "__main__":
    sys.stdout.write(solve(sys.stdin.read()) + "\n")
