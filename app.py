import streamlit as st
import pandas as pd
from datetime import datetime

# --- KURUMSAL AYARLAR ---
st.set_page_config(page_title="Çbk Mali Müşavirlik - Kira Vergi Asistanı", layout="wide")

# Özel CSS ile daha profesyonel görünüm
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
    mesken_brut = st.number_input("Yıllık Mesken (Konut) Kira Geliri", min_value=0.0, step=1000.0, help="Yıl içinde tahsil edilen toplam konut kirası")
    isyeri_brut = st.number_input("Yıllık İşyeri Kira Geliri (Brüt)", min_value=0.0, step=1000.0, help="Stopaj dahil brüt işyeri kirası")
    st.markdown("---")
    st.caption("© 2026 Çbk Mali Müşavirlik")

# --- YILA GÖRE PARAMETRE TANIMLARI ---
if vergi_yili == "2025":
    istisna_siniri = 47000
    haddi_siniri = 1200000
    # 2025 Vergi Dilimleri (İstediğiniz Baremler)
    dilimler = [158000, 330000, 800000, 4300000]
    oranlar = [0.15, 0.20, 0.27, 0.35, 0.40]
    sabitlemeler = [0, 23700, 58100, 185000, 1410000]
else:
    istisna_siniri = 58000
    haddi_siniri = 1500000
    # 2026 Vergi Dilimleri (İstediğiniz Baremler)
    dilimler = [190000, 400000, 1000000, 5300000]
    oranlar = [0.15, 0.20, 0.27, 0.35, 0.40]
    sabitlemeler = [0, 28500, 70500, 232500, 1737500]

# --- HESAPLAMA MOTORU ---
toplam_gelir = isyeri_brut + mesken_brut
istisna_tutari = 0.0

# İstisna Kuralı: İşyeri geliri varsa veya toplam gelir haddi aşıyorsa istisna = 0
# Değilse: İstisna, konut gelirini aşamaz (Formülünüz: MIN(istisna; mesken_geliri))
if isyeri_brut == 0 and mesken_brut > 0 and toplam_gelir < haddi_siniri:
    istisna_tutari = min(float(istisna_siniri), mesken_brut)

# Matrah Hesaplama (%15 Götürü Gider)
istisna_sonrasi = toplam_gelir - istisna_tutari
matrah = max(0.0, istisna_sonrasi * 0.85)

# Dinamik Vergi Hesaplama Fonksiyonu
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

# --- SONUÇ RAPORU (Excel Görünümü) ---
st.markdown(f"### 📊 {vergi_yili} Yılı Gelir Vergisi Hesaplama Sonucu")
now = datetime.now().strftime("%d-%m-%Y %H:%M")
st.caption(f"İşlem Zamanı: {now}")

# Paylaştığınız Excel tablosuna uygun yapı
report_df = pd.DataFrame({
    "Sıra": [1],
    "Vergi Dönemi": [f"01/{vergi_yili}-12/{vergi_yili}"],
    "Gelir Unsuru": ["Kira Geliri (GMSİ)"],
    "Matrah": [f"{matrah:,.2f} TL"],
    "Tahakkuk Eden Vergi": [f"{tahakkuk_eden:,.2f} TL"]
})
st.table(report_df)

# Özet Kartları
col1, col2, col3, col4 = st.columns(4)
col1.metric("Brüt Toplam", f"{toplam_gelir:,.2f} TL")
col2.metric("İndirilen İstisna", f"{istisna_tutari:,.2f} TL")
col3.metric("Ödenen Stopaj", f"{kesilen_stopaj:,.2f} TL")

if net_odenecek > 0:
    col4.metric("Ödenecek Vergi", f"{net_odenecek:,.2f} TL", delta_color="inverse")
else:
    col4.metric("İade Alınacak", f"{iade_durumu:,.2f} TL", delta_color="normal")

# --- WHATSAPP ENTEGRASYONU ---
st.markdown("---")
st.subheader("📲 Müşavir Onayı")
wa_numara = "905XXXXXXXXX" # BURAYA KENDİ NUMARANIZI YAZIN
durum_metni = f"Ödenecek: {net_odenecek:,.2f} TL" if net_odenecek > 0 else f"İade: {iade_durumu:,.2f} TL"
wa_msg = (
    f"*Çbk Mali Müşavirlik Kira Raporu ({vergi_yili})*\n\n"
    f"*Mesken:* {mesken_brut:,.2f} TL\n"
    f"*İşyeri:* {isyeri_brut:,.2f} TL\n"
    f"*İstisna:* {istisna_tutari:,.2f} TL\n"
    f"*Matrah:* {matrah:,.2f} TL\n"
    f"*Sonuç:* {durum_metni}\n\n"
    f"Kontrolünüzü rica ederim."
)
wa_link = f"https://wa.me/{wa_numara}?text={wa_msg.replace(' ', '%20').replace('*', '%2A')}"

st.markdown(f"""
    <a href="{wa_link}" target="_blank">
        <div style="background-color: #25D366; color: white; padding: 15px; text-align: center; border-radius: 10px; font-weight: bold; text-decoration: none; font-size: 18px;">
            ✅ HESAPLAMAYI ONAYA GÖNDER (WhatsApp)
        </div>
    </a>
    """, unsafe_allow_html=True)

st.warning("Not: Bu hesaplama bilgilendirme amaçlıdır. Kesin beyanname öncesi mali müşavir onayı şarttır.")
