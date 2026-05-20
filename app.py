import streamlit as st
import pdfplumber

# Import fungsi dari modul lokal
from database import (
    init_db, create_new_session, get_all_sessions, 
    get_messages, save_message, update_session_title
)
from llm_handler import generate_response_stream

# ================= CSS KUSTOM =================
def inject_custom_css():
    st.markdown("""
        <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        [data-testid="stChatMessage"] {
            border-radius: 15px;
            padding: 15px;
            margin-bottom: 10px;
        }
        [data-testid="stChatInput"] {
            border-radius: 20px !important;
            border: 1px solid #4b5563 !important;
        }
        </style>
        """, unsafe_allow_html=True)

# ================= KONFIGURASI HALAMAN =================
st.set_page_config(page_title="Local AI Assistant", page_icon="🤖", layout="wide")

inject_custom_css()
init_db()

if "current_session_id" not in st.session_state:
    sessions = get_all_sessions()
    if sessions:
        st.session_state.current_session_id = sessions[0][0]
    else:
        st.session_state.current_session_id = create_new_session()

# ================= SIDEBAR =================
with st.sidebar:
    st.title("Chat History")
    
    if st.button("New Chat", use_container_width=True):
        st.session_state.current_session_id = create_new_session()
        st.rerun() 
    
    st.divider()
    
    sessions = get_all_sessions()
    
    # Sesuai dengan database.py versi awal (hanya 2 output)
    for session_id, title in sessions:
        btn_label = f"{title}" if session_id == st.session_state.current_session_id else title
        if st.button(btn_label, key=session_id, use_container_width=True):
            st.session_state.current_session_id = session_id
            st.rerun()

# ================= AREA CHAT =================
st.title("Asisten Qwen 2.5 (7B) Lokal")

chat_history = get_messages(st.session_state.current_session_id)

for msg in chat_history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ================= INPUT & LOGIKA =================
user_input = st.chat_input("Tanyakan sesuatu dan lampirkan PDF...", accept_file=True, file_type=["pdf"])

if user_input:
    if isinstance(user_input, str): 
        pesan_teks = user_input
        file_lampiran = []
    else:
        pesan_teks = getattr(user_input, "text", "")
        file_lampiran = getattr(user_input, "files", [])

    is_first_message = len(chat_history) == 0
    pdf_text_context = ""
    nama_file = ""

    if file_lampiran:
        try:
            uploaded_file = file_lampiran[0]
            nama_file = uploaded_file.name
            
            with pdfplumber.open(uploaded_file) as pdf:
                for page in pdf.pages:
                    extracted = page.extract_text()
                    if extracted:
                        pdf_text_context += extracted + "\n"
            
            # BATAS AMAN VRAM: Dikurangi menjadi 3000 agar GTX 1650 tidak crash (CUDA 500)
            pdf_text_context = pdf_text_context[:5000] 
        except Exception as e:
            st.error(f"Gagal membaca PDF: {e}")

    if not pesan_teks and nama_file:
        pesan_teks = "Tolong analisis dokumen ini."

    with st.chat_message("user"):
        st.markdown(pesan_teks)
        if nama_file:
            st.caption(f"📎 *Melampirkan dokumen: {nama_file}*")

    konten_db = pesan_teks
    if nama_file:
        konten_db += f"\n\n*[Melampirkan dokumen: {nama_file}]*"
    
    save_message(st.session_state.current_session_id, "user", konten_db)
    chat_history.append({"role": "user", "content": konten_db})
    
    konteks_terbatas = chat_history[-10:]

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        layar_teks = ""
        
        try:
            for chunk_text in generate_response_stream(konteks_terbatas, pdf_text_context, pesan_teks):
                full_response += chunk_text
                
                # Render ulang matematika untuk mencegah layar bocor
                layar_teks = full_response.replace("\\[", "$$").replace("\\]", "$$").replace("\\(", "$").replace("\\)", "$")
                
                message_placeholder.markdown(layar_teks + "▌")
                
            message_placeholder.markdown(layar_teks)
        except Exception as e:
            st.error(f"Terjadi kesalahan: {e}")
            layar_teks = "Maaf, terjadi kesalahan saat menyambungkan ke Ollama. Pastikan mesin Ollama sudah dinyalakan ulang."
        
    save_message(st.session_state.current_session_id, "assistant", layar_teks)

    if is_first_message:
        new_title = pesan_teks[:25] + "..." if len(pesan_teks) > 25 else pesan_teks
        update_session_title(st.session_state.current_session_id, new_title)
        st.rerun()