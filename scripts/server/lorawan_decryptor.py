"""
lorawan_decryptor.py
--------------------

Handles decryption of encrypted LoRaWAN FRMPayloads using AppSKey and LoRaWAN 1.0 ABP spec.

This module performs low-level AES-128 decryption using the standard LoRaWAN block cipher approach:

- Decrypts FRMPayload using the AppSKey for the node
- Follows ABP mode semantics: uses DevAddr, FCnt, direction (uplink = 0)
- Compatible with AES ECB mode using Crypto.Cipher

Responsibilities:
- Perform secure payload decryption for uplinks
- Abstract away LoRaWAN bit-packing from dispatcher

Limitations:
- Only supports LoRaWAN 1.0.x ABP mode (no join nonce/session key handling)
- Does not verify MIC — MIC is ignored for now

Usage:
    from lorawan_decryptor import decrypt_frmpayload

    decrypted_bytes = decrypt_frmpayload(appskey, devaddr, fcnt, direction, encrypted_hex)
"""

from Crypto.Cipher import AES


def decrypt_frmpayload(appskey_hex, devaddr_hex, fcnt, direction, payload_hex):
    appskey = bytes.fromhex(appskey_hex)
    devaddr = bytes.fromhex(devaddr_hex)[::-1]  # LSB for LoRaWAN
    fcnt_bytes = fcnt.to_bytes(4, 'little')
    payload = bytes.fromhex(payload_hex)

    # Build B0 block (see LoRaWAN 1.0 spec section 4.3.3)
    block = (
        b'\x01' + b'\x00' * 4 +
        bytes([direction]) +
        devaddr +
        fcnt_bytes +
        b'\x00' + b'\x01'
    )

    cipher = AES.new(appskey, AES.MODE_ECB)
    s_block = cipher.encrypt(block)
    return bytes(a ^ b for a, b in zip(payload, s_block))

