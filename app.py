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
    /* Giriş kutularını belirginleştir */
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

# --- VERİ GİRİŞİ (MOBİLDE ÜSTTE GÖRÜNECEK ŞEKİLDE ANA EKRANDA) ---
st.markdown("#### 📌 Veri Girişi")
col_year = st.columns([1, 2])[0]
vergi_yili = col_year.selectbox("Hesaplama Yılı", ["2026", "2025"])

c1, c2 = st.columns(2)
with c1:
    mesken_brut = st.number_input("Konut Kira Geliri", min_value=0.0, step=1000.0)
with c2:
    isyeri_brut = st.number_input("İşyeri Kira Geliri (Brüt)", min_value=0.0, step=1000.0)

# --- YILA GÖRE PARAMETRELER ---
if vergi_yili == "2025":
    istisna_siniri, haddi_siniri, beyan_siniri = 47000, 1200000, 330000
    dilimler, oranlar, sabitlemeler = [158000, 330000, 800000, 4300000], [0.15, 0.20, 0.27, 0.35, 0.40], [0, 23700, 58100, 185000, 1410000]
else:
    istisna_siniri, haddi_siniri, beyan_siniri = 58000, 1500000, 400000
    dilimler, oranlar, sabitlemeler = [190000, 400000, 1000000, 5300000], [0.15, 0.20, 0.27, 0.35, 0.40], [0, 28500, 70500, 232500, 1737500]

# --- HESAPLAMA MOTORU ---
toplam_gelir_brut = isyeri_brut + mesken_brut
beyana_dahil_isyeri = isyeri_brut if toplam_gelir_brut > beyan_siniri else 0.0
isyeri_notu = "Beyana Dahil" if beyana_dahil_isyeri > 0 else "Beyan Sınırı Altında"

istisna_tutari = min(float(istisna_siniri), mesken_brut) if (mesken_brut > 0 and toplam_gelir_brut < haddi_siniri) else 0.0
matrah = max(0.0, (mesken_brut + beyana_dahil_isyeri - istisna_tutari) * 0.85)

def vergi_hesapla(m, d, o, s):
    if m <= d[0]: return m * o[0]
    elif m <= d[1]: return s[1] + (m - d[0]) * o[1]
    elif m <= d[2]: return s[2] + (m - d[1]) * o[2]
    elif m <= d[3]: return s[3] + (m - d[2]) * o[3]
    else: return s[4] + (m - d[3]) * o[4]

tahakkuk_
