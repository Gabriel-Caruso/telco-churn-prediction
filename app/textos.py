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
        "separador_decimal": ",",
        "pestana_resumen": "Resumen",
        "resumen_problema": (
            "Una operadora de telecomunicaciones pierde a uno de cada cuatro clientes. "
            "Este proyecto ordena a los clientes actuales por su probabilidad de baja "
            "para que el equipo de retención sepa a quién contactar primero."
        ),
        "resumen_kpi_clientes": "Clientes en el dataset",
        "resumen_kpi_tasa": "Tasa de baja",
        "resumen_kpi_pr_auc": "PR-AUC en test",
        "resumen_ayuda_pr_auc": (
            "Mide lo bien que el modelo ordena a los clientes por riesgo, sobre {n} "
            "clientes que no vio al entrenar. Un modelo al azar obtendría {base}, "
            "la proporción de bajas en ese conjunto."
        ),
        "resumen_arquitectura": "Arquitectura",
        "resumen_arquitectura_nota": (
            "Todo el ciclo se ejecuta en Databricks Free Edition. Esta app carga el "
            "modelo exportado y calcula las features con el mismo paquete que el entrenamiento."
        ),
        "resumen_decisiones": "Decisiones clave",
        "resumen_decisiones_lista": (
            "- **Métrica: PR-AUC.** Con un {tasa} de bajas, la accuracy premiaría a un "
            "modelo que no detecta a nadie. Lo que importa es ordenar bien a los clientes por riesgo.\n"
            "- **Umbral {umbral}.** El análisis de umbrales marcó el tramo 0,30-0,40, donde "
            "cada baja detectada cuesta alrededor de una llamada y media de más. El valor "
            "exacto depende del coste de una oferta y del valor de un cliente retenido.\n"
            "- **Champion: regresión logística.** Random forest, gradient boosting y XGBoost "
            "ajustados la superan en unos 0,02 de PR-AUC, en el límite del ruido entre folds. "
            "No compensa perder la explicabilidad de los coeficientes.\n"
            "- **Mismo código en entrenamiento y en la app.** Las features se calculan en un "
            "paquete propio con tests, y la tabla gold y esta app usan la misma función."
        ),
        "resumen_uso": "Qué puedes hacer en esta app",
        "resumen_uso_lista": (
            "- **Consultar un cliente:** introduce un perfil o carga uno real y obtén su "
            "probabilidad de baja.\n"
            "- **Lista de riesgo:** los clientes actuales ordenados por riesgo, con filtros "
            "y descarga en CSV.\n"
            "- **Simular un mes:** cómo cambia la lista con el paso del tiempo y las altas nuevas."
        ),
        "arquitectura": {
            "datos": "Dataset IBM Telco\\n7043 clientes",
            "bronze": "Bronze\\nCSV sin modificar",
            "silver": "Silver\\nlimpieza y validación",
            "gold": "Gold\\n8 features derivadas",
            "paquete": "Paquete churn\\nfeatures con tests",
            "entrenamiento": "Entrenamiento\\nscikit-learn, CV 5 folds",
            "challenger": "Challengers\\nRF, GB, XGBoost",
            "mlflow": "MLflow\\nexperimentos y métricas",
            "registro": "Unity Catalog\\nmodelo con alias champion",
            "batch": "Batch scoring\\ntabla customer_scores",
            "serving": "Model Serving\\nendpoint REST",
            "exportacion": "Exportación\\njoblib + JSON",
            "app": "Esta app",
            "grupo_databricks": "Databricks Free Edition",
            "grupo_streamlit": "Streamlit Community Cloud",
        },
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
        "sim_alcance": (
            "La simulación parte de los clientes actuales y no modela bajas: ningún "
            "cliente se va. Solo muestra cómo cambia el riesgo con el paso del tiempo "
            "y con las altas nuevas. Los clientes con 72 meses, el máximo del dataset, "
            "no cambian al pasar el mes."
        ),
        "boton_pasar_mes": "Pasar un mes",
        "sim_n_altas": "Número de altas nuevas",
        "ayuda_altas": "Cada alta copia el perfil de un cliente real, con antigüedad 0.",
        "boton_altas": "Añadir altas",
        "boton_reiniciar": "Reiniciar simulación",
        "ind_mes": "Mes simulado",
        "ind_total": "Clientes totales",
        "ind_entran": "Entran en la lista",
        "ind_salen": "Salen de la lista",
        "sim_sin_acciones": "Todavía no se ha hecho ninguna acción.",
        "sim_ultima_mes": "Última acción: paso al mes {mes}. Entradas y salidas respecto al mes anterior.",
        "sim_ultima_altas": (
            "Última acción: {n} altas nuevas en el mes {mes}. "
            "Entradas y salidas respecto al estado anterior a las altas."
        ),
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
        "separador_decimal": ".",
        "pestana_resumen": "Overview",
        "resumen_problema": (
            "A telecom operator loses one in four customers. This project ranks current "
            "customers by churn probability so the retention team knows who to contact first."
        ),
        "resumen_kpi_clientes": "Customers in the dataset",
        "resumen_kpi_tasa": "Churn rate",
        "resumen_kpi_pr_auc": "Test PR-AUC",
        "resumen_ayuda_pr_auc": (
            "Measures how well the model ranks customers by risk, on {n} customers it "
            "did not see during training. A random model would score {base}, the share "
            "of churners in that set."
        ),
        "resumen_arquitectura": "Architecture",
        "resumen_arquitectura_nota": (
            "The whole lifecycle runs on Databricks Free Edition. This app loads the "
            "exported model and computes features with the same package used in training."
        ),
        "resumen_decisiones": "Key decisions",
        "resumen_decisiones_lista": (
            "- **Metric: PR-AUC.** With {tasa} churn, accuracy would reward a model that "
            "detects nobody. What matters is ranking customers well by risk.\n"
            "- **Threshold {umbral}.** The threshold analysis pointed to the 0.30-0.40 "
            "range, where each detected churner costs about one and a half extra calls. "
            "The exact value depends on the cost of an offer and the value of a retained customer.\n"
            "- **Champion: logistic regression.** Tuned random forest, gradient boosting and "
            "XGBoost beat it by about 0.02 PR-AUC, at the edge of fold-to-fold noise. Not "
            "worth losing the explainability of its coefficients.\n"
            "- **Same code in training and in the app.** Features are computed in a tested "
            "in-house package, and both the gold table and this app use the same function."
        ),
        "resumen_uso": "What you can do in this app",
        "resumen_uso_lista": (
            "- **Score a customer:** enter a profile or load a real one and get its churn "
            "probability.\n"
            "- **Risk list:** current customers ranked by risk, with filters and CSV download.\n"
            "- **Simulate a month:** how the list changes over time and with new customers."
        ),
        "arquitectura": {
            "datos": "IBM Telco dataset\\n7,043 customers",
            "bronze": "Bronze\\nraw CSV",
            "silver": "Silver\\ncleaning and validation",
            "gold": "Gold\\n8 derived features",
            "paquete": "churn package\\ntested features",
            "entrenamiento": "Training\\nscikit-learn, 5-fold CV",
            "challenger": "Challengers\\nRF, GB, XGBoost",
            "mlflow": "MLflow\\nexperiments and metrics",
            "registro": "Unity Catalog\\nmodel with champion alias",
            "batch": "Batch scoring\\ncustomer_scores table",
            "serving": "Model Serving\\nREST endpoint",
            "exportacion": "Export\\njoblib + JSON",
            "app": "This app",
            "grupo_databricks": "Databricks Free Edition",
            "grupo_streamlit": "Streamlit Community Cloud",
        },
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
        "sim_alcance": (
            "The simulation starts from the current customers and does not model "
            "churn: no customer leaves. It only shows how risk changes over time and "
            "with new customers. Customers at 72 months, the dataset maximum, do not "
            "change when a month passes."
        ),
        "boton_pasar_mes": "Advance one month",
        "sim_n_altas": "Number of new customers",
        "ayuda_altas": "Each new customer copies the profile of a real one, with tenure 0.",
        "boton_altas": "Add new customers",
        "boton_reiniciar": "Reset simulation",
        "ind_mes": "Simulated month",
        "ind_total": "Total customers",
        "ind_entran": "Entering the list",
        "ind_salen": "Leaving the list",
        "sim_sin_acciones": "No action taken yet.",
        "sim_ultima_mes": "Last action: moved to month {mes}. Changes relative to the previous month.",
        "sim_ultima_altas": (
            "Last action: {n} new customers in month {mes}. "
            "Changes relative to the state before they were added."
        ),
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
