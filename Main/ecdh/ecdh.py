import os
from sys import byteorder
from Math_Engine import Math_Engine
import hashlib
def GeneratePrivateKey():
    rand_bytes = bytearray(os.urandom(32))
    rand_bytes[0] &= 248
    rand_bytes[31] &= 127
    rand_bytes[31] |= 64
    return bytes(rand_bytes)


def GeneratePublicKey(PrivateKey):
    private_ints = int.from_bytes(PrivateKey, byteorder="little")
    base_x = 9
    final_x = Math_Engine.double_and_add(private_ints, base_x)
    public_bytes = final_x.to_bytes(32,byteorder="little")
    return public_bytes


def ComputeSharedSecret(private_bytes, foreign_public_bits):
    private_ints = int.from_bytes(private_bytes, byteorder="little")
    foreign_public_ints = int.from_bytes(foreign_public_bits, byteorder="little")
    final_x = Math_Engine.double_and_add(private_ints, foreign_public_ints)
    computed_bytes = final_x.to_bytes(32, byteorder="little")
    return (hashlib.sha256(computed_bytes)).digest()