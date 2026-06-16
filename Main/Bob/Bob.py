from ssl import _Cipher
import websockets
import asyncio
import os
from ECDH import ECDH
from aead import EncryptMSG, UnpackPoly1305Key, GeneratePoly1305Tag, ChaCha20_Encrypt

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
    bob_priv, bob_pub = ECDH.GeneratePrivateKey(), ECDH.GeneratePublicKey(bob_priv, alice_pub_bytes)
    shared_secret = ECDH.ComputeSharedSecret(bob_priv, alice_pub_bytes)
    print("Bob has shared his secret key with alice")
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
                message = await loop.run_in_executor(None, input, "type a message, bob")
                if not message:
                    continue
                nonce = os.urandom(12)
                ciphertext, tag = EncryptMSG(shared_secret, nonce, message.encode('utf-8'))
                payload = nonce + tag + ciphertext
                await websocket.send(payload)
        except Exception as e:
            print("Couldnt send your message, bob")
    await asyncio.gather(recieve_loop(), send_loop())

async def main():
    print("Hello, bob. the server starts at port 8765, waiting for Alice...")
    async with websockets.serve(handle_alice, "localhost", 8765):
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())







