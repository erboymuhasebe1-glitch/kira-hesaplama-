import streamlit as st
import pandas as pd
from datetime import datetime
import urllib.parse

# --- KURUMSAL AYARLAR ---
st.set_page_config(page_title="Çbk Mali Müşavirlik - Kira Vergi Asistanı", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    h1, h2, h3 { color: #1e3d59; }
    </style>
    """, unsafe_allow_html=True)

st.title("⚖️ Çbk Mali Müşavirlik")
st.subheader("Kira Geliri Beyanname Hesaplama Sistemi")
st.markdown("---")

# --- GİRİŞ ALANI (SOL PANEL) ---
with st.sidebar:
    st.header("📋 Hesaplama Parametreleri")
    vergi_yili = st.selectbox("Hesaplanacak Yılı Seçiniz", ["2025", "2026"])
    st.markdown("---")
    mesken_brut = st.number_input("Yıllık Mesken (Konut) Kira Geliri", min_value=0.0, step=1000.0)
    isyeri_brut = st.number_input("Yıllık İşyeri Kira Geliri (Brüt)", min_value=0.0, step=1000.0)
    st.markdown("---")
    tel_no = st.text_input("Müşavir WhatsApp No", value="902165670945")
    st.caption("© 2026 Çbk Mali Müşavirlik")

# --- YILA GÖRE PARAMETRELER ---
if vergi_yili == "2025":
    istisna_siniri = 47000
    haddi_siniri = 1200000
    dilimler = [158000, 330000, 800000, 4300000]
    oranlar = [0.15, 0.20, 0.27, 0.35, 0.40]
    sabitlemeler = [0, 23700, 58100, 185000, 1410000]
else:
    istisna_siniri = 58000
    haddi_siniri = 1500000
    dilimler = [190000, 400000, 1000000, 5300000]
    oranlar = [0.15, 0.20, 0.27, 0.35, 0.40]
    sabitlemeler = [0, 28500, 70500, 232500, 1737500]

# --- HESAPLAMA MOTORU (DÜZELTİLDİ) ---
toplam_gelir = isyeri_brut + mesken_brut
istisna_tutari = 0.0

# DÜZELTME: İşyeri geliri olsa dahi toplam gelir sınırı aşılmadıysa mesken istisnası uygulanır.
if mesken_brut > 0 and toplam_gelir < haddi_siniri:
    istisna_tutari = min(float(istisna_siniri), mesken_brut)

matrah = max(0.0, (toplam_gelir - istisna_tutari) * 0.85)

def vergi_hesapla(m, d, o, s):
    if m <= d[0]: return m * o[0]
    elif m <= d[1]: return s[1] + (m - d[0]) * o[1]
    elif m <= d[2]: return s[2] + (m - d[1]) * o[2]
    elif m <= d[3]: return s[3] + (m - d[2]) * o[3]
    else: return s[4] + (m - d[3]) * o[4]

tahakkuk_eden = vergi_hesapla(matrah, dilimler, oranlar, sabitlemeler)
kesilen_stopaj = isyeri_brut * 0.20
net_odenecek = max(0.0, tahakkuk_eden - kesilen_stopaj)
iade_durumu = max(0.0, kesilen_stopaj - tahakkuk_eden)

# --- SONUÇ RAPORU (AYRI STOPAJ ALANI) ---
st.markdown(f"### 📊 {vergi_yili} Yılı Vergi Hesaplama Özeti")

# Sonuç metni hazırlama
if net_odenecek > 0:
    son_etiket = "Ödenecek Gelir Vergisi"
    son_deger = f"{net_odenecek:,.2f} TL"
else:
    son_etiket = "İade Alınacak Gelir Vergisi"
    son_deger = f"{iade_durumu:,.2f} TL"

report_df = pd.DataFrame({
    "Açıklama": [
        "Toplam Brüt Hasılat", 
        "Uygulanan Mesken İstisnası", 
        "Vergi Matrahı (%15 Götürü)", 
        "Hesaplanan Gelir Vergisi", 
        "Düşülen (Mahsup Edilen) Stopaj", 
        son_etiket
    ],
    "Tutar (TL)": [
        f"{toplam_gelir:,.2f} TL",
        f"- {istisna_tutari:,.2f} TL",
        f"{matrah:,.2f} TL",
        f"{tahakkuk_eden:,.2f} TL",
        f"- {kesilen_stopaj:,.2f} TL",
        f"**{son_deger}**"
    ]
})
st.table(report_df)

# Özet Kartları
c1, c2, c3 = st.columns(3)
c1.metric("İndirilen İstisna", f"{istisna_tutari:,.2f} TL")
c2.metric("Mahsup Edilen Stopaj", f"{kesilen_stopaj:,.2f} TL")
if net_odenecek > 0:
    c3.metric("Net Ödenecek", f"{net_odenecek:,.2f} TL", delta_color="inverse")
else:
    c3.metric("İade Tutarı", f"{iade_durumu:,.2f} TL")

# --- WHATSAPP BUTONU ---
st.markdown("---")
durum_msg = f"Ödenecek: {net_odenecek:,.2f} TL" if net_odenecek > 0 else f"İade: {iade_durumu:,.2f} TL"
wa_msg = (
    f"*Çbk Mali Müşavirlik Kira Raporu ({vergi_yili})*\n\n"
    f"*Mesken Geliri:* {mesken_brut:,.2f} TL\n"
    f"*İşyeri Geliri (Brüt):* {isyeri_brut:,.2f} TL\n"
    f"*İstisna:* {istisna_tutari:,.2f} TL\n"
    f"*Matrah:* {matrah:,.2f} TL\n"
    f"*Hesaplanan Vergi:* {tahakkuk_eden:,.2f} TL\n"
    f"*Düşülen Stopaj:* {kesilen_stopaj:,.2f} TL\n"
    f"*Sonuç:* {durum_msg}"
)

encoded_msg = urllib.parse.quote(wa_msg)
wa_link = f"https://api.whatsapp.com/send?phone={tel_no}&text={encoded_msg}"

st.markdown(f"""
    <a href="{wa_link}" target="_blank" style="text-decoration: none;">
        <div style="background-color: #25D366; color: white; padding: 18px; text-align: center; border-radius: 12px; font-weight: bold; font-size: 20px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">
            🟢 HESAPLAMAYI WHATSAPP İLE ONAYA GÖNDER
        </div>
    </a>
    """, unsafe_allow_html=True)
