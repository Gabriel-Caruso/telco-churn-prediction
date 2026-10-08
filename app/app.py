import json
import sys
from datetime import datetime
from pathlib import Path

import altair as alt
import joblib
import numpy as np
import pandas as pd
import streamlit as st
from sklearn.metrics import average_precision_score, precision_recall_curve

CARPETA_APP = Path(__file__).resolve().parent
sys.path.insert(0, str(CARPETA_APP.parent))

from churn.config import ID, SERVICIOS_OCIO, SERVICIOS_SOPORTE
from logica import (
    altas_nuevas, cambios_en_riesgo, contribuciones, curva_ganancia, importancia_global,
    matriz_confusion, medias_transformadas, pasar_un_mes, puntuar,
)
from textos import TEXTOS

URL_REPO = "https://github.com/Gabriel-Caruso/telco-churn-prediction"

# Okabe-Ito: naranja para riesgo, azul para fuera de riesgo
COLOR_RIESGO = "#E69F00"
COLOR_SIN_RIESGO = "#0072B2"

SERVICIOS_INTERNET = SERVICIOS_SOPORTE + SERVICIOS_OCIO
SI_NO = ["Yes", "No"]
OPCIONES = {
    "gender": ["Female", "Male"],
    "senior_citizen": [0, 1],
    "partner": SI_NO,
    "dependents": SI_NO,
    "contract": ["Month-to-month", "One year", "Two year"],
    "paperless_billing": SI_NO,
    "payment_method": [
        "Electronic check",
        "Mailed check",
        "Bank transfer (automatic)",
        "Credit card (automatic)",
    ],
    "phone_service": SI_NO,
    "internet_service": ["DSL", "Fiber optic", "No"],
}
COLUMNAS_TABLA = [
    ID, "churn_probability", "en_riesgo", "contract", "tenure",
    "monthly_charges", "internet_service", "payment_method",
]
COLUMNAS_FILTRO = ["contract", "internet_service", "payment_method"]
COLUMNAS_ENTERAS = ["senior_citizen", "tenure"]
# Variables que más suben y más bajan el riesgo que se muestran en la explicación
N_EXPLICACION = 5
# Variables que se muestran en el gráfico de importancia global
N_IMPORTANCIA = 12
COLUMNAS_DECIMALES = ["monthly_charges", "total_charges"]

st.set_page_config(page_title="Telco churn", layout="wide")


@st.cache_resource
def cargar_modelo():
    modelo = joblib.load(CARPETA_APP / "model" / "churn_classifier.joblib")
    metadatos = json.loads((CARPETA_APP / "model" / "churn_classifier.json").read_text())
    return modelo, metadatos


@st.cache_data
def cargar_clientes_actuales():
    return pd.read_csv(CARPETA_APP / "data" / "clientes_actuales.csv")


@st.cache_data
def puntuar_clientes_actuales(_modelo, umbral):
    """Puntúa los clientes del CSV una sola vez. El guion bajo de _modelo le dice
    a Streamlit que no use ese argumento para decidir si el resultado está en caché."""
    return puntuar(cargar_clientes_actuales(), _modelo, umbral)


@st.cache_data
def cargar_clientes_silver():
    """Los 7043 clientes de silver, con la columna churn."""
    return pd.read_csv(CARPETA_APP / "data" / "clientes_silver.csv")


@st.cache_data
def cargar_ids_test():
    """IDs del conjunto de test: el mismo split que se usó en Databricks
    (ids_test.csv sale de gold_split.csv, exportado en 11_challenger)."""
    return pd.read_csv(CARPETA_APP / "data" / "ids_test.csv")[ID]


@st.cache_data
def puntuar_test(_modelo, umbral):
    silver = cargar_clientes_silver()
    test = silver[silver[ID].isin(cargar_ids_test())]
    return puntuar(test, _modelo, umbral)


@st.cache_data
def medias_entrenamiento(_modelo):
    """Cliente medio de entrenamiento, con el que se compara cada cliente en la explicación."""
    silver = cargar_clientes_silver()
    train = silver[~silver[ID].isin(cargar_ids_test())]
    return medias_transformadas(train, _modelo)


@st.cache_data
def cargar_challengers():
    """Diferencias de PR-AUC por fold frente a la regresión logística, copiadas de
    notebooks/11_challenger.ipynb. No se calculan aquí: habría que reentrenar los modelos."""
    return pd.read_csv(CARPETA_APP / "data" / "challenger_folds.csv")


@st.cache_data
def importancia_test(_modelo, umbral):
    return importancia_global(puntuar_test(_modelo, umbral), _modelo, medias_entrenamiento(_modelo))


modelo, metadatos = cargar_modelo()
umbral = metadatos["umbral"]
clientes = cargar_clientes_actuales()
COLUMNAS_FORMULARIO = clientes.columns.drop(ID).tolist()


def clave(columna):
    """Nombre en st.session_state del widget de una columna del formulario."""
    return f"form_{columna}"


def mostrar_valor(valor):
    """Traduce un valor del dataset para mostrarlo; si no hay traducción, lo deja igual."""
    return textos["valores"].get(valor, valor)


def rellenar_formulario(cliente):
    """Copia los valores de un cliente (una fila de silver) en los widgets del formulario."""
    for columna in COLUMNAS_FORMULARIO:
        valor = cliente[columna]
        if columna in COLUMNAS_ENTERAS:
            valor = int(valor)
        elif columna in COLUMNAS_DECIMALES:
            valor = float(valor)
        st.session_state[clave(columna)] = valor
    st.session_state["form_customer_id"] = cliente[ID]


def cargar_cliente_azar(clientes):
    fila = st.session_state["generador"].integers(len(clientes))
    rellenar_formulario(clientes.iloc[fila])


def proponer_total():
    """Al cambiar antigüedad o cargo mensual, propone su producto como cargo acumulado.
    Con antigüedad 0 el resultado es 0, que es la regla que se pide."""
    tenure = st.session_state[clave("tenure")]
    mensual = st.session_state[clave("monthly_charges")]
    st.session_state[clave("total_charges")] = round(tenure * mensual, 2)


def ajustar_lineas():
    """Sin línea telefónica, varias líneas solo puede valer 'No phone service'."""
    if st.session_state[clave("phone_service")] == "No":
        st.session_state[clave("multiple_lines")] = "No phone service"
    elif st.session_state[clave("multiple_lines")] == "No phone service":
        st.session_state[clave("multiple_lines")] = "No"


def ajustar_servicios_internet():
    """Sin internet, los seis servicios de internet solo pueden valer 'No internet service'."""
    sin_internet = st.session_state[clave("internet_service")] == "No"
    for servicio in SERVICIOS_INTERNET:
        if sin_internet:
            st.session_state[clave(servicio)] = "No internet service"
        elif st.session_state[clave(servicio)] == "No internet service":
            st.session_state[clave(servicio)] = "No"


def construir_cliente():
    """Devuelve el cliente del formulario como un DataFrame de una fila en formato silver."""
    cliente = {}
    for columna in COLUMNAS_FORMULARIO:
        cliente[columna] = st.session_state[clave(columna)]
    return pd.DataFrame([cliente])


def etiqueta_riesgo(en_riesgo):
    """Etiqueta con color y texto: el color nunca es la única diferencia."""
    if en_riesgo:
        color_fondo, color_texto, texto = COLOR_RIESGO, "#000000", textos["en_riesgo"]
    else:
        color_fondo, color_texto, texto = COLOR_SIN_RIESGO, "#FFFFFF", textos["sin_riesgo"]
    return (
        f'<span style="background-color: {color_fondo}; color: {color_texto}; '
        f'padding: 0.25rem 0.75rem; border-radius: 0.5rem; font-weight: 600;">{texto}</span>'
    )


def reiniciar_simulacion(clientes):
    """Deja la simulación en el mes 0, con los clientes actuales ya puntuados."""
    st.session_state["sim_clientes"] = clientes
    st.session_state["sim_puntuados"] = puntuar_clientes_actuales(modelo, umbral)
    st.session_state["sim_mes"] = 0
    st.session_state["sim_entran"] = None
    st.session_state["sim_salen"] = None
    st.session_state["sim_ultima_accion"] = None


def aplicar_nuevo_estado(nuevo_estado):
    """Puntúa el nuevo estado y guarda quién entra y sale de la lista respecto al anterior."""
    puntuados = puntuar(nuevo_estado, modelo, umbral)
    entran, salen = cambios_en_riesgo(st.session_state["sim_puntuados"], puntuados)
    st.session_state["sim_clientes"] = nuevo_estado
    st.session_state["sim_puntuados"] = puntuados
    st.session_state["sim_entran"] = len(entran)
    st.session_state["sim_salen"] = len(salen)


def simular_un_mes():
    st.session_state["sim_mes"] = st.session_state["sim_mes"] + 1
    aplicar_nuevo_estado(pasar_un_mes(st.session_state["sim_clientes"]))
    st.session_state["sim_ultima_accion"] = ("mes", 0)


def simular_altas():
    n = st.session_state["sim_n_altas"]
    mes = st.session_state["sim_mes"]
    aplicar_nuevo_estado(altas_nuevas(st.session_state["sim_clientes"], n, semilla=42 + mes))
    st.session_state["sim_ultima_accion"] = ("altas", n)


def diagrama_arquitectura():
    """Devuelve el diagrama del proyecto en lenguaje DOT de Graphviz.
    Cada nodo es 'id [label="..."]' y cada flecha 'origen -> destino'."""
    nodos = textos["arquitectura"]
    nodos_databricks = [
        "datos", "bronze", "silver", "gold", "entrenamiento", "challenger",
        "mlflow", "registro", "batch", "serving", "exportacion",
    ]
    flechas = [
        ("datos", "bronze"), ("bronze", "silver"), ("silver", "gold"),
        ("gold", "entrenamiento"), ("gold", "challenger"),
        ("entrenamiento", "mlflow"), ("challenger", "mlflow"), ("mlflow", "registro"),
        ("registro", "batch"), ("registro", "serving"), ("registro", "exportacion"),
        ("exportacion", "app"),
    ]
    # El paquete churn alimenta la capa gold y la app: flechas discontinuas
    flechas_paquete = [("paquete", "gold"), ("paquete", "app")]

    lineas = [
        "digraph {",
        'rankdir=LR; bgcolor="transparent";',
        'node [shape=box, style="rounded,filled", fillcolor="#F2F2F2", '
        'color="#999999", fontcolor="#1A1A1A", fontname="sans-serif", fontsize=11];',
        'edge [color="#999999"];',
        "subgraph cluster_databricks {",
        f'label="{nodos["grupo_databricks"]}"; fontcolor="#999999"; color="#999999"; style="dashed,rounded";',
    ]
    for nodo in nodos_databricks:
        lineas.append(f'{nodo} [label="{nodos[nodo]}"];')
    lineas.append("}")
    lineas.append("subgraph cluster_streamlit {")
    lineas.append(
        f'label="{nodos["grupo_streamlit"]}"; fontcolor="#999999"; color="#999999"; style="dashed,rounded";'
    )
    lineas.append(f'app [label="{nodos["app"]}"];')
    lineas.append("}")
    lineas.append(f'paquete [label="{nodos["paquete"]}"];')

    for origen, destino in flechas:
        lineas.append(f"{origen} -> {destino};")
    for origen, destino in flechas_paquete:
        lineas.append(f"{origen} -> {destino} [style=dashed];")
    lineas.append("}")
    return "\n".join(lineas)


def formatear_valor(valor):
    """Valor de una variable gold para mostrarlo: números con su cifra, el resto traducido.
    Los enteros no pasan por mostrar_valor porque 0 y 1 se traducirían como No y Sí."""
    if isinstance(valor, (bool, np.bool_)):
        return mostrar_valor(int(valor))
    if isinstance(valor, (int, np.integer)):
        return str(valor)
    if isinstance(valor, (float, np.floating)):
        return f"{valor:.2f}"
    return mostrar_valor(valor)


def grafico_contribuciones(tabla):
    """Barras horizontales con las variables que más suben y más bajan el riesgo."""
    suben = tabla[tabla["contribucion"] > 0].head(N_EXPLICACION)
    # La tabla está ordenada de mayor a menor: las que más bajan están al final
    bajan = tabla[tabla["contribucion"] < 0].tail(N_EXPLICACION)
    datos = pd.concat([suben, bajan], ignore_index=True)

    etiquetas = []
    efectos = []
    for variable, valor, aporte in zip(datos["variable"], datos["valor"], datos["contribucion"]):
        etiquetas.append(f"{textos['campos'][variable]}: {formatear_valor(valor)}")
        if aporte > 0:
            efectos.append(textos["explicacion_sube"])
        else:
            efectos.append(textos["explicacion_baja"])
    datos["etiqueta"] = etiquetas
    datos["efecto"] = efectos
    # La columna valor mezcla texto, números y booleanos y el gráfico no la necesita
    datos = datos[["etiqueta", "efecto", "contribucion"]]

    colores = alt.Scale(
        domain=[textos["explicacion_sube"], textos["explicacion_baja"]],
        range=[COLOR_RIESGO, COLOR_SIN_RIESGO],
    )
    barras = alt.Chart(datos).mark_bar().encode(
        x=alt.X("contribucion:Q", title=textos["explicacion_eje"]),
        y=alt.Y("etiqueta:N", sort="-x", title=None),
        color=alt.Color("efecto:N", title=textos["explicacion_efecto"], scale=colores),
        tooltip=[
            alt.Tooltip("etiqueta:N", title=textos["explicacion_variable"]),
            alt.Tooltip("contribucion:Q", title=textos["explicacion_eje"], format="+.2f"),
        ],
    )
    cero = alt.Chart(pd.DataFrame({"cero": [0]})).mark_rule(color="gray").encode(x="cero:Q")
    return barras + cero


def grafico_precision_recall(test, umbral_prueba, matriz):
    """Curva PR del conjunto de test, con el umbral de prueba marcado y la línea del azar."""
    precision, recall, _ = precision_recall_curve(test["churn"], test["churn_probability"])
    curva = pd.DataFrame({"recall": recall, "precision": precision, "orden": range(len(recall))})
    base = test["churn"].mean()

    linea = alt.Chart(curva).mark_line(color="gray").encode(
        x=alt.X("recall:Q", title=textos["eje_recall"], scale=alt.Scale(domain=[0, 1])),
        y=alt.Y("precision:Q", title=textos["eje_precision"], scale=alt.Scale(domain=[0, 1])),
        order="orden:Q",
    )
    azar = alt.Chart(pd.DataFrame({"base": [base]})).mark_rule(
        color="gray", strokeDash=[6, 4],
    ).encode(y="base:Q")

    detectados = matriz["detectados"]
    marcados = detectados + matriz["falsas_alarmas"]
    if marcados > 0:
        precision_umbral = detectados / marcados
    else:
        precision_umbral = 1.0
    punto_datos = pd.DataFrame({
        "recall": [detectados / (detectados + matriz["perdidos"])],
        "precision": [precision_umbral],
        "etiqueta": [f"{textos['modelo_slider']}: {umbral_prueba:.2f}"],
    })
    punto = alt.Chart(punto_datos).mark_point(size=120, filled=True, color="gray").encode(
        x="recall:Q", y="precision:Q", tooltip=["etiqueta:N"],
    )
    return linea + azar + punto


def grafico_ganancia(test, umbral_prueba):
    """Curva de ganancia acumulada del modelo frente a contactar al azar.
    Las dos series se distinguen por el trazo, no solo por el color."""
    curva = curva_ganancia(test["churn"], test["churn_probability"])
    curva["serie"] = textos["serie_modelo"]
    azar = pd.DataFrame({
        "contactados": [0.0, 1.0],
        "capturadas": [0.0, 1.0],
        "serie": [textos["serie_azar"], textos["serie_azar"]],
    })
    datos = pd.concat([curva, azar], ignore_index=True)

    lineas = alt.Chart(datos).mark_line(color="gray").encode(
        x=alt.X("contactados:Q", title=textos["eje_contactados"], axis=alt.Axis(format="%")),
        y=alt.Y("capturadas:Q", title=textos["eje_capturadas"], axis=alt.Axis(format="%")),
        strokeDash=alt.StrokeDash(
            "serie:N", title=textos["serie"],
            scale=alt.Scale(
                domain=[textos["serie_modelo"], textos["serie_azar"]],
                range=[[1, 0], [6, 4]],
            ),
        ),
    )

    marcados = test["churn_probability"] >= umbral_prueba
    punto_datos = pd.DataFrame({
        "contactados": [marcados.mean()],
        "capturadas": [test.loc[marcados, "churn"].sum() / test["churn"].sum()],
        "etiqueta": [f"{textos['modelo_slider']}: {umbral_prueba:.2f}"],
    })
    punto = alt.Chart(punto_datos).mark_point(size=120, filled=True, color="gray").encode(
        x="contactados:Q", y="capturadas:Q", tooltip=["etiqueta:N"],
    )
    return lineas + punto


def grafico_importancia(importancia):
    """Barras horizontales con las variables que más mueven la predicción."""
    primeras = importancia.head(N_IMPORTANCIA)
    etiquetas = []
    for variable in primeras.index:
        etiquetas.append(textos["campos"][variable])
    datos = pd.DataFrame({"variable": etiquetas, "importancia": primeras.to_numpy()})
    return alt.Chart(datos).mark_bar(color="gray").encode(
        x=alt.X("importancia:Q", title=textos["eje_importancia"]),
        y=alt.Y("variable:N", sort="-x", title=None),
        tooltip=[alt.Tooltip("importancia:Q", format=".2f")],
    )


def grafico_challengers(folds):
    """Diferencia por fold de cada challenger frente a la regresión logística, con su media
    y la banda de +-0,02 que se consideró ruido. Folds y media se distinguen por la forma."""
    medias = folds.groupby("modelo", as_index=False)["diferencia"].mean()
    puntos = folds.copy()
    puntos["tipo"] = textos["fold"]
    medias["tipo"] = textos["media"]
    medias["fold"] = 0
    datos = pd.concat([puntos, medias], ignore_index=True)

    banda = alt.Chart(pd.DataFrame({"desde": [-0.02], "hasta": [0.02]})).mark_rect(
        color="gray", opacity=0.2,
    ).encode(x="desde:Q", x2="hasta:Q")
    cero = alt.Chart(pd.DataFrame({"cero": [0]})).mark_rule(color="gray").encode(x="cero:Q")
    marcas = alt.Chart(datos).mark_point(filled=True, color="gray", size=90).encode(
        x=alt.X("diferencia:Q", title=textos["eje_diferencia"], axis=alt.Axis(format="+.2f")),
        y=alt.Y("modelo:N", title=None),
        shape=alt.Shape(
            "tipo:N", title=textos["tipo"],
            scale=alt.Scale(domain=[textos["fold"], textos["media"]], range=["circle", "diamond"]),
        ),
        tooltip=[
            alt.Tooltip("modelo:N", title=textos["eje_modelo"]),
            alt.Tooltip("tipo:N", title=textos["tipo"]),
            alt.Tooltip("fold:Q", title=textos["fold"]),
            alt.Tooltip("diferencia:Q", format="+.3f"),
        ],
    )
    return banda + cero + marcas


def texto_estado(en_riesgo):
    if en_riesgo:
        return textos["en_riesgo"]
    return textos["sin_riesgo"]


def grafico_probabilidades(puntuados):
    """Histograma de probabilidades coloreado por estado, con la línea del umbral."""
    datos = pd.DataFrame({
        "probabilidad": puntuados["churn_probability"],
        "estado": puntuados["en_riesgo"].map(texto_estado),
    })
    colores = alt.Scale(
        domain=[textos["en_riesgo"], textos["sin_riesgo"]],
        range=[COLOR_RIESGO, COLOR_SIN_RIESGO],
    )
    barras = alt.Chart(datos).mark_bar().encode(
        x=alt.X(
            "probabilidad:Q",
            bin=alt.Bin(step=0.05, extent=[0, 1]),
            title=textos["probabilidad"],
            axis=alt.Axis(format="%"),
        ),
        y=alt.Y("count():Q", title=textos["grafico_eje_y"]),
        color=alt.Color("estado:N", title=textos["columna_estado"], scale=colores),
        tooltip=[
            alt.Tooltip("estado:N", title=textos["columna_estado"]),
            alt.Tooltip("count():Q", title=textos["grafico_eje_y"]),
        ],
    )

    datos_umbral = pd.DataFrame({
        "umbral": [umbral],
        "etiqueta": [textos["grafico_umbral"].format(umbral=f"{umbral:.0%}")],
    })
    linea = alt.Chart(datos_umbral).mark_rule(strokeDash=[6, 4], color="gray").encode(
        x="umbral:Q",
    )
    etiqueta = alt.Chart(datos_umbral).mark_text(align="left", dx=6, dy=-6, color="gray").encode(
        x="umbral:Q",
        y=alt.value(0),
        text="etiqueta:N",
    )
    return (barras + linea + etiqueta).properties(title=textos["grafico_titulo"])


# Estado inicial: se ejecuta solo la primera vez que se abre la app en el navegador
if "generador" not in st.session_state:
    st.session_state["generador"] = np.random.default_rng(42)
if clave("tenure") not in st.session_state:
    rellenar_formulario(clientes.iloc[0])
if "sim_clientes" not in st.session_state:
    reiniciar_simulacion(clientes)

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
        st.markdown(f"{textos['ficha_umbral']}: {umbral:.0%}")
        st.markdown(f"{textos['ficha_fecha']}: {fecha_exportado}")

st.title(textos["titulo"])
st.write(textos["subtitulo"])

pestana_resumen, pestana_cliente, pestana_riesgo, pestana_simulacion, pestana_modelo = st.tabs([
    textos["pestana_resumen"],
    textos["pestana_cliente"],
    textos["pestana_riesgo"],
    textos["pestana_simulacion"],
    textos["pestana_modelo"],
])

with pestana_resumen:
    st.write(textos["resumen_problema"])

    silver = cargar_clientes_silver()
    tasa_baja = silver["churn"].mean()
    test = puntuar_test(modelo, umbral)
    pr_auc_test = average_precision_score(test["churn"], test["churn_probability"])
    # Un modelo al azar tiene una PR-AUC igual a la proporción de bajas
    base_aleatoria = test["churn"].mean()

    col_clientes, col_tasa, col_pr_auc, col_umbral = st.columns(4, border=True)
    col_clientes.metric(textos["resumen_kpi_clientes"], len(silver))
    col_tasa.metric(textos["resumen_kpi_tasa"], f"{tasa_baja:.1%}")
    col_pr_auc.metric(
        textos["resumen_kpi_pr_auc"], f"{pr_auc_test:.3f}",
        help=textos["resumen_ayuda_pr_auc"].format(n=len(test), base=f"{base_aleatoria:.3f}"),
    )
    col_umbral.metric(textos["ficha_umbral"], f"{umbral:.0%}")

    st.subheader(textos["resumen_arquitectura"])
    st.graphviz_chart(diagrama_arquitectura(), width="stretch")
    st.caption(textos["resumen_arquitectura_nota"])

    col_decisiones, col_uso = st.columns([3, 2])
    with col_decisiones:
        st.subheader(textos["resumen_decisiones"])
        st.markdown(textos["resumen_decisiones_lista"].format(
            tasa=f"{tasa_baja:.1%}",
            umbral=f"{umbral:.2f}".replace(".", textos["separador_decimal"]),
        ))
    with col_uso:
        st.subheader(textos["resumen_uso"])
        st.markdown(textos["resumen_uso_lista"])

with pestana_cliente:
    st.button(textos["boton_azar"], on_click=cargar_cliente_azar, args=(clientes,))
    st.caption(textos["cliente_cargado"].format(customer_id=st.session_state["form_customer_id"]))

    campos = textos["campos"]
    col_personales, col_contrato, col_servicios = st.columns(3, border=True)

    with col_personales:
        st.markdown(f"**{textos['grupo_personales']}**")
        for columna in ["gender", "senior_citizen", "partner", "dependents"]:
            st.selectbox(
                campos[columna], OPCIONES[columna],
                key=clave(columna), format_func=mostrar_valor,
            )

    with col_contrato:
        st.markdown(f"**{textos['grupo_contrato']}**")
        st.slider(
            campos["tenure"], min_value=0, max_value=72,
            key=clave("tenure"), on_change=proponer_total,
        )
        for columna in ["contract", "paperless_billing", "payment_method"]:
            st.selectbox(
                campos[columna], OPCIONES[columna],
                key=clave(columna), format_func=mostrar_valor,
            )
        # El cargo mensual se limita al rango de los clientes del CSV
        st.number_input(
            campos["monthly_charges"],
            min_value=float(clientes["monthly_charges"].min()),
            max_value=float(clientes["monthly_charges"].max()),
            step=1.0, format="%.2f",
            key=clave("monthly_charges"), on_change=proponer_total,
        )
        st.number_input(
            campos["total_charges"], min_value=0.0, step=1.0, format="%.2f",
            key=clave("total_charges"), help=textos["ayuda_total"],
            disabled=st.session_state[clave("tenure")] == 0,
        )

    with col_servicios:
        st.markdown(f"**{textos['grupo_servicios']}**")
        st.selectbox(
            campos["phone_service"], OPCIONES["phone_service"],
            key=clave("phone_service"), format_func=mostrar_valor, on_change=ajustar_lineas,
        )
        sin_telefono = st.session_state[clave("phone_service")] == "No"
        if sin_telefono:
            opciones_lineas = ["No phone service"]
        else:
            opciones_lineas = SI_NO
        st.selectbox(
            campos["multiple_lines"], opciones_lineas,
            key=clave("multiple_lines"), format_func=mostrar_valor, disabled=sin_telefono,
        )

        st.selectbox(
            campos["internet_service"], OPCIONES["internet_service"],
            key=clave("internet_service"), format_func=mostrar_valor,
            on_change=ajustar_servicios_internet,
        )
        sin_internet = st.session_state[clave("internet_service")] == "No"
        if sin_internet:
            opciones_servicio = ["No internet service"]
        else:
            opciones_servicio = SI_NO
        for servicio in SERVICIOS_INTERNET:
            st.selectbox(
                campos[servicio], opciones_servicio,
                key=clave(servicio), format_func=mostrar_valor, disabled=sin_internet,
            )

    if st.button(textos["boton_calcular"], type="primary"):
        cliente = construir_cliente()
        tenure = cliente["tenure"].iloc[0]
        total = cliente["total_charges"].iloc[0]
        if tenure > 0 and total <= 0:
            st.error(textos["error_total"])
        else:
            puntuado = puntuar(cliente, modelo, umbral)
            probabilidad = puntuado["churn_probability"].iloc[0]
            en_riesgo = puntuado["en_riesgo"].iloc[0]

            if en_riesgo:
                frase = textos["frase_riesgo"]
            else:
                frase = textos["frase_sin_riesgo"]

            with st.container(border=True):
                st.metric(textos["probabilidad"], f"{probabilidad:.1%}")
                st.markdown(etiqueta_riesgo(en_riesgo), unsafe_allow_html=True)
                st.write(frase.format(probabilidad=f"{probabilidad:.1%}", umbral=f"{umbral:.0%}"))

            with st.container(border=True):
                st.markdown(f"**{textos['explicacion_titulo']}**")
                st.caption(textos["explicacion_nota"].format(n=N_EXPLICACION))
                tabla = contribuciones(cliente, modelo, medias_entrenamiento(modelo))
                st.altair_chart(grafico_contribuciones(tabla), width="stretch")

with pestana_riesgo:
    puntuados = puntuar_clientes_actuales(modelo, umbral)

    n_actuales = len(puntuados)
    n_riesgo = int(puntuados["en_riesgo"].sum())
    col_actuales, col_riesgo, col_porcentaje = st.columns(3, border=True)
    col_actuales.metric(textos["indicador_actuales"], n_actuales)
    col_riesgo.metric(textos["indicador_riesgo"], n_riesgo)
    col_porcentaje.metric(textos["indicador_porcentaje"], f"{n_riesgo / n_actuales:.1%}")

    # Filtros: por defecto están marcadas todas las opciones, es decir, no se filtra nada
    with st.container(border=True):
        seleccion = {}
        for columna in COLUMNAS_FILTRO:
            seleccion[columna] = st.pills(
                campos[columna], OPCIONES[columna],
                selection_mode="multi", default=OPCIONES[columna],
                format_func=mostrar_valor, key=f"filtro_{columna}",
            )
        solo_riesgo = st.toggle(textos["filtro_solo_riesgo"], key="filtro_solo_riesgo")

    mascara = pd.Series(True, index=puntuados.index)
    for columna in COLUMNAS_FILTRO:
        mascara = mascara & puntuados[columna].isin(seleccion[columna])
    if solo_riesgo:
        mascara = mascara & puntuados["en_riesgo"]
    filtrados = puntuados[mascara].sort_values("churn_probability", ascending=False)

    if len(filtrados) == 0:
        st.info(textos["sin_resultados"])
    else:
        st.caption(textos["clientes_filtrados"].format(n=len(filtrados)))
        col_tabla, col_grafico = st.columns([3, 2])

        with col_tabla:
            # La tabla muestra valores traducidos; la descarga, los valores originales
            tabla = filtrados[COLUMNAS_TABLA].copy()
            tabla["en_riesgo"] = tabla["en_riesgo"].map(texto_estado)
            for columna in COLUMNAS_FILTRO:
                tabla[columna] = tabla[columna].map(mostrar_valor)

            configuracion = {
                ID: st.column_config.TextColumn(textos["columna_cliente"]),
                "churn_probability": st.column_config.ProgressColumn(
                    textos["probabilidad"], format="percent", min_value=0.0, max_value=1.0,
                ),
                "en_riesgo": st.column_config.TextColumn(textos["columna_estado"]),
                "monthly_charges": st.column_config.NumberColumn(
                    campos["monthly_charges"], format="%.2f",
                ),
            }
            for columna in ["contract", "tenure", "internet_service", "payment_method"]:
                configuracion[columna] = st.column_config.Column(campos[columna])

            st.dataframe(tabla, hide_index=True, column_config=configuracion)
            st.download_button(
                textos["boton_descargar"],
                data=filtrados.to_csv(index=False),
                file_name=textos["nombre_descarga"],
                mime="text/csv",
                on_click="ignore",
            )

        with col_grafico:
            st.altair_chart(grafico_probabilidades(filtrados), width="stretch")

with pestana_simulacion:
    st.caption(textos["sim_alcance"])

    col_mes, col_altas, col_reiniciar = st.columns(3, border=True, vertical_alignment="bottom")
    with col_mes:
        st.button(textos["boton_pasar_mes"], on_click=simular_un_mes, type="primary")
    with col_altas:
        st.number_input(
            textos["sim_n_altas"], min_value=0, max_value=500, value=100, step=10,
            key="sim_n_altas", help=textos["ayuda_altas"],
        )
        st.button(textos["boton_altas"], on_click=simular_altas)
    with col_reiniciar:
        st.button(textos["boton_reiniciar"], on_click=reiniciar_simulacion, args=(clientes,))

    sim_puntuados = st.session_state["sim_puntuados"]
    col_ind_mes, col_ind_total, col_ind_riesgo, col_ind_entran, col_ind_salen = st.columns(5, border=True)
    col_ind_mes.metric(textos["ind_mes"], st.session_state["sim_mes"])
    col_ind_total.metric(textos["ind_total"], len(sim_puntuados))
    col_ind_riesgo.metric(textos["indicador_riesgo"], int(sim_puntuados["en_riesgo"].sum()))

    # Antes de la primera acción no hay estado anterior con el que comparar
    ultima_accion = st.session_state["sim_ultima_accion"]
    if ultima_accion is None:
        col_ind_entran.metric(textos["ind_entran"], "-")
        col_ind_salen.metric(textos["ind_salen"], "-")
        st.caption(textos["sim_sin_acciones"])
    else:
        col_ind_entran.metric(textos["ind_entran"], st.session_state["sim_entran"])
        col_ind_salen.metric(textos["ind_salen"], st.session_state["sim_salen"])
        tipo, n = ultima_accion
        if tipo == "mes":
            st.caption(textos["sim_ultima_mes"].format(mes=st.session_state["sim_mes"]))
        else:
            st.caption(textos["sim_ultima_altas"].format(n=n, mes=st.session_state["sim_mes"]))

with pestana_modelo:
    test = puntuar_test(modelo, umbral)
    st.caption(textos["modelo_intro"].format(n=len(test), umbral=f"{umbral:.2f}"))
    umbral_prueba = st.slider(
        textos["modelo_slider"], min_value=0.05, max_value=0.95, value=float(umbral), step=0.05,
        key="umbral_prueba",
    )
    matriz = matriz_confusion(test["churn"], test["churn_probability"], umbral_prueba)

    col_matriz, col_pr = st.columns([2, 3])
    with col_matriz:
        st.markdown(f"**{textos['modelo_matriz_titulo']}**")
        fila_arriba = st.columns(2, border=True)
        fila_arriba[0].metric(textos["modelo_detectados"], matriz["detectados"])
        fila_arriba[1].metric(textos["modelo_falsas"], matriz["falsas_alarmas"])
        fila_abajo = st.columns(2, border=True)
        fila_abajo[0].metric(textos["modelo_perdidos"], matriz["perdidos"])
        fila_abajo[1].metric(textos["modelo_descartados"], matriz["bien_descartados"])

        marcados = matriz["detectados"] + matriz["falsas_alarmas"]
        bajas = matriz["detectados"] + matriz["perdidos"]
        recall = matriz["detectados"] / bajas
        if marcados > 0:
            precision = matriz["detectados"] / marcados
            st.markdown(textos["modelo_precision"].format(
                p=f"{precision:.2f}", p100=round(precision * 100),
            ))
        st.markdown(textos["modelo_recall"].format(r=f"{recall:.2f}", r100=round(recall * 100)))

    with col_pr:
        st.markdown(f"**{textos['modelo_pr_titulo']}**")
        st.altair_chart(grafico_precision_recall(test, umbral_prueba, matriz), width="stretch")
        st.caption(textos["modelo_pr_nota"].format(base=f"{test['churn'].mean():.3f}"))

    col_ganancia, col_importancia = st.columns(2)
    with col_ganancia:
        st.markdown(f"**{textos['modelo_ganancia_titulo']}**")
        st.altair_chart(grafico_ganancia(test, umbral_prueba), width="stretch")
        st.caption(textos["modelo_ganancia_nota"])
    with col_importancia:
        st.markdown(f"**{textos['modelo_importancia_titulo']}**")
        st.altair_chart(grafico_importancia(importancia_test(modelo, umbral)), width="stretch")
        st.caption(textos["modelo_importancia_nota"].format(n=N_IMPORTANCIA))

    st.markdown(f"**{textos['modelo_challenger_titulo']}**")
    st.altair_chart(grafico_challengers(cargar_challengers()), width="stretch")
    st.caption(textos["modelo_challenger_nota"])
    st.write(textos["modelo_challenger_llamadas"])
