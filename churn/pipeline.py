from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression

CATEGORICAS_TEXTO = [
    "gender", "partner", "dependents",
    "phone_service", "multiple_lines",
    "internet_service", "online_security", "online_backup",
    "device_protection", "tech_support", "streaming_tv", "streaming_movies",
    "contract", "paperless_billing", "payment_method",
]

NUMERICAS = [
    "tenure", "monthly_charges", "avg_historical_charge", "charge_ratio",
    "n_support_services", "n_entertainment_services",
]

BINARIAS = [
    "senior_citizen", "is_new_customer", "tenure_max",
    "fiber_no_support", "automatic_payment",
]

def construir_preprocesado() -> ColumnTransformer:
    """Aplica una transformación distinta a cada grupo de columnas."""
    return ColumnTransformer(
        transformers=[
            ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False),
             CATEGORICAS_TEXTO),
            ("num", StandardScaler(), NUMERICAS),
            ("bin", "passthrough", BINARIAS),
        ]
    )


def construir_pipeline(modelo) -> Pipeline:
    """Encadena el preprocesado con el modelo que se le pase."""
    return Pipeline([
        ("preprocesado", construir_preprocesado()),
        ("modelo", modelo),
    ])