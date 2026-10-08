from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import pytest

from app.logica import altas_nuevas, pasar_un_mes, puntuar

RUTA_MODELO = Path(__file__).resolve().parents[1] / "app" / "model" / "churn_classifier.joblib"


@pytest.fixture(scope="module")
def modelo():
    """El modelo exportado que usa la app."""
    return joblib.load(RUTA_MODELO)


@pytest.fixture
def clientes():
    """Tres clientes inventados en formato silver: nuevo sin internet,
    fibra sin teléfono y cliente de 72 meses con todo contratado."""
    return pd.DataFrame({
        "customer_id": ["TEST-0001", "TEST-0002", "TEST-0003"],
        "gender": ["Female", "Male", "Female"],
        "senior_citizen": [0, 1, 0],
        "partner": ["No", "Yes", "Yes"],
        "dependents": ["No", "No", "Yes"],
        "tenure": [0, 5, 72],
        "phone_service": ["Yes", "No", "Yes"],
        "multiple_lines": ["No", "No phone service", "Yes"],
        "internet_service": ["No", "Fiber optic", "DSL"],
        "online_security": ["No internet service", "No", "Yes"],
        "online_backup": ["No internet service", "No", "Yes"],
        "device_protection": ["No internet service", "No", "Yes"],
        "tech_support": ["No internet service", "No", "Yes"],
        "streaming_tv": ["No internet service", "Yes", "Yes"],
        "streaming_movies": ["No internet service", "No", "Yes"],
        "contract": ["Month-to-month", "Month-to-month", "Two year"],
        "paperless_billing": ["No", "Yes", "Yes"],
        "payment_method": ["Mailed check", "Electronic check", "Credit card (automatic)"],
        "monthly_charges": [20.0, 80.0, 110.0],
        "total_charges": [0.0, 400.0, 7920.0],
    })


class ModeloFijo:
    """Sustituto del modelo que devuelve probabilidades conocidas,
    para comprobar la comparación con el umbral sin depender del modelo real."""

    def __init__(self, probabilidades):
        self.probabilidades = np.array(probabilidades)

    def predict_proba(self, X):
        return np.column_stack([1 - self.probabilidades, self.probabilidades])


def test_puntuar_devuelve_una_fila_por_cliente(clientes, modelo):
    puntuados = puntuar(clientes, modelo, 0.4)
    assert len(puntuados) == len(clientes)


def test_puntuar_probabilidades_entre_0_y_1(clientes, modelo):
    puntuados = puntuar(clientes, modelo, 0.4)
    assert puntuados["churn_probability"].between(0, 1).all()


def test_puntuar_no_modifica_la_entrada(clientes, modelo):
    original = clientes.copy()
    puntuar(clientes, modelo, 0.4)
    pd.testing.assert_frame_equal(clientes, original)


def test_puntuar_funciona_sin_customer_id(clientes, modelo):
    sin_id = clientes.drop(columns=["customer_id"])
    puntuados = puntuar(sin_id, modelo, 0.4)
    assert len(puntuados) == len(sin_id)


def test_puntuar_umbral_incluye_el_limite(clientes):
    modelo_fijo = ModeloFijo([0.39, 0.40, 0.41])
    puntuados = puntuar(clientes, modelo_fijo, 0.40)
    assert puntuados["en_riesgo"].tolist() == [False, True, True]


def test_pasar_un_mes_suma_un_mes_con_tope(clientes):
    siguiente = pasar_un_mes(clientes)
    assert siguiente["tenure"].tolist() == [1, 6, 72]


def test_pasar_un_mes_suma_el_cargo_mensual(clientes):
    siguiente = pasar_un_mes(clientes)
    # El cliente con 72 meses no cambia: ni antigüedad ni cargos
    assert siguiente["total_charges"].tolist() == [20.0, 480.0, 7920.0]


def test_pasar_un_mes_no_modifica_la_entrada(clientes):
    original = clientes.copy()
    pasar_un_mes(clientes)
    pd.testing.assert_frame_equal(clientes, original)


def test_altas_nuevas_crea_el_numero_pedido(clientes):
    con_altas = altas_nuevas(clientes, 5, semilla=42)
    assert len(con_altas) == len(clientes) + 5


def test_altas_nuevas_ids_no_chocan(clientes):
    con_altas = altas_nuevas(clientes, 5, semilla=42)
    nuevas = con_altas.iloc[len(clientes):]
    assert con_altas["customer_id"].is_unique
    assert not nuevas["customer_id"].isin(clientes["customer_id"]).any()


def test_altas_nuevas_continuan_la_numeracion(clientes):
    primera_tanda = altas_nuevas(clientes, 3, semilla=42)
    segunda_tanda = altas_nuevas(primera_tanda, 2, semilla=42)
    nuevos_ids = segunda_tanda["customer_id"].iloc[len(primera_tanda):].tolist()
    assert nuevos_ids == ["NEW-0004", "NEW-0005"]
    assert segunda_tanda["customer_id"].is_unique


def test_altas_nuevas_empiezan_de_cero(clientes):
    con_altas = altas_nuevas(clientes, 5, semilla=42)
    nuevas = con_altas.iloc[len(clientes):]
    assert (nuevas["tenure"] == 0).all()
    assert (nuevas["total_charges"] == 0).all()


def test_altas_nuevas_reproducibles_con_semilla(clientes):
    primera = altas_nuevas(clientes, 5, semilla=42)
    segunda = altas_nuevas(clientes, 5, semilla=42)
    pd.testing.assert_frame_equal(primera, segunda)


def test_altas_nuevas_no_modifica_la_entrada(clientes):
    original = clientes.copy()
    altas_nuevas(clientes, 5, semilla=42)
    pd.testing.assert_frame_equal(clientes, original)


def test_simulacion_se_puede_puntuar(clientes, modelo):
    """Tras altas y varios meses, los clientes siguen siendo válidos para silver_a_gold."""
    estado = altas_nuevas(clientes, 5, semilla=42)
    for _ in range(3):
        estado = pasar_un_mes(estado)
    puntuados = puntuar(estado, modelo, 0.4)
    assert len(puntuados) == len(estado)
