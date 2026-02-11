import streamlit as st
import pandas as pd
from datetime import datetime
import urllib.parse
import os

# --- KURUMSAL AYARLAR ---
st.set_page_config(page_title="Çbk Mali Müşavirlik - Kira Vergi Asistanı", layout="centered")

# Mobil Odaklı ve Belirgin Tasarım (CSS)
st.markdown("""
    <style>
    .main { background-color: #f0f2f6; }
    /* Giriş kutularını beyaz ve gölgeli yaparak belirginleştirir */
    div[data-baseweb="input"] {
        background-color: white !important;
        border: 2px solid #1e3d59 !important;
        border-radius: 10px !important;
    }
    /* Başlıkların rengini kurumsal lacivert yapar */
    h1, h2, h3, h4 { color: #1e3d59; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
    /* Metrik kutuları (Sonuçlar) */
    [data-testid="stMetricValue"] { font-size: 24px !important; color: #d9534f; }
    /* Buton tasarımı */
    .stButton>button {
        width: 100%;
        border-radius: 10px;
        height: 3em;
        background-color: #1e3d59;
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)

# --- LOGO VE ÜST BİLGİ ---
if os.path.exists("logo.png"):
    st.image("logo.png", width=350)
else:
    st.title("ÇBK MALİ MÜŞAVİRLİK")
    st.caption("Şakir ÇETİN, Mali Müşavir - CPA")

st.markdown("---")

# --- ANA EKRAN VERİ GİRİŞİ (MOBİLDE EN ÜSTTE GÖRÜNÜR) ---
st.subheader("📌 Veri Giriş Paneli")
st.info("Lütfen beyan etmek istediğiniz kira gelirlerini aşağıdaki kutucuklara yazınız.")

# Veri Girişi Alanları (Belirgin ve Büyük)
col_y = st.columns(1)[0]
vergi_yili = col_y.selectbox("📅 Hesaplama Yılını Seçiniz", ["2026", "2025"])

c1, c2 = st.columns(2)
with c1:
    mesken_brut = st.number_input("🏠 Yıllık Konut Kirası", min_value=0.0, step=5000.0, help="Toplam konut geliri")
with c2:
    isyeri_brut = st.number_input("🏢 Yıllık İşyeri Kirası (Brüt)", min_value=0.0, step=5000.0, help="Stopaj dahil brüt tutar")

st.markdown("---")

# --- YILA GÖRE PARAMETRELER ---
if vergi_yili == "2025":
    istisna_siniri, haddi_siniri, beyan_siniri = 47000, 1200000, 330000
    dilimler = [158000, 330000, 800000, 4300000]
    oranlar = [0.15, 0.20, 0.27, 0.35, 0.40]
    sabitlemeler = [0, 23700, 58100, 185000, 1410000]
else:
    istisna_siniri, haddi_siniri, beyan_siniri = 58000, 1500000, 400000
    dilimler = [190000, 400000, 1000000, 5300000]
    oranlar = [0.15, 0.20, 0.27, 0.35, 0.40]
    sabitlemeler = [0, 28500, 70500, 232500, 1737500]

# --- HESAPLAMA MOTORU ---
toplam_gelir_brut = isyeri_brut + mesken_brut
beyana_dahil_isyeri = isyeri_brut if toplam_gelir_brut > beyan_siniri else 0.0
istisna_tutari = min(float(istisna_siniri), mesken_brut) if (mesken_brut > 0 and toplam_gelir_brut < haddi_siniri) else 0.0

matrah = max(0.0, (mesken_brut + beyana_dahil_isyeri - istisna_tutari) * 0.85)

def vergi_hesapla(m, d, o, s):
    if m <= d[0]: return m * o[0]
    elif m <= d[1]: return s[1] + (m - d[0]) * o[1]
    elif m <= d[2]: return s[2] + (m - d[1]) * o[2]
    elif m <= d[3]: return s[3] + (m - d[2]) * o[3]
    else: return s[4] + (m - d[3]) * o[4]

tahakkuk_eden = vergi_hesapla(matrah, dilimler, oranlar, sabitlemeler)
kesilen_stopaj = beyana_dahil_isyeri * 0.20
net_sonuc = tahakkuk_eden - kesilen_stopaj

# --- SONUÇ RAPORU ---
st.subheader("📊 Hesaplama Özeti")
sonuc_metni = f"Ödenecek: {net_sonuc:,.2f} TL" if net_sonuc > 0 else f"İade: {abs(net_sonuc):,.2f} TL"

report_df = pd.DataFrame({
    "Açıklama": ["Toplam Brüt", "İstisna", "Matrah", "Stopaj Mahsubu", "SONUÇ"],
    "Tutar": [f"{toplam_gelir_brut:,.2f}", f"-{istisna_tutari:,.2f}", f"{matrah:,.2f}", f"-{kesilen_stopaj:,.2f}", sonuc_metni]
})
st.table(report_df)

# --- WHATSAPP BUTONU (EN ALTTA SABİT VE BÜYÜK) ---
tel_no = "902165670945"
wa_msg = urllib.parse.quote(f"*Çbk Mali Müşavirlik Raporu*\nBrüt: {toplam_gelir_brut:,.2f} TL\nSonuç: {sonuc_metni}")
wa_link = f"https://api.whatsapp.com/send?phone={tel_no}&text={wa_msg}"

st.markdown(f"""
    <a href="{wa_link}" target="_blank" style="text-decoration: none;">
        <div style="background-color: #25D366; color: white; padding: 18px; text-align: center; border-radius: 12px; font-weight: bold; font-size: 18px; margin-top: 20px;">
            🟢 WHATSAPP İLE ONAYA GÖNDER
        </div>
    </a>
    """, unsafe_allow_html=True)
