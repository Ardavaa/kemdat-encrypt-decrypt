def caesar_encrypt(text, shift):
    # geser huruf sejumlah 'shift'
    hasil = ""
    for c in text:
        if c.isalpha():
            base = 'A' if c.isupper() else 'a'
            hasil += chr((ord(c) - ord(base) + shift) % 26 + ord(base))
        else:
            hasil += c
    return hasil

def caesar_decrypt(cipher, shift):
    # kebalikan dari encrypt (geser negatif)
    return caesar_encrypt(cipher, -shift)