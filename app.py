report_df = pd.DataFrame({
    "Açıklama": [
        "0️⃣ Toplam Brüt Kira Hasılatı 💰",
        "1️⃣ İşyeri Beyan Durumu 🏢",
        "2️⃣ Uygulanan Mesken İstisnası 💎",
        "3️⃣ Düşülen %15 Götürü Gider 📉",
        "4️⃣ Vergi Matrahı 📝",
        "5️⃣ Hesaplanan Gelir Vergisi 📋",
        "6️⃣ Mahsup Edilecek Stopaj (İşyeri) ✂️",
        f"7️⃣ {son_etiket}" # Burası otomatik emoji (💸 veya 🏦) alıyor
    ],
    "Tutar / Bilgi": [
        f"{toplam_gelir_brut:,.2f} TL",
        "Beyana Dahil" if beyana_dahil_isyeri > 0 else "Sınır Altı (Beyana Dahil Değil)",
        f"- {istisna_tutari:,.2f} TL",
        f"- {gider_tutari:,.2f} TL",
        f"{matrah:,.2f} TL",
        f"{tahakkuk_eden:,.2f} TL",
        f"- {kesilen_stopaj:,.2f} TL",
        f"**{son_deger}**"
    ]
})
