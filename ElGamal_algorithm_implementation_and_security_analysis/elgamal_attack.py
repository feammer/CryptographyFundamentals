# -*- coding:utf-8 -*-
from gmpy2 import sqrt, ceil, powmod


def shanks(key_info):
    p = key_info['p']
    alpha = key_info['alpha']
    beta = key_info['beta']
    m = int(ceil(sqrt(p - 1)))
    l1 = []
    alpha_m = powmod(alpha, m, p)  # 预计算，加速
    for j in range(m):
        l1.append([powmod(alpha_m, j, p), j])  # 为方便使用键值查找，这里反转两个值的位置
    dict_l1 = dict(l1)
    pos_i = 0
    pos_j = 0
    for i in range(m):
        val = powmod(alpha, -i, p) * beta % p
        pos_j = dict_l1.get(val)
        if pos_j is not None:
            pos_i = i
            break
    a = (m * pos_j + pos_i) % (p - 1)
    return a


def sieve_of_factors(n):
    """
    数域筛法分解质因数
    :param n: 待分解的正整数
    :return: 分解出的质因数列表
    """
    factors = {}
    d = 2
    while d * d <= n:
        while n % d == 0:
            factors.update({d: factors.get(d, 0) + 1})
            n //= d
        d += 1
    if n > 1:
        factors.update({n: 1})
    return factors


def CRT(nums, mods):
    """
    使用中国剩余定理（CRT）解决同余式组。
    nums：各个同余式中x的系数。
    mods：各个同余式中模数。
    返回同余方程组的唯一解。
    """
    # 计算模数之积，用于后面除法的计算。
    prod = 1
    for mod in mods:
        prod *= mod
    result = 0
    for num, mod in zip(nums, mods):
        # 计算 m 和 Mi
        m = prod // mod
        Mi = pow(m, -1, mod)
        # 计算结果
        result += num * m * Mi
    return result % prod


def pohlig_hellman(key_info):
    p = key_info['p']
    n = p - 1
    fac_n = sieve_of_factors(n)
    alpha = key_info['alpha']
    beta = key_info['beta']
    num_CRT = []
    # P-H 算法核心
    for q in list(fac_n.keys()):
        c = fac_n.get(q)
        gamma = powmod(alpha, n // q, p)  # gamma = {\alpha}^{n/q}
        beta_j = beta  # initial \beta_0 = \beta
        a_mod_qc = 0
        for j in range(c):
            pow_value = n // q ** (j + 1)
            target = powmod(beta_j, pow_value, p)  # target = {\beta}_j^{n/q^{j+1}}
            a_j = 0
            while powmod(gamma, a_j, p) != target:
                a_j += 1
            a_mod_qc += a_j * q ** j
            beta_j = beta_j * powmod(alpha, -a_j * q ** j, p) % p
        num_CRT.append(a_mod_qc)
    # CRT解同余式组
    modulo_CRT = list(fac_n.keys())
    return CRT(num_CRT, modulo_CRT)


if __name__ == '__main__':
    # Shanks算法验证
    p = 809
    alpha = 3
    beta = 525
    a = shanks({'p': p, 'alpha': alpha, 'beta': beta})  # a = 309
    print('Shanks算法验证')
    print({'p': p, 'alpha': alpha, 'beta': beta})
    print('a: {}'.format(a))
    print('alpha^a: {}'.format(powmod(alpha, a, p)))
    # Pohlig-Hellman算法验证
    p = 813431819900321539
    alpha = 3
    beta = 233663611284485306
    a = pohlig_hellman({'p': p, 'alpha': alpha, 'beta': beta})
    print('Pohlig-Hellman算法验证')
    print({'p': p, 'alpha': alpha, 'beta': beta})
    print('a: {}'.format(a))
    print('alpha^a: {}'.format(powmod(alpha, a, p)))
