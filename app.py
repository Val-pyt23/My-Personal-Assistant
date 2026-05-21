import streamlit as st
import pdfplumber
import ollama

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
        /* ── Google Fonts ── */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

        /* ── Root Variables ── */
        :root {
          --bg-body:       #0b0f1a;
          --bg-sidebar:    #0e1320;
          --bg-card:       #141c2e;
          --bg-card2:      #1a2438;
          --bg-hover:      #1e2d4a;
          --bg-active:     #162040;
          --accent:        #4f6ef7;
          --accent-light:  #8899ff;
          --accent-glow:   rgba(79,110,247,0.28);
          --accent-border: rgba(79,110,247,0.40);
          --border:        rgba(255,255,255,0.07);
          --border2:       rgba(255,255,255,0.11);
          --text-1:        #e4eaf5;
          --text-2:        #8b96b5;
          --text-3:        #4a5578;
          --text-4:        #2b3455;
          --green:         #20d9a0;
          --green-glow:    rgba(32,217,160,0.25);
          --red:           #f06c6c;
          --r-sm: 8px; --r-md: 13px; --r-lg: 18px; --r-full: 9999px;
        }

        /* ── Global Reset ── */
        *, *::before, *::after { box-sizing: border-box; }

        html, body,
        [data-testid="stApp"],
        [data-testid="stAppViewContainer"],
        .main {
          background: var(--bg-body) !important;
          font-family: 'Inter', -apple-system, sans-serif !important;
          color: var(--text-1) !important;
        }

        /* ── Hide Streamlit chrome ── */
        #MainMenu, footer,
        [data-testid="stToolbar"],
        [data-testid="stDecoration"],
        [data-testid="stStatusWidget"],
        .stDeployButton { display: none !important; }

        /* ── Remove main padding ── */
        .main .block-container {
          padding-top: 1.5rem !important;
          padding-left: 2rem !important;
          padding-right: 2rem !important;
          max-width: 860px !important;
          margin: 0 auto !important;
        }

        /* ════════════════════════════
           SIDEBAR
        ════════════════════════════ */
        [data-testid="stSidebar"] {
          background: var(--bg-sidebar) !important;
          border-right: 1px solid var(--border2) !important;
          min-width: 260px !important;
          max-width: 280px !important;
        }
        [data-testid="stSidebar"] > div:first-child,
        [data-testid="stSidebarContent"] {
          padding: 0 !important;
          background: var(--bg-sidebar) !important;
        }
        [data-testid="stSidebar"] [data-testid="stVerticalBlock"] {
          gap: 2px !important;
        }
        [data-testid="stSidebar"] [data-testid="stVerticalBlock"] > div {
          padding: 0 8px !important;
        }

        /* Sidebar title (st.title) */
        [data-testid="stSidebar"] h1 {
          font-size: 15px !important;
          font-weight: 700 !important;
          color: var(--text-1) !important;
          padding: 20px 12px 14px !important;
          margin: 0 !important;
          letter-spacing: -0.3px !important;
          border-bottom: 1px solid var(--border2) !important;
          font-family: 'Inter', sans-serif !important;
          display: flex !important;
          align-items: center !important;
          gap: 8px !important;
        }
        [data-testid="stSidebar"] h1::before {
          content: '✦';
          font-size: 16px;
          background: linear-gradient(135deg, var(--accent), #9b5cf6);
          -webkit-background-clip: text;
          -webkit-text-fill-color: transparent;
          background-clip: text;
        }

        /* New Chat button */
        [data-testid="stSidebar"] .stButton > button {
          background: transparent !important;
          color: var(--text-2) !important;
          border: none !important;
          border-radius: var(--r-sm) !important;
          padding: 8px 12px !important;
          text-align: left !important;
          font-size: 13px !important;
          font-weight: 400 !important;
          width: 100% !important;
          transition: background .15s, color .15s !important;
          font-family: 'Inter', sans-serif !important;
          white-space: nowrap !important;
          overflow: hidden !important;
          text-overflow: ellipsis !important;
        }
        [data-testid="stSidebar"] .stButton > button:hover {
          background: var(--bg-hover) !important;
          color: var(--text-1) !important;
        }
        /* First button = New Chat — styled as accent pill */
        [data-testid="stSidebar"] [data-testid="stVerticalBlock"] > div:nth-child(2) .stButton > button {
          background: linear-gradient(135deg, var(--accent), #7c3aed) !important;
          color: #fff !important;
          border-radius: var(--r-md) !important;
          font-weight: 600 !important;
          font-size: 13px !important;
          padding: 10px 16px !important;
          box-shadow: 0 4px 18px var(--accent-glow) !important;
          margin: 10px 0 4px !important;
        }
        [data-testid="stSidebar"] [data-testid="stVerticalBlock"] > div:nth-child(2) .stButton > button:hover {
          filter: brightness(1.1) !important;
          box-shadow: 0 6px 24px var(--accent-glow) !important;
          transform: translateY(-1px) !important;
        }

        /* Sidebar divider */
        [data-testid="stSidebar"] hr {
          border-color: var(--border2) !important;
          margin: 4px 0 !important;
        }

        /* ════════════════════════════
           MAIN TITLE
        ════════════════════════════ */
        .main h1 {
          font-size: 22px !important;
          font-weight: 800 !important;
          color: var(--text-1) !important;
          letter-spacing: -0.5px !important;
          margin-bottom: 0 !important;
          padding: 4px 0 16px !important;
          font-family: 'Inter', sans-serif !important;
          border-bottom: 1px solid var(--border) !important;
          display: flex !important;
          align-items: center !important;
          gap: 10px !important;
        }

        /* ════════════════════════════
           CHAT MESSAGES
        ════════════════════════════ */
        [data-testid="stChatMessage"] {
          background: transparent !important;
          border: none !important;
          border-radius: 0 !important;
          padding: 4px 0 !important;
          margin-bottom: 0 !important;
          gap: 10px !important;
        }

        /* Avatars */
        [data-testid="chatAvatarIcon-user"],
        [data-testid="chatAvatarIcon-assistant"] {
          border-radius: 50% !important;
          width: 32px !important;
          height: 32px !important;
          flex-shrink: 0 !important;
          font-size: 14px !important;
          display: grid !important;
          place-items: center !important;
          align-self: flex-end !important;
        }
        [data-testid="chatAvatarIcon-assistant"] {
          background: linear-gradient(135deg, var(--accent), #9b5cf6) !important;
          box-shadow: 0 0 12px var(--accent-glow) !important;
        }
        [data-testid="chatAvatarIcon-user"] {
          background: linear-gradient(135deg, #1d4ed8, #3b5cf6) !important;
        }

        /* AI bubble */
        [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"])
          [data-testid="stMarkdownContainer"],
        [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"])
          .stMarkdown {
          background: var(--bg-card) !important;
          border: 1px solid var(--border2) !important;
          border-radius: 4px 16px 16px 16px !important;
          padding: 12px 16px !important;
          font-size: 13.5px !important;
          line-height: 1.75 !important;
          color: var(--text-1) !important;
          box-shadow: 0 2px 12px rgba(0,0,0,0.3) !important;
        }

        /* User bubble */
        [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"])
          [data-testid="stMarkdownContainer"],
        [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"])
          .stMarkdown {
          background: linear-gradient(135deg, #2d46d6, #3d5af1) !important;
          border: 1px solid rgba(79,110,247,0.2) !important;
          border-radius: 16px 4px 16px 16px !important;
          padding: 12px 16px !important;
          font-size: 13.5px !important;
          line-height: 1.75 !important;
          color: #fff !important;
          box-shadow: 0 2px 16px rgba(61,90,241,0.35) !important;
        }

        /* ════════════════════════════
           CHAT INPUT
        ════════════════════════════ */
        [data-testid="stBottom"] {
          background: linear-gradient(to top, var(--bg-body) 60%, transparent) !important;
          padding-bottom: 12px !important;
        }
        [data-testid="stChatInput"] {
          background: var(--bg-card) !important;
          border: 1.5px solid var(--border2) !important;
          border-radius: 16px !important;
          box-shadow: 0 4px 24px rgba(0,0,0,0.4) !important;
          transition: border-color .2s, box-shadow .2s !important;
        }
        [data-testid="stChatInput"]:focus-within {
          border-color: var(--accent-border) !important;
          box-shadow: 0 0 0 3px var(--accent-glow), 0 4px 24px rgba(0,0,0,0.4) !important;
        }
        [data-testid="stChatInput"] textarea {
          color: var(--text-1) !important;
          background: transparent !important;
          font-family: 'Inter', sans-serif !important;
          font-size: 13.5px !important;
        }
        [data-testid="stChatInput"] textarea::placeholder {
          color: var(--text-3) !important;
        }
        [data-testid="stChatInputSubmitButton"] button {
          background: linear-gradient(135deg, var(--accent), #7c3aed) !important;
          border: none !important;
          border-radius: 10px !important;
          box-shadow: 0 0 14px var(--accent-glow) !important;
          transition: transform .2s, box-shadow .2s !important;
        }
        [data-testid="stChatInputSubmitButton"] button:hover {
          transform: scale(1.06) !important;
          box-shadow: 0 0 22px var(--accent-glow) !important;
        }
        [data-testid="stChatInputFileButton"] button {
          background: var(--bg-card2) !important;
          border: 1px solid var(--border2) !important;
          border-radius: 10px !important;
          color: var(--accent-light) !important;
          transition: background .2s !important;
        }
        [data-testid="stChatInputFileButton"] button:hover {
          background: var(--bg-hover) !important;
          border-color: var(--accent-border) !important;
        }

        /* ════════════════════════════
           CODE BLOCKS
        ════════════════════════════ */
        code {
          background: rgba(79,110,247,0.12) !important;
          color: #93a4ff !important;
          padding: 2px 6px !important;
          border-radius: 5px !important;
          font-size: 12.5px !important;
          font-family: 'JetBrains Mono', 'Fira Code', monospace !important;
        }
        pre code { background: transparent !important; padding: 0 !important; }
        pre {
          background: #060b15 !important;
          border: 1px solid var(--border2) !important;
          border-radius: var(--r-md) !important;
          padding: 14px 16px !important;
          overflow-x: auto !important;
        }

        /* ════════════════════════════
           MISC
        ════════════════════════════ */
        ::-webkit-scrollbar { width: 4px; }
        ::-webkit-scrollbar-track { background: transparent; }
        ::-webkit-scrollbar-thumb {
          background: var(--bg-hover);
          border-radius: 3px;
        }
        ::-webkit-scrollbar-thumb:hover { background: var(--accent); }

        .stAlert {
          border-radius: var(--r-md) !important;
          background: var(--bg-card) !important;
          border: 1px solid var(--border2) !important;
          font-family: 'Inter', sans-serif !important;
        }
        .stSpinner > div { border-top-color: var(--accent) !important; }

        /* Caption (lampiran PDF) */
        [data-testid="stChatMessage"] .stMarkdown small,
        [data-testid="stCaptionContainer"] {
          color: rgba(255,255,255,0.5) !important;
          font-size: 11.5px !important;
        }

        /* Typing indicator cursor */
        @keyframes cursor-blink {
          0%,100%{ opacity:1; } 50%{ opacity:0; }
        }

        /* ════════════════════════════
           SIDEBAR TOGGLE — sembunyikan hanya tombol close di dalam sidebar
        ════════════════════════════ */
        /* Sembunyikan tombol collapse di DALAM sidebar */
        [data-testid="stSidebarCollapseButton"] { display: none !important; }

        /* ════════════════════════════
           HOMEPAGE START BUTTON
        ════════════════════════════ */
        div[data-testid="stMainBlockContainer"] .hp-start-btn-wrap {
          display: flex;
          justify-content: center;
          margin-top: -8px;
        }
        /* Style the homepage CTA button */
        [data-testid="stMain"] [data-testid="stVerticalBlock"] > div:has(button[kind="primary"]) {
          display: flex;
          justify-content: center;
        }
        /* Override start button styling */
        .hp-cta button {
          background: linear-gradient(135deg, #4f6ef7, #9b5cf6) !important;
          color: #fff !important;
          border: none !important;
          border-radius: 14px !important;
          font-size: 15px !important;
          font-weight: 600 !important;
          padding: 14px 36px !important;
          min-width: 220px !important;
          box-shadow: 0 6px 28px rgba(79,110,247,0.40) !important;
          transition: filter .2s, transform .2s, box-shadow .2s !important;
          font-family: 'Inter', sans-serif !important;
          letter-spacing: -0.2px !important;
        }
        .hp-cta button:hover {
          filter: brightness(1.1) !important;
          transform: translateY(-2px) !important;
          box-shadow: 0 10px 36px rgba(79,110,247,0.50) !important;
        }

        /* ════════════════════════════
           HOMEPAGE
        ════════════════════════════ */
        .homepage {
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          min-height: 80vh;
          text-align: center;
          gap: 18px;
          padding: 40px 24px;
          animation: fadeIn .5s ease;
        }
        @keyframes fadeIn {
          from { opacity:0; transform: translateY(14px); }
          to   { opacity:1; transform: translateY(0); }
        }
        .hp-orb-wrap { position: relative; margin-bottom: 6px; }
        .hp-orb {
          width: 88px; height: 88px;
          background: linear-gradient(135deg, #4f6ef7, #9b5cf6);
          border-radius: 26px;
          display: grid; place-items: center;
          font-size: 40px;
          box-shadow: 0 0 60px rgba(79,110,247,0.35), 0 0 120px rgba(79,110,247,0.12);
          animation: hp-float 3.5s ease-in-out infinite;
        }
        .hp-ring {
          position: absolute; inset: -10px;
          border-radius: 36px;
          border: 2px solid rgba(79,110,247,0.20);
          animation: hp-pulse 3.5s ease-in-out infinite;
        }
        .hp-ring2 {
          position: absolute; inset: -20px;
          border-radius: 46px;
          border: 1px solid rgba(79,110,247,0.09);
          animation: hp-pulse 3.5s ease-in-out infinite .5s;
        }
        @keyframes hp-float {
          0%,100%{ transform: translateY(0) rotate(0deg); }
          50%{ transform: translateY(-10px) rotate(2deg); }
        }
        @keyframes hp-pulse {
          0%,100%{ opacity:1; transform:scale(1); }
          50%{ opacity:.5; transform:scale(1.04); }
        }
        .hp-title {
          font-size: 32px; font-weight: 800;
          color: #e4eaf5; letter-spacing: -0.7px;
          line-height: 1.2; font-family: 'Inter', sans-serif;
        }
        .hp-title span {
          background: linear-gradient(90deg, #8899ff, #c084fc);
          -webkit-background-clip: text;
          -webkit-text-fill-color: transparent;
          background-clip: text;
        }
        .hp-sub {
          font-size: 14.5px; color: #8b96b5;
          line-height: 1.75; max-width: 480px;
          font-family: 'Inter', sans-serif;
        }
        .hp-chips {
          display: flex; flex-wrap: wrap;
          gap: 10px; justify-content: center;
          margin-top: 6px;
        }
        .hp-chip {
          background: #141c2e;
          border: 1px solid rgba(255,255,255,0.10);
          border-radius: 20px;
          padding: 9px 18px;
          font-size: 13px; color: #8b96b5;
          font-family: 'Inter', sans-serif;
          transition: border-color .2s, color .2s, background .2s, transform .2s;
        }
        .hp-chip:hover {
          border-color: rgba(79,110,247,0.45);
          color: #8899ff;
          background: rgba(79,110,247,0.08);
          transform: translateY(-2px);
        }
        .hp-divider {
          width: 100%; max-width: 400px;
          border-top: 1px solid rgba(255,255,255,0.07);
          margin: 4px 0;
        }
        .hp-model-tag {
          display: flex; align-items: center; gap: 8px;
          background: #141c2e;
          border: 1px solid rgba(255,255,255,0.10);
          border-radius: 999px;
          padding: 8px 18px;
          font-size: 12px; color: #4a5578;
          font-family: 'Inter', sans-serif;
        }
        .hp-dot {
          width: 7px; height: 7px;
          background: #20d9a0;
          border-radius: 50%;
          box-shadow: 0 0 6px rgba(32,217,160,0.4);
          animation: blink-dot 2.4s ease-in-out infinite;
          flex-shrink: 0;
        }
        @keyframes blink-dot {
          0%,100%{opacity:1;} 50%{opacity:.35;}
        }
        </style>
        """, unsafe_allow_html=True)

# ================= KONFIGURASI HALAMAN =================
st.set_page_config(page_title="Local AI Assistant", page_icon="", layout="wide", initial_sidebar_state="expanded")

inject_custom_css()

# ── JavaScript: paksa sidebar selalu terbuka (Versi Anti-Macet) ──
st.markdown("""
<script>
(function forceSidebarOpen() {
    // Cari semua elemen tombol di halaman
    var buttons = document.querySelectorAll('button');
    buttons.forEach(function(btn) {
        // Jika menemukan tombol dengan ikon pembuka atau label "Show sidebar"
        if (btn.innerText === "›" || btn.getAttribute('aria-label') === "Show sidebar") {
            btn.click();
        }
    });
    
    // Sembunyikan tombol close di dalam sidebar agar user tidak bisa menutupnya lagi
    var collapseBtn = document.querySelector('[data-testid="stSidebarCollapseButton"]');
    if (collapseBtn) {
        collapseBtn.style.display = 'none';
    }
    
    // Ulangi setiap 500ms secara senyap
    setTimeout(forceSidebarOpen, 500);
}());
</script>
""", unsafe_allow_html=True)

init_db()

if "current_session_id" not in st.session_state:
    sessions = get_all_sessions()
    if sessions:
        st.session_state.current_session_id = sessions[0][0]
    else:
        st.session_state.current_session_id = create_new_session()

# Page routing: 'home' saat pertama buka, 'chat' setelah masuk percakapan
if "page" not in st.session_state:
    st.session_state.page = "home"

# ================= SIDEBAR =================
with st.sidebar:
    st.title("Chat History")
    
    # 1. Tombol New Chat di paling atas (Diberi key khusus agar aman)
    if st.button("New Chat", use_container_width=True, key="btn_new_chat_sidebar"):
        st.session_state.current_session_id = create_new_session()
        st.session_state.page = "chat"  
        st.rerun()
    
    st.divider()
    
    # 2. Tampilkan daftar riwayat chat
    sessions = get_all_sessions()
    for session_id, title in sessions:
        btn_label = f"{title}" if session_id == st.session_state.current_session_id else title
        if st.button(btn_label, key=session_id, use_container_width=True):
            st.session_state.current_session_id = session_id
            st.session_state.page = "chat"  
            st.rerun()
            
    # 3. Beri garis pembatas antara riwayat dan menu model
    st.divider()

    # 4. Pendeteksi model dinamis
    try:
        daftar_model_lokal = [model['name'] for model in ollama.list()['models']]
    except Exception:
        daftar_model_lokal = ["qwen2.5:7b", "llama3.2:1b"]
        
    tag_model_ollama = st.selectbox(
        "Pilih Model:",
        daftar_model_lokal,
        label_visibility="collapsed"
    )

# ================= ROUTING: HOME vs CHAT =================
if st.session_state.page == "home":
    # ── HOMEPAGE ──
    from datetime import datetime
    now_hour = datetime.now().hour
    greeting = "Selamat pagi" if now_hour < 12 else ("Selamat siang" if now_hour < 15 else ("Selamat sore" if now_hour < 18 else "Selamat malam"))

    st.markdown(f"""
    <div class="homepage">
        <div class="hp-orb-wrap">
            <div class="hp-ring2"></div>
            <div class="hp-ring"></div>
            <div class="hp-orb">✦</div>
        </div>
        <div class="hp-title">{greeting}! 👋<br><span>Ada yang bisa saya bantu?</span></div>
        <div class="hp-sub">
            Saya adalah asisten AI pribadi Anda yang berjalan sepenuhnya di perangkat lokal
            menggunakan model <strong style="color:#8899ff;">Qwen 2.5 (7B)</strong> via Ollama.
            Mulai percakapan baru atau pilih riwayat di sidebar kiri.
        </div>
        <div class="hp-chips">
            <div class="hp-chip">📄 Analisis Dokumen PDF</div>
            <div class="hp-chip">💡 Jawab Pertanyaan</div>
            <div class="hp-chip">✍️ Bantu Menulis</div>
            <div class="hp-chip">🔢 Data &amp; Statistika</div>
            <div class="hp-chip">🌐 Terjemahkan Teks</div>
            <div class="hp-chip">🐍 Kode Python</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Tombol CTA: Mulai Chat ──
    col_l, col_c, col_r = st.columns([1, 2, 1])
    with col_c:
        st.markdown('<div class="hp-cta">', unsafe_allow_html=True)
        if st.button("✦  Mulai Percakapan Baru", key="hp_start_btn", use_container_width=True):
            st.session_state.current_session_id = create_new_session()
            st.session_state.page = "chat"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    # ── Model tag ──
    st.markdown("""
    <div style="display:flex;justify-content:center;margin-top:16px;">
        <div class="hp-model-tag">
            <span class="hp-dot"></span>
            Qwen 2.5 (7B) &nbsp;·&nbsp; Ollama &nbsp;·&nbsp; Running Locally
        </div>
    </div>
    """, unsafe_allow_html=True)

else:
    # ================= AREA CHAT =================
    st.title("Hai")

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
            btn_placeholder = st.empty() 
            
            # Variabel penampung untuk menyelamatkan teks jika distop mendadak
            st.session_state.temp_layar_teks = ""
            
            # Fungsi Callback: Dieksekusi seketika SAAT tombol stop ditekan
            def stop_generation_callback():
                if st.session_state.temp_layar_teks:
                    save_message(st.session_state.current_session_id, "assistant", st.session_state.temp_layar_teks)
            
            # Tampilkan tombol Stop melayang di atas teks
            with btn_placeholder.container():
                st.button("Stop Generate", on_click=stop_generation_callback, key=f"stop_btn_{len(chat_history)}")
            
            full_response = ""
            layar_teks = ""
            
            try:
                for chunk_text in generate_response_stream(konteks_terbatas, pdf_text_context, pesan_teks,tag_model_ollama):
                    full_response += chunk_text
                    
                    # Render ulang matematika untuk mencegah layar bocor
                    layar_teks = full_response.replace("\\[", "$$").replace("\\]", "$$").replace("\\(", "$").replace("\\)", "$")
                    
                    # Update memori sementara secara real-time
                    st.session_state.temp_layar_teks = layar_teks
                    
                    message_placeholder.markdown(layar_teks + "▌")
                    
                message_placeholder.markdown(layar_teks)
                
                # Simpan ke database jika AI selesai menjawab dengan normal (TIDAK distop)
                save_message(st.session_state.current_session_id, "assistant", layar_teks)
                
            except Exception as e:
                st.error(f"Terjadi kesalahan: {e}")
                save_message(st.session_state.current_session_id, "assistant", "Maaf, terjadi kesalahan saat menyambungkan ke Ollama. Pastikan mesin Ollama sudah dinyalakan ulang.")
                
            # Hancurkan/sembunyikan tombol stop setelah AI selesai menjawab
            btn_placeholder.empty()

        if is_first_message:
            new_title = pesan_teks[:25] + "..." if len(pesan_teks) > 25 else pesan_teks
            update_session_title(st.session_state.current_session_id, new_title)
            st.rerun()