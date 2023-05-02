# -*- coding:utf-8 -*-

try:
    from primality_test_gmpy2 import *
    from gmpy2 import gcd, invert
    from gmpy2 import powmod as quick_mod
    from gmpy2 import gcdext as ext_gcd
except ModuleNotFoundError:
    from primality_test import *
    from custom_gcd import gcd, invert, ext_gcd


# 使用中国剩余定理加速的解密
def decrypt_CRT(ciphertext, d, p, q):
    dp = d % (p - 1)
    dq = d % (q - 1)
    m1 = quick_mod(ciphertext, dp, p)
    m2 = quick_mod(ciphertext, dq, q)
    q_inv = invert(q, p)
    h = q_inv * (m1 - m2) % p
    return (m2 + h * q) % (p * q)


class RSA:
    def __init__(self, key_pair=None, nbits=None, only_encrypt=None):
        """
        RSA初始化函数，包括参数指定和生成
        :param key_pair: 密钥信息，优先级高于nbits
        :param nbits: 指定密钥长度，随机生成密钥信息
        :param only_encrypt: 仅加密模式，只需要提供公钥信息
        """
        if only_encrypt is not None:
            self.only_encrypt = False
            self.n = key_pair['n']
            self.e = key_pair['e']
        else:
            self.nbits = 0
            self.only_encrypt = False
            if not (key_pair is None):  # 指定密钥对信息
                # 必须包含的密钥对信息，否则无效
                for i in ['p', 'q', 'e']:
                    if key_pair.get(i) is None:
                        return
                self.p = key_pair['p']
                self.q = key_pair['q']
                self.nbits = max(len(bin(self.p)[2:]), len(bin(self.q)[2:]))
                if not (key_pair.get('n') is None):
                    self.n = key_pair['n']
                else:
                    self.n = self.p * self.q
                self.e = key_pair['e']
                if not (key_pair.get('d') is None):
                    self.d = key_pair['d']
                else:
                    self.d = invert(self.e, (self.p - 1) * (self.q - 1))
                self.only_encrypt = True

            elif not (nbits is None):  # 指定密钥长度，随机生成密钥对
                if nbits < 2:
                    return
                self.nbits = nbits
                self.p = get_random_prime(nbits=nbits)
                self.q = get_random_prime(nbits=nbits)
                self.n = self.p * self.q
                phi_n = (self.p - 1) * (self.q - 1)
                self.e = 0
                while gcd(phi_n, self.e) != 1:
                    self.e = randint(2 ** (len(bin(phi_n - 1)[2:]) - 1), phi_n - 1)
                self.d = invert(self.e, phi_n)
                self.only_encrypt = True

            else:
                print('No parameters specified')

    def encrypt(self, message):
        """
        RSA加密函数
        :param message: int/mpz
        :return: int/mpz
        """
        return quick_mod(message, self.e, self.n)

    def decrypt(self, ciphertext):
        if not self.only_encrypt:
            print('only encrypt mode\nn:{} e:{}'.format(self.n, self.e))
            return None
        return quick_mod(ciphertext, self.d, self.n)

    def key_pair_info(self):
        if not self.only_encrypt:
            print('only encrypt mode\nn:{} e:{}'.format(self.n, self.e))
        else:
            public_key = {'n': self.n, 'e': self.e}
            private_key = {'n': self.n, 'e': self.e, 'd': self.d, 'p': self.p, 'q': self.q}
            return {'public_key': public_key, 'private_key': private_key}


if __name__ == '__main__':
    # 公共模攻击验证
    n = 114381625757888867669235779976146612010218296721242362562561842935706935245733897830597123563958705058989075147599290026879543541
    e1 = 9007
    e2 = 65537
    m = 19050321180920251905182209030519
    g, s, t = ext_gcd(e1, e2)
    ins1 = RSA(only_encrypt=True, key_pair={'n': n, 'e': e1})
    c1 = ins1.encrypt(m)
    ins2 = RSA(only_encrypt=True, key_pair={'n': n, 'e': e2})
    c2 = ins2.encrypt(m)
    print(quick_mod(c1, s, n) * quick_mod(c2, t, n) % n)
    # 不动点攻击验证
    ins3 = RSA(only_encrypt=True, key_pair={'n': 2773, 'e': 17})
    print(ins3.encrypt(2302))
    # ins
    ins4 = RSA(key_pair={'p': 1187, 'q': 2039, 'e': 2193835, 'd': 547019})
