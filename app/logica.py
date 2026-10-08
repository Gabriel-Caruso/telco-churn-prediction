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


def matriz_contribuciones(clientes: pd.DataFrame, modelo, medias: np.ndarray) -> pd.DataFrame:
    """Aportación de cada variable para cada cliente, respecto al cliente medio de entrenamiento.

    En una regresión logística el logit es intercepto + suma de coef * valor. La aportación
    de cada columna es coef * (valor - media), así que la suma de aportaciones de un cliente
    es su logit menos el logit del cliente medio: positivo sube la probabilidad de baja.
    Es el valor SHAP exacto de un modelo lineal. Las columnas del OneHot se suman por variable.

    Devuelve un DataFrame con una fila por cliente y una columna por variable gold."""
    coeficientes = modelo.named_steps["modelo"].coef_[0]
    aportes = coeficientes * (_transformar(clientes, modelo) - medias)

    por_variable = {}
    for posicion, variable in enumerate(variable_de_cada_columna(modelo)):
        if variable not in por_variable:
            por_variable[variable] = aportes[:, posicion]
        else:
            por_variable[variable] = por_variable[variable] + aportes[:, posicion]
    return pd.DataFrame(por_variable, index=clientes.index)


def contribuciones(cliente: pd.DataFrame, modelo, medias: np.ndarray) -> pd.DataFrame:
    """Aportaciones de un solo cliente (una fila en formato silver), con su valor en gold.
    Devuelve una fila por variable, ordenada de mayor a menor aportación."""
    aportes = matriz_contribuciones(cliente, modelo, medias).iloc[0]
    gold = silver_a_gold(cliente)

    filas = []
    for variable, aporte in aportes.items():
        filas.append({
            "variable": variable,
            "valor": gold[variable].iloc[0],
            "contribucion": aporte,
        })
    tabla = pd.DataFrame(filas)
    return tabla.sort_values("contribucion", ascending=False, ignore_index=True)


def importancia_global(clientes: pd.DataFrame, modelo, medias: np.ndarray) -> pd.Series:
    """Media del valor absoluto de la aportación de cada variable sobre un conjunto de
    clientes: cuánto mueve cada variable la predicción, en promedio y sin importar el signo.
    Ordenada de mayor a menor."""
    absolutas = matriz_contribuciones(clientes, modelo, medias).abs()
    return absolutas.mean().sort_values(ascending=False)


def matriz_confusion(churn_real: pd.Series, probabilidad: pd.Series, umbral: float) -> dict:
    """Cuenta de las cuatro casillas con el criterio de la app: en riesgo si probabilidad >= umbral."""
    marcados = probabilidad >= umbral
    se_van = churn_real == 1
    return {
        "detectados": int((marcados & se_van).sum()),
        "falsas_alarmas": int((marcados & ~se_van).sum()),
        "perdidos": int((~marcados & se_van).sum()),
        "bien_descartados": int((~marcados & ~se_van).sum()),
    }


def curva_ganancia(churn_real: pd.Series, probabilidad: pd.Series) -> pd.DataFrame:
    """Curva de ganancia acumulada: si se contacta a los clientes de mayor a menor
    probabilidad, qué fracción de las bajas se ha capturado tras contactar a cada fracción
    de clientes. Empieza en (0, 0) y termina en (1, 1)."""
    orden = probabilidad.sort_values(ascending=False).index
    capturadas = churn_real.loc[orden].cumsum().to_numpy() / churn_real.sum()
    contactados = np.arange(1, len(orden) + 1) / len(orden)
    return pd.DataFrame({
        "contactados": np.concatenate([[0.0], contactados]),
        "capturadas": np.concatenate([[0.0], capturadas]),
    })


def tasa_por_grupo(clientes: pd.DataFrame, columna: str) -> pd.DataFrame:
    """Tasa de baja y número de clientes de cada valor de una columna.
    Necesita la columna churn (formato silver completo)."""
    agrupado = clientes.groupby(columna)[TARGET]
    return pd.DataFrame({
        "grupo": agrupado.mean().index,
        "tasa": agrupado.mean().to_numpy(),
        "clientes": agrupado.size().to_numpy(),
    })


def numero_de_extras(clientes: pd.DataFrame, servicios: list) -> pd.Series:
    """Cuántos de los servicios indicados tiene contratados cada cliente."""
    return (clientes[servicios] == "Yes").sum(axis=1)


def diferencia_por_servicio(clientes: pd.DataFrame, servicios: list) -> pd.DataFrame:
    """Para cada servicio, tasa de baja sin el servicio menos tasa con el servicio,
    entre los clientes que pueden contratarlo (se excluye 'No internet service')."""
    filas = []
    for servicio in servicios:
        tasa_sin = clientes.loc[clientes[servicio] == "No", TARGET].mean()
        tasa_con = clientes.loc[clientes[servicio] == "Yes", TARGET].mean()
        filas.append({"servicio": servicio, "diferencia": tasa_sin - tasa_con})
    tabla = pd.DataFrame(filas)
    return tabla.sort_values("diferencia", ascending=False, ignore_index=True)


def tasa_por_tramos(clientes: pd.DataFrame, columna: str, n_tramos: int) -> pd.DataFrame:
    """Tasa de baja por tramos de igual número de clientes (cuantiles) de una columna numérica.
    El grupo es el rango del tramo como texto, por ejemplo '68-81'."""
    tramos = pd.qcut(clientes[columna], n_tramos)
    agrupado = clientes.groupby(tramos, observed=True)[TARGET]
    nombres = []
    for intervalo in agrupado.mean().index:
        nombres.append(f"{intervalo.left:.0f}-{intervalo.right:.0f}")
    return pd.DataFrame({
        "grupo": nombres,
        "tasa": agrupado.mean().to_numpy(),
        "clientes": agrupado.size().to_numpy(),
    })
