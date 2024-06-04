import numpy as np

l_list = [0, 1, 2, 3, 4, 5, 6]
l = l_list[6]
w = (2 ** l)
b = 25 * w

shifts = [[0, 36, 3, 41, 18],
          [1, 44, 10, 45, 2],
          [62, 6, 43, 15, 61],
          [28, 55, 25, 21, 56],
          [27, 20, 39, 8, 14]]

RCs = [0x0000000000000001, 0x0000000000008082, 0x800000000000808a,
       0x8000000080008000, 0x000000000000808b, 0x0000000080000001,
       0x8000000080008081, 0x8000000000008009, 0x000000000000008a,
       0x0000000000000088, 0x0000000080008009, 0x000000008000000a,
       0x000000008000808b, 0x800000000000008b, 0x8000000000008089,
       0x8000000000008003, 0x8000000000008002, 0x8000000000000080,
       0x000000000000800a, 0x800000008000000a, 0x8000000080008081,
       0x8000000000008080, 0x0000000080000001, 0x8000000080008008]

# Функция для чтения битовой строки из файла
def get_bitstring_from_file(filename):
    with open(filename, 'rb') as fh:
        bytetext = fh.read()
    return bytes_to_bitstring(bytetext)

# Функция для преобразования байтов в битовую строку
def bytes_to_bitstring(in_bytes):
    bitstring = ''
    for bytechar in in_bytes:
        byte = '{0:08b}'.format(bytechar)
        byte = byte[::-1]
        bitstring += byte
    bitstring += '01100000'
    return bitstring

# Функция для преобразования строки в массив состояния
def string_to_array(string, w=64):
    state_array = np.zeros([5, 5, w], dtype=int)
    for x in range(5):
        for y in range(5):
            for z in range(w):
                if (w * (5 * x + y) + z) < len(string):
                    state_array[y][x][z] = int(string[w * (5 * x + y) + z])
    return state_array

# Функция для преобразования шестнадцатеричного числа в массив
def hex_to_array(hexnum, w=64):
    bitstring = '{0:064b}'.format(hexnum)
    bitstring = bitstring[-w:]
    array = np.array([int(bitstring[i]) for i in range(w)])
    return array

# Функция для дополнения сообщения
def pad(rate, message_length):
    j = (-(message_length + 1)) % rate
    return '0' * j + '1'

# Функция Theta преобразования
def theta(array, w=64):
    array_prime = array.copy()
    C, D = np.zeros([5, w], dtype=int), np.zeros([5, w], dtype=int)
    for x in range(5):
        for y in range(5):
            C[x] ^= array[x][y]
    for x in range(5):
        D[x] = C[(x - 1) % 5] ^ np.roll(C[(x + 1) % 5], 1)
    for x in range(5):
        for y in range(5):
            array_prime[x][y] ^= D[x]
    return array_prime

# Функция Rho преобразования
def rho(array):
    array_prime = array.copy()
    for x in range(5):
        for y in range(5):
            array_prime[x][y] = np.roll(array[x][y], shifts[x][y])
    return array_prime

# Функция Pi преобразования
def pi(array):
    array_prime = array.copy()
    for x in range(5):
        for y in range(5):
            array_prime[x][y] = array[((x) + (3 * y)) % 5][x]
    return array_prime

# Функция Chi преобразования
def chi(array):
    array_prime = np.zeros(array.shape, dtype=int)
    for x in range(5):
        for y in range(5):
            array_prime[x][y] = array[x][y] ^ ((array[(x + 1) % 5][y] ^ 1) & (array[(x + 2) % 5][y]))
    return array_prime

# Функция Iota преобразования
def iota(array, round_index, w=64):
    RC = hex_to_array(RCs[round_index], w)
    RC = np.flip(RC)
    array_prime = array.copy()
    array_prime[0][0] ^= RC
    return array_prime

# Функция Keccak для выполнения всех раундов преобразований
def keccak(state):
    for round_index in range(24):
        state = iota(chi(pi(rho(theta(state)))), round_index)
    return state

# Функция для преобразования массива состояния в хэш-значение
def squeeze(array, bits):
    hash = ''
    for i in range(5):
        for j in range(5):
            lane = array[j][i]
            lanestring = ''
            for m in range(len(lane)):
                lanestring += str(lane[m])
            for n in range(0, len(lanestring), 8):
                byte = lanestring[n:n + 8]
                byte = byte[::-1]
                hash += '{0:02x}'.format(int(byte, 2))
    return hash[:int(bits / 4)]

# Основная функция для хэширования файла
def hash_file(path):
    outbits = 256
    capacity = 2 * outbits
    rate = b - capacity
    bitstring = get_bitstring_from_file(path)
    padded = bitstring + pad(rate, len(bitstring) % rate)
    sponge_rounds = len(padded) // rate
    state = np.zeros(b, dtype=int).reshape(5, 5, w)
    for i in range(sponge_rounds):
        current_string = padded[(i * rate):(i * rate) + rate]
        array = string_to_array(current_string, w=64)
        state = np.bitwise_xor(state, array)
        state = keccak(state)
    return squeeze(state, outbits)

# Функция для сохранения хэш-значения в файл
def save_file(hash_val, output_path):
    with open(output_path, 'w') as file:
        file.write(hash_val)

# Основной блок программы
if __name__ == "__main__":
    input_file = "input.txt"
    output_file = "output_hash.txt"

    hash_val = hash_file(input_file)
    save_file(hash_val, output_file)

    print(f"Хэш сохранён в файл {output_file}: {hash_val}")