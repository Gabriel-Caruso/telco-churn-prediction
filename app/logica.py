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


def _transformar(clientes: pd.DataFrame, modelo) -> np.ndarray:
    """Aplica silver_a_gold y el paso de preprocesado del pipeline."""
    gold = silver_a_gold(clientes)
    X = gold.drop(columns=[ID, TARGET], errors="ignore")
    return modelo.named_steps["preprocesado"].transform(X)


def medias_transformadas(clientes_train: pd.DataFrame, modelo) -> np.ndarray:
    """Media de cada variable transformada (tras OneHot y StandardScaler) en entrenamiento.
    Representa al 'cliente medio' con el que se compara cada cliente."""
    return _transformar(clientes_train, modelo).mean(axis=0)


def variable_de_cada_columna(modelo) -> list:
    """Para cada columna transformada, la variable gold de la que sale.
    Por ejemplo, cat__contract_Month-to-month sale de contract."""
    preprocesado = modelo.named_steps["preprocesado"]
    variables = []
    for nombre, transformador, columnas in preprocesado.transformers_:
        if transformador == "drop":
            continue
        if nombre == "cat":
            # El OneHotEncoder crea una columna por cada categoría de cada variable
            for columna, categorias in zip(columnas, transformador.categories_):
                for _ in categorias:
                    variables.append(columna)
        else:
            for columna in columnas:
                variables.append(columna)
    return variables


def contribuciones(cliente: pd.DataFrame, modelo, medias: np.ndarray) -> pd.DataFrame:
    """Aportación de cada variable a la predicción de un cliente (una fila en formato silver),
    respecto al cliente medio de entrenamiento.

    En una regresión logística el logit es intercepto + suma de coef * valor. La aportación
    de cada columna es coef * (valor - media), así que la suma de aportaciones es el logit
    del cliente menos el logit del cliente medio: positivo sube la probabilidad de baja.
    Es el valor SHAP exacto de un modelo lineal. Las columnas del OneHot se suman por variable.

    Devuelve una fila por variable con su valor en gold y su aportación, ordenada de mayor
    a menor aportación."""
    coeficientes = modelo.named_steps["modelo"].coef_[0]
    valores = _transformar(cliente, modelo)[0]
    aportes = coeficientes * (valores - medias)

    suma_por_variable = {}
    for variable, aporte in zip(variable_de_cada_columna(modelo), aportes):
        suma_por_variable[variable] = suma_por_variable.get(variable, 0.0) + aporte

    gold = silver_a_gold(cliente)
    filas = []
    for variable, aporte in suma_por_variable.items():
        filas.append({
            "variable": variable,
            "valor": gold[variable].iloc[0],
            "contribucion": aporte,
        })
    tabla = pd.DataFrame(filas)
    return tabla.sort_values("contribucion", ascending=False, ignore_index=True)
