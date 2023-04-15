"""
密钥扩展算法相关函数
"""


def pc_1(key: int) -> int:
    """
    PC-1置换，这里丢掉了初始密钥的校验位
    :param key: 64 bits
    :return: 56 bits
    """
    C0_table = [57, 49, 41, 33, 25, 17, 9,
                1, 58, 50, 42, 34, 26, 18,
                10, 2, 59, 51, 43, 35, 27,
                19, 11, 3, 60, 52, 44, 36]
    D0_table = [63, 55, 47, 39, 31, 23, 15,
                7, 62, 54, 46, 38, 30, 22,
                14, 6, 61, 53, 45, 37, 29,
                21, 13, 5, 28, 20, 12, 4]
    C0 = 0
    D0 = 0
    for c in C0_table:
        C0 = C0 << 1
        C0 += (key & (0b1 << (64 - c))) >> (64 - c)
    for d in D0_table:
        D0 = D0 << 1
        D0 += (key & (0b1 << (64 - d))) >> (64 - d)
    return (C0 << 28) + D0


def inv_pc_1(key_stream_initial: int) -> int:
    """
    PC-1置换的逆函数，对于丢弃的位置使用 0 占位
    根据 PC-1 置换表得到丢弃的位置为校验位 [8, 16, 24, 32, 40, 48, 56, 64]范围(1-64)
    :param key_stream_initial: 56 bits
    :return: 64 bits
    """
    key_stream_initial = bin(key_stream_initial)[2:].zfill(56)
    seed_key_list = [0] * 64
    pc_1_table = [57, 49, 41, 33, 25, 17, 9,
                  1, 58, 50, 42, 34, 26, 18,
                  10, 2, 59, 51, 43, 35, 27,
                  19, 11, 3, 60, 52, 44, 36,
                  63, 55, 47, 39, 31, 23, 15,
                  7, 62, 54, 46, 38, 30, 22,
                  14, 6, 61, 53, 45, 37, 29,
                  21, 13, 5, 28, 20, 12, 4]
    for i in range(56):
        seed_key_list[pc_1_table[i] - 1] = int(key_stream_initial[i], base=2)
    # 校验位恢复
    for i in range(8):
        seed_key_list[8 * (i + 1) - 1] = (sum(seed_key_list[8 * i:8 * (i + 1) - 1]) + 1) % 2
    seed_key = sum([seed_key_list[i] << (63 - i) for i in range(64)])
    return seed_key


def shift_left(key: int, round_index: int) -> int:
    """
    左循环移位
    :param key: 56 bits
    :param round_index: 1-16
    :return: 56 bits
    """
    C0 = key >> 28
    D0 = key & 0xfffffff
    shift_table = [1, 1, 2, 2, 2, 2, 2, 2, 1, 2, 2, 2, 2, 2, 2, 1]
    shift_cnt = sum(shift_table[:round_index])
    C0 = ((C0 << shift_cnt) & 0xfffffff) + ((C0 << shift_cnt) >> 28)
    D0 = ((D0 << shift_cnt) & 0xfffffff) + ((D0 << shift_cnt) >> 28)
    return (C0 << 28) + D0


"""
在左移位变换中，密钥分为左28位和右28位分别进行移位，最后拼接成56位
因此在第3轮密钥中被 PC-2 置换丢弃的比特位 [9, 18, 22, 25, 35, 38, 43, 54]范围(1-56) 的初始位置是
[1, 13, 22 ,26, 30, 39, 42, 47]范围(1-56)
"""


def inv_shift_left(key: int, round_index: int) -> int:
    """
    右循环移位
    :param key: 56 bits
    :param round_index: 1-16
    :return: 56 bits
    """
    C0 = key >> 28
    D0 = key & 0xfffffff
    shift_table = [1, 1, 2, 2, 2, 2, 2, 2, 1, 2, 2, 2, 2, 2, 2, 1]
    shift_cnt = sum(shift_table[:round_index])
    C0 = (C0 >> shift_cnt) + ((C0 & ((1 << shift_cnt) - 1)) << (28 - shift_cnt))
    D0 = (D0 >> shift_cnt) + ((D0 & ((1 << shift_cnt) - 1)) << (28 - shift_cnt))
    return (C0 << 28) + D0


def pc_2(key: int) -> int:
    """
    PC-2置换
    :param key: 56 bits
    :return: 48 bits 轮密钥
    """
    a1_table = [14, 17, 11, 24, 1, 5,
                3, 28, 15, 6, 21, 10,
                23, 19, 12, 4, 26, 8,
                16, 7, 27, 20, 13, 2]
    b1_table = [41, 52, 31, 37, 47, 55,
                30, 40, 51, 45, 33, 48,
                44, 49, 39, 56, 34, 53,
                46, 42, 50, 36, 29, 32]
    a1 = 0
    b1 = 0
    for a in a1_table:
        a1 = a1 << 1
        a1 += (key & (0b1 << (56 - a))) >> (56 - a)
    for b in b1_table:
        b1 = b1 << 1
        b1 += (key & (0b1 << (56 - b))) >> (56 - b)
    return (a1 << 24) + b1


def inv_pc_2(round_key: int) -> int:
    """
    PC-2置换的逆函数，对于丢弃的位置使用 0 占位
    根据 PC-2 置换表得到丢弃的位置为 [9, 18, 22, 25, 35, 38, 43, 54]范围(1-56)
    :param round_key: 48 bits
    :return: 56 bits
    """
    round_key = bin(round_key)[2:].zfill(48)
    origin_key = ['0'] * 56
    pc_2_table = [14, 17, 11, 24, 1, 5,
                  3, 28, 15, 6, 21, 10,
                  23, 19, 12, 4, 26, 8,
                  16, 7, 27, 20, 13, 2,
                  41, 52, 31, 37, 47, 55,
                  30, 40, 51, 45, 33, 48,
                  44, 49, 39, 56, 34, 53,
                  46, 42, 50, 36, 29, 32]
    for i in range(48):
        origin_key[pc_2_table[i] - 1] = round_key[i]
    return int(''.join(origin_key), base=2)


def get_round_key(seed_key: int, round_index: int) -> int:
    """
    获取轮子密钥
    :param seed_key: 64 bits seed key
    :param round_index: 1-16
    :return: 48 bits round key
    """
    return pc_2(shift_left(pc_1(seed_key), round_index))


def get_round_key_from_initial_stream(key_stream_initial: int, round_index: int) -> int:
    """
    获取轮子密钥
    :param key_stream_initial: 经过 PC-1 置换的 56 bits 密钥
    :param round_index: 1-16
    :return: 48 bits round key
    """
    return pc_2(shift_left(key_stream_initial, round_index))


if __name__ == '__main__':
    pass
