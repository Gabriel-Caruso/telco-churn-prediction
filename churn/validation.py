import pandas as pd
import numpy as np

from churn.config import FEATURES_DERIVADAS

def validar_silver(pdf: pd.DataFrame, filas: int = 7043, columnas: int = 21) -> None:
    """Contrato de la tabla silver. Vale como salida de 03 y como entrada de 04."""
    sin_normalizar = [c for c in pdf.columns if c != c.lower()]
    nulos = pdf.isna().sum().sum()

    assert pdf.shape == (filas, columnas), f"Forma inesperada: {pdf.shape}"
    assert not sin_normalizar, f"Columnas sin normalizar: {sin_normalizar}"
    assert pdf["customer_id"].is_unique, "Hay customer_id duplicados"
    assert pdf["total_charges"].dtype == "float64", \
        f"total_charges es {pdf['total_charges'].dtype}"
    assert pdf["churn"].isin([0, 1]).all(), "churn contiene valores fuera de 0 y 1"
    assert nulos == 0, f"Hay {nulos} nulos en la tabla"

    print(f"Contrato de silver OK — {pdf.shape[0]:,} filas x {pdf.shape[1]} columnas")

def validar_gold(pdf: pd.DataFrame, filas: int = 7043, columnas: int = 28) -> None:
    """Contrato de la tabla gold. Vale como salida de 04 y como entrada del modelado."""
    faltan = [c for c in FEATURES_DERIVADAS if c not in pdf.columns]
    numericas = pdf.select_dtypes("number")
    nulos = pdf.isna().sum().sum()

    assert pdf.shape == (filas, columnas), f"Forma inesperada: {pdf.shape}"
    assert not faltan, f"Faltan features en gold: {faltan}"
    assert "total_charges" not in pdf.columns, "total_charges debería estar descartada"
    assert pdf["customer_id"].is_unique, "Hay customer_id duplicados"
    assert pdf["churn"].isin([0, 1]).all(), "churn fuera de 0 y 1"
    assert nulos == 0, f"Hay {nulos} nulos en la tabla"
    assert np.isfinite(numericas).all().all(), "Hay infinitos en alguna columna numérica"

    print(f"Contrato de gold OK — {pdf.shape[0]:,} filas x {pdf.shape[1]} columnas")