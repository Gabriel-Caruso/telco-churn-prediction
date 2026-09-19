import numpy as np
import pandas as pd

from churn.config import SERVICIOS_SOPORTE, SERVICIOS_OCIO, METODOS_AUTOMATICOS

def is_new_customer(pdf: pd.DataFrame) -> pd.Series:
    return pdf["tenure"] == 0

def tenure_max(pdf: pd.DataFrame) -> pd.Series:
    return pdf["tenure"] == 72

def n_support_services(pdf: pd.DataFrame, columnas=SERVICIOS_SOPORTE) -> pd.Series:
    return (pdf[columnas] == "Yes").sum(axis=1)

def n_entertainment_services(pdf: pd.DataFrame, columnas=SERVICIOS_OCIO) -> pd.Series:
    return (pdf[columnas] == "Yes").sum(axis=1)

def avg_historical_charge(pdf: pd.DataFrame) -> pd.Series:
    sin_facturar = (pdf["total_charges"] == 0) & (pdf["tenure"] > 0)
    assert not sin_facturar.any(), \
        f"{sin_facturar.sum()} clientes con antigüedad pero sin facturación"

    tenure_seguro = pdf["tenure"].replace(0, np.nan)
    return (pdf["total_charges"] / tenure_seguro).fillna(pdf["monthly_charges"])

def charge_ratio(monthly: pd.Series, historical: pd.Series) -> pd.Series:
    return monthly / historical

def fiber_no_support(pdf: pd.DataFrame) -> pd.Series:
    return (pdf["internet_service"] == "Fiber optic") & (n_support_services(pdf) == 0)


def automatic_payment(pdf: pd.DataFrame, metodos=METODOS_AUTOMATICOS) -> pd.Series:
    return pdf["payment_method"].isin(metodos)