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
st.markdown("#### 📊 Vergi Hesaplama Paneli")
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

# Beyan Sınırı Kontrolü
beyana_dahil_isyeri = isyeri_brut if toplam_gelir_brut > beyan_siniri else 0.0

# İstisna Hesaplama
istisna_tutari = min(float(istisna_siniri), mesken_brut) if (mesken_brut > 0 and toplam_gelir_brut < haddi_siniri) else 0.0

# GİDER HESAPLAMA (Talebiniz üzerine ayrıştırıldı)
istisna_sonrasi_toplam = (
