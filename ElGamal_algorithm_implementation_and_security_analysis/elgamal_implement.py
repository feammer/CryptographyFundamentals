# -*- coding:utf-8 -*-
import os
from time import time
from random import randint
import matplotlib.pyplot as plt

try:
    from primality_test_gmpy2 import get_random_prime
    from gmpy2 import ceil
    from gmpy2 import powmod as quick_mod
    from gmpy2 import gcdext as ext_gcd
except ModuleNotFoundError:
    from primality_test import get_random_prime, quick_mod
    from math import ceil
    # from custom_gcd import ext_gcd


# 判断 k 是否为 p 的原根，这里要求 p 是安全素数
def is_primitive_root(k, p) -> bool:
    a = (p - 1) // 2
    if quick_mod(k, 2, p) == 1:
        return False
    elif quick_mod(k, a, p) == 1:
        return False
    else:
        return True
    # r = 1
    # for _ in range((base-1)//2):
    #     r = (r * element) % base
    #     if r == 1:
    #         return False
    # if r == base - 1:  # a^{(\phi(p)-1)/2} equiv -1 mod p -> ord(a)=p-1
    #     return True
    # else:
    #     return False


class ElGamal:
    def __init__(self, key_info=None, nbits=None, only_encrypt=None):
        if key_info is not None:  # 指定密钥信息
            for element in ['p', 'alpha']:
                if key_info.get(element) is None:
                    print('incomplete key info, require p or alpha')
                    return
            self.p = key_info['p']
            self.alpha = key_info['alpha']
            if only_encrypt is None:  # 非仅加密，要求完整密钥信息
                if key_info.get('a') is None:
                    print('incomplete key info, require a')
                    return
                self.a = key_info['a']
                if key_info.get('beta') is not None:
                    self.beta = key_info['beta']
                else:
                    self.beta = quick_mod(self.alpha, self.a, self.p)
            else:  # 仅加密，不要求提供私钥信息
                self.a = None
                if key_info.get('beta') is None:
                    print('incomplete key info, require beta')
                    return
                self.beta = key_info['beta']
        elif nbits is not None:  # 指定密钥长度，随机生成密钥信息
            self.p = get_random_prime(nbits)
            self.alpha = randint(2, self.p - 1)
            while not is_primitive_root(self.alpha, self.p):
                self.alpha = randint(2, self.p - 1)
            self.a = randint((self.p - 1) // 2, self.p - 1)
            self.beta = quick_mod(self.alpha, self.a, self.p)
        else:
            print('no key info specified')
            pass

    def encrypt(self, message) -> tuple:
        x = randint(2, self.p - 1)
        y1 = quick_mod(self.alpha, x, self.p)
        y2 = message * quick_mod(self.beta, x, self.p) % self.p
        return y1, y2

    def decrypt(self, ciphertext: tuple):
        if self.a is None:
            print('no private key')
            return None
        if len(ciphertext) != 2:
            print('incomplete ciphertext pair')
            return None
        y1 = ciphertext[0]
        y2 = ciphertext[1]
        # reference: ext_gcd(a,b) -> (gcd(a,b), s, t) which satisfies as+bt=gcd(a,b)
        tmp = ext_gcd(quick_mod(y1, self.a, self.p), self.p)[1]
        message = y2 * tmp % self.p
        return message

    def show_key_info(self):
        public_key = {'p': self.p, 'alpha': self.alpha, 'beta': self.beta}
        private_key = {'p': self.p, 'alpha': self.alpha, 'a': self.a, 'beta': self.beta}
        return {'public_key': public_key, 'private_key': private_key}


if __name__ == '__main__':
    # e = ElGamal(key_info={'p': 2579, 'alpha': 2, 'a': 765, 'beta': 949})
    # 128bits 明文信息加解密
    e = ElGamal(nbits=129)
    r = randint(2 ** 128, 2 ** 129 - 1)
    c = e.encrypt(r)
    m = e.decrypt(c)
    print(e.show_key_info())
    print('ciphertext pair: {}'.format({'y1': hex(c[0]), 'y2': hex(c[1])}))
    print('message recovered from ciphertext: {}'.format(hex(m)))
    # 文本文件加密
    e = ElGamal(nbits=128)
    print(e.show_key_info())
    p = e.p
    try:
        os.mkdir('message_file')
        os.mkdir('cipher_file')
    except FileExistsError:
        print('folder exists')
    encrypt_time = 0
    decrypt_time = 0
    entire_time = time()
    for file_name in os.listdir('./OANC_data'):
        # 加密
        with open('./OANC_data/' + file_name, 'rb') as plaintext:
            plain_data = plaintext.read()
            plain_data_int = int.from_bytes(plain_data, byteorder='little', signed=False)
        with open('./cipher_file/' + file_name, 'w') as f:
            while plain_data_int != 0:
                plain_data_block = plain_data_int % p
                plain_data_int //= p
                t = time()
                cipher_data = e.encrypt(plain_data_block)
                encrypt_time += time() - t
                f.write(str(cipher_data[0]) + ' ' + str(cipher_data[1]) + '\n')
        # 解密
        plain_data_int = 0
        k = 0
        with open('./cipher_file/' + file_name, 'r') as f:
            cipher_data = f.readline()[:-1].split(' ')
            while cipher_data != ['']:
                y1, y2 = int(cipher_data[0]), int(cipher_data[1])
                t = time()
                plain_data_int += e.decrypt((y1, y2)) * p ** k
                decrypt_time += time() - t
                k += 1
                cipher_data = f.readline()[:-1].split(' ')
        with open('./message_file/' + file_name, 'wb') as f:
            f.write(
                int(plain_data_int).to_bytes(length=int(ceil(len(hex(plain_data_int)[2:]) / 2)), byteorder='little'))
    entire_time = time() - entire_time
    with open('./assets/crypto_time.txt', 'w') as f:
        f.write('{} {} {}'.format(encrypt_time, decrypt_time, entire_time))
    print('encrypt time: {}\ndecrypt time: {}\nentire time: {}'.
          format(encrypt_time, decrypt_time, entire_time))
    print('encrypt speed: {} KB/s\ndecrypt speed: {} KB/s'
          .format(27369401 / 1024 / encrypt_time, 27369401 / 1024 / decrypt_time))
    # 可视化
    file_size_set = []
    for file_name in os.listdir('./OANC_data'):
        with open('./OANC_data/' + file_name, 'rb') as plaintext:
            file_size_set.append(len(plaintext.read()) / 1024)
    plt.scatter(range(len(file_size_set)), file_size_set,
                color='#70a1ff', sizes=[1 for _ in range(len(file_size_set))])
    plt.axhline(y=sum(file_size_set) / len(file_size_set), label='average file size',
                xmin=0, xmax=len(file_size_set), linestyle='--', color='#ff6348')
    plt.title('file size distribution')
    plt.ylim([0, max(file_size_set) + 1])
    plt.ylabel('size(KB)')
    plt.legend()
    plt.savefig('./assets/file_size_distribution.svg', format='svg')
    plt.show()

    with open('./assets/crypto_time.txt', 'r') as f:
        t = f.read().split(' ')
        entire_time, decrypt_time, entire_time = [float(e) for e in t]
    plt.pie(x=[encrypt_time, decrypt_time, entire_time - encrypt_time - decrypt_time],
            labels=[str(int(encrypt_time * 100) // 100) + ' s',
                    str(int(decrypt_time * 100) // 100) + ' s',
                    str(int((entire_time - encrypt_time - decrypt_time) * 100) // 100) + ' s'],
            colors=['#7bed9f', '#70a1ff', '#eccc68'], autopct='%.1f%%')
    plt.title('ElGamal speed test')
    plt.legend(['encrypt', 'decrypt', 'file IO and others'], loc='lower left', bbox_to_anchor=(-0.3, 0))
    plt.savefig('./assets/crypto_time.svg', format='svg')
    plt.show()
