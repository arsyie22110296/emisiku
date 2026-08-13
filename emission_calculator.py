"""
MODUL PERHITUNGAN EMISI KARBON
Multi-Fuel Support: Solar, Bensin, Kayu Bakar, LPG
Sesuai proposal skripsi - Faktor emisi IPCC 2022 & Kementerian LHK
"""

import pandas as pd
import numpy as np

# ================= FAKTOR EMISI PER JENIS BAHAN BAKAR =================
# Sumber: IPCC 2022, Kementerian LHK, PLN Grid Indonesia 2025
FUEL_FACTORS = {
    'solar': {
        'value': 2.68,
        'unit': 'kg CO₂/liter',
        'sumber': 'IPCC 2022',
        'icon': '⛽'
    },
    'bensin': {
        'value': 2.31,
        'unit': 'kg CO₂/liter',
        'sumber': 'IPCC 2022',
        'icon': '⛽'
    },
    'kayu': {
        'value': 1.82,
        'unit': 'kg CO₂/kg',
        'sumber': 'KLHK (biomassa)',
        'icon': '🌲'
    },
    'lpg': {
        'value': 1.51,
        'unit': 'kg CO₂/kg',
        'sumber': 'IPCC 2022',
        'icon': '🛢️'
    },
    'listrik': {
        'value': 0.85,
        'unit': 'kg CO₂/kWh',
        'sumber': 'PLN Grid Average 2025',
        'icon': '⚡'
    },
    'transportasi': {
        'value': 0.27,
        'unit': 'kg CO₂/km',
        'sumber': 'IPCC 2022, Light Duty Vehicle',
        'icon': '🚚'
    }
}

# Faktor Default (untuk kompatibilitas)
FACTORS = {
    'electricity': FUEL_FACTORS['listrik'],
    'bbm': FUEL_FACTORS['solar'],
    'transportation': FUEL_FACTORS['transportasi']
}


def calculate_emissions(df: pd.DataFrame, fuel_type: str = 'solar') -> pd.DataFrame:
    """
    Menghitung emisi karbon dengan jenis bahan bakar fleksibel
    
    Args:
        df: DataFrame dengan kolom 
            - listrik_kwh (wajib)
            - bahan_bakar_liter atau bahan_bakar_kg (wajib)
            - jarak_tempuh_km (wajib)
            - atau kolom lama: solar_liter / bbm_liter untuk kompatibilitas
        fuel_type: 'solar', 'bensin', 'kayu', 'lpg'
    
    Returns:
        DataFrame dengan kolom emisi
    """
    
    df = df.copy()
    
    # ========== 1. Hitung Emisi Listrik ==========
    if 'listrik_kwh' in df.columns:
        df['emisi_listrik_kg'] = (df['listrik_kwh'] * FUEL_FACTORS['listrik']['value']).round(2)
    else:
        df['emisi_listrik_kg'] = 0
    
    # ========== 2. Hitung Emisi Bahan Bakar (Multi-Fuel) ==========
    bbm_value = FUEL_FACTORS[fuel_type]['value']
    
    # Cek berbagai kemungkinan nama kolom
    if 'bahan_bakar_liter' in df.columns:
        df['emisi_bbm_kg'] = (df['bahan_bakar_liter'] * bbm_value).round(2)
        df['satuan_bbm'] = 'liter'
    elif 'bahan_bakar_kg' in df.columns:
        df['emisi_bbm_kg'] = (df['bahan_bakar_kg'] * bbm_value).round(2)
        df['satuan_bbm'] = 'kg'
    elif 'solar_liter' in df.columns:
        df['emisi_bbm_kg'] = (df['solar_liter'] * FUEL_FACTORS['solar']['value']).round(2)
        df['satuan_bbm'] = 'liter'
    elif 'bbm_liter' in df.columns:
        df['emisi_bbm_kg'] = (df['bbm_liter'] * bbm_value).round(2)
        df['satuan_bbm'] = 'liter'
    else:
        df['emisi_bbm_kg'] = 0
        df['satuan_bbm'] = 'unknown'
    
    # Simpan jenis bahan bakar yang digunakan
    df['jenis_bahan_bakar'] = fuel_type
    
    # ========== 3. Hitung Emisi Transportasi ==========
    if 'jarak_tempuh_km' in df.columns:
        df['emisi_transport_kg'] = (df['jarak_tempuh_km'] * FUEL_FACTORS['transportasi']['value']).round(2)
    else:
        df['emisi_transport_kg'] = 0
    
    # ========== 4. Total Emisi ==========
    df['total_emisi_kgco2'] = (df['emisi_listrik_kg'] + df['emisi_bbm_kg'] + df['emisi_transport_kg']).round(2)
    
    return df


def get_emission_summary(df: pd.DataFrame) -> dict:
    """Menghasilkan ringkasan statistik emisi"""
    
    if 'total_emisi_kgco2' not in df.columns:
        df = calculate_emissions(df)
    
    # Handle jika kolom emisi_bbm_kg tidak ada
    if 'emisi_bbm_kg' not in df.columns:
        if 'emisi_solar_kg' in df.columns:
            df['emisi_bbm_kg'] = df['emisi_solar_kg']
        else:
            df['emisi_bbm_kg'] = 0
    
    total = df['total_emisi_kgco2'].sum()
    
    summary = {
        'total_emisi_kg': total,
        'total_emisi_ton': total / 1000,
        'rata_rata_emisi_per_periode': df['total_emisi_kgco2'].mean(),
        'emisi_tertinggi': df['total_emisi_kgco2'].max(),
        'emisi_terendah': df['total_emisi_kgco2'].min(),
        'std_emisi': df['total_emisi_kgco2'].std(),
        'jumlah_periode': len(df),
    }
    
    # Kontribusi per sumber (hindari division by zero)
    if total > 0:
        summary['kontribusi_listrik_persen'] = (df['emisi_listrik_kg'].sum() / total) * 100
        summary['kontribusi_bbm_persen'] = (df['emisi_bbm_kg'].sum() / total) * 100
        summary['kontribusi_transport_persen'] = (df['emisi_transport_kg'].sum() / total) * 100
    else:
        summary['kontribusi_listrik_persen'] = 0
        summary['kontribusi_bbm_persen'] = 0
        summary['kontribusi_transport_persen'] = 0
    
    return summary


def get_fuel_info(fuel_type: str) -> dict:
    """Mendapatkan informasi tentang jenis bahan bakar"""
    return FUEL_FACTORS.get(fuel_type, FUEL_FACTORS['solar'])


def calculate_carbon_credit(df: pd.DataFrame, baseline_emission_kg: float = None,
                           carbon_price_idr_per_ton: float = 30000) -> dict:
    """
    Hitung estimasi carbon credit yang bisa dijual berdasarkan reduction dari baseline

    Args:
        df: DataFrame dengan total_emisi_kgco2
        baseline_emission_kg: Average emisi periode baseline (default: rata-rata current)
        carbon_price_idr_per_ton: Harga karbon IDR per ton
                                 Default: Rp 30.000 (Perpres 98/2021)
                                 Range: Rp 30.000 - Rp 150.000

    Returns:
        dict dengan:
        - total_emisi_kg: Total emisi dalam periode
        - baseline_emisi_kg: Baseline emisi reference
        - reduction_kg: Pengurangan emisi (kg)
        - carbon_credit_ton: Carbon credit dalam ton CO2e
        - carbon_price_used: Harga karbon yang digunakan (IDR/ton)
        - potential_revenue_idr_perpres: Revenue dengan harga Perpres (Rp 30k)
        - potential_revenue_idr_market: Revenue dengan harga market (Rp 70k aprox)
        - trees_to_plant: Jumlah pohon yang perlu ditanam untuk offset
        - carbon_neutral_percentage: Persentase neutralisasi terhadap baseline
    """
    if 'total_emisi_kgco2' not in df.columns:
        raise ValueError("DataFrame harus memiliki kolom 'total_emisi_kgco2'")

    total_emisi_kg = df['total_emisi_kgco2'].sum()

    # Set baseline jika tidak diberikan
    if baseline_emission_kg is None:
        baseline_emission_kg = df['total_emisi_kgco2'].mean()

    # Calculate reduction (relative to baseline)
    baseline_total = baseline_emission_kg * len(df)
    reduction_kg = max(0, baseline_total - total_emisi_kg)

    # Convert to ton CO2e
    carbon_credit_ton = reduction_kg / 1000

    # Calculate revenue dengan berbagai harga acuan
    # Perpres 98/2021: Rp 30.000/ton
    revenue_perpres = carbon_credit_ton * 30000

    # Market rate (IDXCarbon aprox Rp 70.000/ton)
    revenue_market = carbon_credit_ton * 70000

    # Revenue dengan user input price
    revenue_user_price = carbon_credit_ton * carbon_price_idr_per_ton

    # Trees needed (1 pohon offset ~20kg CO2/tahun)
    trees_to_plant = int(np.ceil(total_emisi_kg / 20))

    # Carbon neutral percentage (reduction relative to baseline)
    if baseline_total > 0:
        carbon_neutral_pct = (reduction_kg / baseline_total) * 100
    else:
        carbon_neutral_pct = 0

    return {
        'total_emisi_kg': float(total_emisi_kg),
        'baseline_emisi_kg': float(baseline_emission_kg),
        'reduction_kg': float(reduction_kg),
        'carbon_credit_ton': float(carbon_credit_ton),
        'carbon_price_used': float(carbon_price_idr_per_ton),
        'potential_revenue_idr_perpres': float(revenue_perpres),
        'potential_revenue_idr_market': float(revenue_market),
        'potential_revenue_idr_user': float(revenue_user_price),
        'trees_to_plant': trees_to_plant,
        'carbon_neutral_percentage': float(carbon_neutral_pct),
        'data_points': len(df)
    }


def calculate_carbon_credit_per_row(df: pd.DataFrame, baseline_kg: float,
                                   carbon_price_idr: float = 30000) -> pd.DataFrame:
    """
    Tambahkan kolom carbon credit per baris untuk tracking harian

    Args:
        df: DataFrame dengan total_emisi_kgco2
        baseline_kg: Baseline emisi per hari (kg)
        carbon_price_idr: Harga karbon (IDR/ton)

    Returns:
        DataFrame dengan kolom tambahan:
        - carbon_credit_kg: Emisi tersebut (sebagai credit)
        - offset_trees: Pohon needed untuk offset
        - revenue_per_day_idr: Potensi revenue hari itu
    """
    df_result = df.copy()

    # Per-day carbon credit = emisi hari itu (dalam kg)
    df_result['carbon_credit_kg'] = df_result['total_emisi_kgco2']

    # Per-day trees needed (1 pohon ~20kg CO2)
    df_result['offset_trees'] = (df_result['total_emisi_kgco2'] / 20).round(0).astype(int)

    # Per-day revenue (dalam rupiah)
    # Konversi kg ke ton dulu
    df_result['revenue_per_day_idr'] = (
        (df_result['total_emisi_kgco2'] / 1000) * carbon_price_idr
    ).round(0).astype(int)

    return df_result
