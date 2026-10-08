"""Lógica de la app, separada de la interfaz para poder testearla sin Streamlit.

Ninguna función modifica los DataFrames que recibe: todas devuelven copias.
"""
import numpy as np
import pandas as pd

from churn.config import ID, TARGET
from churn.features import silver_a_gold

# Antigüedad máxima del dataset: el modelo nunca vio clientes con más meses
TENURE_MAXIMO = 72
PREFIJO_ALTA = "NEW-"


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


def pasar_un_mes(clientes: pd.DataFrame) -> pd.DataFrame:
    """Devuelve una copia de los clientes un mes después: tenure + 1 y
    total_charges + monthly_charges.

    Los clientes que ya tienen TENURE_MAXIMO meses no cambian. Si solo se sumaran
    los cargos, avg_historical_charge (total / tenure) crecería mes a mes sin que
    el cliente cambiara nada, y el modelo vería valores que nunca vio al entrenar."""
    siguiente = clientes.copy()
    avanzan = siguiente["tenure"] < TENURE_MAXIMO

    siguiente.loc[avanzan, "tenure"] = siguiente.loc[avanzan, "tenure"] + 1
    nuevo_total = siguiente.loc[avanzan, "total_charges"] + siguiente.loc[avanzan, "monthly_charges"]
    # Redondeo a céntimos para que las sumas sucesivas no acumulen error de coma flotante
    siguiente.loc[avanzan, "total_charges"] = nuevo_total.round(2)
    return siguiente


def siguiente_numero_alta(clientes: pd.DataFrame) -> int:
    """Primer número libre para un ID de alta nueva (NEW-0001, NEW-0002...)."""
    ids_altas = clientes.loc[clientes[ID].str.startswith(PREFIJO_ALTA), ID]
    if len(ids_altas) == 0:
        return 1
    numeros = ids_altas.str.removeprefix(PREFIJO_ALTA).astype(int)
    return int(numeros.max()) + 1


def altas_nuevas(clientes: pd.DataFrame, n: int, semilla: int | None = None) -> pd.DataFrame:
    """Devuelve una copia de los clientes con n altas nuevas añadidas al final.

    Cada alta copia el perfil de un cliente elegido al azar, con un customer_id
    nuevo, tenure = 0 y total_charges = 0. Con la misma semilla se eligen
    siempre los mismos perfiles."""
    generador = np.random.default_rng(semilla)
    filas = generador.integers(len(clientes), size=n)
    nuevas = clientes.iloc[filas].copy()

    primero = siguiente_numero_alta(clientes)
    ids_nuevos = []
    for i in range(n):
        ids_nuevos.append(f"{PREFIJO_ALTA}{primero + i:04d}")

    nuevas[ID] = ids_nuevos
    nuevas["tenure"] = 0
    nuevas["total_charges"] = 0.0
    return pd.concat([clientes, nuevas], ignore_index=True)


def cambios_en_riesgo(anterior: pd.DataFrame, actual: pd.DataFrame) -> tuple[list, list]:
    """Compara dos estados puntuados y devuelve los customer_id que entran y
    los que salen de la lista de riesgo. Una alta nueva en riesgo cuenta como entrada."""
    riesgo_antes = set(anterior.loc[anterior["en_riesgo"], ID])
    riesgo_ahora = set(actual.loc[actual["en_riesgo"], ID])
    entran = sorted(riesgo_ahora - riesgo_antes)
    salen = sorted(riesgo_antes - riesgo_ahora)
    return entran, salen
