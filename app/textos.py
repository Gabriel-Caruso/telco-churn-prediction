"""Textos de la interfaz en español e inglés.

Cada idioma es un diccionario con las mismas claves. La app elige el
diccionario según el idioma seleccionado y lee los textos por su clave.

- "campos": etiqueta de cada columna de silver en el formulario.
- "valores": cómo se muestran los valores del dataset. Si un valor no
  aparece, se muestra tal cual (por eso en inglés solo hacen falta 0 y 1).
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
        "grupo_personales": "Datos personales",
        "grupo_contrato": "Contrato y pago",
        "grupo_servicios": "Servicios",
        "boton_azar": "Cargar un cliente real al azar",
        "cliente_cargado": "Datos del cliente {customer_id}. Puedes modificarlos.",
        "boton_calcular": "Calcular probabilidad",
        "ayuda_total": "Se propone antigüedad por cargo mensual. Puedes editarlo.",
        "error_total": "Con antigüedad mayor que 0, el cargo acumulado debe ser mayor que 0.",
        "probabilidad": "Probabilidad de baja",
        "en_riesgo": "En riesgo",
        "sin_riesgo": "Fuera de riesgo",
        "frase_riesgo": (
            "La probabilidad de baja es del {probabilidad}, igual o superior al umbral "
            "del {umbral}. El cliente entra en la lista de riesgo y sería candidato a "
            "una acción de retención."
        ),
        "frase_sin_riesgo": (
            "La probabilidad de baja es del {probabilidad}, inferior al umbral del "
            "{umbral}. El cliente no entra en la lista de riesgo."
        ),
        "indicador_actuales": "Clientes actuales",
        "indicador_riesgo": "Clientes en riesgo",
        "indicador_porcentaje": "Porcentaje en riesgo",
        "filtro_solo_riesgo": "Solo clientes en riesgo",
        "clientes_filtrados": "{n} clientes con los filtros aplicados.",
        "sin_resultados": "Ningún cliente cumple los filtros.",
        "boton_descargar": "Descargar lista filtrada (CSV)",
        "nombre_descarga": "lista_riesgo.csv",
        "columna_cliente": "Cliente",
        "columna_estado": "Estado",
        "grafico_titulo": "Distribución de la probabilidad de baja",
        "grafico_eje_y": "Clientes",
        "grafico_umbral": "Umbral {umbral}",
        "campos": {
            "gender": "Género",
            "senior_citizen": "Mayor de 65 años",
            "partner": "Pareja",
            "dependents": "Personas a cargo",
            "tenure": "Antigüedad (meses)",
            "contract": "Contrato",
            "paperless_billing": "Factura electrónica",
            "payment_method": "Método de pago",
            "monthly_charges": "Cargo mensual",
            "total_charges": "Cargo acumulado",
            "phone_service": "Línea telefónica",
            "multiple_lines": "Varias líneas",
            "internet_service": "Internet",
            "online_security": "Seguridad online",
            "online_backup": "Copia de seguridad online",
            "device_protection": "Protección de dispositivos",
            "tech_support": "Soporte técnico",
            "streaming_tv": "TV en streaming",
            "streaming_movies": "Películas en streaming",
        },
        "valores": {
            0: "No",
            1: "Sí",
            "Yes": "Sí",
            "No": "No",
            "Female": "Mujer",
            "Male": "Hombre",
            "No phone service": "Sin línea telefónica",
            "No internet service": "Sin internet",
            "Fiber optic": "Fibra óptica",
            "Month-to-month": "Mensual",
            "One year": "Un año",
            "Two year": "Dos años",
            "Electronic check": "Cheque electrónico",
            "Mailed check": "Cheque por correo",
            "Bank transfer (automatic)": "Transferencia bancaria (automática)",
            "Credit card (automatic)": "Tarjeta de crédito (automática)",
        },
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
        "grupo_personales": "Personal details",
        "grupo_contrato": "Contract and billing",
        "grupo_servicios": "Services",
        "boton_azar": "Load a random real customer",
        "cliente_cargado": "Data from customer {customer_id}. You can edit it.",
        "boton_calcular": "Calculate probability",
        "ayuda_total": "Suggested as tenure times monthly charges. You can edit it.",
        "error_total": "With tenure above 0, total charges must be above 0.",
        "probabilidad": "Churn probability",
        "en_riesgo": "At risk",
        "sin_riesgo": "Not at risk",
        "frase_riesgo": (
            "The churn probability is {probabilidad}, at or above the {umbral} "
            "threshold. The customer enters the risk list and would be a candidate "
            "for a retention action."
        ),
        "frase_sin_riesgo": (
            "The churn probability is {probabilidad}, below the {umbral} threshold. "
            "The customer does not enter the risk list."
        ),
        "indicador_actuales": "Current customers",
        "indicador_riesgo": "Customers at risk",
        "indicador_porcentaje": "Share at risk",
        "filtro_solo_riesgo": "Only customers at risk",
        "clientes_filtrados": "{n} customers with the current filters.",
        "sin_resultados": "No customer matches the filters.",
        "boton_descargar": "Download filtered list (CSV)",
        "nombre_descarga": "risk_list.csv",
        "columna_cliente": "Customer",
        "columna_estado": "Status",
        "grafico_titulo": "Churn probability distribution",
        "grafico_eje_y": "Customers",
        "grafico_umbral": "Threshold {umbral}",
        "campos": {
            "gender": "Gender",
            "senior_citizen": "Senior citizen (65+)",
            "partner": "Partner",
            "dependents": "Dependents",
            "tenure": "Tenure (months)",
            "contract": "Contract",
            "paperless_billing": "Paperless billing",
            "payment_method": "Payment method",
            "monthly_charges": "Monthly charges",
            "total_charges": "Total charges",
            "phone_service": "Phone service",
            "multiple_lines": "Multiple lines",
            "internet_service": "Internet service",
            "online_security": "Online security",
            "online_backup": "Online backup",
            "device_protection": "Device protection",
            "tech_support": "Tech support",
            "streaming_tv": "Streaming TV",
            "streaming_movies": "Streaming movies",
        },
        "valores": {
            0: "No",
            1: "Yes",
        },
    },
}
