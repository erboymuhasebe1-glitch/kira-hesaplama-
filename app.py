import streamlit as st
import pandas as pd
from datetime import datetime
import urllib.parse
import os

# --- KURUMSAL AYARLAR ---
st.set_page_config(page_title="Çbk Mali Müşavirlik - Kira Vergi Asistanı", layout="wide")

# Özel Tasarım (CSS)
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    h1, h2, h3 { color: #1e3d59; font-family: 'Arial'; }
    .report-table { width: 100%; border-collapse: collapse; }
    </style>
    """, unsafe_allow_html=True)

# --- LOGO VE BAŞLIK ---
# Eğer logo.png dosyası klasörde varsa onu göster, yoksa text başlık göster
if os.path.exists("logo.png"):
    st.image("logo.png", width=400)
else:
    st.title("ÇBK MALİ MÜŞAVİRLİK")
    st.subheader("Şakir ÇETİN, Mali Müşavir - CPA")

st.markdown("### Kira Geliri Vergi Hesaplama")
st.markdown("---")

# --- GİRİŞ ALANI (SOL PANEL) ---
with st.sidebar:
    st.header("📋 Hesaplama Seçenekleri")
    vergi_yili = st.selectbox("Hesaplanacak Yılı Seçiniz", ["2025", "2026"])
    st.markdown("---")
    mesken_brut = st.number_input("Yıllık Mesken (Konut) Kira Geliri", min_value=0.0, step=1000.0)
    isyeri_brut = st.number_input("Yıllık İşyeri Kira Geliri (Brüt)", min_value=0.0, step=1000.0)
    st.markdown("---")
    # Sabit Hattınız
    tel_no = "902165670945"
    st.write(f"📞 Ofis Tel: {tel_no}")
    st.caption("© 2026 Çbk Mali Müşavirlik")

# --- YILA GÖRE PARAMETRELER ---
if vergi_yili == "2025":
    istisna_siniri = 47000
    haddi_siniri = 1200000
    beyan_siniri = 330000  # 330.000 TL dahil kuralı
    dilimler = [158000, 330000, 800000, 4300000]
    oranlar = [0.15, 0.20, 0.27, 0.35, 0.40]
    sabitlemeler = [0, 23700, 58100, 185000, 1410000]
else:
    istisna_siniri = 58000
    haddi_siniri = 1500000
    beyan_siniri = 400000  # 400.000 TL dahil kuralı
    dilimler = [190000, 400000, 1000000, 5300000]
    oranlar = [0.15, 0.20, 0.27, 0.35, 0.40]
    sabitlemeler = [0, 28500, 70500, 232500, 1737500]

# --- HESAPLAMA MOTORU ---
toplam_gelir_brut = isyeri_brut + mesken_brut
istisna_tutari = 0.0

# İşyeri Beyan Kontrolü (Sınır Dahil: Toplam <= Sınır ise işyeri yok)
beyana_dahil_isyeri = 0.0
if toplam_gelir_brut > beyan_siniri:
    beyana_dahil_isyeri = isyeri_brut
    isyeri_notu = "Beyana Dahil (Sınır Aşıldı)"
else:
    isyeri_notu = f"{beyan_siniri:,.0f} TL Sınırı Aşılmadı (İşyeri Beyan Edilmez)"

# İstisna Hesaplama (Geliri aşamaz kuralı dahil)
if mesken_brut > 0 and toplam_gelir_brut < haddi_siniri:
    istisna_tutari = min(float(istisna_siniri), mesken_brut)

# Matrah Hesaplama
matrah = max(0.0, (mesken_brut + beyana_dahil_isyeri - istisna_tutari) * 0.85)

# Vergi Hesaplama
def vergi_hesapla(m, d, o, s):
    if m <= d[0]: return m * o[0]
    elif m <= d[1]: return s[1] + (m - d[0]) * o[1]
    elif m <= d[2]: return s[2] + (m - d[1]) * o[2]
    elif m <= d[3]: return s[3] + (m - d[2]) * o[3]
    else: return s[4] + (m - d[3]) * o[4]

tahakkuk_eden = vergi_hesapla(matrah, dilimler, oranlar, sabitlemeler)
kesilen_stopaj = beyana_dahil_isyeri * 0.20
net_sonuc = tahakkuk_eden - kesilen_stopaj

# --- RAPORLAMA ---
st.markdown(f"#### 📊 {vergi_yili} Yılı Vergi Hesaplama Raporu")

# Tablo Verisi
sonuc_metni = f"Ödenecek: {net_sonuc:,.2f} TL" if net_sonuc > 0 else f"İade: {abs(net_sonuc):,.2f} TL"

report_df = pd.DataFrame({
    "Açıklama": [
        "Toplam Brüt Kira Hasılatı",
        "İşyeri Beyan Durumu",
        "Uygulanan Mesken İstisnası",
        "Vergi Matrahı (%15 Götürü Gider)",
        "Hesaplanan Gelir Vergisi",
        "Mahsup Edilen Stopaj (İşyeri)",
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

# Özet Kartları
c1, c2, c3 = st.columns(3)
c1.metric("Matrah", f"{matrah:,.2f} TL")
c2.metric("Kesilen Stopaj", f"{kesilen_stopaj:,.2f} TL")
if net_sonuc > 0:
    c3.metric("Ödenecek Vergi", f"{net_sonuc:,.2f} TL", delta_color="inverse")
else:
    c3.metric("İade Alınacak", f"{abs(net_sonuc):,.2f} TL")

# --- WHATSAPP BUTONU ---
st.markdown("---")
wa_msg = (
    f"*Çbk Mali Müşavirlik Kira Raporu ({vergi_yili})*\n\n"
    f"*Toplam Brüt:* {toplam_gelir_brut:,.2f} TL\n"
    f"*Matrah:* {matrah:,.2f} TL\n"
    f"*Sonuç:* {sonuc_metni}\n\n"
    f"Onayınızı rica ederim."
)
encoded_msg = urllib.parse.quote(wa_msg)
wa_link = f"https://api.whatsapp.com/send?phone={tel_no}&text={encoded_msg}"

st.markdown(f"""
    <a href="{wa_link}" target="_blank" style="text-decoration: none;">
        <div style="background-color: #25D366; color: white; padding: 20px; text-align: center; border-radius: 12px; font-weight: bold; font-size: 20px;">
            🟢 HESAPLAMAYI WHATSAPP İLE ONAYA GÖNDER
        </div>
    </a>
    """, unsafe_allow_html=True)
