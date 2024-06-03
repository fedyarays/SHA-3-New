HashLength = 32
SHA3_WORD = 64  # Длина слова в битах
SHA3_BLOCKSIZE = 1600  # Длина блока в битах
SHA3_ROUND = 24  # Количество раундов

c = HashLength * 8 * 2  # Capacity
r = 1600 - c  # Bit rate

# Константы для алгоритма
MM1M5 = [4, 0, 1, 2, 3]
MP1M5 = [1, 2, 3, 4, 0]
M2XP3YM5 = [[0, 2, 4, 1, 3], [3, 0, 2, 4, 1], [1, 3, 0, 2, 4], [4, 1, 3, 0, 2], [2, 4, 1, 3, 0]]
R = [
    [0, 1, 62, 28, 27], [36, 44, 6, 55, 20], [3, 10, 43, 25, 39], [41, 45, 15, 21, 8], [18, 2, 61, 56, 14]
]
RC = [
    0x0000000000000001, 0x0000000000008082, 0x800000000000808A, 0x8000000080008000, 0x000000000000808B,
    0x0000000080000001,
    0x8000000080008081, 0x8000000000008009, 0x000000000000008A, 0x0000000000000088, 0x0000000080008009,
    0x000000008000000A,
    0x000000008000808B, 0x800000000000008B, 0x8000000000008089, 0x8000000000008003, 0x8000000000008002,
    0x8000000000000080,
    0x000000000000800A, 0x800000008000000A, 0x8000000080008081, 0x8000000000008080, 0x0000000080000001,
    0x8000000080008008
]


def ROT(val, r_bits):
    return ((val << r_bits) & ((1 << 64) - 1)) | (val >> (64 - r_bits))


def Round(A):
    for rnd in range(SHA3_ROUND):
        C = [A[x] ^ A[x + 5] ^ A[x + 10] ^ A[x + 15] ^ A[x + 20] for x in range(5)]
        D = [C[x] ^ ROT(C[MP1M5[x]], 1) for x in range(5)]
        A = [(A[x] ^ D[x % 5]) for x in range(25)]

        B = [0] * 25
        for x in range(5):
            for y in range(5):
                B[y * 5 + M2XP3YM5[x][y]] = ROT(A[x * 5 + y], R[x][y])

        for x in range(5):
            for y in range(5):
                A[x * 5 + y] = B[x * 5 + y] ^ ((~B[MP1M5[x] * 5 + y]) & B[MP1M5[MP1M5[x]] * 5 + y])

        A[0] ^= RC[rnd]

    return A


def pad10star1(message, r):
    padding = [0] * ((r - len(message) % r) // 8)
    padding[0] = 0x01
    padding[-1] |= 0x80
    return message + bytes(padding)


def Keccak(message, r, c):
    message = pad10star1(message, r)
    n = len(message) * 8 // r
    state = [0] * 25

    for i in range(n):
        block = int.from_bytes(message[i * (r // 8):(i + 1) * (r // 8)], 'little')
        for j in range(r // 64):
            state[j] ^= (block >> (64 * j)) & 0xFFFFFFFFFFFFFFFF
        state = Round(state)

    hash_val = b''
    while len(hash_val) * 8 < c:
        hash_val += (state[0] & 0xFFFFFFFFFFFFFFFF).to_bytes(8, 'little')
        state = Round(state)

    return hash_val[:c // 8]


def hash_file(path):
    with open(path, 'rb') as file:
        data = file.read()
    hash_val = Keccak(data, r, c)
    return hash_val.hex()


def save_file(hash_val, output_path):
    with open(output_path, 'w') as file:
        file.write(hash_val)


if __name__ == "__main__":
    input_file = "input.txt"
    output_file = "output_hash.txt"

    hash_val = hash_file(input_file)
    save_file(hash_val, output_file)

    print(f"Хэш сохранён в файл {output_file}: {hash_val}")