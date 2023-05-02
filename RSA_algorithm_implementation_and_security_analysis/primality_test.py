# -*- coding:utf-8 -*-
from random import randint
from time import time


# 使用二进指数的快速乘算法
def _quick_multi_with_mod(a, b, modulo):
    a %= modulo
    b %= modulo
    ret = 0
    while b:
        if b & 1:
            ret = (a + ret) % modulo
        a = (a + a) % modulo
        b = b >> 1
    return ret


# 使用二进制数的快速幂算法
def quick_mod(base, power, modulo):
    base %= modulo
    ret = 1
    while power:
        if power & 1:
            ret = _quick_multi_with_mod(base, ret, modulo)
        base = _quick_multi_with_mod(base, base, modulo)
        power = power >> 1
    return ret


# True if test_num is probably prime, False if test_num is definitely composite
def miller_rabin(test_num: int) -> bool:
    if test_num < 2:
        return False
    m = test_num - 1
    k = 0
    while not (m & 1):
        k = k + 1
        m = m >> 1
    # factor test_num = m * 2^k, m is odd
    n = test_num
    b = quick_mod(randint(1, n - 1), m, n)
    if b == 1:
        return True
    for _ in range(k):
        if b == n - 1:
            return True
        else:
            b = quick_mod(b, 2, n)
    return False


def primality_test(test_num, n=6):
    """
    素性测试
    :param test_num: 测试数
    :param n: 测试轮数
    :return: 是否为素数
    """
    for _ in range(n):
        if not miller_rabin(test_num):
            return False
    return True


def get_random_prime(nbits):
    """
    获取一个安全素数
    :param nbits: 素数比特长度
    :return: 安全素数
    """
    r = 0
    while not ((r & 1) and primality_test(r) and primality_test(2 * r + 1)):
        r = randint(2 ** (nbits - 1), 2 ** nbits - 1)
    return 2 * r + 1


if __name__ == '__main__':
    t1 = time()
    for i in range(10):
        get_random_prime(50)
    print(time() - t1)
