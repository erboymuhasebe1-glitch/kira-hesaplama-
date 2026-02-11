import streamlit as st
import pandas as pd
from datetime import datetime

# Kurumsal Kimlik Ayarları
st.set_page_config(page_title="Çbk Mali Müşavirlik - Vergi Asistanı", layout="wide")
st.title("⚖️ Çbk Mali Müşavirlik")
st.subheader("Kira Geliri Beyanname Hesaplama Sistemi (2026)")

# --- GİRİŞ ALANI ---
with st.sidebar:
    st.header("📋 Veri Girişi")
    isyeri_brut = st.number_input("İşyeri Kira Geliri (Brüt)", min_value=0.0, value=0.0, step=1000.0)
    mesken_brut = st.number_input("Mesken (Konut) Kira Geliri", min_value=0.0, value=0.0, step=1000.0)
    st.markdown("---")
    vergi_yili = st.selectbox("Vergi Dönemi", ["2025", "2026"])

# --- HESAPLAMA MANTIĞI ---
toplam_gelir = isyeri_brut + mesken_brut

# İstisna Hesaplama (Sizin son formülünüz: =EĞER(D3=0; D4; EĞER(D4<1500000; MAK(0; D4-MİN(58000; D3)); D4)))
# Not: İşyeri geliri varsa istisna uygulanmaz kuralını da ekliyoruz.
istisna_tutari = 0
if isyeri_brut == 0 and mesken_brut > 0 and toplam_gelir < 1500000:
    istisna_tutari = min(58000, mesken_brut)

gelir_eksi_istisna = toplam_gelir - istisna_tutari
gider_orani = 0.15
matrah = max(0.0, gelir_eksi_istisna * (1 - gider_orani))

# Vergi Dilimleri (2026 Tahmini)
def gelir_vergisi_hesapla(m):
    if m <= 230000: return m * 0.15
    elif m <= 580000: return 34500 + (m - 230000) * 0.20
    elif m <= 1200000: return 104500 + (m - 580000) * 0.27
    elif m <= 3000000: return 271900 + (m - 1200000) * 0.35
    else: return 901900 + (m - 3000000) * 0.40

tahakkuk_eden = gelir_vergisi_hesapla(matrah)
kesilen_stopaj = isyeri_brut * 0.20
net_odenecek = max(0.0, tahakkuk_eden - kesilen_stopaj)

# --- RAPORLAMA (Yeni Dosyanızdaki Görünüm) ---
st.markdown("### 📊 Gelir Vergisi Hesaplama Sonucu")
now = datetime.now().strftime("%d-%m-%Y %H:%M")
st.caption(f"Rapor Tarihi: {now}")

# Paylaştığınız son dosyaya benzer tablo yapısı
report_data = {
    "Sıra": [1],
    "Vergi Dönemi": [f"01/{vergi_yili}-12/{vergi_yili}"],
    "Gelir Unsuru": ["Kira Geliri (GMSİ)"],
    "Matrah": [f"{matrah:,.2f} TL"],
    "Tahakkuk Eden Vergi": [f"{tahakkuk_eden:,.2f} TL"]
}
df_report = pd.DataFrame(report_data)
st.table(df_report)

# Özet Bilgi Kartları
c1, c2, c3 = st.columns(3)
c1.metric("Toplam Brüt Gelir", f"{toplam_gelir:,.2f} TL")
c2.metric("İndirilen İstisna", f"{istisna_tutari:,.2f} TL")
c3.metric("Ödenecek Net Vergi", f"{net_odenecek:,.2f} TL", delta_color="inverse")

# WhatsApp Gönderimi
st.markdown("---")
wa_msg = f"*Çbk Mali Müşavirlik Kira Raporu*\n\n*Matrah:* {matrah:,.2f} TL\n*Vergi:* {tahakkuk_eden:,.2f} TL\n*Stopaj Mahsubu:* {kesilen_stopaj:,.2f} TL\n*Net Ödenecek:* {net_odenecek:,.2f} TL"
wa_link = f"https://wa.me/905XXXXXXXXX?text={wa_msg.replace(' ', '%20').replace('*', '%2A')}"

if st.button("📱 Sonucu WhatsApp'tan Paylaş"):
    st.write(f"[Buraya tıklayarak WhatsApp'a gönderin]({wa_link})")
