## AES-256 CBC Encrypt/Decrypt UI (Streamlit)

Aplikasi web berbasis Streamlit untuk enkripsi dan dekripsi menggunakan algoritma **AES-256** dalam mode **CBC (Cipher Block Chaining)**. Aplikasi ini menyediakan antarmuka yang ramah pengguna untuk mengenkripsi dan mendekripsi teks maupun file.

🌐 **Aplikasi Online:** [https://aes-256-encrypt-decrypt.streamlit.app/](https://aes-256-encrypt-decrypt.streamlit.app/)  
🎥 **Video Demo:** [https://youtu.be/n4YqjEzMDdE](https://youtu.be/n4YqjEzMDdE)

### Fitur

- ✅ Enkripsi dan dekripsi menggunakan AES-256 CBC
- ✅ Input melalui text area atau upload file
- ✅ Download hasil sebagai file `.txt`
- ✅ Password-based encryption dengan PBKDF2 key derivation
- ✅ Keamanan tinggi dengan salt dan IV acak
- ✅ Antarmuka yang modern dan mudah digunakan

### Teknologi

- **Algoritma**: AES-256 (Advanced Encryption Standard dengan kunci 256-bit)
- **Mode Operasi**: CBC (Cipher Block Chaining)
- **Key Derivation**: PBKDF2 dengan SHA256 (100,000 iterations)
- **Format Output**: Base64 (berisi salt + IV + ciphertext)

### Persyaratan

- Python >= 3.10
- Dependencies dikelola melalui `pyproject.toml`

### Instalasi

#### Menggunakan UV (Direkomendasikan)

UV adalah package installer Python yang cepat. Pertama, install UV:

```bash
# Di Windows
curl -LsSf https://astral.sh/uv/install.ps1 | powershell
# Atau melalui pip
pip install uv
```

Kemudian install dependencies:

```bash
# Install di environment saat ini
uv pip install -e .

# Atau buat dan gunakan virtual environment
uv venv
source .venv/bin/activate  # Di Windows: .venv\Scripts\activate
uv pip install -e .
```

#### Menggunakan pip

```bash
# Install dari pyproject.toml
pip install -e .

# Atau install manual
pip install streamlit cryptography
```

### Menjalankan Aplikasi

Aplikasi tersedia secara online di: [https://aes-256-encrypt-decrypt.streamlit.app/](https://aes-256-encrypt-decrypt.streamlit.app/)

Atau jalankan secara lokal dari root project:

```bash
streamlit run app.py
```

Di Windows (PowerShell atau Git Bash), perintahnya sama.

Video demo aplikasi dapat dilihat di: [https://youtu.be/n4YqjEzMDdE](https://youtu.be/n4YqjEzMDdE)

### Cara Penggunaan

1. **Enkripsi**:
   - Pilih mode "Encrypt"
   - Masukkan plaintext (teks atau upload file)
   - Masukkan password yang kuat
   - Klik proses untuk mendapatkan ciphertext (Base64)
   - Download dan simpan hasil dengan aman

2. **Dekripsi**:
   - Pilih mode "Decrypt"
   - Masukkan ciphertext (Base64) yang sebelumnya dienkripsi
   - Masukkan password yang sama dengan saat enkripsi
   - Klik proses untuk mendapatkan plaintext
   - Download hasil jika diperlukan

### Catatan Keamanan

- ⚠️ **Simpan password dengan aman**: Jika password hilang atau salah, data tidak dapat didekripsi
- 🔒 **Gunakan password yang kuat**: Minimal 12 karakter dengan kombinasi huruf, angka, dan simbol
- 🔐 **Simpan ciphertext dengan aman**: Ciphertext berisi semua informasi yang diperlukan untuk dekripsi (kecuali password)
- 🔄 **Setiap enkripsi menghasilkan output berbeda**: Karena menggunakan IV acak, plaintext yang sama akan menghasilkan ciphertext yang berbeda

### Detail Teknis

- **Key Size**: 256-bit (32 bytes)
- **Block Size**: 128-bit (16 bytes)
- **Salt Size**: 128-bit (16 bytes)
- **IV Size**: 128-bit (16 bytes)
- **Key Derivation**: PBKDF2-HMAC-SHA256 dengan 100,000 iterations
- **Padding**: PKCS7
- **Output Encoding**: Base64

### Struktur Output

Output enkripsi adalah string Base64 dengan format:
```
Base64(Salt (16 bytes) + IV (16 bytes) + Ciphertext (variable length))
```

### Lisensi

Proyek ini dibuat untuk keperluan pendidikan dan pembelajaran.
