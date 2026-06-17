import websockets
import asyncio
import os
import sys
solution_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(solution_root)
from ecdh.ecdh import GeneratePrivateKey, GeneratePublicKey, ComputeSharedSecret
from aead.aead import EncryptMSG, UnpackPoly1305Key, GeneratePoly1305Tag, ChaCha20_Encrypt

def DecryptMSG(shared_key, nonce, ciphertext, expected_tag):
    _, poly_key = ChaCha20_Encrypt(shared_key, nonce, b"")
    r,s = UnpackPoly1305Key(poly_key)
    calculated_tag = GeneratePoly1305Tag(ciphertext, r, s)

    if calculated_tag != expected_tag:
        raise ValueError("Message authentication failed")

    plaintext, _ = ChaCha20_Encrypt(shared_key, nonce, ciphertext)
    return plaintext

async def handle_alice(websocket):
    print("Bob has established a connection")
    alice_pub_bytes = await websocket.recv()
    print(f"Alice public key -> {alice_pub_bytes}")
    bob_priv  = GeneratePrivateKey()
    bob_pub = GeneratePublicKey(bob_priv)
    shared_key = ComputeSharedSecret(bob_priv, alice_pub_bytes)
    print(f"shared secret -> {shared_key}")
    await websocket.send(bob_pub)
    print("completed handshake")

    async def recieve_loop():
        try:
            async for payload in websocket:
                nonce, tag, ciphertext = payload[0:12], payload[12:28], payload[28:]
                try:
                    plaintext = DecryptMSG(shared_key,nonce, ciphertext, tag)
                    print(f"Alice: {plaintext.decode('utf-8')}")
                    print("your message, bob", end="", flush=True)
                except Exception as e:
                    print("failed to decrypt the message on your side, bob")
        except websockets.exceptions.ConnectionClosed:
            print("Alice disconnected")

    async def send_loop():
        loop = asyncio.get_event_loop()
        try:
            while True:
                message = await loop.run_in_executor(None, input, "type a message, bob ")
                if not message:
                    continue
                nonce = os.urandom(12)
                ciphertext, tag = EncryptMSG(shared_key, nonce, message.encode('utf-8'))
                payload = nonce + tag + ciphertext
                await websocket.send(payload)
        except Exception as e:
            print("Couldnt send your message, bob")
    await asyncio.gather(recieve_loop(), send_loop())

async def main():
    print("Hello, bob. the server starts at port 8765, waiting for Alice...")
    bob_server = await websockets.serve(handle_alice, "localhost", 8765)
    await bob_server.wait_closed()

if __name__ == "__main__":
    asyncio.run(main())







