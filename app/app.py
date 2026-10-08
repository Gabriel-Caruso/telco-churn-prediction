import json
import sys
from datetime import datetime
from pathlib import Path

import joblib
import streamlit as st

CARPETA_APP = Path(__file__).resolve().parent
sys.path.insert(0, str(CARPETA_APP.parent))

from textos import TEXTOS

URL_REPO = "https://github.com/Gabriel-Caruso/telco-churn-prediction"

st.set_page_config(page_title="Telco churn", layout="wide")


@st.cache_resource
def cargar_modelo():
    modelo = joblib.load(CARPETA_APP / "model" / "churn_classifier.joblib")
    metadatos = json.loads((CARPETA_APP / "model" / "churn_classifier.json").read_text())
    return modelo, metadatos


modelo, metadatos = cargar_modelo()

with st.sidebar:
    # La etiqueta va en los dos idiomas porque todavía no se sabe cuál se ha elegido.
    idioma = st.segmented_control(
        "Idioma / Language",
        options=["es", "en"],
        default="es",
        required=True,
        format_func=str.upper,
        key="idioma",
    )
    textos = TEXTOS[idioma]

    st.markdown(textos["sobre_proyecto"])
    st.markdown(f"[{textos['enlace_repo']}]({URL_REPO})")

    fecha_exportado = datetime.fromisoformat(metadatos["exportado"]).date().isoformat()
    with st.container(border=True):
        st.markdown(f"**{textos['ficha_modelo']}**")
        st.markdown(f"{textos['ficha_nombre']}: `{metadatos['model_name']}`")
        st.markdown(f"{textos['ficha_version']}: {metadatos['version']}")
        st.markdown(f"{textos['ficha_umbral']}: {metadatos['umbral']:.0%}")
        st.markdown(f"{textos['ficha_fecha']}: {fecha_exportado}")

st.title(textos["titulo"])
st.write(textos["subtitulo"])

pestana_cliente, pestana_riesgo, pestana_simulacion = st.tabs([
    textos["pestana_cliente"],
    textos["pestana_riesgo"],
    textos["pestana_simulacion"],
])
