import sys
import copy
import random
from operator import add
from functools import reduce

from utils import read, read_struct, write, ratio, cleanup
from prime import gen_prime


def solve(mat_orig, d, p):
    mat = copy.deepcopy(mat_orig)
    d = d[:]
    k = len(mat[0])
    for i in range(k):
        aii = mat[i][i]
        for j in range(k):
            mat[i][j] = ratio(mat[i][j], aii, p)
        d[i] = ratio(d[i], aii, p)
        for row in range(len(mat)):
            if row != i:
                coeff = -mat[row][i] % p
                d[row] = (d[row] + d[i] * coeff) % p
                for col in range(k):
                    mat[row][col] = (mat[row][col] + mat[i][col] * coeff) % p
    if any(map(lambda r: not any(mat[r]), range(k))):
        return
    return d


def gen_parts(p_size, m, n, k):
    if n < k:
        print('ОШИБКА: число долей={} больше k={}'.format(n, k))
        return

    with open(m, 'rb') as f:
        msg = int.from_bytes(f.read(), byteorder='big')

    msg_size = msg.bit_length()
    if p_size <= msg_size:
        p_size = msg_size + 1
        print('Размер модуля изменен до размера сообщения {} бит'.format(p_size))
    p = gen_prime(p_size)
    q = [msg] + [random.randint(0, p - 1) for _idx in range(k - 1)]

    while True:
        parts = []
        mat, ds = [], []
        for i in range(n):
            coeffs = [random.randint(0, p - 1) for _idx in range(k)]
            d = -reduce(add, map(lambda ax: ax[0] * ax[1] % p, zip(coeffs, q))) % p
            parts.append(tuple(coeffs + [d]))
            mat.append(coeffs), ds.append(-d % p)

        if solve(mat, ds, p) is not None:
            break

    write('p.txt', p)
    for idx, part in enumerate(parts):
        write('part_{}.txt'.format(idx + 1), part)


def check_secret(p, parts):
    mat = [list(part)[:-1] for part in parts]
    if len(mat) < len(mat[0]):
        print('ОШИБКА: не хватает частей секрета')
        return
    d = [-part[-1] % p for part in parts]
    sol = solve(mat, d, p)
    x = sol[0]
    with open('secret.txt', 'wb') as f:
        f.write(bytes.fromhex(hex(x)[2:]))


def main():
    if sys.argv[1] == '-g':
        gen_parts(int(sys.argv[2]), sys.argv[3], int(sys.argv[4]), int(sys.argv[5]))
    elif sys.argv[1] == '-c':
        idx_parts = list(map(lambda idx: int(idx), sys.argv[2:]))
        if len(set(idx_parts)) != len(idx_parts):
            print('ОШИБКА: дубликаты в массиве индексов')
            return
        parts = [read_struct('part_{}.txt'.format(idx)) for idx in idx_parts]
        check_secret(read('p.txt'), parts)
    elif sys.argv[1] == '-clean':
        cleanup()
    else:
        print('ОШИБКА: неверный код операции')


if __name__ == '__main__':
    main()
