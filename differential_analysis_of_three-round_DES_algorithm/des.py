from cipher_function import *
from key_expansion import *

import logging

log_format = '%(message)s'
logging.basicConfig(level=logging.INFO, filename='runtime_log', filemode='w', format=log_format)

if __name__ == '__main__':
    message_pair = [
        [0x748502CD38451097, 0x3874756438451097],
        [0x486911026ACDFF31, 0x375BD31F6ACDFF31],
        [0x357418DA013FEC86, 0x12549847013FEC86]
    ]
    ciphertext_pair = [
        [0x03C70306D8A09F10, 0x78560A0960E6D4CB],
        [0x45FA285BE5ADC730, 0x134F7915AC253457],
        [0xD8A31B2F28BBC5CF, 0x0F317AC2B23CB944]
    ]
    for i in range(3):
        logging.info('第{}组'.format(i + 1))
        logging.info('明文对: {} {}'.format(hex(message_pair[i][0])[2:].zfill(16).upper(),
                                         hex(message_pair[i][1])[2:].zfill(16).upper()))
        logging.info('密文对: {} {}'.format(hex(ciphertext_pair[i][0])[2:].zfill(16).upper(),
                                         hex(ciphertext_pair[i][1])[2:].zfill(16).upper()))

    logging.info('\n\n第3轮S盒针对明文对左半部分的差分')
    B_table = []  # 3组S盒输入差分
    C_table = []  # 3组S盒输出差分
    for i in range(3):
        logging.info('  第{}组'.format(i + 1))
        # plain text pair
        message = message_pair[i]
        # cipher text pair (3 round_index)
        ciphertext = ciphertext_pair[i]
        # B_table = E(L3) ^ E(L3*) = [B1, ..., B8] 6 bits per unit
        L3 = ciphertext[0] >> 32
        L3_ast = ciphertext[1] >> 32
        Sin_diff = E(L3) ^ E(L3_ast)
        B_table.append([(Sin_diff >> (42 - 6 * i)) & 0b111111 for i in range(8)])
        # f(R2,k3) ^ f(R2_p,k3) = R3_diff ^ L0_diff
        R3_diff = (ciphertext[0] ^ ciphertext[1]) & 0xffffffff
        L0_diff = (message[0] ^ message[1]) >> 32
        Sout3_diff = inv_P(R3_diff ^ L0_diff)
        # C_table = inv_P(R3_diff ^ L0_diff) = [C1, ..., C8] 4 bits per unit
        C_table.append([(Sout3_diff >> (28 - 4 * i)) & 0b1111 for i in range(8)])
        logging.info(
            '    输入差分E(L3) XOR E(L3*)= {}'.format(' '.join([bin(B_table[i][j])[2:].zfill(6) for j in range(8)])))
        logging.info(
            '    输出差分P-1(R\'3 XOR L\'0)= {}'.format(' '.join([bin(C_table[i][j])[2:].zfill(4) for j in range(8)])))
    # print(B_table)
    # print(C_table)

    logging.info('\n\nf函数中明文扩展结果')
    A_table = []  # E(L3)
    A_ast_table = []
    for i in range(3):
        logging.info('第{}组'.format(i + 1))
        ciphertext = ciphertext_pair[i]
        L3 = ciphertext[0] >> 32
        L3_ast = ciphertext[1] >> 32
        A_table.append([(E(L3) >> (42 - 6 * j)) & 0b111111 for j in range(8)])
        A_ast_table.append([(E(L3_ast) >> (42 - 6 * j)) & 0b111111 for j in range(8)])
        logging.info('  E(L3) = {}'.format(' '.join([bin(A_table[i][j])[2:].zfill(6) for j in range(8)])))
        logging.info('  E(L3*)= {}'.format(' '.join([bin(A_table[i][j])[2:].zfill(6) for j in range(8)])))
    # print(A_table)

    J = []
    logging.info('\n\n计数器')
    for i in range(8):
        # 计数器
        Ji = [0] * 64
        # 遍历3个明密对
        for t in range(3):
            # 穷举 6bits 密钥
            for ji in range(2 ** 6):
                Ai = A_table[t][i]
                Bi = B_table[t][i]
                Ci = C_table[t][i]
                Xi = ji ^ Ai
                Yi = Bi ^ Xi
                Si_X = (S(Xi << (42 - 6 * i)) >> (28 - 4 * i)) & 0b1111
                Si_Y = (S(Yi << (42 - 6 * i)) >> (28 - 4 * i)) & 0b1111
                if Si_X ^ Si_Y == Ci:
                    Ji[ji] += 1
        J.append(Ji.index(3))
        logging.info('J{} = {}'.format(i, ''.join([str(Ji[i]) for i in range(64)])))
    logging.info(
        '\n\n第3轮加密可能的48比特密钥(计数器为3的对应6比特密钥级联)\n  {}'.format(' '.join([bin(J[i])[2:].zfill(6) for i in range(8)])))

    # 第3轮加密使用的 48 bits 轮密钥
    subkey_round3 = sum([J[i] << (42 - 6 * i) for i in range(8)])

    # 经过3次左移位的 56 bits 密钥 key_stream_round3
    # 注意在 PC-2 置换中丢弃了部分比特，因此在key_stream_round3中有如下未知比特位
    # [9, 18, 22, 25, 35, 38, 43, 54]范围(1-56)，这些位置暂时使用 0 占位填充
    key_stream_round3 = inv_pc_2(subkey_round3)
    logging.info('\n\n经过3次左移位变换得到的56比特密钥，未知位置暂时使用 0 占位填充\n未知比特位[9, 18, 22, 25, 35, 38, 43, 54]范围(1-56)\n  {}'.format(
        bin(key_stream_round3)[2:].zfill(56)))
    # print(bin(key_stream_round3)[2:].zfill(56))

    # 经过 PC-1 置换的 56 bits 密钥 key_stream_initial
    # 未知比特位[1, 13, 22 ,26, 30, 39, 42, 47]范围(1-56)，这些位置暂时使用 0 占位填充
    key_stream_initial = inv_shift_left(key_stream_round3, 3)
    logging.info('\n\n种子密钥经过PC-1置换得到的56比特密钥，未知位置暂时使用 0 占位填充\n未知比特位[1, 13, 22 ,26, 30, 39, 42, 47]范围(1-56)\n  {}'.format(
        bin(key_stream_initial)[2:].zfill(56)))

    unknown_pos = [1, 13, 22, 26, 30, 39, 42, 47]  # 范围(1-56)

    seed_key_56bits = 0
    # 穷举8个未知比特位还原 56 bits 密钥
    for i in range(2 ** 8):
        key_stream_initial_str = list(bin(key_stream_initial)[2:].zfill(56))
        for pos in range(8):
            key_stream_initial_str[unknown_pos[pos] - 1] = str((i >> pos) & 1)
        key_stream_initial_possible = int(''.join(key_stream_initial_str), base=2)
        # print(hex(key_stream_initial_possible))
        # 带入 6 个明密文对验证
        test_pass = 0
        for pair in range(3):
            for j in range(2):
                message = message_pair[pair][j]
                ciphertext = None
                for round in range(3):
                    round_key = get_round_key_from_initial_stream(key_stream_initial_possible, round + 1)
                    ciphertext = encrypt_round(message, round_key)
                    message = ciphertext
                if ciphertext == ciphertext_pair[pair][j]:
                    test_pass += 1
        # 通过所有明密对测试，得到正确密钥
        if test_pass == 6:
            seed_key_56bits = key_stream_initial_possible
            break
    logging.info('\n\n穷举得到种子密钥经过PC-1置换得到的56比特密钥\n  {}'.format(bin(seed_key_56bits)[2:].zfill(56)))

    seed_key_56bits_list = [(seed_key_56bits >> (55 - i)) & 1 for i in range(56)]
    seed_key = inv_pc_1(seed_key_56bits)
    logging.info('\n\n添加校验位得到种子密钥\n  bin: {}\n  hex: {}'.format(bin(seed_key)[2:].zfill(64),
                                                            hex(seed_key)[2:].upper().zfill(16)))
    print(hex(seed_key)[2:].upper())
