"""Lógica de la app, separada de la interfaz para poder testearla sin Streamlit.

Ninguna función modifica los DataFrames que recibe: todas devuelven copias.
"""
import pandas as pd

from churn.config import ID, TARGET
from churn.features import silver_a_gold


def puntuar(clientes: pd.DataFrame, modelo, umbral: float) -> pd.DataFrame:
    """Recibe clientes en formato silver y devuelve una copia con dos columnas nuevas:
    churn_probability (probabilidad de irse) y en_riesgo (probabilidad >= umbral)."""
    gold = silver_a_gold(clientes)

    # El formulario de la pestaña 1 no tiene customer_id y los clientes actuales
    # no tienen churn, por eso se ignoran las columnas que no existan.
    X = gold.drop(columns=[ID, TARGET], errors="ignore")

    puntuados = clientes.copy()
    puntuados["churn_probability"] = modelo.predict_proba(X)[:, 1]
    puntuados["en_riesgo"] = puntuados["churn_probability"] >= umbral
    return puntuados
