"""Aplikasi Streamlit untuk enkripsi dan dekripsi menggunakan AES-256 CBC.

Aplikasi ini menyediakan antarmuka web yang ramah pengguna untuk mengenkripsi
dan mendekripsi teks menggunakan algoritma AES-256 dalam mode CBC.
"""

from __future__ import annotations

from io import BytesIO
from pathlib import Path
from typing import Callable, Optional, Tuple

import streamlit as st
import importlib.util


def _load_aes_functions() -> Tuple[Callable[[str, str], str], Callable[[str, str], str]]:
    """Memuat fungsi `aes256_encrypt` dan `aes256_decrypt` dari `encrypt-decrypt.py`.

    Returns:
        Tuple[Callable, Callable]: Fungsi encrypt dan decrypt yang dapat dipanggil.

    Raises:
        RuntimeError: Jika modul atau fungsi yang diperlukan tidak dapat dimuat.
    """
    project_dir = Path(__file__).resolve().parent
    target = project_dir / "encrypt-decrypt.py"

    if not target.exists():
        raise RuntimeError(f"Tidak menemukan file: {target}")

    spec = importlib.util.spec_from_file_location("aes_module", str(target))
    if spec is None or spec.loader is None:
        raise RuntimeError("Gagal memuat spesifikasi modul untuk encrypt-decrypt.py")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)  # type: ignore[assignment]

    try:
        encrypt = getattr(module, "aes256_encrypt")
        decrypt = getattr(module, "aes256_decrypt")
    except AttributeError as exc:
        raise RuntimeError(
            "Fungsi aes256_encrypt/aes256_decrypt tidak ditemukan di encrypt-decrypt.py"
        ) from exc

    if not callable(encrypt) or not callable(decrypt):
        raise RuntimeError("Objek yang dimuat bukan fungsi yang dapat dipanggil")

    return encrypt, decrypt


def _prepare_download_bytes(text: str) -> BytesIO:
    """Encode text ke UTF-8 bytes untuk download.

    Args:
        text: Teks yang akan diencode.

    Returns:
        BytesIO yang berisi UTF-8 bytes.
    """
    return BytesIO(text.encode("utf-8"))


def run_app() -> None:
    """Menjalankan aplikasi Streamlit AES-256."""
    st.set_page_config(
        page_title="AES-256 Encrypt/Decrypt",
        page_icon="🔐",
        layout="wide",
        menu_items={
            "Get help": "https://docs.streamlit.io/",
            "Report a bug": "https://github.com/Ardavaa/kemdat-encrypt-decrypt",
            "About": "AES-256 CBC Encryption/Decryption UI built with Streamlit.",
        },
    )

    # Minimal theming via CSS
    st.markdown(
        """
        <style>
        .app-header {padding: 1.2rem 1.5rem; border-radius: 0.75rem; background: linear-gradient(90deg, #0ea5e9 0%, #6366f1 100%); color: white;}
        .app-subtitle {opacity: 0.95;}
        .stDownloadButton > button {border-radius: 0.5rem;}
        .stTextArea textarea {font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;}
        .password-input {font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;}
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="app-header">
            <h2 style="margin-bottom: 0.25rem;">🔐 AES-256 CBC Encryption Studio</h2>
            <div class="app-subtitle">Enkripsi dan dekripsi teks menggunakan AES-256 dalam mode CBC dengan antarmuka yang ramah dan aman.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    try:
        aes_encrypt, aes_decrypt = _load_aes_functions()
    except RuntimeError as err:
        st.error(str(err))
        st.stop()

    with st.sidebar:
        st.header("Pengaturan")
        mode: str = st.radio("Mode", options=["Encrypt", "Decrypt"], horizontal=True)
        
        # Password input
        password: str = st.text_input(
            "Password",
            type="password",
            help="Password untuk enkripsi/dekripsi. Gunakan password yang kuat untuk keamanan optimal.",
            placeholder="Masukkan password...",
        )
        
        # Show password strength indicator
        if password:
            strength = len(password)
            if strength < 8:
                st.warning("⚠️ Password terlalu pendek. Disarankan minimal 8 karakter.")
            elif strength < 12:
                st.info("ℹ️ Password cukup kuat, namun disarankan minimal 12 karakter untuk keamanan optimal.")
            else:
                st.success("✅ Password kuat!")
        
        input_method: str = st.selectbox("Sumber Input", options=["Teks", "File"], index=0)
        
        st.markdown("---")
        st.caption("**Catatan Keamanan:**")
        st.caption("• Simpan password Anda dengan aman. Jika lupa password, data tidak dapat didekripsi.")
        st.caption("• Setiap enkripsi menghasilkan output yang berbeda karena IV acak.")
        st.caption("• Untuk keamanan maksimal, gunakan password yang panjang dan kompleks.")

    st.write("")
    tabs = st.tabs(["Editor", "Tentang"])

    with tabs[0]:
        if input_method == "Teks":
            sample = "The quick brown fox jumps over the lazy dog."
            st.caption("Masukkan teks di bawah ini atau gunakan contoh.")
            col_a, col_b = st.columns([3, 1])
            with col_b:
                use_sample = st.button("Gunakan Contoh")
            if use_sample:
                st.session_state.setdefault("input_text", sample)

            input_text: str = st.text_area(
                "Teks Masukan",
                value=st.session_state.get("input_text", ""),
                height=180,
                placeholder="Ketik atau tempel teks di sini...",
            )

            processed_text: str = ""
            error_message: Optional[str] = None

            if input_text and password:
                try:
                    if mode == "Encrypt":
                        processed_text = aes_encrypt(input_text, password)
                    else:
                        processed_text = aes_decrypt(input_text, password)
                except ValueError as e:
                    error_message = str(e)
                except Exception as e:
                    error_message = f"Terjadi kesalahan: {str(e)}"

            if error_message:
                st.error(error_message)

            st.markdown("---")
            st.subheader("Hasil")
            
            # Display result differently for encrypted vs decrypted
            if mode == "Encrypt" and processed_text:
                st.caption("Ciphertext (Base64):")
                st.text_area(
                    "Teks Keluaran",
                    value=processed_text,
                    height=180,
                    help="Hasil enkripsi dalam format Base64. Simpan dengan aman bersama password Anda.",
                )
            elif mode == "Decrypt":
                st.text_area(
                    "Teks Keluaran",
                    value=processed_text,
                    height=180,
                    help="Plaintext yang didekripsi.",
                )

            col1, col2, col3 = st.columns([1, 1, 2])
            with col1:
                st.download_button(
                    label="Unduh Hasil",
                    data=_prepare_download_bytes(processed_text),
                    file_name=("hasil_encrypt.txt" if mode == "Encrypt" else "hasil_decrypt.txt"),
                    mime="text/plain",
                    disabled=not bool(processed_text),
                )
            with col2:
                st.write(f"Karakter: {len(processed_text)}")
                if mode == "Encrypt" and processed_text:
                    st.write(f"Size: {len(processed_text.encode('utf-8'))} bytes")

            st.session_state["last_input_text"] = input_text
            st.session_state["last_output_text"] = processed_text

        else:  # File
            uploaded = st.file_uploader(
                "Unggah file teks (.txt, .md)", type=["txt", "md", "csv", "log"]
            )
            input_text = ""
            file_name: Optional[str] = None
            if uploaded is not None:
                file_name = uploaded.name
                try:
                    input_text = uploaded.read().decode("utf-8")
                except UnicodeDecodeError:
                    try:
                        uploaded.seek(0)  # Reset file pointer
                        input_text = uploaded.read().decode("latin-1")
                    except Exception as exc:  # noqa: BLE001
                        st.error(f"Gagal membaca file: {exc}")
                        input_text = ""

            if input_text:
                st.caption("Pratinjau (2000 karakter pertama)")
                st.text_area("Isi File", value=input_text[:2000], height=180, disabled=True)

            processed_text = ""
            error_message: Optional[str] = None

            if input_text and password:
                try:
                    if mode == "Encrypt":
                        processed_text = aes_encrypt(input_text, password)
                    else:
                        processed_text = aes_decrypt(input_text, password)
                except ValueError as e:
                    error_message = str(e)
                except Exception as e:
                    error_message = f"Terjadi kesalahan: {str(e)}"

            if error_message:
                st.error(error_message)

            st.markdown("---")
            st.subheader("Hasil")
            
            if mode == "Encrypt" and processed_text:
                st.caption("Ciphertext (Base64) - Pertama 2000 karakter:")
                st.text_area(
                    "Teks Keluaran",
                    value=processed_text[:2000] + ("..." if len(processed_text) > 2000 else ""),
                    height=180,
                    disabled=True,
                )
            else:
                st.text_area(
                    "Teks Keluaran",
                    value=processed_text[:2000] + ("..." if len(processed_text) > 2000 else ""),
                    height=180,
                    disabled=True,
                )
            
            safe_base = (file_name or "hasil").rsplit(".", 1)[0]
            out_name = f"{safe_base}_{'encrypted' if mode == 'Encrypt' else 'decrypted'}.txt"
            st.download_button(
                label="Unduh Hasil",
                data=_prepare_download_bytes(processed_text),
                file_name=out_name,
                mime="text/plain",
                disabled=not bool(processed_text),
            )

            st.session_state["last_input_text"] = input_text
            st.session_state["last_output_text"] = processed_text

    with tabs[1]:
        st.markdown(
            """
            ## Tentang AES-256 CBC Encryption

            **AES (Advanced Encryption Standard)** adalah algoritma enkripsi simetris yang digunakan secara luas
            untuk keamanan data. AES-256 menggunakan kunci 256-bit, yang merupakan ukuran kunci terbesar yang
            didukung oleh AES dan memberikan tingkat keamanan yang sangat tinggi.

            ### Mode CBC (Cipher Block Chaining)

            CBC adalah mode operasi yang menggunakan Initialization Vector (IV) untuk memastikan bahwa
            blok plaintext yang sama menghasilkan ciphertext yang berbeda. Setiap blok di-XOR dengan
            ciphertext blok sebelumnya sebelum dienkripsi.

            ### Fitur Keamanan

            - **PBKDF2 Key Derivation**: Password diturunkan menjadi kunci menggunakan PBKDF2 dengan SHA256
              dan 100,000 iterasi untuk meningkatkan keamanan terhadap brute-force attacks.
            - **Random Salt**: Setiap enkripsi menggunakan salt acak yang unik.
            - **Random IV**: Setiap enkripsi menggunakan IV acak yang berbeda, sehingga plaintext yang sama
              menghasilkan ciphertext yang berbeda.
            - **PKCS7 Padding**: Plaintext di-pad ke kelipatan 16 bytes (ukuran blok AES).

            ### Format Output

            Output enkripsi adalah string Base64 yang berisi:
            1. Salt (16 bytes)
            2. IV (16 bytes)
            3. Ciphertext (variable length)

            Semua komponen digabungkan dan di-encode ke Base64 untuk kemudahan penyimpanan dan transmisi.

            ### Cara Penggunaan

            1. **Enkripsi**: Masukkan plaintext dan password, klik "Encrypt", lalu simpan hasil ciphertext.
            2. **Dekripsi**: Masukkan ciphertext (Base64) dan password yang sama, klik "Decrypt".

            ⚠️ **Peringatan**: Simpan password Anda dengan aman. Jika password hilang atau salah,
            data tidak dapat didekripsi!
            """
        )


if __name__ == "__main__":
    run_app()
