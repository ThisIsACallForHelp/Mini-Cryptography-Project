
from threading import local
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

def ChaCha20(foreign_public_key, nonce_bytes):
    matrix = [0] * 16
    start_phrase = b"expand 32-byte k"
    for i in range(4):
        chunk = start_phrase[((i*4)):(i*4) + 4]
        matrix[i] = int.from_bytes(chunk, byteorder="little")
    private_key = ECDH.GeneratePrivateKey()
    public_key = ECDH.GeneratePublicKey(private_key)
    key = ECDH.ComputeSharedSecret(private_key, foreign_public_key)
    for i in range(8):
        chunk = key[i*4: (i*4)+4]
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
    


        
