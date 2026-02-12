import streamlit as st
import pandas as pd
from datetime import datetime
import urllib.parse
import os

# --- KURUMSAL AYARLAR ---
st.set_page_config(page_title="Çbk Mali Müşavirlik - Kira Vergi Asistanı", layout="wide")

# Kurumsal Stil Ayarları
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    h1, h2, h3, h4 { color: #1e3d59; font-family: 'Arial'; }
    .stNumberInput, .stSelectbox { border: 1px solid #1e3d59 !important; border-radius: 5px; }
    </style>
    """, unsafe_allow_html=True)

# --- LOGO VE ÜST BİLGİ ---
if os.path.exists("logo.png"):
    st.image("logo.png", width=400)
else:
    st.title("ÇBK MALİ MÜŞAVİRLİK")
    st.caption("Şakir ÇETİN, Mali Müşavir - CPA")

st.markdown("---")

# --- VERİ GİRİŞİ (ANA EKRAN) ---
st.markdown("#### 📊 Yalnızca Kira Geliri Elde Edenlere Yönelik Vergi Hesaplama Tablosu")
col_year = st.columns([1, 2])[0]
vergi_yili = col_year.selectbox("Kiranın Tahsil Edildiği Yıl", ["2026", "2025"])

c1, c2 = st.columns(2)
with c1:
    mesken_brut = st.number_input("Konut Kira Geliri", min_value=0.0, step=1000.0, key="mesken")
with c2:
    isyeri_brut = st.number_input("İşyeri Kira Geliri (Brüt)", min_value=0.0, step=1000.0, key="isyeri")

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

# İşyeri Beyan Durumu (Dahillik kuralı: Toplam <= Sınır ise işyeri beyan edilmez)
beyana_dahil_isyeri = 0.0
if toplam_gelir_brut > beyan_siniri:
    beyana_dahil_isyeri = isyeri_brut
    isyeri_notu = "Beyana Dahil (Sınır Aşıldı)"
else:
    beyana_dahil_isyeri = 0.0
    isyeri_notu = f"{beyan_siniri:,.0f} TL Sınırı Aşılmadı (İşyeri Dahil Edilmedi)"

# İstisna Hesaplama
istisna_tutari = 0.0
if mesken_brut > 0 and toplam_gelir_brut < haddi_siniri:
    istisna_tutari = min(float(istisna_siniri), mesken_brut)

# Matrah Hesaplama
matrah = max(0.0, (mesken_brut + beyana_dahil_isyeri - istisna_tutari) * 0.85)

# Vergi Hesaplama Fonksiyonu
def vergi_hesapla(m, d, o, s):
    if m <= d[0]: return m * o[0]
    elif m <= d[1]: return s[1] + (m - d[0]) * o[1]
    elif m <= d[2]: return s[2] + (m - d[1]) * o[2]
    elif m <= d[3]: return s[3] + (m - d[2]) * o[3]
    else: return s[4] + (m - d[3]) * o[4]

# HATA ALINAN SATIRIN DÜZELTİLMİŞ HALİ
tahakkuk_eden = vergi_hesapla(matrah, dilimler, oranlar, sabitlemeler)
kesilen_stopaj = beyana_dahil_isyeri * 0.20
net_sonuc = tahakkuk_eden - kesilen_stopaj

# --- SONUÇ TABLOSU ---
st.markdown(f"#### 🧾 {vergi_yili} Yılı Ödenecek Vergi")
sonuc_metni = f"Ödenecek: {net_sonuc:,.2f} TL" if net_sonuc > 0 else f"İade: {abs(net_sonuc):,.2f} TL"

report_df = pd.DataFrame({
    "Açıklama": [
        "Toplam Brüt Kira Hasılatı",
        "İşyeri Beyan Durumu",
        "Uygulanan Mesken İstisnası",
        "Beyan Edilen Matrah (%15 Götürü Gider Düşüldü)",
        "Hesaplanan Gelir Vergisi",
        "Mahsup Edilecek Stopaj (İşyeri)",
        "Net Ödenecek / İade"
    ],
    "Tutar / Bilgi": [
        f"{toplam_gelir_brut:,.2f} TL",
        isyeri_notu,
        f"- {istisna_tutari:,.2f} TL",
        f"{matrah:,.2f} TL",
        f"{tahakkuk_eden:,.2f} TL",
        f"- {kesilen_stopaj:,.2f} TL",
        f"**{sonuc_metni}**"
    ]
})
st.table(report_df)

# --- WHATSAPP BUTONU ---
tel_no = "902165670945"
wa_msg = urllib.parse.quote(f"*Çbk Mali Müşavirlik Kira Raporu ({vergi_yili})*\n\n*Toplam Brüt:* {toplam_gelir_brut:,.2f} TL\n*Matrah:* {matrah:,.2f} TL\n*Sonuç:* {sonuc_metni}")
wa_link = f"https://api.whatsapp.com/send?phone={tel_no}&text={wa_msg}"

st.markdown(f"""
    <a href="{wa_link}" target="_blank" style="text-decoration: none;">
        <div style="background-color: #25D366; color: white; padding: 18px; text-align: center; border-radius: 10px; font-weight: bold; font-size: 18px; margin-top: 10px;">
            🟢 WHATSAPP İLE ONAYA GÖNDER
        </div>
    </a>
    """, unsafe_allow_html=True)
