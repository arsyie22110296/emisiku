"""
MODUL ANOMALY DETECTION EMISI KARBON
Deteksi hari anomal dengan emisi abnormal menggunakan Isolation Forest
Skripsi S1 - Fitur Advanced untuk Dashboard Monitoring
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings('ignore')


class AnomalyDetector:
    """
    Detector untuk mengidentifikasi hari-hari dengan pola emisi abnormal
    menggunakan Isolation Forest algorithm
    """

    def __init__(self, contamination: float = 0.05, random_state: int = 42):
        """
        Args:
            contamination: Expected fraction of anomalies (default 5%)
                          Untuk 30 hari data = ~1-2 hari anomali
            random_state: Seed untuk reproducibility
        """
        self.contamination = contamination
        self.random_state = random_state
        self.scaler = StandardScaler()
        self.model = IsolationForest(
            contamination=contamination,
            random_state=random_state,
            n_estimators=100
        )
        self.scaled_data = None

    def detect_anomalies(self, df: pd.DataFrame, feature_cols: list = None) -> pd.DataFrame:
        """
        Deteksi anomali di data emisi

        Args:
            df: DataFrame dengan data emisi (harus punya 'total_emisi_kgco2')
            feature_cols: Kolom yang digunakan untuk anomaly detection
                         Default: ['listrik_kwh', 'total_emisi_kgco2', 'jarak_tempuh_km']

        Returns:
            DataFrame dengan kolom tambahan:
            - 'is_anomaly': boolean (True = anomali)
            - 'anomaly_score': float (0-1, lebih tinggi = lebih anomal)
            - 'anomaly_severity': str ('Rendah', 'Sedang', 'Tinggi')
        """
        df_result = df.copy()

        # Define default feature columns untuk detection
        if feature_cols is None:
            feature_cols = ['total_emisi_kgco2']
            # Tambah feature lain jika tersedia
            if 'listrik_kwh' in df.columns:
                feature_cols = ['listrik_kwh'] + feature_cols
            if 'jarak_tempuh_km' in df.columns:
                feature_cols = feature_cols + ['jarak_tempuh_km']

        # Ambil feature yang tersedia
        available_cols = [col for col in feature_cols if col in df.columns]

        if len(available_cols) == 0:
            raise ValueError("Tidak ada kolom yang dapat digunakan untuk anomaly detection")

        features = df_result[available_cols].values

        # Normalisasi data
        self.scaled_data = self.scaler.fit_transform(features)

        # Fit dan predict Isolation Forest
        predictions = self.model.fit_predict(self.scaled_data)
        anomaly_scores = self.model.score_samples(self.scaled_data)

        # Konversi predictions ke boolean
        # -1 = anomaly, 1 = normal
        is_anomaly = predictions == -1

        # Normalize anomaly scores ke range [0, 1]
        # Higher score = more anomalous
        anomaly_scores_normalized = 1 / (1 + np.exp(anomaly_scores))

        # Tentukan severity
        severity = self._determine_severity(anomaly_scores_normalized, is_anomaly)

        # Tambah kolom ke result
        df_result['is_anomaly'] = is_anomaly
        df_result['anomaly_score'] = anomaly_scores_normalized
        df_result['anomaly_severity'] = severity

        return df_result

    def _determine_severity(self, scores: np.ndarray, is_anomaly: np.ndarray) -> list:
        """
        Tentukan severity level setiap data point

        Returns:
            List dengan nilai 'Normal', 'Rendah', 'Sedang', 'Tinggi'
        """
        severity = []

        for score, is_anom in zip(scores, is_anomaly):
            if not is_anom:
                severity.append('Normal')
            else:
                # Untuk anomali, classify berdasarkan score
                if score < 0.4:
                    severity.append('Rendah')
                elif score < 0.7:
                    severity.append('Sedang')
                else:
                    severity.append('Tinggi')

        return severity

    def get_anomaly_details(self, df: pd.DataFrame) -> dict:
        """
        Generate ringkasan anomaly detection results

        Returns:
            Dict dengan:
            - total_anomalies: Jumlah hari anomali terdeteksi
            - anomaly_percentage: Persentase anomali dari total data
            - top_anomalies: DataFrame 5 anomali terparah
            - severity_breakdown: Dict breakdown by severity
        """
        if 'is_anomaly' not in df.columns:
            raise ValueError("DataFrame harus sudah di-detect dengan detect_anomalies()")

        total_anomalies = df['is_anomaly'].sum()
        total_data = len(df)
        anomaly_percentage = (total_anomalies / total_data) * 100 if total_data > 0 else 0

        # Top 5 anomali terparah (sorted by anomaly_score)
        anomalies_df = df[df['is_anomaly']].copy()
        top_anomalies = anomalies_df.nlargest(5, 'anomaly_score')[
            ['tanggal', 'total_emisi_kgco2', 'anomaly_score', 'anomaly_severity']
        ].reset_index(drop=True)

        # Severity breakdown
        severity_breakdown = {}
        if len(anomalies_df) > 0:
            severity_counts = anomalies_df['anomaly_severity'].value_counts()
            for severity_type in ['Tinggi', 'Sedang', 'Rendah']:
                severity_breakdown[severity_type] = int(severity_counts.get(severity_type, 0))

        return {
            'total_anomalies': int(total_anomalies),
            'anomaly_percentage': float(anomaly_percentage),
            'top_anomalies': top_anomalies,
            'severity_breakdown': severity_breakdown,
            'total_data_points': total_data
        }

    def get_anomaly_recommendations(self, df: pd.DataFrame) -> list:
        """
        Generate rekomendasi tindakan berdasarkan anomali terdeteksi

        Returns:
            List of recommendations (string)
        """
        if 'is_anomaly' not in df.columns:
            return ["Jalankan detect_anomalies() terlebih dahulu"]

        recommendations = []

        anomalies_df = df[df['is_anomaly']].copy()

        if len(anomalies_df) == 0:
            recommendations.append("✅ Tidak ada anomali terdeteksi - Emisi normal")
            return recommendations

        # Cek severity breakdown
        severity_counts = anomalies_df['anomaly_severity'].value_counts()

        if 'Tinggi' in severity_counts.index and severity_counts['Tinggi'] > 0:
            recommendations.append(
                f"🔴 **{severity_counts['Tinggi']} Anomali Tinggi Terdeteksi** - "
                "Segera investigasi aktivitas pada hari tersebut"
            )

        if 'Sedang' in severity_counts.index and severity_counts['Sedang'] > 0:
            recommendations.append(
                f"🟡 **{severity_counts['Sedang']} Anomali Sedang** - "
                "Review dan dokumentasikan penyebabnya"
            )

        # Cek kolom emisi untuk pattern
        if 'total_emisi_kgco2' in df.columns:
            avg_emisi = df['total_emisi_kgco2'].mean()
            anomaly_avg_emisi = anomalies_df['total_emisi_kgco2'].mean()

            if anomaly_avg_emisi > avg_emisi * 1.5:
                recommendations.append(
                    f"📈 Anomali hari ini ~{(anomaly_avg_emisi/avg_emisi - 1)*100:.0f}% "
                    "lebih tinggi dari rata-rata - Cek penggunaan energi"
                )

        if len(recommendations) == 0:
            recommendations.append("⚠️ Ada anomali terdeteksi - Review data lebih lanjut")

        return recommendations


def validate_anomaly_data(df: pd.DataFrame) -> tuple:
    """
    Validasi data untuk anomaly detection

    Returns:
        (is_valid: bool, message: str)
    """
    if df is None or len(df) == 0:
        return False, "Data kosong"

    if 'total_emisi_kgco2' not in df.columns:
        return False, "Kolom 'total_emisi_kgco2' tidak ditemukan"

    if len(df) < 5:
        return False, "Minimal 5 data points diperlukan untuk anomaly detection"

    # Check variance (jika semua nilai identik, tidak bisa detect anomali)
    if df['total_emisi_kgco2'].std() == 0:
        return False, "Semua nilai emisi identik - tidak ada variasi untuk mendeteksi anomali"

    return True, "Data valid"


def compare_anomaly_methods(df: pd.DataFrame, contamination: float = 0.05) -> dict:
    """
    Compare multiple anomaly detection approaches (optional - untuk research)

    Returns:
        Dict dengan hasil dari berbagai methods
    """
    results = {}

    try:
        # Method 1: Isolation Forest
        detector = AnomalyDetector(contamination=contamination)
        df_iso = detector.detect_anomalies(df)
        results['isolation_forest'] = {
            'n_anomalies': df_iso['is_anomaly'].sum(),
            'method': 'Isolation Forest'
        }
    except Exception as e:
        results['isolation_forest'] = {'error': str(e)}

    try:
        # Method 2: Z-Score (simple method untuk comparison)
        from scipy import stats
        z_scores = np.abs(stats.zscore(df['total_emisi_kgco2']))
        threshold = 3
        n_anomalies_zscore = (z_scores > threshold).sum()
        results['zscore'] = {
            'n_anomalies': int(n_anomalies_zscore),
            'method': 'Z-Score (σ=3)'
        }
    except Exception as e:
        results['zscore'] = {'error': str(e)}

    return results
