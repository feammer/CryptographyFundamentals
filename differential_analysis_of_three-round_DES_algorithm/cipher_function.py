import logging

log_format = '%(message)s'
logging.basicConfig(level=logging.INFO, filename='runtime_log', filemode='w', format=log_format)


def E(message: int) -> int:
    """
    明文扩展函数
    :param message: 32bits int
    :return: 48 bits int 扩展明文
    """
    e_table = [32, 1, 2, 3, 4, 5,
               4, 5, 6, 7, 8, 9,
               8, 9, 10, 11, 12, 13,
               12, 13, 14, 15, 16, 17,
               16, 17, 18, 19, 20, 21,
               20, 21, 22, 23, 24, 25,
               24, 25, 26, 27, 28, 29,
               28, 29, 30, 31, 32, 1]
    extend = 0
    for e in e_table:
        extend = extend << 1
        extend += (message & (0b1 << (32 - e))) >> (32 - e)
    return extend


def S(data: int) -> int:
    """
    S盒变换函数
    :param data: 48bits int
    :return: 32 bits int
    """
    s1 = [14, 4, 13, 1, 2, 15, 11, 8, 3, 10, 6, 12, 5, 9, 0, 7,
          0, 15, 7, 4, 14, 2, 13, 1, 10, 6, 12, 11, 9, 5, 3, 8,
          4, 1, 14, 8, 13, 6, 2, 11, 15, 12, 9, 7, 3, 10, 5, 0,
          15, 12, 8, 2, 4, 9, 1, 7, 5, 11, 3, 14, 10, 0, 6, 13]
    s2 = [15, 1, 8, 14, 6, 11, 3, 4, 9, 7, 2, 13, 12, 0, 5, 10,
          3, 13, 4, 7, 15, 2, 8, 14, 12, 0, 1, 10, 6, 9, 11, 5,
          0, 14, 7, 11, 10, 4, 13, 1, 5, 8, 12, 6, 9, 3, 2, 15,
          13, 8, 10, 1, 3, 15, 4, 2, 11, 6, 7, 12, 0, 5, 14, 9]
    s3 = [10, 0, 9, 14, 6, 3, 15, 5, 1, 13, 12, 7, 11, 4, 2, 8,
          13, 7, 0, 9, 3, 4, 6, 10, 2, 8, 5, 14, 12, 11, 15, 1,
          13, 6, 4, 9, 8, 15, 3, 0, 11, 1, 2, 12, 5, 10, 14, 7,
          1, 10, 13, 0, 6, 9, 8, 7, 4, 15, 14, 3, 11, 5, 2, 12]
    s4 = [7, 13, 14, 3, 0, 6, 9, 10, 1, 2, 8, 5, 11, 12, 4, 15,
          13, 8, 11, 5, 6, 15, 0, 3, 4, 7, 2, 12, 1, 10, 14, 9,
          10, 6, 9, 0, 12, 11, 7, 13, 15, 1, 3, 14, 5, 2, 8, 4,
          3, 15, 0, 6, 10, 1, 13, 8, 9, 4, 5, 11, 12, 7, 2, 14]
    s5 = [2, 12, 4, 1, 7, 10, 11, 6, 8, 5, 3, 15, 13, 0, 14, 9,
          14, 11, 2, 12, 4, 7, 13, 1, 5, 0, 15, 10, 3, 9, 8, 6,
          4, 2, 1, 11, 10, 13, 7, 8, 15, 9, 12, 5, 6, 3, 0, 14,
          11, 8, 12, 7, 1, 14, 2, 13, 6, 15, 0, 9, 10, 4, 5, 3]
    s6 = [12, 1, 10, 15, 9, 2, 6, 8, 0, 13, 3, 4, 14, 7, 5, 11,
          10, 15, 4, 2, 7, 12, 9, 5, 6, 1, 13, 14, 0, 11, 3, 8,
          9, 14, 15, 5, 2, 8, 12, 3, 7, 0, 4, 10, 1, 13, 11, 6,
          4, 3, 2, 12, 9, 5, 15, 10, 11, 14, 1, 7, 6, 0, 8, 13]
    s7 = [4, 11, 2, 14, 15, 0, 8, 13, 3, 12, 9, 7, 5, 10, 6, 1,
          13, 0, 11, 7, 4, 9, 1, 10, 14, 3, 5, 12, 2, 15, 8, 6,
          1, 4, 11, 13, 12, 3, 7, 14, 10, 15, 6, 8, 0, 5, 9, 2,
          6, 11, 13, 8, 1, 4, 10, 7, 9, 5, 0, 15, 14, 2, 3, 12]
    s8 = [13, 2, 8, 4, 6, 15, 11, 1, 10, 9, 3, 14, 5, 0, 12, 7,
          1, 15, 13, 8, 10, 3, 7, 4, 12, 5, 6, 11, 0, 14, 9, 2,
          7, 11, 4, 1, 9, 12, 14, 2, 0, 6, 10, 13, 15, 3, 5, 8,
          2, 1, 14, 7, 4, 10, 8, 13, 15, 12, 9, 0, 3, 5, 6, 11]
    sbox = [s1, s2, s3, s4, s5, s6, s7, s8]
    out = 0
    for i in range(8):
        z = (data & (0xfc0000000000 >> (6 * i))) >> (42 - 6 * i)
        row = ((z & 0b100000) >> 4) + (z & 0b1)
        col = ((z & 0b011110) >> 1)
        out = out << 4
        out += sbox[i][row * 16 + col]
    return out


def S_i(box_index: int, data: int) -> int:
    """
    单独获取第i个S盒的输出
    :param box_index: 1-8
    :param data: 6 bits
    :return: 4 bits
    """
    return (S(data << (48 - 6 * box_index)) >> (32 - 4 * box_index)) & 0b1111


# input: 32bits, output: 32bits
def P(data: int) -> int:
    """
    P置换函数
    :param data: 32 bits int
    :return: 32 bits int 置换结果
    """
    p_table = [16, 7, 20, 21,
               29, 12, 28, 17,
               1, 15, 23, 26,
               5, 18, 31, 10,
               2, 8, 24, 14,
               32, 27, 3, 9,
               19, 13, 30, 6,
               22, 11, 4, 25]
    substitution = 0
    for p in p_table:
        substitution = substitution << 1
        substitution += (data & (0b1 << (32 - p))) >> (32 - p)
    return substitution


def inv_P(substitution: int) -> int:
    """
    P置换的逆变换函数
    :param substitution: 32 bits int 置换结果
    :return: 32 bits int 源数据
    """
    inv_p_table = [9, 17, 23, 31,
                   13, 28, 2, 18,
                   24, 16, 30, 6,
                   26, 20, 10, 1,
                   8, 14, 25, 3,
                   4, 29, 11, 19,
                   32, 12, 22, 7,
                   5, 27, 15, 21]
    data = 0
    for inv_p in inv_p_table:
        data = data << 1
        data += (substitution & (0b1 << (32 - inv_p))) >> (32 - inv_p)
    return data


def f(message: int, round_key: int) -> int:
    """
    轮加密的 f 函数
    :param message: 32bits int 明文Ri
    :param round_key: 48bits int 轮密钥
    :return: 32bits int
    """
    if type(message) != int or type(round_key) != int:
        logging.error('incorrect data type: message ' + str(type(message)) + ' round_key ' + str(type(round_key)))
        return -1
    if message < 0:
        logging.warning('message < 0: ' + str(message))
    elif message > 2 ** 32:
        logging.warning('incorrect message length: ' + str(len(bin(message)[2:])))
    if round_key < 0:
        logging.warning('round_key < 0: ' + str(round_key))
    elif round_key > 2 ** 48:
        logging.warning('incorrect round_key length: ' + str(len(bin(round_key)[2:])))

    s_in = E(message) ^ round_key
    s_out = S(s_in)
    return P(s_out)


def encrypt_round(message: int, round_key: int) -> int:
    """
    轮加密函数 (feistel)
    :param message: 64bits int
    :param round_key: 48bits int
    :return: 64bits int ciphertext
    """
    if type(message) != int or type(round_key) != int:
        logging.error('incorrect data type: message ' + str(type(message)) + ' round_key ' + str(type(round_key)))
        return -1
    if message < 0:
        logging.warning('message < 0: ' + str(message))
    elif message > 2 ** 64:
        logging.warning('incorrect message length: ' + str(len(bin(message)[2:])))
    if round_key < 0:
        logging.warning('round_key < 0: ' + str(round_key))
    elif round_key > 2 ** 48:
        logging.warning('incorrect round_key length: ' + str(len(bin(round_key)[2:])))

    l_message = message >> 32
    r_message = message & 0xffffffff
    l_cipher = r_message
    r_cipher = l_message ^ f(message=r_message, round_key=round_key)
    return (l_cipher << 32) + r_cipher


if __name__ == '__main__':
    pass
