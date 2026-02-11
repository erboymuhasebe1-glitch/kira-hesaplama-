import streamlit as st
import pandas as pd
from datetime import datetime

# Kurumsal Kimlik Ayarları
st.set_page_config(page_title="Çbk Mali Müşavirlik - Vergi Asistanı", layout="wide")
st.title("⚖️ Çbk Mali Müşavirlik")
st.subheader("Kira Geliri Beyanname Hesaplama Sistemi")

# --- GİRİŞ ALANI ---
with st.sidebar:
    st.header("📋 Veri Girişi")
    vergi_yili = st.selectbox("Hesaplanacak Yılı Seçiniz", ["2025", "2026"])
    st.markdown("---")
    isyeri_brut = st.number_input("İşyeri Kira Geliri (Brüt)", min_value=0.0, step=1000.0)
    mesken_brut = st.number_input("Mesken (Konut) Kira Geliri", min_value=0.0, step=1000.0)

# --- YILA GÖRE PARAMETRELER ---
if vergi_yili == "2025":
    istisna_siniri = 47000
    haddi_siniri = 1200000
    # 2025 Gelir Vergisi Tarifesi
    dilimler = [
        (158000, 0.15),
        (382000, 0.20),
        (940000, 0.27),
        (3000000, 0.35)
    ]
    sabitlemeler = [0, 23700, 68500, 219160] # Her dilimin başlangıç vergi toplamı
else: # 2026 Parametreleri
    istisna_siniri = 58000
    haddi_siniri = 1500000
    dilimler = [
        (230000, 0.15),
        (580000, 0.20),
        (1200000, 0.27),
        (3000000, 0.35)
    ]
    sabitlemeler = [0, 34500, 104500, 271900]

# --- HESAPLAMA MANTIĞI ---
toplam_gelir = isyeri_brut + mesken_brut
istisna_tutari = 0

# İstisna Uygulama Şartları (Yeni formülünüze uygun)
if isyeri_brut == 0 and mesken_brut > 0 and toplam_gelir < haddi_siniri:
    istisna_tutari = min(istisna_siniri, mesken_brut)

matrah = max(0.0, (toplam_gelir - istisna_tutari) * 0.85) # %15 Götürü Gider

# Dinamik Vergi Hesaplama Fonksiyonu
def vergi_hesapla(m, d, s):
    if m <= d[0][0]: return m * d[0][1]
    elif m <= d[1][0]: return s[1] + (m - d[0][0]) * d[1][1]
    elif m <= d[2][0]: return s[2] + (m - d[1][0]) * d[2][1]
    elif m <= d[3][0]: return s[3] + (m - d[2][0]) * d[3][1]
    else: return s[3] + (d[3][0] - d[2][0]) * d[3][1] + (m - d[3][0]) * 0.40

tahakkuk_eden = vergi_hesapla(matrah, dilimler, sabitlemeler)
kesilen_stopaj = isyeri_brut * 0.20
net_odenecek = max(0.0, tahakkuk_eden - kesilen_stopaj)

# --- RAPORLAMA ---
st.markdown(f"### 📊 {vergi_yili} Yılı Gelir Vergisi Hesaplama Sonucu")
now = datetime.now().strftime("%d-%m-%Y %H:%M")
st.caption(f"Rapor Tarihi: {now}")

report_data = {
    "Sıra": [1],
    "Vergi Dönemi": [f"01/{vergi_yili}-12/{vergi_yili}"],
    "Gelir Unsuru": ["Kira Geliri (GMSİ)"],
    "Matrah": [f"{matrah:,.2f} TL"],
    "Tahakkuk Eden Vergi": [f"{tahakkuk_eden:,.2f} TL"]
}
st.table(pd.DataFrame(report_data))

c1, c2, c3 = st.columns(3)
c1.metric("Toplam Brüt Gelir", f"{toplam_gelir:,.2f} TL")
c2.metric("İndirilen İstisna", f"{istisna_tutari:,.2f} TL")
c3.metric("Ödenecek Net Vergi", f"{net_odenecek:,.2f} TL")

# WhatsApp Paylaşımı
st.markdown("---")
wa_msg = f"*Çbk Mali Müşavirlik {vergi_yili} Kira Raporu*\n\n*Matrah:* {matrah:,.2f} TL\n*Net Vergi:* {net_odenecek:,.2f} TL"
# BURAYA KENDİ NUMARANIZI EKLEYİN (Örn: 905321234567)
wa_link = f"https://wa.me/902165670945?text={wa_msg.replace(' ', '%20').replace('*', '%2A')}"

if st.button("📱 Sonucu WhatsApp'tan Müşavirime Gönder"):
    st.markdown(f"[✅ WhatsApp ile Gönderilmeye Hazır (Tıklayın)]({wa_link})")
