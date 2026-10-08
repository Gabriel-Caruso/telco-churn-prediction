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
    altas_nuevas, cambios_en_riesgo, contribuciones, curva_ganancia, diferencia_por_servicio,
    importancia_global, matriz_confusion, medias_transformadas, numero_de_extras,
    pasar_un_mes, puntuar, tasa_por_grupo, tasa_por_tramos,
)
from estilo import cabecera_html, css_global
from textos import TEXTOS

URL_REPO = "https://github.com/Gabriel-Caruso/telco-churn-prediction"

# Colores. Los del tema (fondo, texto, acento) están en .streamlit/config.toml.
# Okabe-Ito: naranja para riesgo, azul para fuera de riesgo. Son los únicos con significado.
COLOR_RIESGO = "#E69F00"
COLOR_SIN_RIESGO = "#0072B2"
# Gráficos sin categorías de riesgo: marcas de datos, líneas de referencia y punto destacado
COLOR_DATOS = "#6EE7B7"
COLOR_REFERENCIA = "#8A9A94"
COLOR_DESTACADO = "#E6EDEA"
# Iconos de las cuatro etapas de la arquitectura (Material Symbols)
ICONOS_ETAPAS = [
    ":material/database:", ":material/model_training:",
    ":material/rocket_launch:", ":material/dashboard:",
]

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

# Columna centrada de ancho fijo: líneas de texto cortas y lectura de arriba abajo
st.set_page_config(page_title="Telco churn", layout="centered")
st.html(css_global())


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


def mostrar_grafico(grafico, width="stretch"):
    """Muestra un gráfico de Altair con fondo transparente, para que tome el de su tarjeta."""
    st.altair_chart(grafico.properties(background="transparent"), width=width)


def tarjeta(nombre):
    """Contenedor con borde. La clave le da la clase CSS st-key-tarjeta_<nombre>, que
    estilo.py usa para darle un fondo distinto del de la página."""
    return st.container(border=True, key=f"tarjeta_{nombre}")


def columnas_tarjeta(numero, nombre, vertical_alignment="top"):
    """Como st.columns(numero, border=True), pero cada columna es una tarjeta con clave.
    height="stretch" iguala la altura de las tarjetas de una misma fila."""
    tarjetas = []
    for posicion, columna in enumerate(st.columns(numero, vertical_alignment=vertical_alignment)):
        with columna:
            tarjetas.append(st.container(
                border=True, key=f"tarjeta_{nombre}_{posicion}", height="stretch",
            ))
    return tarjetas


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


def formatear_porcentaje(valor, decimales=1):
    """Porcentaje con el separador decimal y el símbolo de cada idioma: 62,0 % o 62.0%."""
    numero = f"{valor * 100:.{decimales}f}".replace(".", textos["separador_decimal"])
    return numero + textos["simbolo_porcentaje"]


def formatear_decimal(valor, decimales):
    """Número con el separador decimal de cada idioma."""
    return f"{valor:.{decimales}f}".replace(".", textos["separador_decimal"])


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
    cero = alt.Chart(pd.DataFrame({"cero": [0]})).mark_rule(color=COLOR_REFERENCIA).encode(x="cero:Q")
    return barras + cero


def grafico_precision_recall(test, umbral_prueba, matriz):
    """Curva PR del conjunto de test, con el umbral de prueba marcado y la línea del azar."""
    precision, recall, _ = precision_recall_curve(test["churn"], test["churn_probability"])
    curva = pd.DataFrame({"recall": recall, "precision": precision, "orden": range(len(recall))})
    base = test["churn"].mean()

    linea = alt.Chart(curva).mark_line(color=COLOR_DATOS).encode(
        x=alt.X("recall:Q", title=textos["eje_recall"], scale=alt.Scale(domain=[0, 1])),
        y=alt.Y("precision:Q", title=textos["eje_precision"], scale=alt.Scale(domain=[0, 1])),
        order="orden:Q",
    )
    azar = alt.Chart(pd.DataFrame({"base": [base]})).mark_rule(
        color=COLOR_REFERENCIA, strokeDash=[6, 4],
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
    punto = alt.Chart(punto_datos).mark_point(size=120, filled=True, color=COLOR_DESTACADO).encode(
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

    lineas = alt.Chart(datos).mark_line(color=COLOR_DATOS).encode(
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
    punto = alt.Chart(punto_datos).mark_point(size=120, filled=True, color=COLOR_DESTACADO).encode(
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
    return alt.Chart(datos).mark_bar(color=COLOR_DATOS).encode(
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
        color=COLOR_REFERENCIA, opacity=0.2,
    ).encode(x="desde:Q", x2="hasta:Q")
    cero = alt.Chart(pd.DataFrame({"cero": [0]})).mark_rule(color=COLOR_REFERENCIA).encode(x="cero:Q")
    marcas = alt.Chart(datos).mark_point(filled=True, color=COLOR_DATOS, size=90).encode(
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


def posicion_respecto(tasas, referencia):
    """Para cada tasa, si queda por encima o por debajo de la referencia (texto de la leyenda)."""
    posiciones = []
    for tasa in tasas:
        if tasa > referencia:
            posiciones.append(textos["exp_por_encima"])
        else:
            posiciones.append(textos["exp_por_debajo"])
    return posiciones


def escala_posicion():
    """Naranja por encima de la referencia (más bajas) y azul por debajo, como en el resto de la app."""
    return alt.Scale(
        domain=[textos["exp_por_encima"], textos["exp_por_debajo"]],
        range=[COLOR_RIESGO, COLOR_SIN_RIESGO],
    )


def capa_referencia(referencia, etiqueta, horizontal):
    """Línea discontinua de la tasa de referencia, con su nombre escrito junto a ella.
    horizontal=True es para gráficos con las categorías en el eje vertical."""
    datos = pd.DataFrame({"referencia": [referencia], "etiqueta": [etiqueta]})
    if horizontal:
        linea = alt.Chart(datos).mark_rule(strokeDash=[6, 4], color=COLOR_REFERENCIA).encode(
            x="referencia:Q",
        )
        texto = alt.Chart(datos).mark_text(
            align="right", baseline="top", dx=-6, dy=2, fontSize=12, color=COLOR_REFERENCIA,
        ).encode(x="referencia:Q", y=alt.value(0), text="etiqueta:N")
    else:
        linea = alt.Chart(datos).mark_rule(strokeDash=[6, 4], color=COLOR_REFERENCIA).encode(
            y="referencia:Q",
        )
        # La etiqueta va encima del gráfico, a la derecha, para que ninguna barra la tape;
        # los guiones imitan la línea discontinua
        datos["etiqueta"] = "- - " + datos["etiqueta"]
        texto = alt.Chart(datos).mark_text(
            align="right", baseline="bottom", dy=-6, fontSize=12, color=COLOR_REFERENCIA,
        ).encode(x=alt.value("width"), y=alt.value(0), text="etiqueta:N")
    return linea + texto


def nombres_de_grupos(grupos, etiquetas):
    """Nombre que se muestra para cada grupo: de etiquetas si se pasan, si no traducido."""
    nombres = []
    for grupo in grupos:
        if etiquetas is None:
            nombres.append(str(mostrar_valor(grupo)))
        else:
            nombres.append(etiquetas[grupo])
    return nombres


def grafico_tasa_barras(tabla, referencia, etiqueta_referencia, titulo_x, etiquetas=None):
    """Barras verticales con la tasa de baja de cada grupo, coloreadas según queden por encima
    o por debajo de la referencia, y la línea de referencia etiquetada."""
    datos = tabla.copy()
    datos["nombre"] = nombres_de_grupos(datos["grupo"], etiquetas)
    datos["posicion"] = posicion_respecto(datos["tasa"], referencia)
    datos = datos[["nombre", "tasa", "clientes", "posicion"]]

    barras = alt.Chart(datos).mark_bar().encode(
        x=alt.X("nombre:N", sort=None, title=titulo_x, axis=alt.Axis(labelAngle=0)),
        y=alt.Y("tasa:Q", title=textos["exp_eje_tasa"], axis=alt.Axis(format="%")),
        color=alt.Color(
            "posicion:N", title=textos["exp_posicion"], scale=escala_posicion(),
            legend=alt.Legend(orient="bottom", title=None, labelLimit=400),
        ),
        tooltip=[
            alt.Tooltip("nombre:N", title=titulo_x),
            alt.Tooltip("tasa:Q", title=textos["exp_eje_tasa"], format=".1%"),
            alt.Tooltip("clientes:Q", title=textos["exp_eje_clientes"]),
        ],
    )
    return barras + capa_referencia(referencia, etiqueta_referencia, horizontal=False)


def grafico_tasa_puntos(tabla, referencia, etiqueta_referencia, titulo):
    """Gráfico de puntos horizontal: cada grupo es un punto unido por un trazo a la referencia,
    así se lee a la vez la tasa y la distancia a la media."""
    datos = tabla.copy()
    datos["nombre"] = nombres_de_grupos(datos["grupo"], None)
    datos["posicion"] = posicion_respecto(datos["tasa"], referencia)
    datos["referencia"] = referencia
    datos = datos[["nombre", "tasa", "clientes", "posicion", "referencia"]]

    eje_y = alt.Y(
        "nombre:N", title=None,
        sort=alt.EncodingSortField(field="tasa", order="descending"),
        axis=alt.Axis(labelLimit=320),
    )
    color = alt.Color(
        "posicion:N", title=textos["exp_posicion"], scale=escala_posicion(),
        legend=alt.Legend(orient="bottom", title=None, labelLimit=400),
    )
    trazos = alt.Chart(datos).mark_rule(strokeWidth=3).encode(
        x=alt.X("referencia:Q", title=textos["exp_eje_tasa"], axis=alt.Axis(format="%")),
        x2="tasa:Q",
        y=eje_y,
        color=color,
    )
    puntos = alt.Chart(datos).mark_circle(size=180, opacity=1).encode(
        x="tasa:Q",
        y=eje_y,
        color=color,
        tooltip=[
            alt.Tooltip("nombre:N", title=titulo),
            alt.Tooltip("tasa:Q", title=textos["exp_eje_tasa"], format=".1%"),
            alt.Tooltip("clientes:Q", title=textos["exp_eje_clientes"]),
        ],
    )
    capas = trazos + puntos + capa_referencia(referencia, etiqueta_referencia, horizontal=True)
    return capas.properties(height=alt.Step(44))


def grafico_tasa_antiguedad(tabla, referencia, etiqueta_referencia):
    """Tasa de baja mes a mes de antigüedad: una línea con un punto por mes, coloreado según
    quede por encima o por debajo de la media de la empresa."""
    datos = tabla.rename(columns={"grupo": "tenure"})
    datos["posicion"] = posicion_respecto(datos["tasa"], referencia)

    eje_x = alt.X("tenure:Q", title=textos["campos"]["tenure"], scale=alt.Scale(domain=[0, 72]))
    eje_y = alt.Y("tasa:Q", title=textos["exp_eje_tasa"], axis=alt.Axis(format="%"))
    linea = alt.Chart(datos).mark_line(color=COLOR_REFERENCIA).encode(x=eje_x, y=eje_y)
    puntos = alt.Chart(datos).mark_circle(size=45, opacity=1).encode(
        x=eje_x,
        y=eje_y,
        color=alt.Color(
            "posicion:N", title=textos["exp_posicion"], scale=escala_posicion(),
            legend=alt.Legend(orient="bottom", title=None, labelLimit=400),
        ),
        tooltip=[
            alt.Tooltip("tenure:Q", title=textos["campos"]["tenure"]),
            alt.Tooltip("tasa:Q", title=textos["exp_eje_tasa"], format=".1%"),
            alt.Tooltip("clientes:Q", title=textos["exp_eje_clientes"]),
        ],
    )
    return linea + puntos + capa_referencia(referencia, etiqueta_referencia, horizontal=False)


def grafico_servicios(tabla, maximo):
    """Barras con los puntos de diferencia de tasa de baja entre no tener y tener cada servicio.
    maximo fija el eje para que los gráficos de soporte y ocio se puedan comparar."""
    datos = tabla.copy()
    nombres = []
    for servicio in datos["servicio"]:
        nombres.append(textos["campos"][servicio])
    datos["nombre"] = nombres
    datos["puntos"] = datos["diferencia"] * 100
    datos = datos[["nombre", "puntos"]]
    return alt.Chart(datos).mark_bar(color=COLOR_DATOS).encode(
        x=alt.X(
            "puntos:Q", title=textos["exp_servicios_eje"], scale=alt.Scale(domain=[0, maximo]),
        ),
        # minExtent reserva el mismo hueco para las etiquetas en los dos gráficos y alinea los ejes
        y=alt.Y("nombre:N", sort="-x", title=None, axis=alt.Axis(labelLimit=320, minExtent=190)),
        tooltip=[alt.Tooltip("puntos:Q", title=textos["exp_servicios_eje"], format=".1f")],
    ).properties(height=alt.Step(34))


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
    linea = alt.Chart(datos_umbral).mark_rule(strokeDash=[6, 4], color=COLOR_REFERENCIA).encode(
        x="umbral:Q",
    )
    etiqueta = alt.Chart(datos_umbral).mark_text(align="left", dx=6, dy=-6, color=COLOR_REFERENCIA).encode(
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

# Cabecera: título a la izquierda y barra de iconos a la derecha. La barra se rellena
# primero porque el idioma elegido decide en qué idioma se escribe el título.
col_titulo, col_barra = st.columns([3, 2], vertical_alignment="center")

with col_barra:
    with st.container(horizontal=True, horizontal_alignment="right", vertical_alignment="center"):
        # La etiqueta va en los dos idiomas porque todavía no se sabe cuál se ha elegido.
        idioma = st.segmented_control(
            "Idioma / Language",
            options=["es", "en"],
            default="es",
            required=True,
            format_func=str.upper,
            key="idioma",
            label_visibility="collapsed",
        )
        textos = TEXTOS[idioma]
        campos = textos["campos"]

        with st.popover("", icon=":material/info:", help=textos["ayuda_info"]):
            st.markdown(textos["sobre_proyecto"])
            fecha_exportado = datetime.fromisoformat(metadatos["exportado"]).date().isoformat()
            st.markdown(f"**{textos['ficha_modelo']}**")
            st.markdown(f"{textos['ficha_nombre']}: `{metadatos['model_name']}`")
            st.markdown(f"{textos['ficha_version']}: {metadatos['version']}")
            st.markdown(f"{textos['ficha_umbral']}: {formatear_porcentaje(umbral, 0)}")
            st.markdown(f"{textos['ficha_fecha']}: {fecha_exportado}")

        st.link_button("", URL_REPO, icon=":material/code:", help=textos["enlace_repo"])

with col_titulo:
    st.markdown(f":material/cell_tower: **{textos['titulo']}**")

st.html(
    cabecera_html(textos["cabecera_etiqueta"], textos["cabecera_titulo"], textos["resumen_problema"]),
    unsafe_allow_javascript=True,
)

(
    pestana_resumen, pestana_cliente, pestana_riesgo, pestana_simulacion,
    pestana_exploracion, pestana_modelo,
) = st.tabs([
    textos["pestana_resumen"],
    textos["pestana_cliente"],
    textos["pestana_riesgo"],
    textos["pestana_simulacion"],
    textos["pestana_exploracion"],
    textos["pestana_modelo"],
])

with pestana_resumen:
    silver = cargar_clientes_silver()
    tasa_baja = silver["churn"].mean()
    test = puntuar_test(modelo, umbral)
    pr_auc_test = average_precision_score(test["churn"], test["churn_probability"])
    # Un modelo al azar tiene una PR-AUC igual a la proporción de bajas
    base_aleatoria = test["churn"].mean()

    fila_arriba = columnas_tarjeta(2, "bloque_11")
    fila_arriba[0].metric(textos["resumen_kpi_clientes"], len(silver))
    fila_arriba[1].metric(textos["resumen_kpi_tasa"], formatear_porcentaje(tasa_baja))
    fila_abajo = columnas_tarjeta(2, "bloque_12")
    fila_abajo[0].metric(
        textos["resumen_kpi_pr_auc"], formatear_decimal(pr_auc_test, 3),
        help=textos["resumen_ayuda_pr_auc"].format(
            n=len(test), base=formatear_decimal(base_aleatoria, 3),
        ),
    )
    fila_abajo[1].metric(textos["ficha_umbral"], formatear_porcentaje(umbral, 0))

    st.subheader(textos["resumen_arquitectura"])
    for numero, (icono, etapa) in enumerate(zip(ICONOS_ETAPAS, textos["etapas"])):
        with tarjeta(f"etapa_{numero}"):
            st.markdown(f"#### {icono} {etapa['titulo']}")
            st.write(etapa["texto"])
            with st.container(horizontal=True):
                for tecnologia in etapa["tecnologias"].split(" · "):
                    st.badge(tecnologia, color="green")

    st.subheader(textos["resumen_decisiones"])
    decisiones = textos["decisiones"]
    for inicio in range(0, len(decisiones), 2):
        fila = columnas_tarjeta(2, f"decision_{inicio}")
        for columna, decision in zip(fila, decisiones[inicio:inicio + 2]):
            with columna:
                st.markdown(f"**{decision['titulo'].format(umbral=formatear_decimal(umbral, 2))}**")
                st.write(decision["texto"].format(tasa=formatear_porcentaje(tasa_baja)))

    st.subheader(textos["resumen_uso"])
    st.markdown(textos["resumen_uso_lista"])

with pestana_cliente:
    st.button(textos["boton_azar"], on_click=cargar_cliente_azar, args=(clientes,))
    st.caption(textos["cliente_cargado"].format(customer_id=st.session_state["form_customer_id"]))

    # Dos tarjetas de la misma altura (6 campos cada una) y debajo la de internet
    col_personales, col_contrato = columnas_tarjeta(2, "bloque_14")

    with col_personales:
        st.markdown(f"**{textos['grupo_personales']}**")
        for columna in ["gender", "senior_citizen", "partner", "dependents"]:
            st.selectbox(
                campos[columna], OPCIONES[columna],
                key=clave(columna), format_func=mostrar_valor,
            )
        st.markdown(f"**{textos['grupo_telefonia']}**")
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

    with tarjeta("bloque_2"):
        st.markdown(f"**{textos['grupo_servicios']}**")
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
        col_servicios_izquierda, col_servicios_derecha = st.columns(2)
        for posicion, servicio in enumerate(SERVICIOS_INTERNET):
            # Tres servicios en cada columna
            if posicion < 3:
                columna_servicio = col_servicios_izquierda
            else:
                columna_servicio = col_servicios_derecha
            with columna_servicio:
                st.selectbox(
                    campos[servicio], opciones_servicio,
                    key=clave(servicio), format_func=mostrar_valor, disabled=sin_internet,
                )

    if st.button(textos["boton_calcular"], type="primary", key="primario_calcular"):
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

            with tarjeta("bloque_3"):
                st.metric(textos["probabilidad"], formatear_porcentaje(probabilidad))
                st.markdown(etiqueta_riesgo(en_riesgo), unsafe_allow_html=True)
                st.write(frase.format(
                    probabilidad=formatear_porcentaje(probabilidad),
                    umbral=formatear_porcentaje(umbral, 0),
                ))

            with tarjeta("bloque_4"):
                st.markdown(f"**{textos['explicacion_titulo']}**")
                st.caption(textos["explicacion_nota"].format(n=N_EXPLICACION))
                tabla = contribuciones(cliente, modelo, medias_entrenamiento(modelo))
                mostrar_grafico(grafico_contribuciones(tabla), width="stretch")

with pestana_riesgo:
    puntuados = puntuar_clientes_actuales(modelo, umbral)

    n_actuales = len(puntuados)
    n_riesgo = int(puntuados["en_riesgo"].sum())
    col_actuales, col_riesgo, col_porcentaje = columnas_tarjeta(3, "bloque_15")
    col_actuales.metric(textos["indicador_actuales"], n_actuales)
    col_riesgo.metric(textos["indicador_riesgo"], n_riesgo)
    col_porcentaje.metric(textos["indicador_porcentaje"], formatear_porcentaje(n_riesgo / n_actuales))

    # Filtros: por defecto están marcadas todas las opciones, es decir, no se filtra nada
    with tarjeta("bloque_5"):
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
        mostrar_grafico(grafico_probabilidades(filtrados), width="stretch")

with pestana_simulacion:
    st.caption(textos["sim_alcance"])

    col_mes, col_altas, col_reiniciar = columnas_tarjeta(3, "bloque_16", vertical_alignment="bottom")
    with col_mes:
        st.button(textos["boton_pasar_mes"], on_click=simular_un_mes, type="primary", key="primario_mes")
    with col_altas:
        st.number_input(
            textos["sim_n_altas"], min_value=0, max_value=500, value=100, step=10,
            key="sim_n_altas", help=textos["ayuda_altas"],
        )
        st.button(textos["boton_altas"], on_click=simular_altas)
    with col_reiniciar:
        st.button(textos["boton_reiniciar"], on_click=reiniciar_simulacion, args=(clientes,))

    sim_puntuados = st.session_state["sim_puntuados"]
    col_ind_mes, col_ind_total, col_ind_riesgo = columnas_tarjeta(3, "bloque_17")
    col_ind_mes.metric(textos["ind_mes"], st.session_state["sim_mes"])
    col_ind_total.metric(textos["ind_total"], len(sim_puntuados))
    col_ind_riesgo.metric(textos["indicador_riesgo"], int(sim_puntuados["en_riesgo"].sum()))
    col_ind_entran, col_ind_salen = columnas_tarjeta(2, "bloque_18")

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

with pestana_exploracion:
    silver = cargar_clientes_silver()
    tasa_global = silver["churn"].mean()
    referencia_empresa = textos["exp_ref_empresa"].format(tasa=formatear_porcentaje(tasa_global))
    fibra = silver[silver["internet_service"] == "Fiber optic"].copy()
    tasa_fibra = fibra["churn"].mean()
    referencia_fibra = textos["exp_ref_fibra"].format(tasa=formatear_porcentaje(tasa_fibra))
    st.caption(textos["exp_intro"].format(n=len(silver)))

    # Cada sección: título, una cifra destacada sacada de los datos, el gráfico y la conclusión
    with tarjeta("exp_antiguedad"):
        st.subheader(textos["exp_tenure_titulo"])
        por_antiguedad = tasa_por_grupo(silver, "tenure")
        primer_mes = por_antiguedad.loc[por_antiguedad["grupo"] == 1, "tasa"].iloc[0]
        st.metric(textos["exp_dest_tenure"], formatear_porcentaje(primer_mes))
        mostrar_grafico(
            grafico_tasa_antiguedad(por_antiguedad, tasa_global, referencia_empresa),
            width="stretch",
        )
        st.markdown(textos["exp_tenure_texto"])

    with tarjeta("exp_contrato"):
        st.subheader(textos["exp_contrato_titulo"])
        por_contrato = tasa_por_grupo(silver, "contract")
        mensual_tasa = por_contrato.loc[por_contrato["grupo"] == "Month-to-month", "tasa"].iloc[0]
        st.metric(textos["exp_dest_contrato"], formatear_porcentaje(mensual_tasa))
        mostrar_grafico(
            grafico_tasa_barras(por_contrato, tasa_global, referencia_empresa, campos["contract"]),
            width="stretch",
        )
        st.markdown(textos["exp_contrato_texto"])

    with tarjeta("exp_simpson"):
        st.subheader(textos["exp_simpson_titulo"])
        # Misma variable (cuota mensual) mirada en todos los clientes y solo en fibra
        por_cuota = tasa_por_tramos(silver, "monthly_charges", 5)
        por_cuota_fibra = tasa_por_tramos(fibra, "monthly_charges", 4)
        st.metric(
            textos["exp_dest_simpson"],
            f"{formatear_porcentaje(por_cuota_fibra['tasa'].iloc[0])} / "
            f"{formatear_porcentaje(por_cuota_fibra['tasa'].iloc[-1])}",
        )
        st.caption(textos["exp_simpson_todos"])
        mostrar_grafico(
            grafico_tasa_barras(por_cuota, tasa_global, referencia_empresa, textos["exp_simpson_eje"]),
            width="stretch",
        )
        st.caption(textos["exp_simpson_fibra"])
        mostrar_grafico(
            grafico_tasa_barras(por_cuota_fibra, tasa_fibra, referencia_fibra, textos["exp_simpson_eje"]),
            width="stretch",
        )
        st.markdown(textos["exp_simpson_texto"])

    with tarjeta("exp_fibra"):
        st.subheader(textos["exp_fibra_titulo"])
        fibra["n_extras"] = numero_de_extras(fibra, SERVICIOS_INTERNET)
        por_extras = tasa_por_grupo(fibra, "n_extras")
        sin_extras = por_extras.loc[por_extras["grupo"] == 0, "tasa"].iloc[0]
        st.metric(textos["exp_dest_fibra"], formatear_porcentaje(sin_extras))
        etiquetas_extras = {}
        for numero in range(len(SERVICIOS_INTERNET) + 1):
            etiquetas_extras[numero] = str(numero)
        mostrar_grafico(
            grafico_tasa_barras(
                por_extras, tasa_fibra, referencia_fibra,
                textos["exp_fibra_eje"], etiquetas=etiquetas_extras,
            ),
            width="stretch",
        )
        st.markdown(textos["exp_fibra_texto"])

    with tarjeta("exp_pago"):
        st.subheader(textos["exp_pago_titulo"])
        mensual = silver[silver["contract"] == "Month-to-month"]
        por_pago_mensual = tasa_por_grupo(mensual, "payment_method")
        cheque = por_pago_mensual.loc[por_pago_mensual["grupo"] == "Electronic check", "tasa"].iloc[0]
        st.metric(textos["exp_dest_pago"], formatear_porcentaje(cheque))
        st.markdown(textos["exp_pago_contexto"])
        # La misma comparación en bruto y a igualdad de contrato
        st.caption(textos["exp_pago_todos"])
        mostrar_grafico(
            grafico_tasa_puntos(
                tasa_por_grupo(silver, "payment_method"), tasa_global, referencia_empresa,
                campos["payment_method"],
            ),
            width="stretch",
        )
        st.caption(textos["exp_pago_mensual"])
        tasa_mensual = mensual["churn"].mean()
        mostrar_grafico(
            grafico_tasa_puntos(
                por_pago_mensual, tasa_mensual,
                textos["exp_ref_mensual"].format(tasa=formatear_porcentaje(tasa_mensual)),
                campos["payment_method"],
            ),
            width="stretch",
        )
        st.markdown(textos["exp_pago_texto"])

    with tarjeta("exp_servicios"):
        st.subheader(textos["exp_servicios_titulo"])
        diferencias = diferencia_por_servicio(silver, SERVICIOS_INTERNET)
        seguridad = diferencias.loc[diferencias["servicio"] == "online_security", "diferencia"].iloc[0]
        st.metric(
            textos["exp_dest_servicios"],
            textos["exp_dest_puntos"].format(puntos=formatear_decimal(seguridad * 100, 0)),
        )
        # Mismo eje en los dos gráficos para poder comparar soporte con ocio
        maximo = diferencias["diferencia"].max() * 100 * 1.1
        st.caption(textos["exp_servicios_soporte"])
        mostrar_grafico(
            grafico_servicios(diferencias[diferencias["servicio"].isin(SERVICIOS_SOPORTE)], maximo),
            width="stretch",
        )
        st.caption(textos["exp_servicios_ocio"])
        mostrar_grafico(
            grafico_servicios(diferencias[diferencias["servicio"].isin(SERVICIOS_OCIO)], maximo),
            width="stretch",
        )
        st.markdown(textos["exp_servicios_texto"])

    with st.expander(textos["exp_limites_titulo"]):
        st.markdown(textos["exp_limites_texto"])

with pestana_modelo:
    test = puntuar_test(modelo, umbral)
    st.caption(textos["modelo_intro"].format(n=len(test), umbral=formatear_decimal(umbral, 2)))
    umbral_prueba = st.slider(
        textos["modelo_slider"], min_value=0.05, max_value=0.95, value=float(umbral), step=0.05,
        key="umbral_prueba",
    )
    matriz = matriz_confusion(test["churn"], test["churn_probability"], umbral_prueba)

    with tarjeta("bloque_6"):
        st.subheader(textos["modelo_matriz_titulo"])
        fila_arriba = columnas_tarjeta(2, "bloque_19")
        fila_arriba[0].metric(textos["modelo_detectados"], matriz["detectados"])
        fila_arriba[1].metric(textos["modelo_falsas"], matriz["falsas_alarmas"])
        fila_abajo = columnas_tarjeta(2, "bloque_20")
        fila_abajo[0].metric(textos["modelo_perdidos"], matriz["perdidos"])
        fila_abajo[1].metric(textos["modelo_descartados"], matriz["bien_descartados"])

        marcados = matriz["detectados"] + matriz["falsas_alarmas"]
        bajas = matriz["detectados"] + matriz["perdidos"]
        recall = matriz["detectados"] / bajas
        if marcados > 0:
            precision = matriz["detectados"] / marcados
            st.markdown(textos["modelo_precision"].format(
                p=formatear_decimal(precision, 2), p100=round(precision * 100),
            ))
        st.markdown(textos["modelo_recall"].format(
            r=formatear_decimal(recall, 2), r100=round(recall * 100),
        ))

    with tarjeta("bloque_7"):
        st.subheader(textos["modelo_pr_titulo"])
        mostrar_grafico(grafico_precision_recall(test, umbral_prueba, matriz), width="stretch")
        st.caption(textos["modelo_pr_nota"].format(base=formatear_decimal(test["churn"].mean(), 3)))

    with tarjeta("bloque_8"):
        st.subheader(textos["modelo_ganancia_titulo"])
        mostrar_grafico(grafico_ganancia(test, umbral_prueba), width="stretch")
        st.caption(textos["modelo_ganancia_nota"])

    with tarjeta("bloque_9"):
        st.subheader(textos["modelo_importancia_titulo"])
        mostrar_grafico(grafico_importancia(importancia_test(modelo, umbral)), width="stretch")
        st.caption(textos["modelo_importancia_nota"].format(n=N_IMPORTANCIA))

    with tarjeta("bloque_10"):
        st.subheader(textos["modelo_challenger_titulo"])
        mostrar_grafico(grafico_challengers(cargar_challengers()), width="stretch")
        st.caption(textos["modelo_challenger_nota"])
        st.write(textos["modelo_challenger_llamadas"])
