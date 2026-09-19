import numpy as np
import pandas as pd
import pytest

from churn.features import (is_new_customer, tenure_max, n_support_services, n_entertainment_services, avg_historical_charge, charge_ratio)

SOPORTE = ["online_security", "online_backup", "device_protection", "tech_support"]
OCIO = ["streaming_tv", "streaming_movies"]


@pytest.fixture
def clientes():
    """Cuatro clientes inventados que cubren los casos importantes."""
    return pd.DataFrame({
        "tenure": [0,    5,    10,   72],
        "monthly_charges": [50.0, 30.0, 50.0, 60.0],
        "total_charges": [0.0,  100.0, 1000.0, 4320.0],
        "online_security": ["Yes", "No", "Yes", "No internet service"],
        "online_backup": ["Yes", "No", "Yes", "No internet service"],
        "device_protection": ["No",  "No", "Yes", "No internet service"],
        "tech_support": ["No",  "No", "Yes", "No internet service"],
        "streaming_tv": ["Yes", "No", "Yes", "No internet service"],
        "streaming_movies": ["No",  "No", "Yes", "No internet service"],
        "internet_service": ["Fiber optic", "Fiber optic", "DSL", "No"],
        "payment_method": ["Electronic check", "Credit card (automatic)",
                     "Mailed check", "Bank transfer (automatic)"],
    })


def test_is_new_customer(clientes):
    assert is_new_customer(clientes).tolist() == [True, False, False, False]


def test_tenure_max(clientes):
    assert tenure_max(clientes).tolist() == [False, False, False, True]


def test_n_support_services(clientes):
    assert n_support_services(clientes, SOPORTE).tolist() == [2, 0, 4, 0]


def test_n_entertainment_services(clientes):
    assert n_entertainment_services(clientes, OCIO).tolist() == [1, 0, 2, 0]


def test_avg_historical_charge(clientes):
    esperado = [50.0, 20.0, 100.0, 60.0]
    assert avg_historical_charge(clientes).tolist() == esperado


def test_avg_historical_charge_no_modifica_entrada(clientes):
    antes = clientes.copy()
    avg_historical_charge(clientes)
    pd.testing.assert_frame_equal(clientes, antes)


def test_charge_ratio(clientes):
    historico = avg_historical_charge(clientes)
    ratio = charge_ratio(clientes["monthly_charges"], historico)
    assert ratio.tolist() == [1.0, 1.5, 0.5, 1.0]

def test_fiber_no_support(clientes):
    # fila 0: fibra con 2 servicios -> False
    # fila 1: fibra con 0 servicios -> True
    # fila 2: DSL -> False
    # fila 3: sin internet -> False
    assert fiber_no_support(clientes).tolist() == [False, True, False, False]


def test_automatic_payment(clientes):
    assert automatic_payment(clientes).tolist() == [False, True, False, True]