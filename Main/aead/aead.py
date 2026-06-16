from ctypes.wintypes import BYTE
from ECDH import ECDH


def Quarter_Round(x,a,b,c,d):
    x[a] = (x[a] + x[b]) & 0xffffffff
    x[d] ^= x[a]
    x[d] = ((x[d] << 16) & 0xffffffff | (x[d] >> 16))

    x[c] = (x[c] + x[d]) & 0xffffffff
    x[b] ^= x[c]
    x[b] = ((x[b] << 12) & 0xffffffff) | (x[b] >> 20)

    x[a] = (x[a] + x[b]) & 0xffffffff
    x[d] ^= x[a]
    x[d] = ((x[d] << 8) & 0xffffffff) | (x[d] >> 24)

    x[c] = (x[c] + x[d]) & 0xffffffff
    x[b] ^= x[c]
    x[b] = ((x[b] << 7) & 0xffffffff) | (x[b] >> 25)

def ChaCha20(shared_key, nonce_bytes):
    matrix = [0] * 16
    start_phrase = b"expand 32-byte k"
    for i in range(4):
        chunk = start_phrase[(i*4):(i*4) + 4]
        matrix[i] = int.from_bytes(chunk, byteorder="little")
    for i in range(8):
        chunk = shared_key[i*4: (i*4)+4]
        matrix[4 + i] = int.from_bytes(chunk, byteorder="little")
    for i in range(3):
        chunk = nonce_bytes[i*4: (i*4) + 4]
        matrix[13 + i] = int.from_bytes(chunk, byteorder="little")
    return matrix


def ChaCha20_block(ChaChaMatrix):
    local_matrix = list(ChaChaMatrix)
    for i in range(10):
        Quarter_Round(local_matrix,0,4,8,12)
        Quarter_Round(local_matrix,1,5,9,13)
        Quarter_Round(local_matrix,2,6,10,14)
        Quarter_Round(local_matrix,3,7,11,15)

        Quarter_Round(local_matrix,0,5,10,15)
        Quarter_Round(local_matrix,1,6,11,12)
        Quarter_Round(local_matrix,2,7,8,13)
        Quarter_Round(local_matrix,3,4,9,14)
    matrix_bytes = b""
    for i in range(16):
        local_matrix[i] = (local_matrix[i] + ChaChaMatrix[i]) & 0xffffffff
        matrix_bytes += local_matrix[i].to_bytes(4, byteorder="little")
    return matrix_bytes


def ChaCha20_Encrypt(shared_key, nonce_bytes, plaintext): #we generate the unique keys here
    matrix = ChaCha20(shared_key, nonce_bytes)

    block_0 = ChaCha20_block(matrix)
    poly_1305_key = block_0[0:32]
    matrix[12],ciphertext, m_length = 1, b"", len(plaintext)

    for i in range(0,m_length, 64):
        chunk = plaintext[i : i + 64]
        keystream = ChaCha20_block(matrix)
        for j in range(len(chunk)):
            ciphertext += bytes([chunk[j] ^ keystream[j]])
        matrix[12] = (matrix[12] + 1) & 0xffffffff
    return ciphertext, poly_1305_key

def UnpackPoly1305Key(Poly_1305_Bytes):
    s_bytes = Poly_1305_Bytes[16:32]
    s_integer = int.from_bytes(s_bytes, byteorder="little")
    r_bytes = bytearray(Poly_1305_Bytes[0:16])
    for i in range(3,16,4):
        r_bytes[i] &= 0x0f
    for i in range(4, 13, 4):
        r_bytes[i] &= 0xfc
    r_integer = int.from_bytes(r_bytes, byteorder="little")
    return r_integer, s_integer

def GeneratePoly1305Tag(ciphertext_bytes, r_integer, s_integer):
    accumulator, prime = 0, pow(2,130) - 5
    for i in range (0, len(ciphertext_bytes), 16):
        chunk = ciphertext_bytes[i:i + 16]
        block_number = int.from_bytes(chunk, byteorder="little")
        marker = pow(2,8 * len(chunk))
        block_number += marker
        accumulator = ((accumulator + block_number) * r_integer) % prime
    final = (accumulator + s_integer) & 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF
    tag_bytes = final.to_bytes(16, byteorder="little")
    return tag_bytes

def EncryptMSG(shared_key, nonce, plaintext):
    ciphertext, poly_key = ChaCha20_Encrypt(shared_key, nonce, plaintext)
    r,s = UnpackPoly1305Key(poly_key)
    tag = GeneratePoly1305Tag(ciphertext, r,s)
    return ciphertext, tag