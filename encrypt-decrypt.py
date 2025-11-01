"""Modul enkripsi dan dekripsi menggunakan AES-256 dalam mode CBC.

Modul ini menyediakan fungsi untuk mengenkripsi dan mendekripsi teks
menggunakan algoritma AES-256 dengan mode operasi CBC (Cipher Block Chaining).
"""

from __future__ import annotations

import base64
import os

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend


def _derive_key(password: str, salt: bytes) -> bytes:
    """Menurunkan kunci 256-bit (32 bytes) dari password menggunakan PBKDF2.

    Args:
        password: Password pengguna sebagai string.
        salt: Salt untuk key derivation.

    Returns:
        Kunci 256-bit sebagai bytes (32 bytes untuk AES-256).
    """
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,  # 32 bytes = 256 bits untuk AES-256
        salt=salt,
        iterations=100000,  # 100k iterations untuk keamanan yang baik
        backend=default_backend(),
    )
    return kdf.derive(password.encode("utf-8"))


def aes256_encrypt(plaintext: str, password: str) -> str:
    """Enkripsi teks menggunakan AES-256 dalam mode CBC.

    Fungsi ini mengenkripsi plaintext menggunakan algoritma AES-256 dengan mode
    operasi CBC. Kunci diturunkan dari password menggunakan PBKDF2 dengan SHA256.
    IV (Initialization Vector) dihasilkan secara acak untuk setiap enkripsi.
    Output dikembalikan dalam format base64 yang berisi salt, IV, dan ciphertext.

    Format output: base64(salt + iv + ciphertext)

    Args:
        plaintext: Teks yang akan dienkripsi.
        password: Password untuk enkripsi.

    Returns:
        String base64 yang berisi salt, IV, dan ciphertext yang dienkripsi.

    Raises:
        ValueError: Jika password kosong atau plaintext kosong.
        Exception: Jika terjadi kesalahan selama proses enkripsi.

    Example:
        >>> encrypted = aes256_encrypt("Hello World", "my_password")
        >>> print(encrypted)  # Output: base64 encoded string
    """
    if not password:
        raise ValueError("Password tidak boleh kosong")
    if not plaintext:
        raise ValueError("Plaintext tidak boleh kosong")

    # Generate salt dan IV secara acak
    salt = os.urandom(16)  # 16 bytes salt
    iv = os.urandom(16)  # 16 bytes IV untuk AES block size

    # Derive key dari password
    key = _derive_key(password, salt)

    # Enkripsi
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()

    # Padding plaintext ke kelipatan 16 bytes (AES block size)
    padder = padding.PKCS7(128).padder()  # 128 bits = 16 bytes
    padded_data = padder.update(plaintext.encode("utf-8"))
    padded_data += padder.finalize()

    # Enkripsi
    ciphertext = encryptor.update(padded_data) + encryptor.finalize()

    # Gabungkan salt + IV + ciphertext dan encode ke base64
    output = salt + iv + ciphertext
    return base64.b64encode(output).decode("utf-8")


def aes256_decrypt(ciphertext_base64: str, password: str) -> str:
    """Dekripsi teks yang dienkripsi menggunakan AES-256 dalam mode CBC.

    Fungsi ini mendekripsi ciphertext yang dienkripsi dengan aes256_encrypt.
    Format input harus berupa base64 string yang berisi salt, IV, dan ciphertext.

    Args:
        ciphertext_base64: String base64 yang berisi salt, IV, dan ciphertext.
        password: Password yang digunakan untuk dekripsi (harus sama dengan saat enkripsi).

    Returns:
        Plaintext yang didekripsi sebagai string.

    Raises:
        ValueError: Jika password kosong atau ciphertext tidak valid.
        Exception: Jika terjadi kesalahan selama proses dekripsi (misalnya password salah).

    Example:
        >>> encrypted = aes256_encrypt("Hello World", "my_password")
        >>> decrypted = aes256_decrypt(encrypted, "my_password")
        >>> print(decrypted)  # Output: "Hello World"
    """
    if not password:
        raise ValueError("Password tidak boleh kosong")
    if not ciphertext_base64:
        raise ValueError("Ciphertext tidak boleh kosong")

    try:
        # Decode base64
        data = base64.b64decode(ciphertext_base64)

        # Ekstrak salt (16 bytes pertama), IV (16 bytes berikutnya), dan ciphertext (sisanya)
        if len(data) < 32:  # Minimal salt (16) + IV (16) = 32 bytes
            raise ValueError("Ciphertext terlalu pendek atau tidak valid")

        salt = data[:16]
        iv = data[16:32]
        ciphertext = data[32:]

        # Derive key dari password (harus sama dengan saat enkripsi)
        key = _derive_key(password, salt)

        # Dekripsi
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        decryptor = cipher.decryptor()

        # Dekripsi ciphertext
        padded_plaintext = decryptor.update(ciphertext) + decryptor.finalize()

        # Unpadding
        unpadder = padding.PKCS7(128).unpadder()
        plaintext = unpadder.update(padded_plaintext)
        plaintext += unpadder.finalize()

        return plaintext.decode("utf-8")

    except Exception as exc:
        raise ValueError(f"Gagal dekripsi: {exc}. Pastikan password benar dan ciphertext valid.") from exc


# Alias untuk kompatibilitas dengan kode lama jika diperlukan
def encrypt(text: str, password: str) -> str:
    """Alias untuk aes256_encrypt untuk kompatibilitas.

    Args:
        text: Teks yang akan dienkripsi.
        password: Password untuk enkripsi.

    Returns:
        String base64 yang berisi ciphertext.
    """
    return aes256_encrypt(text, password)


def decrypt(ciphertext: str, password: str) -> str:
    """Alias untuk aes256_decrypt untuk kompatibilitas.

    Args:
        ciphertext: Ciphertext base64 yang akan didekripsi.
        password: Password untuk dekripsi.

    Returns:
        Plaintext yang didekripsi.
    """
    return aes256_decrypt(ciphertext, password)
