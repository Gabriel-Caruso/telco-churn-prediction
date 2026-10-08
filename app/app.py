import json
import sys
from pathlib import Path

import joblib
import streamlit as st

CARPETA_APP = Path(__file__).resolve().parent
sys.path.insert(0, str(CARPETA_APP.parent))

from churn.features import silver_a_gold


@st.cache_resource
def cargar_modelo():
    modelo = joblib.load(CARPETA_APP / "model" / "churn_classifier.joblib")
    metadatos = json.loads((CARPETA_APP / "model" / "churn_classifier.json").read_text())
    return modelo, metadatos


modelo, metadatos = cargar_modelo()

st.title("Telco churn")
st.write(f"Modelo {metadatos['model_name']}, versión {metadatos['version']}")