"""
MODUL FORECASTING EMISI KARBON
Menggunakan Linear Time Series Regression (OLS)
Skripsi S1 - Fitur Advanced untuk Dashboard Monitoring
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error
import warnings
warnings.filterwarnings('ignore')


class EmissionForecaster:
    """
    Forecaster untuk memprediksi emisi karbon menggunakan Linear Regression
    dengan fitur time-based (trend, day-of-week, day-of-month, month)
    """

    def __init__(self, random_state: int = 42):
        self.random_state = random_state
        self.model = LinearRegression()
        self.metrics = {}
        self.is_fitted = False

    def _prepare_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Membuat fitur time-based untuk regresi linier:
        - trend (hari ke-n)
        - day_of_week (0=Senin, 6=Minggu) sebagai one-hot
        - day_of_month
        - month
        """
        df_feat = df.copy()
        df_feat['ds'] = pd.to_datetime(df_feat['tanggal'])
        df_feat['trend'] = np.arange(len(df_feat))
        df_feat['day_of_week'] = df_feat['ds'].dt.dayofweek
        df_feat['day_of_month'] = df_feat['ds'].dt.day
        df_feat['month'] = df_feat['ds'].dt.month
        
        # One-hot encoding untuk day_of_week (agar pola mingguan tertangkap)
        dummies = pd.get_dummies(df_feat['day_of_week'], prefix='dow', drop_first=True)
        df_feat = pd.concat([df_feat, dummies], axis=1)
        
        return df_feat

    def fit(self, df: pd.DataFrame):
        """
        Melatih model regresi linier
        """
        df_feat = self._prepare_features(df)
        
        # Fitur yang digunakan
        feature_cols = ['trend', 'day_of_month', 'month'] + \
                       [col for col in df_feat.columns if col.startswith('dow_')]
        
        X = df_feat[feature_cols].values
        y = df_feat['total_emisi_kgco2'].values
        
        self.model.fit(X, y)
        self.is_fitted = True
        self.feature_cols = feature_cols
        self.last_date = df['tanggal'].max()
        self.df_feat = df_feat
        
        return self

    def forecast(self, df: pd.DataFrame, periods: int = 30) -> dict:
        """
        Melakukan forecasting untuk 'periods' hari ke depan
        """
        try:
            # Fit model jika belum fitted
            if not self.is_fitted:
                self.fit(df)
            
            # Buat future dataframe
            last_date = df['tanggal'].max()
            future_dates = [last_date + timedelta(days=i+1) for i in range(periods)]
            
            # Buat fitur untuk future dates
            future_df = pd.DataFrame({'tanggal': future_dates})
            future_df['ds'] = pd.to_datetime(future_df['tanggal'])
            future_df['trend'] = np.arange(len(df), len(df) + periods)
            future_df['day_of_week'] = future_df['ds'].dt.dayofweek
            future_df['day_of_month'] = future_df['ds'].dt.day
            future_df['month'] = future_df['ds'].dt.month
            
            # One-hot encoding untuk day_of_week future
            dummies = pd.get_dummies(future_df['day_of_week'], prefix='dow', drop_first=True)
            future_df = pd.concat([future_df, dummies], axis=1)
            
            # Pastikan kolom one-hot yang hilang diisi 0
            for col in self.feature_cols:
                if col not in future_df.columns:
                    future_df[col] = 0
            
            # Predict
            X_future = future_df[self.feature_cols].values
            y_pred = self.model.predict(X_future)
            
            # Hitung confidence interval (sederhana: ±1.96 * std error residuals)
            X_train = self.df_feat[self.feature_cols].values
            y_train = self.df_feat['total_emisi_kgco2'].values
            y_train_pred = self.model.predict(X_train)
            residuals = y_train - y_train_pred
            std_error = np.std(residuals)
            
            forecast_df = pd.DataFrame({
                'tanggal': future_dates,
                'yhat': y_pred,
                'yhat_lower': y_pred - 1.96 * std_error,
                'yhat_upper': y_pred + 1.96 * std_error
            })
            
            # Clip agar tidak negatif
            forecast_df['yhat'] = forecast_df['yhat'].clip(lower=0)
            forecast_df['yhat_lower'] = forecast_df['yhat_lower'].clip(lower=0)
            forecast_df['yhat_upper'] = forecast_df['yhat_upper'].clip(lower=0)
            
            # Hitung metrik akurasi (berdasarkan fitted values)
            self.metrics = self._calculate_metrics(y_train, y_train_pred)
            
            # Tentukan trend
            trend = self._determine_trend(forecast_df)
            
            return {
                'forecast_df': forecast_df,
                'metrics': self.metrics,
                'trend': trend,
                'status': 'success'
            }
            
        except Exception as e:
            return {
                'forecast_df': None,
                'metrics': {},
                'trend': 'UNKNOWN',
                'status': 'error',
                'error_message': str(e)
            }

    def _calculate_metrics(self, y_true, y_pred):
        mae = mean_absolute_error(y_true, y_pred)
        rmse = np.sqrt(mean_squared_error(y_true, y_pred))
        # MAPE (hindari division by zero)
        mask = y_true != 0
        if mask.sum() > 0:
            mape = np.mean(np.abs((y_true[mask] - y_pred[mask]) / y_true[mask])) * 100
        else:
            mape = 0
        return {'mae': mae, 'rmse': rmse, 'mape': mape}

    def _determine_trend(self, forecast_df):
        if len(forecast_df) < 10:
            return 'STABIL'
        first_10 = forecast_df['yhat'].head(10).mean()
        last_10 = forecast_df['yhat'].tail(10).mean()
        if first_10 == 0:
            return 'STABIL'
        pct_change = ((last_10 - first_10) / first_10) * 100
        if pct_change > 5:
            return 'NAIK'
        elif pct_change < -5:
            return 'TURUN'
        else:
            return 'STABIL'


def validate_forecast_data(df: pd.DataFrame) -> tuple:
    if df is None or len(df) == 0:
        return False, "Data kosong"
    if 'total_emisi_kgco2' not in df.columns:
        return False, "Kolom total_emisi_kgco2 tidak ditemukan"
    if 'tanggal' not in df.columns:
        return False, "Kolom tanggal tidak ditemukan"
    if len(df) < 7:
        return False, f"Minimal 7 data point diperlukan, saat ini {len(df)}"
    return True, "Data valid untuk forecasting"