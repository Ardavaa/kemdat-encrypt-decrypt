from __future__ import annotations

from io import BytesIO
from pathlib import Path
from typing import Callable, Dict, List, Optional, Tuple

import altair as alt
import streamlit as st
import importlib.util


def _load_caesar_functions() -> Tuple[Callable[[str, int], str], Callable[[str, int], str]]:
    """Dynamically load `caesar_encrypt` and `caesar_decrypt` from `encrypt-decrypt.py`.

    Returns:
        Tuple[Callable[[str, int], str], Callable[[str, int], str]]: encrypt and decrypt callables.

    Raises:
        RuntimeError: If the module or required functions cannot be loaded.
    """
    project_dir = Path(__file__).resolve().parent
    target = project_dir / "encrypt-decrypt.py"

    if not target.exists():
        raise RuntimeError(f"Tidak menemukan file: {target}")

    spec = importlib.util.spec_from_file_location("caesar_module", str(target))
    if spec is None or spec.loader is None:
        raise RuntimeError("Gagal memuat spesifikasi modul untuk encrypt-decrypt.py")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)  # type: ignore[assignment]

    try:
        encrypt = getattr(module, "caesar_encrypt")
        decrypt = getattr(module, "caesar_decrypt")
    except AttributeError as exc:
        raise RuntimeError("Fungsi caesar_encrypt/caesar_decrypt tidak ditemukan di encrypt-decrypt.py") from exc

    if not callable(encrypt) or not callable(decrypt):
        raise RuntimeError("Objek yang dimuat bukan fungsi yang dapat dipanggil")

    return encrypt, decrypt


def _compute_letter_frequency(text: str) -> Dict[str, int]:
    """Compute frequency of A-Z letters ignoring case.

    Args:
        text: Input text.

    Returns:
        Mapping of uppercase letters A-Z to counts.
    """
    counts: Dict[str, int] = {chr(ord("A") + i): 0 for i in range(26)}
    for ch in text:
        if ch.isalpha():
            counts[ch.upper()] += 1
    return counts


def _frequency_chart(freq: Dict[str, int], title: str) -> alt.Chart:
    """Create an Altair bar chart for letter frequencies.

    Args:
        freq: Mapping letter -> count.
        title: Chart title.

    Returns:
        Altair Chart object.
    """
    letters: List[str] = list(freq.keys())
    values: List[int] = [freq[k] for k in letters]
    data = {"Letter": letters, "Count": values}
    chart = (
        alt.Chart(alt.Data(values=[{"Letter": l, "Count": c} for l, c in zip(letters, values)]))
        .mark_bar(cornerRadiusTopLeft=3, cornerRadiusTopRight=3)
        .encode(
            x=alt.X("Letter:N", sort=letters),
            y=alt.Y("Count:Q"),
            tooltip=["Letter:N", "Count:Q"],
            color=alt.value("#4C78A8"),
        )
        .properties(title=title, width="container", height=220)
    )
    return chart


def _prepare_download_bytes(text: str) -> BytesIO:
    """Encode text to UTF-8 bytes for download.

    Args:
        text: Text to encode.

    Returns:
        BytesIO containing UTF-8 bytes.
    """
    return BytesIO(text.encode("utf-8"))


def run_app() -> None:
    """Run the Streamlit Caesar cipher app."""
    st.set_page_config(
        page_title="Caesar Encrypt/Decrypt",
        page_icon="🔐",
        layout="wide",
        menu_items={
            "Get help": "https://docs.streamlit.io/",
            "Report a bug": "https://github.com/",
            "About": "Caesar Cipher UI built with Streamlit.",
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
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="app-header">
            <h2 style="margin-bottom: 0.25rem;">🔐 Caesar Cipher Studio</h2>
            <div class="app-subtitle">Enkripsi dan dekripsi teks dengan antarmuka yang ramah dan interaktif.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    try:
        caesar_encrypt, caesar_decrypt = _load_caesar_functions()
    except RuntimeError as err:
        st.error(str(err))
        st.stop()

    with st.sidebar:
        st.header("Pengaturan")
        mode: str = st.radio("Mode", options=["Encrypt", "Decrypt"], horizontal=True)
        shift: int = st.slider("Shift", min_value=0, max_value=25, value=3, help="Jumlah pergeseran huruf (0-25)")
        input_method: str = st.selectbox("Sumber Input", options=["Teks", "File"], index=0)
        st.caption("Catatan: Non-huruf tidak berubah. Huruf besar/kecil dipertahankan.")

    st.write("")
    tabs = st.tabs(["Editor", "Analisis Frekuensi", "Tentang"])

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
            if input_text:
                if mode == "Encrypt":
                    processed_text = caesar_encrypt(input_text, shift)
                else:
                    processed_text = caesar_decrypt(input_text, shift)

            st.markdown("---")
            st.subheader("Hasil")
            st.text_area("Teks Keluaran", value=processed_text, height=180)

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

            st.session_state["last_input_text"] = input_text
            st.session_state["last_output_text"] = processed_text

        else:  # File
            uploaded = st.file_uploader("Unggah file teks (.txt, .md)", type=["txt", "md", "csv", "log"])
            input_text = ""
            file_name: Optional[str] = None
            if uploaded is not None:
                file_name = uploaded.name
                try:
                    input_text = uploaded.read().decode("utf-8")
                except UnicodeDecodeError:
                    try:
                        input_text = uploaded.read().decode("latin-1")
                    except Exception as exc:  # noqa: BLE001
                        st.error(f"Gagal membaca file: {exc}")
                        input_text = ""

            if input_text:
                st.caption("Pratinjau (2000 karakter pertama)")
                st.text_area("Isi File", value=input_text[:2000], height=180)

            processed_text = ""
            if input_text:
                if mode == "Encrypt":
                    processed_text = caesar_encrypt(input_text, shift)
                else:
                    processed_text = caesar_decrypt(input_text, shift)

            st.markdown("---")
            st.subheader("Hasil")
            st.text_area("Teks Keluaran", value=processed_text[:2000], height=180)
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
        st.caption("Perbandingan frekuensi huruf sebelum dan sesudah pemrosesan.")
        col_left, col_right = st.columns(2)
        input_text = st.session_state.get("last_input_text", "")
        output_text = st.session_state.get("last_output_text", "")
        with col_left:
            st.subheader("Input")
            freq_in = _compute_letter_frequency(input_text)
            st.altair_chart(_frequency_chart(freq_in, "Frekuensi Huruf (Input)"), use_container_width=True)
        with col_right:
            st.subheader("Output")
            freq_out = _compute_letter_frequency(output_text)
            st.altair_chart(_frequency_chart(freq_out, "Frekuensi Huruf (Output)"), use_container_width=True)

    with tabs[2]:
        st.markdown(
            """
            **Caesar cipher** menggeser setiap huruf sebesar `shift` pada alfabet.
            - Huruf non-alfabet tidak berubah.
            - Huruf besar/kecil dipertahankan seperti input.
            - `shift` 0 berarti teks tidak berubah.
            
            UI ini memuat fungsi langsung dari `encrypt-decrypt.py`, sehingga Anda dapat memodifikasi
            logika di file tersebut dan menyegarkan aplikasi untuk melihat perubahan.
            """
        )


if __name__ == "__main__":
    run_app()


