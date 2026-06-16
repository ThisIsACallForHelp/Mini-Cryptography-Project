import asyncio 
from asyncio import exceptions
import os 
import websockets
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

async def main():
    uri = "ws://localhost:8675"
    print(f"Hello Alice. connecting to bob at {uri}")
    async with websockets.connect(uri) as websocket:
        print("Alice has connected. establishing handshake...")
        alice_priv, alice_pub = ECDH.GeneratePrivateKey(), ECDH.GeneratePublicKey()
        await websocket.send(alice_pub)

        bob_pub_bytes = await websocket.recv()
        shared_key = ECDH.ComputeSharedSecret(alice_priv, bob_pub_bytes)
        print("Shared secret established")

        async def recieve_loop():
            try:
                async for payload in websocket:
                    nonce, tag, ciphertext = payload[0:12], payload[12:28], ciphertext[28:]
                    try:
                        plaintext = DecryptMSG(shared_key, nonce, ciphertext, tag)
                        print(f"Bob: {plaintext.decode('utf-8')}")
                        print("[Alice] Type message: ", end="", flush=True)
                    except Exception as e:
                        print("Decryption failed, Alice")
            except websockets.exceptions.ConnectionClosed:
                print("Bob disconnected")
        async def send_loop():
            loop = asyncio.get_event_loop()
            try:
                while True:
                    message = await loop.run_in_executor(None, input, "type a message, Alice")
                    if not message:
                        continue
                    nonce = os.urandom(12)
                    ciphertext, tag = EncryptMSG(shared_key, nonce, message.encode('utf-8'))
                    payload = nonce + tag + ciphertext
                    await websocket.send(payload)
            except Exception as e:
                print("Couldnt send your message, bob")
        await asyncio.gather(recieve_loop(), send_loop())

if __name__ == "__main__":
    asyncio.run(main())


