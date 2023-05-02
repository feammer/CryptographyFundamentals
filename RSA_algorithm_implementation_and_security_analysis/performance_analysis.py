import random

import gmpy2
import primality_test
import primality_test_gmpy2
import custom_gcd
import rsa_implement

from time import time
import matplotlib.pyplot as plt

if __name__ == '__main__':
    # ============================================================
    # 素数生成速度测试
    # 60秒
    test_num = 200  # 测试次数
    prime_generate_speed_custom = []
    t0 = time()
    for scale in [10, 20, 30, 40]:  # 比特规模
        t1 = time()
        for i in range(test_num):
            primality_test.get_random_prime(nbits=scale)
        prime_generate_speed_custom.append(time() - t1)
    prime_generate_speed_gmpy2 = []
    for scale in [10, 20, 30, 40, 80]:  # 比特规模
        t1 = time()
        for i in range(test_num):
            primality_test_gmpy2.get_random_prime(nbits=scale)
        prime_generate_speed_gmpy2.append(time() - t1)
    print(time() - t0)
    plt.plot([10, 20, 30, 40], prime_generate_speed_custom, marker='o', label='custom function')
    plt.plot([10, 20, 30, 40, 80], prime_generate_speed_gmpy2, marker='o', label='gmpy2  function')
    plt.title('prime number generate speed')
    plt.xlabel('prime number bit length')
    plt.ylabel('seconds per {} generations'.format(test_num))
    plt.legend()
    plt.savefig('./assets/prime_generate_speed.svg', format='svg')
    plt.show()

    # ============================================================
    # GCD函数速度测试
    # 420秒
    test_num = 10000  # 测试次数
    scale_set = [20, 40, 60, 80, 100]  # 比特规模
    gcd_classic_speed = []
    bin_gcd_recursion_speed = []
    bin_gcd_loop_speed = []
    gcd_gmpy2_speed = []
    t0 = time()
    for scale in scale_set:
        num_set = []
        for _ in range(test_num):
            num_set.append(
                [primality_test_gmpy2.get_random_prime(scale - 1), primality_test_gmpy2.get_random_prime(scale)])
        t1 = time()
        for pair in num_set:
            custom_gcd.gcd_classic(pair[0], pair[1])
        gcd_classic_speed.append((time() - t1))
        t1 = time()
        for pair in num_set:
            custom_gcd.bin_gcd_recursion(pair[0], pair[1])
        bin_gcd_recursion_speed.append(time() - t1)
        t1 = time()
        for pair in num_set:
            custom_gcd.bin_gcd_loop(pair[0], pair[1])
        bin_gcd_loop_speed.append(time() - t1)
        t1 = time()
        for pair in num_set:
            gmpy2.gcd(pair[0], pair[1])
        gcd_gmpy2_speed.append(time() - t1)
    print(time() - t0)
    plt.plot(scale_set, gcd_classic_speed, marker='o', label='Euclid Algorithm')
    plt.plot(scale_set, bin_gcd_recursion_speed, marker='o', label='bin Euclid recursion')
    plt.plot(scale_set, bin_gcd_loop_speed, marker='o', label='bin Euclid loop')
    plt.plot(scale_set, gcd_gmpy2_speed, marker='o', label='gcd from gmpy2')
    plt.title('gcd algorithm speed')
    plt.xlabel('number bit length')
    plt.ylabel('seconds per {} operations'.format(test_num))
    plt.legend()
    plt.savefig('./assets/gcd_algorithm_speed.svg', format='svg')
    plt.show()

    # ============================================================
    # 求逆函数速度测试
    # 20秒
    test_num = 1000  # 测试次数
    invert_custom_speed = []
    invert_custom_bin_speed = []
    invert_gmpy2_speed = []
    scale_set = [10, 20, 40, 80]
    t0 = time()
    for scale in scale_set:
        num_set = []
        for _ in range(test_num):
            num_set.append(
                [primality_test_gmpy2.get_random_prime(scale - 1), primality_test_gmpy2.get_random_prime(scale)])
        t1 = time()
        for pair in num_set:
            custom_gcd.ext_gcd(pair[0], pair[1])[1] % pair[1]
        invert_custom_speed.append((time() - t1))
        for pair in num_set:
            custom_gcd.bin_ext_gcd(pair[0], pair[1])[1] % pair[1]
        invert_custom_bin_speed.append((time() - t1))
        t1 = time()
        for pair in num_set:
            gmpy2.invert(pair[0], pair[1])
        invert_gmpy2_speed.append((time() - t1))
    print(time() - t0)
    plt.plot(scale_set, invert_custom_speed, marker='o', label='custom function')
    plt.plot(scale_set, invert_custom_bin_speed, marker='o', label='custom bin function')
    plt.plot(scale_set, invert_gmpy2_speed, marker='o', label='gmpy2  function')
    plt.title('invert function speed')
    plt.xlabel('number bit length')
    plt.ylabel('seconds per {} generations'.format(test_num))
    plt.legend()
    plt.savefig('./assets/invert_function_speed.svg', format='svg')
    plt.show()

    # ============================================================
    # RSA加密速度测试
    # 310秒
    # rsa_encrypt_speed = [0.11600041389465332, 0.49390578269958496, 2.854013681411743, 19.327926635742188, 119.15584468841553]
    scale_set = [64, 128, 256, 512, 1024]
    repeat_num = 10000
    rsa_encrypt_speed = []
    t0 = time()
    for scale in scale_set:
        rsa_instance = rsa_implement.RSA(nbits=scale)
        message = random.randint(2 ** (scale - 1), 2 ** scale - 1)
        t1 = time()
        for _ in range(repeat_num):
            rsa_instance.encrypt(message)
        rsa_encrypt_speed.append(time() - t1)
    print(time() - t0)
    plt.barh([i for i in range(1, len(scale_set) + 1)], rsa_encrypt_speed,
             tick_label=[str(scale) for scale in scale_set])
    plt.title('RSA encrypt speed')
    plt.ylabel('nbits')
    plt.xlabel('seconds per {} encryption'.format(repeat_num))
    plt.savefig('./assets/RSA_encrypt_speed.svg', format='svg')
    plt.show()

    # ============================================================
    # 解密速度测试
    # 270秒
    scale_set = [64, 128, 256, 512, 1024]
    repeat_num = 10000
    rsa_decrypt_speed = []
    rsa_decrypt_CRT_speed = []
    t0 = time()
    for nbits in scale_set:
        rsa_instance = rsa_implement.RSA(nbits=nbits)
        n, p, q, e, d = rsa_instance.n, rsa_instance.p, rsa_instance.q, rsa_instance.e, rsa_instance.d
        ciphertext = random.randint(2 ** (nbits - 1), 2 ** nbits - 1)
        t1 = time()
        for _ in range(repeat_num):
            rsa_instance.decrypt(ciphertext)
        rsa_decrypt_speed.append(time() - t1)
        t1 = time()
        for _ in range(repeat_num):
            rsa_implement.decrypt_CRT(ciphertext, d, p, q)
        rsa_decrypt_CRT_speed.append(time() - t1)
    print(time() - t0)
    plt.barh([i for i in range(1, len(scale_set) + 1)], rsa_decrypt_speed,
             tick_label=[str(scale) for scale in scale_set], label='normal decrypt')
    plt.barh([i for i in range(1, len(scale_set) + 1)],
             [(rsa_decrypt_speed[i] - rsa_decrypt_CRT_speed[i]) for i in range(len(scale_set))],
             tick_label=[str(scale) for scale in scale_set], label='decrypt using CRT')
    plt.title('RSA decrypt speed')
    plt.ylabel('nbits')
    plt.xlabel('seconds per {} decryption'.format(repeat_num))
    plt.legend()
    plt.savefig('./assets/RSA_decrypt_speed.svg', format='svg')
    plt.show()
    pass
