import streamlit as st
import pandas as pd
from datetime import datetime
import urllib.parse
import os

# --- KURUMSAL AYARLAR ---
st.set_page_config(page_title="Çbk Mali Müşavirlik - Kira Vergi Asistanı", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    h1, h2, h3, h4 { color: #1e3d59; font-family: 'Arial'; }
    .stNumberInput, .stSelectbox, .stTextInput { border: 1px solid #1e3d59 !important; border-radius: 5px; }
    </style>
    """, unsafe_allow_html=True)

# --- LOGO VE ÜST BİLGİ ---
if os.path.exists("logo.png"):
    st.image("logo.png", width=400)
else:
    st.title("ÇBK MALİ MÜŞAVİRLİK")
    st.caption("Şakir ÇETİN, Mali Müşavir - CPA")

st.markdown("---")

# --- VERİ GİRİŞİ ---
st.markdown("#### 📊 Kira Geliri Elde Edenlere Yönelik Vergi Hesaplama Paneli")
c_user = st.columns([2, 1])
with c_user[0]:
    user_name = st.text_input("👤 Adınız ve Soyadınız", placeholder="Mesajda görünmesi için lütfen yazınız")
with c_user[1]:
    vergi_yili = st.selectbox("📅 Tahsil Yılı", ["2026", "2025"])

c1, c2 = st.columns(2)
with c1:
    mesken_brut = st.number_input("🏠 Yıllık Konut Kira Geliri", min_value=0.0, step=1000.0)
with c2:
    isyeri_net = st.number_input("🏢 İşyeri Net Kira (Elinize Geçen)", min_value=0.0, step=1000.0)

# --- HESAPLAMA ---
isyeri_brut = isyeri_net / 0.80 if isyeri_net > 0 else 0.0
toplam_gelir_brut = isyeri_brut + mesken_brut

if vergi_yili == "2025":
    istisna_siniri, haddi_siniri, beyan_siniri = 47000, 1200000, 330000
    dilimler, oranlar, sabitlemeler = [158000, 330000, 800000, 4300000], [0.15, 0.20, 0.27, 0.35, 0.40], [0, 23700, 58100, 185000, 1410000]
else:
    istisna_siniri, haddi_siniri, beyan_siniri = 58000, 1500000, 400000
    dilimler, oranlar, sabitlemeler = [190000, 400000, 1000000, 5300000], [0.15, 0.20, 0.27, 0.35, 0.40], [0, 28500, 70500, 232500, 1737500]

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

# --- RAPOR TABLOSU ---
st.markdown(f"#### 🧾 {vergi_yili} Yılı Vergi Detayı")
son_deger = f"{net_sonuc:,.2f} TL" if net_sonuc > 0 else f"{abs(net_sonuc):,.2f} TL (İade)"
son_etiket = "💸 Ödenecek Vergi" if net_sonuc > 0 else "🏦 İade Alınacak"

report_df = pd.DataFrame({
    "Açıklama": ["Brüt Toplam", "İşyeri Durumu", "İstisna", "Matrah", "Hesaplanan Vergi", "Kesilen Stopaj", son_etiket],
    "Tutar": [f"{toplam_gelir_brut:,.2f} TL", "Beyana Dahil" if beyana_dahil_isyeri > 0 else "Sınır Altı", f"-{istisna_tutari:,.2f} TL", f"{matrah:,.2f} TL", f"{tahakkuk_eden:,.2f} TL", f"-{kesilen_stopaj:,.2f} TL", f"**{son_deger}**"]
})
st.table(report_df)

# --- WHATSAPP DETAYLI DÖKÜM ---
tel_no = "902165670945"
emoji_sonuc = "🔴" if net_sonuc > 0 else "🟢"
mesaj_adi = user_name if user_name else "Değerli Mükellefimiz"

wa_msg = (
    f"🏛 *ÇBK MALİ MÜŞAVİRLİK KİRA RAPORU*\n"
    f"------------------------------------\n"
    f"👤 *Mükellef:* {mesaj_adi}\n"
    f"📅 *Dönem:* {vergi_yili}\n\n"
    f"🏠 *Konut Brüt:* {mesken_brut:,.2f} TL\n"
    f"🏢 *İşyeri Brüt:* {isyeri_brut:,.2f} TL\n"
    f"💎 *İstisna:* -{istisna_tutari:,.2f} TL\n"
    f"📝 *Vergi Matrahı:* {matrah:,.2f} TL\n"
    f"------------------------------------\n"
    f"📋 *Hesaplanan Vergi:* {tahakkuk_eden:,.2f} TL\n"
    f"✂️ *Kesilen Stopaj:* -{kesilen_stopaj:,.2f} TL\n"
    f"------------------------------------\n"
    f"{emoji_sonuc} *NET {son_etiket.upper()}: {son_deger}*\n\n"
    f"👉 _Kontrol edilip beyanname sürecine başlanmasını rica ederim._"
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
