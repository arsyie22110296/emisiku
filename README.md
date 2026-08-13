# 🌿 EmisiKu

**EmisiKu** adalah aplikasi web berbasis Python untuk monitoring, analisis, dan pelaporan emisi karbon pada UMKM. Aplikasi ini dirancang untuk membantu pemilik usaha kecil (khususnya sektor pangan) dalam menghitung jejak karbon, menganalisis pola emisi menggunakan **K-Means Clustering**, memprediksi emisi 30 hari ke depan, mendeteksi anomali konsumsi energi, serta menghitung potensi pendapatan dari perdagangan karbon (carbon credit).

## 🚀 Fitur Utama

- 📊 **Dashboard Analitik** — Ringkasan metrik emisi (total, rata-rata, tertinggi, terendah) dan grafik tren harian.
- 📂 **Upload Data** — Unggah data aktivitas energi (CSV/Excel) dengan pilihan bahan bakar (Solar, Bensin, Kayu, LPG).
- 📈 **Perhitungan Emisi** — Konversi aktivitas energi menjadi emisi CO₂ (faktor emisi IPCC 2022 & PLN).
- 🧩 **K-Means Clustering** — Kelompokkan pola emisi menjadi tiga kategori (Tinggi, Sedang, Rendah) dengan evaluasi kualitas cluster (Silhouette Score, Calinski-Harabasz, Davies-Bouldin).
- 🔮 **Forecasting 30 Hari** — Prediksi emisi menggunakan Linear Time Series Regression.
- ⚠️ **Deteksi Anomali** — Identifikasi hari dengan pola emisi tidak wajar menggunakan Isolation Forest.
- 💰 **Carbon Credit** — Estimasi potensi pendapatan dari perdagangan karbon (dua skenario harga: Perpres Rp30.000/ton & IDXCarbon Rp70.000/ton).
- 📄 **Laporan MRV** — Ekspor laporan lengkap ke Excel dan HTML untuk mendukung mekanisme Monitoring, Reporting, and Verification.

## 🛠️ Teknologi

- **Python 3.12.4**
- **Streamlit 1.57.0** — Framework web interaktif
- **pandas, numpy** — Manipulasi data
- **scikit-learn** — K-Means Clustering, Isolation Forest, StandardScaler, metrik evaluasi
- **statsmodels** — Linear Time Series Regression
- **plotly, matplotlib, seaborn** — Visualisasi interaktif dan statis
- **openpyxl, reportlab** — Ekspor laporan Excel dan HTML

## 📂 Struktur Proyek


## 🧪 Cara Menggunakan

1. **Upload Data**: Pilih jenis bahan bakar dan unggah file CSV/Excel dengan kolom:
   - `tanggal` (YYYY-MM-DD)
   - `listrik_kwh`
   - `bahan_bakar_liter` atau `bahan_bakar_kg`
   - `jarak_tempuh_km`
2. **Hitung Emisi**: Sistem akan mengkonversi aktivitas energi menjadi emisi CO₂.
3. **Jalankan Clustering**: Tentukan jumlah cluster (K) dan jalankan K-Means.
4. **Eksplorasi Fitur Lanjutan**: Forecasting, deteksi anomali, estimasi carbon credit, dan unduh laporan MRV.

## 🌐 Akses Online

Aplikasi telah dideploy di **Streamlit Community Cloud**:

👉 https://emisiku-app.streamlit.app

## 📄 Skripsi

Proyek ini merupakan implementasi dari skripsi:

> **Analisis Pola Emisi Karbon Menggunakan Algoritma K-Means Clustering pada Sistem Monitoring Berbasis Web untuk Mendukung Mekanisme MRV pada Perdagangan Karbon**  
> Ariel Adrienne Setiawan (NIM: 22110296)  
> Teknik Informatika S1 – STMIK Mardira Indonesia

## 📝 Lisensi

© 2026 EmisiKu — Skripsi Ariel Adrienne Setiawan.  
Dibuat untuk tujuan akademik dan penelitian.
