"""Textos de la interfaz en español e inglés.

Cada idioma es un diccionario con las mismas claves. La app elige el
diccionario según el idioma seleccionado y lee los textos por su clave.
"""

TEXTOS = {
    "es": {
        "titulo": "Telco churn",
        "subtitulo": "Probabilidad de baja de clientes de una operadora de telecomunicaciones.",
        "pestana_cliente": "Consultar un cliente",
        "pestana_riesgo": "Lista de riesgo",
        "pestana_simulacion": "Simular un mes",
        "sobre_proyecto": (
            "Proyecto de ciclo de vida de machine learning con el dataset IBM Telco "
            "Customer Churn, desarrollado en Databricks con MLflow y Unity Catalog."
        ),
        "enlace_repo": "Código en GitHub",
        "ficha_modelo": "Modelo",
        "ficha_nombre": "Nombre",
        "ficha_version": "Versión",
        "ficha_umbral": "Umbral de riesgo",
        "ficha_fecha": "Exportado",
    },
    "en": {
        "titulo": "Telco churn",
        "subtitulo": "Churn probability for customers of a telecom operator.",
        "pestana_cliente": "Score a customer",
        "pestana_riesgo": "Risk list",
        "pestana_simulacion": "Simulate a month",
        "sobre_proyecto": (
            "End-to-end machine learning project on the IBM Telco Customer Churn "
            "dataset, built on Databricks with MLflow and Unity Catalog."
        ),
        "enlace_repo": "Code on GitHub",
        "ficha_modelo": "Model",
        "ficha_nombre": "Name",
        "ficha_version": "Version",
        "ficha_umbral": "Risk threshold",
        "ficha_fecha": "Exported",
    },
}
