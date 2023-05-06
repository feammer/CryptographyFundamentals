# -*- coding:utf-8 -*-
import gmpy2 as gmp
from random import randint


def primality_test(test_num, n=6):
    """
    素性测试
    :param test_num: 测试数
    :param n: 测试轮数
    :return: 是否为素数
    """
    return gmp.is_prime(test_num, n)


def get_random_prime(nbits):
    """
    获取一个安全素数
    :param nbits: 素数比特长度
    :return: 安全素数
    """
    r = 0
    while not ((r & 1) and primality_test(r) and primality_test(2 * r + 1)):
        r = randint(2 ** (nbits - 2), 2 ** (nbits - 1) - 1)
    return 2 * r + 1


if __name__ == '__main__':
    print(get_random_prime(5))
