def gcd_classic(a: int, b: int) -> int:
    if b > a:
        a, b = b, a
    while b:
        a, b = b, a % b
    return a


def bin_gcd_recursion(a: int, b: int) -> int:
    if a == b:
        return a
    if b > a:
        a, b = b, a
    # since a >= b, just return a, no matter a ?= 0
    if b == 0:
        return a
    if not (a & 1):
        if not (b & 1):
            return 2 * bin_gcd_recursion(a >> 1, b >> 1)  # a even, b even
        else:
            return bin_gcd_recursion(a >> 1, b)  # a even, b odd
    else:
        if not (b & 1):
            return bin_gcd_recursion(a, b >> 1)  # a odd, b even
        else:
            return bin_gcd_recursion(b, (a - b) >> 1)  # a odd, b odd


def bin_gcd_loop(a: int, b: int) -> int:
    if b > a:
        a, b = b, a
    if b == 0:
        return a
    adic = 0
    while not ((a | b) & 1):
        adic += 1
        a >>= 1
        b >>= 1
    while b:
        while not (a & 1):  # a even
            a >>= 1
        while not (b & 1):  # b even
            b >>= 1
        if b > a:
            a, b = b, a
        a, b = b, (a - b) >> 1
    return a * 2 ** adic


def gcd(a: int, b: int) -> int:
    return bin_gcd_loop(a, b)


def ext_gcd(a: int, b: int) -> tuple:
    if b == 0:
        return a, 1, 0
    else:
        gcd_t, x, y = ext_gcd(b, a % b)  # 递归直至余数等于0(需多递归一层用来判断)
        x, y = y, (x - (a // b) * y)  # 辗转相除法反向推导每层a、b的因子使得gcd(a,b)=ax+by成立
        return gcd_t, x, y


def gcd_reverse(r, x, y, alpha, beta):
    if x & 1 == 0 and y & 1 == 0:
        x, y = x >> 1, y >> 1
    else:
        x, y = (x + beta) >> 1, (y - alpha) >> 1
    return r >> 1, x, y


def bin_ext_gcd(a: int, b: int) -> tuple:
    ap, bp = a, b
    d = 1
    x1, y1, x2, y2 = 1, 0, 0, 1
    while ap & 1 == 0 and bp & 1 == 0:
        ap = ap >> 1
        bp = bp >> 1
        d = d << 1
    alpha = ap
    beta = bp

    while not (ap & 1):
        ap, x1, y1 = gcd_reverse(ap, x1, y1, alpha, beta)
    while not (bp & 1):
        bp, x2, y2 = gcd_reverse(bp, x2, y2, alpha, beta)
    if ap < bp:
        ap, x1, y1, bp, x2, y2 = bp, x2, y2, ap, x1, y1
    while bp:
        ap = ap - bp
        x1, y1 = x1 - x2, y1 - y2
        while ap and (not (ap & 1)):
            ap, x1, y1 = gcd_reverse(ap, x1, y1, alpha, beta)
        if ap < bp:
            ap, x1, y1, bp, x2, y2 = bp, x2, y2, ap, x1, y1
    if a < 0:
        x1, x2 = -x1, -x2
    if b < 0:
        y1, y2 = -y1, -y2
    return d * ap, x1, y1


def invert(a: int, modulo: int) -> int:
    return (ext_gcd(a, modulo)[1]) % modulo


if __name__ == '__main__':
    from random import randint
    from time import time

    r = []
    for i in range(200001):
        r.append(randint(2 ** 100, 2 ** 101 - 1))
    t1 = time()
    for i in range(200000):
        bin_gcd_loop(r[i], r[i + 1])
    print(time() - t1)
    t1 = time()
    for i in range(200000):
        gcd(r[i], r[i + 1])
    print(time() - t1)
