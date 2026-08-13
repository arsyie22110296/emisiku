"""
MODUL EKSPOR LAPORAN MRV
Mendukung mekanisme Monitoring, Reporting, Verification
"""

import streamlit as st
import pandas as pd
import io
import base64
from datetime import datetime

def export_to_csv(df: pd.DataFrame, filename: str = None) -> str:
    """Ekspor data ke CSV"""
    if filename is None:
        filename = f"laporan_emisi_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}">📥 Download CSV</a>'
    return href

def export_to_excel(df: pd.DataFrame, forecast_df: pd.DataFrame = None,
                   carbon_credit_summary: dict = None, filename: str = None) -> bytes:
    """Ekspor data ke Excel dengan multiple sheets"""
    if filename is None:
        filename = f"laporan_emisi_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        # Sheet 1: Data lengkap dengan carbon credit jika ada
        if 'carbon_credit_kg' in df.columns:
            df_export = df[[col for col in df.columns if col not in ['cluster']]]
        else:
            df_export = df
        df_export.to_excel(writer, sheet_name='Data Emisi', index=False)

        # Sheet 2: Ringkasan statistik
        if 'cluster_label' in df.columns:
            summary = df.groupby('cluster_label').agg({
                'total_emisi_kgco2': ['count', 'mean', 'std', 'min', 'max'],
                'listrik_kwh': 'mean',
                'jarak_tempuh_km': 'mean'
            }).round(2)
            summary.to_excel(writer, sheet_name='Ringkasan Cluster')

        # Sheet 3: Forecast (jika ada)
        if forecast_df is not None and len(forecast_df) > 0:
            forecast_export = forecast_df[['tanggal', 'yhat', 'yhat_lower', 'yhat_upper']].copy()
            forecast_export.columns = ['Tanggal', 'Prediksi (kg)', 'Batas Bawah', 'Batas Atas']
            forecast_export.to_excel(writer, sheet_name='Forecast 30 Hari', index=False)

        # Sheet 4: Carbon Credit Summary (jika ada)
        if carbon_credit_summary is not None:
            carbon_data = {
                'Metrik': [
                    'Total Emisi (kg)',
                    'Baseline Emisi (kg)',
                    'Pengurangan (kg)',
                    'Carbon Credit (ton)',
                    'Harga Karbon (IDR/ton)',
                    'Potensi Revenue Perpres (IDR)',
                    'Potensi Revenue Market (IDR)',
                    'Pohon untuk Offset',
                    'Persentase Netral Carbon (%)'
                ],
                'Nilai': [
                    f"{carbon_credit_summary.get('total_emisi_kg', 0):.2f}",
                    f"{carbon_credit_summary.get('baseline_emisi_kg', 0):.2f}",
                    f"{carbon_credit_summary.get('reduction_kg', 0):.2f}",
                    f"{carbon_credit_summary.get('carbon_credit_ton', 0):.4f}",
                    f"{carbon_credit_summary.get('carbon_price_used', 30000):.0f}",
                    f"{carbon_credit_summary.get('potential_revenue_idr_perpres', 0):.0f}",
                    f"{carbon_credit_summary.get('potential_revenue_idr_market', 0):.0f}",
                    f"{carbon_credit_summary.get('trees_to_plant', 0)}",
                    f"{carbon_credit_summary.get('carbon_neutral_percentage', 0):.2f}"
                ]
            }
            carbon_df = pd.DataFrame(carbon_data)
            carbon_df.to_excel(writer, sheet_name='Carbon Credit', index=False)

    return output.getvalue()

def generate_forecast_html_section(forecast_df: pd.DataFrame, forecast_metrics: dict) -> str:
    """Generate HTML section untuk forecast results"""
    if forecast_df is None or len(forecast_df) == 0:
        return ""

    avg_forecast = forecast_df['yhat'].mean()
    max_forecast = forecast_df['yhat'].max()
    min_forecast = forecast_df['yhat'].min()

    # Tentukan trend
    first_10_avg = forecast_df['yhat'].head(10).mean()
    last_10_avg = forecast_df['yhat'].tail(10).mean()
    pct_change = ((last_10_avg - first_10_avg) / first_10_avg) * 100
    if pct_change > 5:
        trend = '📈 NAIK'
    elif pct_change < -5:
        trend = '📉 TURUN'
    else:
        trend = '➡️ STABIL'

    html = f"""
    <h2>🔮 Forecast Emisi 30 Hari Ke Depan</h2>
    <div class="summary">
        <table>
            <tr><th>Metrik</th><th>Nilai</th></tr>
            <tr><td>Rata-rata Forecast</td><td>{avg_forecast:.2f} kg CO₂</td></tr>
            <tr><td>Forecast Tertinggi</td><td>{max_forecast:.2f} kg CO₂</td></tr>
            <tr><td>Forecast Terendah</td><td>{min_forecast:.2f} kg CO₂</td></tr>
            <tr><td>Trend Prediksi</td><td>{trend}</td></tr>
            <tr><td>MAE (Mean Absolute Error)</td><td>{forecast_metrics.get('mae', 0):.2f} kg</td></tr>
            <tr><td>RMSE (Root Mean Squared Error)</td><td>{forecast_metrics.get('rmse', 0):.2f} kg</td></tr>
            <tr><td>MAPE (Mean Absolute % Error)</td><td>{forecast_metrics.get('mape', 0):.2f}%</td></tr>
        </table>
    </div>
    <p><strong>Catatan:</strong> Forecast menggunakan NeuralProphet dengan confidence interval ±15%.
    Akurasi ditunjukkan melalui metrik MAE, RMSE, dan MAPE.</p>
    """
    return html


def generate_anomaly_html_section(anomaly_summary: dict) -> str:
    """Generate HTML section untuk anomaly detection results"""
    if anomaly_summary is None or anomaly_summary.get('total_anomalies', 0) == 0:
        html = """
        <h2>⚠️ Anomaly Detection</h2>
        <div class="summary">
            <p><strong>✅ Status:</strong> Tidak ada anomali terdeteksi</p>
            <p>Pola emisi Anda normal dan konsisten selama periode monitoring.</p>
        </div>
        """
        return html

    total_anom = anomaly_summary.get('total_anomalies', 0)
    anom_pct = anomaly_summary.get('anomaly_percentage', 0)
    breakdown = anomaly_summary.get('severity_breakdown', {})

    html = f"""
    <h2>⚠️ Anomaly Detection</h2>
    <div class="summary">
        <table>
            <tr><th>Metrik</th><th>Nilai</th></tr>
            <tr><td>Total Anomali Terdeteksi</td><td><strong>{total_anom} hari</strong></td></tr>
            <tr><td>Persentase Anomali</td><td>{anom_pct:.1f}%</td></tr>
            <tr><td>Anomali Tinggi</td><td><span class="badge-high">{breakdown.get('Tinggi', 0)} hari</span></td></tr>
            <tr><td>Anomali Sedang</td><td><span class="badge-mid">{breakdown.get('Sedang', 0)} hari</span></td></tr>
            <tr><td>Anomali Rendah</td><td><span class="badge-low">{breakdown.get('Rendah', 0)} hari</span></td></tr>
        </table>
    </div>
    <p><strong>Rekomendasi:</strong> Investigasi hari-hari dengan anomali tinggi untuk mengidentifikasi
    penyebab lonjakan emisi dan ambil tindakan korektif.</p>
    """
    return html


def generate_html_report(df: pd.DataFrame, cluster_metrics: dict, emission_summary: dict,
                        forecast_df: pd.DataFrame = None, forecast_metrics: dict = None,
                        anomaly_summary: dict = None,
                        carbon_credit_summary: dict = None) -> str:
    """Generate laporan HTML untuk MRV dengan optional forecast/anomaly/carbon sections"""

    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Hitung distribusi cluster
    if 'cluster_label' in df.columns:
        cluster_dist = df['cluster_label'].value_counts().to_dict()
    else:
        cluster_dist = {}

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Laporan Monitoring Emisi Karbon - MRV</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; }}
            h1 {{ color: #2c3e50; border-bottom: 2px solid #3498db; }}
            h2 {{ color: #34495e; margin-top: 30px; }}
            table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
            th, td {{ border: 1px solid #ddd; padding: 10px; text-align: left; }}
            th {{ background-color: #3498db; color: white; }}
            .summary {{ background-color: #ecf0f1; padding: 15px; border-radius: 8px; margin: 20px 0; }}
            .footer {{ margin-top: 50px; font-size: 12px; color: #7f8c8d; text-align: center; border-top: 1px solid #ddd; padding-top: 20px; }}
            .badge-low {{ background-color: #27ae60; color: white; padding: 3px 8px; border-radius: 4px; }}
            .badge-mid {{ background-color: #f39c12; color: white; padding: 3px 8px; border-radius: 4px; }}
            .badge-high {{ background-color: #e74c3c; color: white; padding: 3px 8px; border-radius: 4px; }}
        </style>
    </head>
    <body>
        <h1>🌿 Laporan Monitoring Emisi Karbon</h1>
        <p><strong>Tanggal Laporan:</strong> {now}</p>
        <p><strong>Periode Data:</strong> {df['tanggal'].min()} s/d {df['tanggal'].max()}</p>
        <p><strong>Jumlah Periode:</strong> {len(df)} hari</p>

        <h2>📊 Ringkasan Emisi</h2>
        <div class="summary">
            <table>
                <tr><th>Metrik</th><th>Nilai</th></tr>
                <tr><td>Total Emisi</td><td><strong>{emission_summary['total_emisi_kg']:,.2f} kg CO₂</strong> ({emission_summary['total_emisi_ton']:.2f} ton)</td></tr>
                <tr><td>Rata-rata Emisi per Hari</td><td>{emission_summary['rata_rata_emisi_per_periode']:.2f} kg CO₂</td></tr>
                <tr><td>Emisi Tertinggi</td><td>{emission_summary['emisi_tertinggi']:.2f} kg CO₂</td></tr>
                <tr><td>Emisi Terendah</td><td>{emission_summary['emisi_terendah']:.2f} kg CO₂</td></tr>
                <tr><td>Standar Deviasi</td><td>{emission_summary['std_emisi']:.2f} kg CO₂</td></tr>
            </table>
        </div>

        <h2>🔍 Kontribusi per Sumber</h2>
        <div class="summary">
            <table>
                <tr><th>Sumber</th><th>Kontribusi</th></tr>
                <tr><td>Listrik</td><td>{emission_summary['kontribusi_listrik_persen']:.1f}%</td></tr>
                <tr><td>BBM</td><td>{emission_summary['kontribusi_bbm_persen']:.1f}%</td></tr>
                <tr><td>Transportasi</td><td>{emission_summary['kontribusi_transport_persen']:.1f}%</td></tr>
            </table>
        </div>

        <h2>🎯 Hasil Clustering K-Means</h2>
        <div class="summary">
            <table>
                <tr><th>Metrik</th><th>Nilai</th></tr>
                <tr><td>Jumlah Cluster</td><td>{cluster_metrics.get('n_clusters', 'N/A')}</td></tr>
                <tr><td>Silhouette Score</td><td>{cluster_metrics.get('silhouette_score', 'N/A'):.4f}</td></tr>
                <tr><td>Calinski-Harabasz Score</td><td>{cluster_metrics.get('calinski_harabasz_score', 'N/A'):.2f}</td></tr>
                <tr><td>Davies-Bouldin Score</td><td>{cluster_metrics.get('davies_bouldin_score', 'N/A'):.4f}</td></tr>
            </table>
        </div>

        <h2>📋 Distribusi Cluster</h2>
        <div class="summary">
            <table>
                <tr><th>Cluster</th><th>Jumlah Periode</th><th>Persentase</th></tr>
    """

    total = sum(cluster_dist.values())
    for cluster, count in cluster_dist.items():
        badge_class = "badge-low" if cluster == "Rendah" else ("badge-mid" if cluster == "Sedang" else "badge-high")
        html += f"""
        <tr>
            <td><span class="{badge_class}">{cluster}</span></td>
            <td>{count}</td>
            <td>{(count/total)*100:.1f}%</td>
        </tr>
        """

    html += """
            </table>
        </div>
    """

    # Tambah forecast section jika ada
    if forecast_df is not None and forecast_metrics is not None:
        html += generate_forecast_html_section(forecast_df, forecast_metrics)

    # Tambah anomaly section jika ada
    if anomaly_summary is not None:
        html += generate_anomaly_html_section(anomaly_summary)

    # Tambah carbon credit section jika ada
    if carbon_credit_summary is not None:
        html += f"""
        <h2>💰 Estimasi Carbon Credit</h2>
        <div class="summary">
            <table>
                <tr><th>Metrik</th><th>Nilai</th></tr>
                <tr><td>Total Emisi</td><td>{carbon_credit_summary.get('total_emisi_kg', 0)/1000:.2f} ton CO₂</td></tr>
                <tr><td>Baseline Emisi</td><td>{carbon_credit_summary.get('baseline_emisi_kg', 0)/1000:.2f} ton CO₂</td></tr>
                <tr><td>Pengurangan Emisi</td><td>{carbon_credit_summary.get('reduction_kg', 0)/1000:.2f} ton CO₂</td></tr>
                <tr><td>Carbon Credit</td><td><strong>{carbon_credit_summary.get('carbon_credit_ton', 0):.4f} ton CO₂e</strong></td></tr>
                <tr><td>Potensi Revenue (Perpres)</td><td>Rp {carbon_credit_summary.get('potential_revenue_idr_perpres', 0)/1e6:.1f}jt</td></tr>
                <tr><td>Potensi Revenue (Market)</td><td>Rp {carbon_credit_summary.get('potential_revenue_idr_market', 0)/1e6:.1f}jt</td></tr>
                <tr><td>Pohon untuk Offset</td><td>{carbon_credit_summary.get('trees_to_plant', 0)} pohon</td></tr>
                <tr><td>Persentase Carbon Neutral</td><td>{carbon_credit_summary.get('carbon_neutral_percentage', 0):.2f}%</td></tr>
            </table>
        </div>
        <p><strong>Catatan:</strong> Carbon credit dihitung berdasarkan pengurangan emisi relatif terhadap baseline.
        Harga referensi: Perpres 98/2021 = Rp 30.000/ton, Market (IDXCarbon) ~Rp 70.000/ton.</p>
        """

    html += f"""
        <div class="footer">
            <p>Laporan ini dihasilkan oleh EmisiKu - Sistem Monitoring Emisi Karbon untuk UMKM</p>
            <p>Sesuai dengan mekanisme MRV (Monitoring, Reporting, Verification)</p>
            <p>Skripsi S1 - STMIK Mardira Indonesia | Fitur: K-Means Clustering, Linear Regression Forecasting, Anomaly Detection</p>
        </div>
    </body>
    </html>
    """

    return html


def get_excel_download_link(df: pd.DataFrame, filename: str = None) -> str:
    """Mendapatkan link download Excel"""
    excel_data = export_to_excel(df, filename)
    b64 = base64.b64encode(excel_data).decode()
    return f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="{filename or "laporan_emisi.xlsx"}">📥 Download Laporan Excel</a>'