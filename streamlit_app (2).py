import html as html_mod
import streamlit as st
import streamlit.components.v1 as components
import base64
import os
from data import compounds_data

# konversi file gambar lokal menjadi string base64 untuk disematkan ke dalam tag HTML
def get_base64_image(path):
    if os.path.exists(path):
        with open(path, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode("utf-8")
    return ""

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
bg_path = os.path.join(BASE_DIR, "static", "assets", "background_search.jpeg")
bg_base64 = get_base64_image(bg_path)

# Mengatur tampilan halaman web di Streamlit (judul, ikon, tata letak)
st.set_page_config(
    page_title="Chemical Safety Database",
    page_icon="🧪",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# Menentukan kelas CSS (warna chip) berdasarkan kata kunci sifat bahaya zat kimia
def get_hazard_class(hz):
    low = hz.lower()
    if "korosif" in low:
        return "chip-korosif"
    if "terbakar" in low:
        return "chip-terbakar"
    if "oksidator" in low:
        return "chip-oksidator"
    if "beracun" in low or "toksik" in low:
        return "chip-toksik"
    if "iritan" in low or "iritasi" in low:
        return "chip-iritan"
    if "karsinogenik" in low or "karsinogen" in low:
        return "chip-karsinogenik"
    if "eksplosif" in low or "meledak" in low:
        return "chip-eksplosif"
    return "chip-neutral"

# Membuat elemen HTML berupa chip/tag penanda sifat bahaya zat kimia
def build_chips_html(hazards, font_size="10px"):
    chips = ""
    for h in hazards:
        cls = get_hazard_class(h)
        chips += f'<span class="chip {cls}" style="font-size:{font_size}">{h}</span>'
    return f'<div class="chips-wrapper">{chips}</div>'

# Menyusun struktur HTML kartu (card) ringkasan zat kimia untuk halaman pencarian
def build_card_html(compound):
    chips = build_chips_html(compound["hazards"])
    return f'''<div class="chem-card">
  <div class="card-top-strip"></div>
  <div class="card-body">
    <div class="card-name">{compound["name"]}</div>
    <div><span class="formula-tag">{compound["formula"]}</span></div>
    <div class="card-divider">
      <div class="label-caps">Warna / Wujud</div>
      <div class="card-wujud">{compound["wujud"]}</div>
    </div>
    {chips}
  </div>
</div>'''   

# Memfilter daftar zat kimia berdasarkan kecocokan query pencarian pada nama, rumus, atau bahaya
def filter_data(query):
    if not query:
        return []
    q = query.lower()
    return [
        c for c in compounds_data
        if q in c["name"].lower()
        or q in c["formula"].lower()
        or any(q in h.lower() for h in c["hazards"])
    ]

# Gaya CSS global (ALL_CSS) mencakup:
# - Font eksternal (Hanken Grotesk & JetBrains Mono)
# - Penyembunyian elemen default Streamlit (header, footer, decoration, dll.)
# - Tata letak dan kustomisasi input text pencarian beserta ikon search
# - Gaya visual untuk chip bahaya, kartu zat kimia (chem-card beserta efek hover-nya)
# - Gaya button sekunder/tertiary Streamlit
# - Komponen modal detail (nama, rumus, grid properti, blok MSDS, dan tombol link)
# - Tata letak gambar rumus bangun (struktur molekul)
# - Tampilan halaman kosong (search-empty) ketika data tidak ditemukan
ALL_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Hanken+Grotesk:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;700&display=swap');

header, footer, .stDeployButton,
div[data-testid="stDecoration"],
div[data-testid="stStatusWidget"],
div[data-testid="stToolbar"] {
    visibility: hidden !important;
    height: 0px !important;
    padding: 0 !important;
    margin: 0 !important;
    position: fixed !important;
}

.stApp {
    font-family: 'Hanken Grotesk', sans-serif !important;
}

div[data-testid="stAppViewBlockContainer"],
div[data-testid="stMainBlockContainer"],
div[data-testid="stVerticalBlock"],
div[data-testid="stVerticalBlockBorderWrapper"],
.main {
    background-color: transparent !important;
    background: transparent !important;
}

div[data-testid="stTextInput"] label {
    display: none !important;
}
div[data-testid="stTextInput"] input {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 14px !important;
    height: 48px !important;
    border: 1px solid #bdc8d2 !important;
    border-radius: 8px !important;
    color: #1a1c1e !important;
    background: white !important;
    background-image: url('data:image/svg+xml;base64,PHN2ZyB4bWxucz0naHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmcnIGZpbGw9J25vbmUnIHN0cm9rZT0nIzAwNjU5MScgc3Ryb2tlLXdpZHRoPScyJyB2aWV3Qm94PScwIDAgMjQgMjQnPjxwYXRoIHN0cm9rZS1saW5lY2FwPSdyb3VuZCcgc3Ryb2tlLWxpbmVqb2luPSdyb3VuZCcgZD0nTTIxIDIxbC02LTZtMi01YTcgNyAwIDExLTE0IDAgNyA3IDAgMDExNCAweicvPjwvc3ZnPg==') !important;
    background-repeat: no-repeat !important;
    background-position: 14px center !important;
    background-size: 20px 20px !important;
    padding-left: 44px !important;
    padding-right: 16px !important;
}
div[data-testid="stTextInput"] input:focus {
    border-color: #006591 !important;
    box-shadow: 0 0 0 3px rgba(0,101,145,0.15) !important;
}
div[data-testid="stTextInput"] input::placeholder {
    color: #8e98a2 !important;
    font-family: 'Hanken Grotesk', sans-serif !important;
    font-size: 14px !important;
}

.chips-wrapper { display: flex; flex-wrap: wrap; gap: 6px; }
.chip {
    padding: 4px 8px; border-radius: 4px;
    display: inline-flex; align-items: center; white-space: nowrap;
    font-family: 'Hanken Grotesk', sans-serif;
    font-weight: 700; letter-spacing: 0.08em; text-transform: uppercase;
    line-height: 16px;
}
.chip-neutral      { background: #f3f3f6; color: #3e4851; }
.chip-korosif      { background: #ffdad6; color: #93000a; }
.chip-terbakar     { background: #fff0d6; color: #7a4100; }
.chip-oksidator    { background: #fff0d6; color: #7a4100; }
.chip-toksik       { background: #f0e6ff; color: #4a007a; }
.chip-iritan       { background: #ffefd6; color: #6b4e00; }
.chip-karsinogenik { background: #ffd6e0; color: #8c0032; }
.chip-eksplosif    { background: #ffdcc8; color: #832200; }

.chem-card {
    border: 1px solid #e2e2e5; border-radius: 12px;
    background: white; overflow: hidden; cursor: pointer;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.03) !important;
    transition: all 150ms ease-in-out !important;
}
.chem-card:hover {
    background: #f9f9fc; border-color: #006591;
    box-shadow: 0 6px 16px rgba(0, 101, 145, 0.08) !important;
}
.card-top-strip {
    height: 8px;
    background: linear-gradient(135deg, #006591, #004c6e);
}
.card-body {
    padding: 16px; display: flex; flex-direction: column; gap: 12px;
}
.card-name {
    font-family: 'Hanken Grotesk', sans-serif;
    font-weight: 700; font-size: 16px; color: #1a1c1e; margin: 0;
}
.formula-tag {
    font-family: 'JetBrains Mono', monospace;
    font-size: 14px; font-weight: 500; color: #006591;
    background: #f3f3f6; padding: 4px 10px; border-radius: 4px;
    display: inline-block; letter-spacing: 0.03em;
}
.card-divider { border-top: 1px solid #e2e2e5; padding-top: 10px; }
.label-caps {
    font-family: 'Hanken Grotesk', sans-serif;
    font-size: 12px; font-weight: 700; letter-spacing: 0.08em;
    text-transform: uppercase; color: #6e7882; margin-bottom: 2px;
}
.card-wujud {
    font-family: 'Hanken Grotesk', sans-serif;
    font-size: 14px; color: #1a1c1e;
}

button[data-testid="stBaseButton-tertiary"] {
    font-family: 'Hanken Grotesk', sans-serif !important;
    font-size: 13px !important;
    font-weight: 600 !important;
    color: #006591 !important;
    background-color: white !important;
    border: 1px solid #bdc8d2 !important;
    border-radius: 8px !important;
    margin-top: 14px !important;
    padding: 8px 16px !important;
    transition: all 150ms ease-in-out !important;
}
button[data-testid="stBaseButton-tertiary"]:hover {
    background-color: #006591 !important;
    border-color: #006591 !important;
    color: white !important;
}

.modal-formula {
    font-family: 'JetBrains Mono', monospace;
    font-size: 24px; font-weight: 700; color: #006591;
    letter-spacing: 0.03em;
}
.modal-name {
    font-family: 'Hanken Grotesk', sans-serif;
    font-size: 20px; font-weight: 600; color: #1a1c1e;
    margin-top: 4px;
}
.stat-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
.stat-cell { background: #f3f3f6; border-radius: 6px; padding: 12px; }
.stat-label {
    font-family: 'Hanken Grotesk', sans-serif;
    font-size: 12px; font-weight: 700; letter-spacing: 0.08em;
    text-transform: uppercase; color: #6e7882; margin-bottom: 4px;
}
.stat-value-formula {
    font-family: 'JetBrains Mono', monospace;
    font-size: 15px; font-weight: 500; color: #006591;
}
.stat-value {
    font-family: 'Hanken Grotesk', sans-serif;
    font-size: 14px; color: #1a1c1e;
}

.msds-block { border-radius: 0 6px 6px 0; padding: 12px; }
.msds-block-title {
    font-family: 'Hanken Grotesk', sans-serif;
    font-size: 12px; font-weight: 700; letter-spacing: 0.08em;
    text-transform: uppercase; margin-bottom: 8px;
}
.msds-block-content {
    font-family: 'Hanken Grotesk', sans-serif;
    font-size: 14px; line-height: 1.6; color: #1a1c1e;
}
.msds-link-button {
    display: inline-flex; align-items: center; justify-content: center;
    gap: 10px; background-color: #006591; color: white !important;
    padding: 14px 20px; border-radius: 8px; text-decoration: none;
    font-family: 'Hanken Grotesk', sans-serif; font-size: 14px;
    font-weight: 600;
    width: 100%;
    box-sizing: border-box;
}
.msds-link-button:hover {
    background-color: #004c6e; color: white !important;
}

.rumus-bangun-wrapper {
    background: #f3f3f6; border-radius: 12px; padding: 20px;
    display: flex; justify-content: center; border: 1px solid #bdc8d2;
}
.rumus-bangun-wrapper img { max-height: 140px; object-fit: contain; }

.search-empty {
    display: flex; flex-direction: column; align-items: center;
    padding: 80px 20px; text-align: center;
}
.search-empty-icon  { font-size: 48px; margin-bottom: 16px; }
.search-empty-title {
    font-family: 'Hanken Grotesk', sans-serif;
    font-size: 18px; font-weight: 700; color: #1a1c1e; margin-bottom: 8px;
}
.search-empty-desc {
    font-family: 'Hanken Grotesk', sans-serif;
    font-size: 14px; color: #6e7882; max-width: 300px; line-height: 1.5;
}
</style>
"""

# Gaya CSS Landing Page (LANDING_CSS) mencakup:
# - Background halaman utama dengan warna gelap (#001e32)
# - Gambar latar belakang landing page dengan efek linear-gradient overlay
# - Penyesuaian padding dan lebar maksimum container utama (1200px) agar terpusat
LANDING_CSS = """
<style>
.stApp {
    background-color: #001e32 !important;
}
div[data-testid="stAppViewContainer"] {
    background-color: #001e32 !important;
    background-image: linear-gradient(rgba(0, 30, 50, 0.55), rgba(0, 30, 50, 0.55)), url('data:image/jpeg;base64,BG_IMAGE_BASE64') !important;
    background-size: cover !important;
    background-position: center !important;
    background-repeat: no-repeat !important;
    background-attachment: fixed !important;
}

div[data-testid="stAppViewBlockContainer"],
div[data-testid="stMainBlockContainer"] {
    padding-top: 0 !important;
    padding-bottom: 0 !important;
    max-width: 1200px !important;
    margin: 0 auto !important;
}
</style>
"""

# Gaya CSS Halaman Pencarian (SEARCH_CSS) mencakup:
# - Background halaman hasil pencarian dengan warna terang (#f9f9fc)
# - Gambar latar belakang yang diperjelas/diterangkan menggunakan linear-gradient overlay putih dominan
# - Penyesuaian padding bawah dan lebar maksimum container utama agar rapi saat menampilkan hasil
SEARCH_CSS = """
<style>
.stApp {
    background-color: #f9f9fc !important;
}
div[data-testid="stAppViewContainer"] {
    background-color: #f9f9fc !important;
    background-image: linear-gradient(rgba(249, 249, 252, 0.9), rgba(249, 249, 252, 0.9)), url('data:image/jpeg;base64,BG_IMAGE_BASE64') !important;
    background-size: cover !important;
    background-position: center !important;
    background-repeat: no-repeat !important;
    background-attachment: fixed !important;
}

div[data-testid="stAppViewBlockContainer"],
div[data-testid="stMainBlockContainer"] {
    padding-top: 0 !important;
    padding-bottom: 40px !important;
    max-width: 1200px !important;
    margin: 0 auto !important;
}
</style>
"""

# Menampilkan modal dialog detail zat kimia berdasarkan ID yang dipilih
@st.dialog("Detail Zat Kimia", width="large")
def show_detail(compound_id):
    # 1. Cari data zat kimia berdasarkan ID, tampilkan error jika tidak ada
    compound = next((c for c in compounds_data if c["id"] == compound_id), None)
    if not compound:
        st.error("Data tidak ditemukan")
        return

    # 2. Tampilkan nama dan rumus kimia utama di bagian atas modal
    st.markdown(
        f'<div style="margin-bottom:16px">'
        f'<div class="modal-formula">{compound["formula"]}</div>'
        f'<div class="modal-name">{compound["name"]}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

    # 3. Tampilkan gambar rumus bangun/struktur molekul jika tersedia
    rumus = compound.get("rumusBangun", "")
    if rumus:
        img_path = os.path.join(BASE_DIR, "static", rumus)
        img_base64 = get_base64_image(img_path)
        ext = rumus.split(".")[-1].lower()
        mime = "image/png" if ext == "png" else "image/jpeg"
        st.markdown(
            f'<div style="margin-bottom:16px">'
            f'<div class="label-caps" style="color:#1a1c1e;margin-bottom:8px">Rumus Bangun</div>'
            f'<div class="rumus-bangun-wrapper">'
            f'<img src="data:{mime};base64,{img_base64}" alt="Struktur {compound["name"]}" />'
            f'</div></div>',
            unsafe_allow_html=True,
        )

    # 4. Tampilkan grid informasi detail (rumus kimia dan warna/wujud)
    st.markdown(
        f'<div style="margin-bottom:16px"><div class="stat-grid">'
        f'<div class="stat-cell">'
        f'<div class="stat-label">Rumus Kimia</div>'
        f'<div class="stat-value-formula">{compound["formula"]}</div>'
        f'</div>'
        f'<div class="stat-cell">'
        f'<div class="stat-label">Warna / Wujud</div>'
        f'<div class="stat-value">{compound["wujud"]}</div>'
        f'</div>'
        f'</div></div>',
        unsafe_allow_html=True,
    )

    # 5. Tampilkan daftar sifat bahaya dengan bentuk chip warna-warni
    chips = build_chips_html(compound["hazards"], "11px")
    st.markdown(
        f'<div style="margin-bottom:16px">'
        f'<div class="label-caps" style="color:#1a1c1e;margin-bottom:8px">Sifat Bahaya</div>'
        f'{chips}</div>',
        unsafe_allow_html=True,
    )

    # 6. Tampilkan tombol link ke dokumen MSDS (PDF) jika tersedia
    st.markdown(
        '<div class="label-caps" style="color:#1a1c1e;margin-bottom:12px">'
        'Keselamatan &amp; Penanganan (MSDS)</div>',
        unsafe_allow_html=True,
    )

    msds = compound.get("msds") or {}  
    has_link = bool(msds.get("link"))

    if has_link:
        st.markdown(
            f'<a href="{msds["link"]}" target="_blank" rel="noopener noreferrer"'
            f' class="msds-link-button" style="margin-bottom:12px">'
            f'<svg width="20" height="20" viewBox="0 0 24 24" fill="none"'
            f' stroke="currentColor" stroke-width="2" stroke-linecap="round"'
            f' stroke-linejoin="round">'
            f'<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>'
            f'<polyline points="14 2 14 8 20 8"/>'
            f'<line x1="16" y1="13" x2="8" y2="13"/>'
            f'<line x1="16" y1="17" x2="8" y2="17"/></svg>'
            f'<span>Lihat Dokumen MSDS (PDF)</span>'
            f'<svg width="16" height="16" viewBox="0 0 24 24" fill="none"'
            f' stroke="currentColor" stroke-width="2" stroke-linecap="round"'
            f' stroke-linejoin="round">'
            f'<path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/>'
            f'<polyline points="15 3 21 3 21 9"/>'
            f'<line x1="10" y1="14" x2="21" y2="3"/></svg></a>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            '<div style="background:#f3f3f6;border-radius:8px;padding:20px;text-align:center">'
            '<div style="font-size:14px;color:#6e7882">Data MSDS belum tersedia.</div>'
            '</div>',
            unsafe_allow_html=True,
        )


# Fungsi utama untuk menjalankan aplikasi Streamlit
def main():
    # 1. Cek status pencarian di session state
    current_query = st.session_state.get("q", "").strip()
    is_searching = bool(current_query)

    # 2. Muat style CSS global ke aplikasi
    st.markdown(ALL_CSS, unsafe_allow_html=True)

    # 3. Alur Tampilan Landing Page (Jika belum melakukan pencarian)
    if not is_searching:
        # Terapkan gaya visual CSS khusus untuk landing page
        st.markdown(LANDING_CSS.replace("BG_IMAGE_BASE64", bg_base64), unsafe_allow_html=True)

        # Beri jarak vertikal agar konten berada di tengah vertikal
        st.markdown(
            '<div style="height:calc(50vh - 180px)"></div>',
            unsafe_allow_html=True,
        )

        # Tampilkan judul utama aplikasi
        st.markdown(
            '<h1 style="'
            "font-family:'Hanken Grotesk',sans-serif;"
            'font-size:32px;font-weight:700;color:#ffffff;'
            'margin:0 0 8px 0;text-align:center;'
            'text-shadow:0 2px 8px rgba(0,0,0,0.3);'
            '">Chemical Safety Database</h1>',
            unsafe_allow_html=True,
        )

        # Tampilkan slogan/deskripsi singkat database
        st.markdown(
            '<p style="'
            "font-family:'Hanken Grotesk',sans-serif;"
            'font-size:15px;color:rgba(255,255,255,0.85);'
            'margin:0 0 28px 0;line-height:1.5;text-align:center;'
            'text-shadow:0 1px 4px rgba(0,0,0,0.2);'
            '">Cari informasi zat kimia, sifat bahaya, dan MSDS</p>',
            unsafe_allow_html=True,
        )

        left_col, center_col, right_col = st.columns([1.2, 2, 1.2])
        with center_col:
            st.text_input(
                "search",
                placeholder="Cari nama zat, rumus, atau sifat bahaya...",
                key="q",
                label_visibility="collapsed",
            )
            # Tampilkan informasi jumlah total zat kimia yang terdaftar
            html_content = (
                '<div style="display: flex; flex-direction: column; align-items: center; width: 100%;">'
                '<p style="'
                "font-family:'Hanken Grotesk',sans-serif;"
                'font-size:15px;color:rgba(255,255,255,0.85);'
                'margin:4px 0 0 0;text-align:center;'
                '"><strong style="color:#fff;font-weight:600">'
                + str(len(compounds_data))
                + "</strong> zat kimia tersedia</p>"
                '<div style="display: inline-block; text-align: left; margin-top: 15px; width: 330px;">'
                '<p style="'
                "font-family:'Hanken Grotesk',sans-serif;"
                'font-size:15px;color:rgba(255,255,255,0.85);'
                'margin:0;text-align:center;padding-left:10px;'
                '">Disusun oleh:</p>'
                '<ul style="'
                "list-style-type:none;padding:0;margin:8px 0 0 0;"
                "font-family:'Hanken Grotesk',sans-serif;"
                'font-size:16px;color:rgba(255,255,255,0.75);'
                '">'
                '<li style="display: flex; justify-content: space-between; margin-bottom: 6px;">'
                '<span>1. Fauziah Hasanah</span>'
                '<span style="font-family:\'JetBrains Mono\', monospace; font-size:14px; opacity:0.85;">(2530614)</span>'
                '</li>'
                '<li style="display: flex; justify-content: space-between; margin-bottom: 6px;">'
                '<span>2. Nabila Agustin</span>'
                '<span style="font-family:\'JetBrains Mono\', monospace; font-size:14px; opacity:0.85;">(2530641)</span>'
                '</li>'
                '<li style="display: flex; justify-content: space-between; margin-bottom: 6px;">'
                '<span>3. Sarah Siti Shalsabila</span>'
                '<span style="font-family:\'JetBrains Mono\', monospace; font-size:14px; opacity:0.85;">(2530651)</span>'
                '</li>'
                '<li style="display: flex; justify-content: space-between; margin-bottom: 6px;">'
                '<span>4. Sirvi Fauziah</span>'
                '<span style="font-family:\'JetBrains Mono\', monospace; font-size:14px; opacity:0.85;">(2530653)</span>'
                '</li>'
                '<li style="display: flex; justify-content: space-between; margin-bottom: 6px;">'
                '<span>5. Sukma Widad Alhana</span>'
                '<span style="font-family:\'JetBrains Mono\', monospace; font-size:14px; opacity:0.85;">(2530655)</span>'
                '</li>'
                '</ul>'
                '</div>'
                '</div>'
            )
            st.markdown(html_content, unsafe_allow_html=True)

    # 4. Alur Tampilan Hasil Pencarian (Jika query pencarian terisi)
    else:
        # Terapkan gaya visual CSS khusus untuk halaman hasil pencarian
        st.markdown(SEARCH_CSS.replace("BG_IMAGE_BASE64", bg_base64), unsafe_allow_html=True)

        # Cari zat kimia yang cocok berdasarkan query
        filtered = filter_data(current_query)

        # Tampilkan judul aplikasi berukuran kecil di bagian atas
        st.markdown(
            '<h1 style="'
            "font-family:'Hanken Grotesk',sans-serif;"
            'font-size:20px;font-weight:700;color:#006591;'
            'margin:20px 0 12px 0;text-align:center;'
            '">Chemical Safety Database</h1>',
            unsafe_allow_html=True,
        )

        # Tampilkan input pencarian agar pengguna bisa mencari ulang
        left_col, center_col, right_col = st.columns([1.2, 2, 1.2])
        with center_col:
            st.text_input(
                "search",
                placeholder="Cari nama zat, rumus, atau sifat bahaya...",
                key="q",
                label_visibility="collapsed",
            )

        # Tampilkan statistik jumlah zat yang ditemukan dari total data
        st.markdown(
            '<p style="'
            "font-family:'Hanken Grotesk',sans-serif;"
            'font-size:13px;color:#6e7882;margin:8px 0 20px 0;text-align:center;'
            '">Ditemukan <strong style="color:#006591;font-weight:600">'
            + str(len(filtered))
            + '</strong> dari <strong style="color:#006591;font-weight:600">'
            + str(len(compounds_data))
            + "</strong> zat kimia</p>",
            unsafe_allow_html=True,
        )

        # Tampilkan empty state jika hasil pencarian nihil
        if not filtered:
            safe_query = html_mod.escape(current_query)
            st.markdown(
                '<div class="search-empty">'
                '<div class="search-empty-icon">🔍</div>'
                '<div class="search-empty-title">Tidak ditemukan</div>'
                '<div class="search-empty-desc">'
                f'Tidak ada zat kimia yang cocok dengan &ldquo;{safe_query}&rdquo;'
                '</div></div>',
                unsafe_allow_html=True,
            )
        # Tampilkan kartu-kartu zat kimia yang cocok dalam grid 3 kolom
        else:
            cols = st.columns(3)
            for idx, compound in enumerate(filtered):
                with cols[idx % 3]:
                    st.markdown(build_card_html(compound), unsafe_allow_html=True)
                    # Tombol interaktif untuk menampilkan modal detail zat kimia
                    if st.button(
                        "Lihat Detail",
                        key=f"btn_{compound['id']}",
                        use_container_width=True,
                        type="tertiary",
                    ):
                        show_detail(compound["id"])



if __name__ == "__main__":
    main()