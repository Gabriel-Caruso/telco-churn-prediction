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
        "cabecera_etiqueta": "Databricks · MLflow · Unity Catalog · scikit-learn",
        "cabecera_titulo": "Predicción de bajas en una operadora de telecomunicaciones",
        "separador_decimal": ",",
        "simbolo_porcentaje": " %",
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
        "resumen_decisiones": "Decisiones clave",
        "etapas": [
            {
                "titulo": "1. Datos",
                "texto": (
                    "El CSV de IBM pasa por tres capas: bronze guarda el original, silver lo "
                    "limpia y valida, y gold añade 8 features calculadas con un paquete propio."
                ),
                "tecnologias": "Databricks · Unity Catalog · tablas Delta · pytest",
            },
            {
                "titulo": "2. Modelado",
                "texto": (
                    "Regresión logística dentro de un pipeline de scikit-learn, comparada por "
                    "PR-AUC con validación cruzada de 5 folds. Random forest, gradient boosting "
                    "y XGBoost compitieron como challengers."
                ),
                "tecnologias": "scikit-learn · MLflow",
            },
            {
                "titulo": "3. Producción",
                "texto": (
                    "El modelo elegido se registra con el alias champion y se usa de tres formas: "
                    "batch scoring en una tabla, un endpoint REST y una exportación para esta app."
                ),
                "tecnologias": "Unity Catalog · Model Serving · joblib",
            },
            {
                "titulo": "4. Esta app",
                "texto": (
                    "Carga el modelo exportado y calcula las features con el mismo paquete que "
                    "el entrenamiento, así que la app y el modelo nunca divergen."
                ),
                "tecnologias": "Streamlit Community Cloud",
            },
        ],
        "decisiones": [
            {
                "titulo": "Métrica: PR-AUC",
                "texto": (
                    "Con un {tasa} de bajas, la accuracy premiaría a un modelo que no detecta "
                    "a nadie. Lo que importa es ordenar bien a los clientes por riesgo."
                ),
            },
            {
                "titulo": "Umbral {umbral}",
                "texto": (
                    "El análisis de umbrales marcó el tramo 0,30-0,40, donde cada baja detectada "
                    "cuesta alrededor de una llamada y media de más. El valor exacto depende del "
                    "coste de una oferta y del valor de un cliente retenido."
                ),
            },
            {
                "titulo": "Champion: regresión logística",
                "texto": (
                    "Random forest, gradient boosting y XGBoost ajustados la superan en unos "
                    "0,02 de PR-AUC, en el límite del ruido entre folds. No compensa perder la "
                    "explicabilidad de los coeficientes."
                ),
            },
            {
                "titulo": "Mismo código en entrenamiento y app",
                "texto": (
                    "Las features se calculan en un paquete propio con tests, y la tabla gold y "
                    "esta app usan la misma función."
                ),
            },
        ],
        "resumen_uso": "Qué puedes hacer en esta app",
        "resumen_uso_lista": (
            "- **Cliente:** introduce un perfil o carga uno real y obtén su probabilidad de "
            "baja y qué variables la explican.\n"
            "- **Lista de riesgo:** los clientes actuales ordenados por riesgo, con filtros "
            "y descarga en CSV.\n"
            "- **Simulación:** cómo cambia la lista con el paso del tiempo y las altas nuevas.\n"
            "- **Exploración:** los hallazgos principales del análisis exploratorio.\n"
            "- **Modelo:** evaluación en test, umbral ajustable y comparación con los challengers."
        ),
        "pestana_cliente": "Cliente",
        "pestana_riesgo": "Lista de riesgo",
        "pestana_simulacion": "Simulación",
        "pestana_exploracion": "Exploración",
        "exp_intro": (
            "Tasa de baja de los {n} clientes del dataset en los cortes más relevantes del "
            "análisis exploratorio. Los textos son las conclusiones del notebook "
            "02_exploration."
        ),
        "exp_eje_tasa": "Tasa de baja",
        "exp_por_encima": "Por encima de la referencia",
        "exp_por_debajo": "Por debajo de la referencia",
        "exp_posicion": "Tasa de baja",
        "exp_ref_empresa": "Media de la empresa: {tasa}",
        "exp_ref_fibra": "Media de la fibra: {tasa}",
        "exp_ref_mensual": "Media de los contratos mensuales: {tasa}",
        "exp_dest_tenure": "Bajas en el primer mes",
        "exp_dest_contrato": "Bajas con contrato mensual",
        "exp_dest_fibra": "Bajas en fibra sin servicios extra",
        "exp_dest_pago": "Bajas con cheque electrónico y contrato mensual",
        "exp_dest_servicios": "Diferencia sin y con seguridad online",
        "exp_dest_puntos": "{puntos} puntos",
        "exp_servicios_soporte": "Servicios de soporte",
        "exp_servicios_ocio": "Servicios de ocio",
        "exp_eje_clientes": "Clientes",
        "exp_tenure_titulo": "Tasa de baja por antigüedad",
        "exp_tenure_texto": (
            "El problema de retención está, principalmente, en los primeros meses. Quien "
            "supera los dos años apenas se marcha."
        ),
        "exp_contrato_titulo": "Tasa de baja por tipo de contrato",
        "exp_contrato_texto": (
            "Puede resultar obvio, ya que los clientes con permanencia son los que más se "
            "retienen por la propia naturaleza del contrato. Sabiendo esto, el resto de "
            "variables —método de pago, cómo recibe la factura, etc.— pueden estar muy "
            "relacionadas con el tipo de contrato y hay que mirarlas con sumo cuidado."
        ),
        "exp_simpson_titulo": "Paradoja de Simpson: cuota mensual y tipo de conexión",
        "exp_simpson_todos": "Todos los clientes, por quintiles de cuota mensual",
        "exp_simpson_fibra": "Solo clientes de fibra, por cuartiles de cuota mensual",
        "exp_simpson_eje": "Cuota mensual",
        "exp_dest_simpson": "Fibra: bajas con la cuota más baja y con la más alta",
        "exp_simpson_texto": (
            "Al mirar **solo a los clientes de fibra**, la tendencia se da la vuelta: los que "
            "pagan entre 68 y 80 se dan de baja el 55 %, y los que pagan más de 101 solo el 26 %, "
            "por debajo incluso de la media de la empresa.\n\n"
            "Es un caso de paradoja de Simpson: la relación aparente entre cuota y baja estaba "
            "explicada por el tipo de conexión, no por el precio. De no haberlo visto, podríamos "
            "haberle dicho a negocio que \"los clientes más caros son los que más se van\" y "
            "ellos haber respondido \"entonces bajamos los precios\" cuando ese no era nuestro "
            "verdadero problema."
        ),
        "exp_fibra_titulo": "Clientes de fibra: tasa de baja según servicios extra contratados",
        "exp_fibra_eje": "Servicios extra contratados (de 6)",
        "exp_fibra_texto": (
            "Los clientes que contratan más servicios tienen una tasa de baja mucho menor. "
            "**El problema está en la fibra contratada sola.**"
        ),
        "exp_pago_titulo": "Variable de confusión: forma de pago y contrato",
        "exp_pago_todos": "Todos los clientes",
        "exp_pago_mensual": "Solo contratos mensuales",
        "exp_pago_contexto": (
            "La lectura inmediata sería \"el cheque electrónico provoca bajas\". Pero antes "
            "de llevar eso a una reunión conviene comprobar algo: **el 78 % de quienes pagan "
            "con cheque electrónico tiene contrato mes a mes**, frente al 55 % del conjunto "
            "de la empresa."
        ),
        "exp_pago_texto": (
            "**Conclusión:** el contrato explicaba una parte, pero no todo. A igualdad de "
            "contrato, el cheque electrónico sigue asociado a unos 20 puntos más de bajas. "
            "Domiciliar el pago, en cambio, se asocia a permanencia incluso entre los "
            "clientes sin compromiso."
        ),
        "exp_servicios_titulo": "Diferencia de tasa de baja entre no tener y tener cada servicio",
        "exp_servicios_eje": "Puntos de diferencia",
        "exp_servicios_texto": (
            "Los servicios que **resuelven problemas** acompañan a la permanencia. Los de "
            "**entretenimiento** no la mueven prácticamente nada."
        ),
        "solucion_titulo": "Qué haría la empresa",
        "solucion_intro": (
            "Los datos señalan tres frentes, ordenados por su peso en las bajas. Ninguno "
            "demuestra una causa, así que cada acción se plantea como una prueba con un grupo de "
            "control antes de extenderla a toda la base."
        ),
        "solucion_frentes": [
            {
                "titulo": "Acompañar los tres primeros meses",
                "texto": (
                    "El 56 % de los clientes con tres meses o menos se va, y de ese 15 % de la "
                    "base sale casi un tercio de todas las bajas. Propuesta: un programa de "
                    "bienvenida (seguimiento en el primer mes, revisión de la instalación) y una "
                    "oferta para pasar a contrato anual, la variable que más separa: 43 % de bajas "
                    "en contrato mensual, 11 % a un año y 3 % a dos años."
                ),
            },
            {
                "titulo": "No bajar precios: completar la fibra con soporte",
                "texto": (
                    "La fibra concentra el 69 % de las bajas, pero el precio no es la palanca: "
                    "dentro de la fibra, quien más paga se va menos (paradoja de Simpson). Lo que "
                    "separa es contratarla sola: sin servicios extra se va el 60 %; con los seis, "
                    "el 9 %. Propuesta: ofrecer seguridad online o soporte técnico a los clientes "
                    "de fibra sin extras, los servicios que más acompañan a la permanencia (unos "
                    "27 puntos), y no streaming (3-4 puntos)."
                ),
            },
            {
                "titulo": "Pasar el cheque electrónico a domiciliación",
                "texto": (
                    "A igualdad de contrato, el cheque electrónico tiene unos 20 puntos más de "
                    "bajas que cualquier pago automático. Propuesta: un incentivo para domiciliar "
                    "el pago, empezando por los contratos mensuales."
                ),
            },
        ],
        "solucion_modelo_titulo": "Cómo usar el modelo",
        "solucion_modelo_texto": (
            "Cada mes, la lista de riesgo indica a quién contactar primero. El umbral de {umbral} "
            "está en el tramo donde cada baja detectada cuesta alrededor de una llamada y media; "
            "el valor definitivo debe fijarse con tres cifras que tiene la empresa: el coste de "
            "una oferta, el valor de un cliente retenido y el porcentaje de ofertas que funcionan."
        ),
        "solucion_falta_titulo": "Qué falta saber",
        "solucion_falta_texto": (
            "Por qué falla la fibra (precio, calidad o competencia) no está en los datos: hacen "
            "falta encuestas de salida. Y solo un experimento con grupo de control dirá si los "
            "servicios retienen o si los contrata quien ya pensaba quedarse."
        ),
        "tldr": [
            "Planes de negocio para los tres primeros meses.",
            "Estudiar planes anuales que compitan fuertemente contra planes mensuales.",
            "Intentar domiciliar el pago.",
            "Gestionar con la aplicación a quién llamar primero según la lista de riesgo.",
        ],
        "exp_limites_titulo": "Lo que estos datos no pueden responder",
        "exp_limites_texto": (
            "**No sabemos por qué la fibra falla.** Los datos dicen que los clientes de fibra "
            "se van mucho más, pero no si es por precio, por calidad del servicio o porque la "
            "competencia ataca justo a ese segmento. Esa información no está en el sistema.\n\n"
            "**No sabemos si los servicios retienen o solo lo parecen.** Puede que contratar "
            "soporte técnico haga más incómodo cambiarse de compañía, o puede que el cliente "
            "que ya pensaba quedarse sea el que va sumando extras. Las dos explicaciones encajan "
            "igual de bien con los datos y llevan a decisiones opuestas: en el primer caso, "
            "regalar servicios reduce la fuga; en el segundo, solo cuesta dinero.\n\n"
            "**Lo mismo vale para el contrato largo.** No sabemos si ata al cliente o si lo "
            "elige quien ya tenía intención de quedarse. Posiblemente sea lo primero, pero no "
            "podemos arriesgarnos a dar un veredicto así.\n\n"
            "Las tres se resolverían igual: con una campaña controlada, ofreciendo el "
            "complemento a un grupo de clientes elegidos al azar y comparando su comportamiento "
            "con el de un grupo equivalente que no lo recibe."
        ),
        "pestana_modelo": "Modelo",
        "modelo_intro": (
            "Evaluación sobre los {n} clientes de test, que el modelo no vio al entrenar. "
            "Mueve el umbral para ver cómo cambia el reparto entre bajas detectadas y "
            "falsas alarmas. El umbral de producción es {umbral}."
        ),
        "modelo_slider": "Umbral de prueba",
        "modelo_matriz_titulo": "Resultado con este umbral",
        "modelo_detectados": "Bajas detectadas",
        "modelo_falsas": "Falsas alarmas",
        "modelo_perdidos": "Bajas no detectadas",
        "modelo_descartados": "Bien fuera de la lista",
        "modelo_precision": "**Precisión {p}:** de cada 100 clientes en la lista, {p100} se van de verdad.",
        "modelo_recall": "**Recall {r}:** se detectan {r100} de cada 100 bajas.",
        "modelo_pr_titulo": "Curva de precisión y recall",
        "modelo_pr_nota": (
            "Cada punto de la curva es un umbral distinto; el punto marcado es el umbral de "
            "prueba. La línea discontinua es un modelo al azar ({base})."
        ),
        "eje_precision": "Precisión",
        "eje_recall": "Recall",
        "modelo_ganancia_titulo": "Curva de ganancia acumulada",
        "modelo_ganancia_nota": (
            "Contactando a los clientes de mayor a menor probabilidad, qué parte de las bajas "
            "se captura según cuántos clientes se contacten. El punto marcado es el umbral de prueba."
        ),
        "eje_contactados": "Clientes contactados",
        "eje_capturadas": "Bajas capturadas",
        "serie_modelo": "Modelo",
        "serie_azar": "Al azar",
        "serie": "Serie",
        "modelo_importancia_titulo": "Qué variables pesan más",
        "modelo_importancia_nota": (
            "Media del valor absoluto de la aportación de cada variable en los clientes de "
            "test, respecto al cliente medio de entrenamiento. Mide cuánto mueve cada variable "
            "la predicción, no en qué dirección. Se muestran las {n} primeras."
        ),
        "eje_importancia": "Aportación media absoluta (logit)",
        "modelo_challenger_titulo": "Champion frente a challengers",
        "modelo_challenger_nota": (
            "Diferencia de PR-AUC de cada modelo ajustado frente a la regresión logística, en "
            "los mismos 5 folds de validación cruzada sobre entrenamiento. La banda gris marca "
            "±0,02, el margen que se consideró ruido. Cifras del notebook 11_challenger: no se "
            "calculan en la app."
        ),
        "modelo_challenger_llamadas": (
            "Con la misma lista de llamadas, XGBoost encuentra 982 de las 1495 bajas de "
            "entrenamiento y la regresión logística 964. Se mantuvo la regresión logística "
            "por la explicabilidad de sus coeficientes."
        ),
        "eje_diferencia": "Diferencia de PR-AUC frente a la regresión logística",
        "eje_modelo": "Modelo",
        "fold": "Fold",
        "media": "Media",
        "tipo": "Tipo",
        "sobre_proyecto": (
            "Proyecto de ciclo de vida de machine learning con el dataset IBM Telco "
            "Customer Churn, desarrollado en Databricks con MLflow y Unity Catalog."
        ),
        "enlace_repo": "Código en GitHub",
        "ayuda_info": "Sobre el proyecto y el modelo",
        "ficha_modelo": "Modelo",
        "ficha_nombre": "Nombre",
        "ficha_version": "Versión",
        "ficha_umbral": "Umbral de riesgo",
        "ficha_fecha": "Exportado",
        "grupo_personales": "Datos personales",
        "grupo_contrato": "Contrato y pago",
        "grupo_servicios": "Servicios",
        "grupo_telefonia": "Telefonía",
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
        "explicacion_titulo": "Por qué esta probabilidad",
        "explicacion_nota": (
            "Aportación de cada variable respecto al cliente medio de entrenamiento, en "
            "escala logit. Las barras naranjas suben la probabilidad de baja y las azules "
            "la bajan. Se muestran las {n} que más pesan en cada sentido."
        ),
        "explicacion_sube": "Sube el riesgo",
        "explicacion_baja": "Baja el riesgo",
        "explicacion_eje": "Aportación al logit",
        "explicacion_efecto": "Efecto",
        "explicacion_variable": "Variable",
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
            "is_new_customer": "Cliente nuevo (0 meses)",
            "tenure_max": "Antigüedad máxima (72 meses)",
            "n_support_services": "Servicios de soporte contratados",
            "n_entertainment_services": "Servicios de ocio contratados",
            "avg_historical_charge": "Cargo medio histórico",
            "charge_ratio": "Cargo actual / cargo medio histórico",
            "fiber_no_support": "Fibra sin servicios de soporte",
            "automatic_payment": "Pago automático",
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
        "cabecera_etiqueta": "Databricks · MLflow · Unity Catalog · scikit-learn",
        "cabecera_titulo": "Churn prediction for a telecom operator",
        "separador_decimal": ".",
        "simbolo_porcentaje": "%",
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
        "resumen_decisiones": "Key decisions",
        "etapas": [
            {
                "titulo": "1. Data",
                "texto": (
                    "The IBM CSV goes through three layers: bronze keeps the original, silver "
                    "cleans and validates it, and gold adds 8 features computed by an in-house package."
                ),
                "tecnologias": "Databricks · Unity Catalog · Delta tables · pytest",
            },
            {
                "titulo": "2. Modelling",
                "texto": (
                    "Logistic regression inside a scikit-learn pipeline, compared by PR-AUC with "
                    "5-fold cross-validation. Random forest, gradient boosting and XGBoost "
                    "competed as challengers."
                ),
                "tecnologias": "scikit-learn · MLflow",
            },
            {
                "titulo": "3. Production",
                "texto": (
                    "The chosen model is registered with the champion alias and used in three "
                    "ways: batch scoring into a table, a REST endpoint and an export for this app."
                ),
                "tecnologias": "Unity Catalog · Model Serving · joblib",
            },
            {
                "titulo": "4. This app",
                "texto": (
                    "Loads the exported model and computes features with the same package used "
                    "in training, so the app and the model never diverge."
                ),
                "tecnologias": "Streamlit Community Cloud",
            },
        ],
        "decisiones": [
            {
                "titulo": "Metric: PR-AUC",
                "texto": (
                    "With {tasa} churn, accuracy would reward a model that detects nobody. "
                    "What matters is ranking customers well by risk."
                ),
            },
            {
                "titulo": "Threshold {umbral}",
                "texto": (
                    "The threshold analysis pointed to the 0.30-0.40 range, where each detected "
                    "churner costs about one and a half extra calls. The exact value depends on "
                    "the cost of an offer and the value of a retained customer."
                ),
            },
            {
                "titulo": "Champion: logistic regression",
                "texto": (
                    "Tuned random forest, gradient boosting and XGBoost beat it by about 0.02 "
                    "PR-AUC, at the edge of fold-to-fold noise. Not worth losing the "
                    "explainability of its coefficients."
                ),
            },
            {
                "titulo": "Same code in training and app",
                "texto": (
                    "Features are computed in a tested in-house package, and both the gold table "
                    "and this app use the same function."
                ),
            },
        ],
        "resumen_uso": "What you can do in this app",
        "resumen_uso_lista": (
            "- **Customer:** enter a profile or load a real one and get its churn probability "
            "and which variables explain it.\n"
            "- **Risk list:** current customers ranked by risk, with filters and CSV download.\n"
            "- **Simulation:** how the list changes over time and with new customers.\n"
            "- **Exploration:** the main findings of the exploratory analysis.\n"
            "- **Model:** test evaluation, adjustable threshold and comparison with the challengers."
        ),
        "pestana_cliente": "Customer",
        "pestana_riesgo": "Risk list",
        "pestana_simulacion": "Simulation",
        "pestana_exploracion": "Exploration",
        "exp_intro": (
            "Churn rate of the {n} customers in the dataset across the most relevant cuts "
            "of the exploratory analysis. The texts are the conclusions of the "
            "02_exploration notebook."
        ),
        "exp_eje_tasa": "Churn rate",
        "exp_por_encima": "Above the reference",
        "exp_por_debajo": "Below the reference",
        "exp_posicion": "Churn rate",
        "exp_ref_empresa": "Company average: {tasa}",
        "exp_ref_fibra": "Fiber average: {tasa}",
        "exp_ref_mensual": "Month-to-month average: {tasa}",
        "exp_dest_tenure": "Churn in the first month",
        "exp_dest_contrato": "Churn on month-to-month contracts",
        "exp_dest_fibra": "Churn on fiber with no extra services",
        "exp_dest_pago": "Churn with electronic check on month-to-month",
        "exp_dest_servicios": "Gap without and with online security",
        "exp_dest_puntos": "{puntos} points",
        "exp_servicios_soporte": "Support services",
        "exp_servicios_ocio": "Entertainment services",
        "exp_eje_clientes": "Customers",
        "exp_tenure_titulo": "Churn rate by tenure",
        "exp_tenure_texto": (
            "The retention problem lies mainly in the first few months. Customers who make "
            "it past two years barely leave at all."
        ),
        "exp_contrato_titulo": "Churn rate by contract type",
        "exp_contrato_texto": (
            "This may seem obvious, since customers under commitment are the ones most likely "
            "to stay by the very nature of the contract. Knowing this, the remaining variables "
            "— payment method, how the invoice is received, and so on — may be closely tied to "
            "contract type and must be examined with great care."
        ),
        "exp_simpson_titulo": "Simpson's paradox: monthly charge and connection type",
        "exp_simpson_todos": "All customers, by monthly charge quintile",
        "exp_simpson_fibra": "Fiber customers only, by monthly charge quartile",
        "exp_simpson_eje": "Monthly charge",
        "exp_dest_simpson": "Fiber: churn at the lowest and at the highest charge",
        "exp_simpson_texto": (
            "Looking at **fibre customers only**, the trend flips: those paying between 68 and 80 "
            "churn at 55%, while those paying above 101 churn at just 26%, below the company "
            "average.\n\n"
            "This is a case of Simpson's paradox: the apparent link between price and churn was "
            "explained by the type of connection, not by the price itself. Without spotting it, we "
            "could have told the business that \"the most expensive customers are the ones who "
            "leave\" and they could have answered \"then let's lower prices\", when that was not "
            "the real problem."
        ),
        "exp_fibra_titulo": "Fiber customers: churn rate by number of extra services",
        "exp_fibra_eje": "Extra services held (out of 6)",
        "exp_fibra_texto": (
            "Customers holding more services churn far less. **The problem is fiber bought "
            "on its own.**"
        ),
        "exp_pago_titulo": "Confounding: payment method and contract",
        "exp_pago_todos": "All customers",
        "exp_pago_mensual": "Month-to-month contracts only",
        "exp_pago_contexto": (
            "The immediate reading would be \"electronic check causes churn\". But before "
            "taking that into a meeting, one thing is worth checking: **78% of those paying "
            "by electronic check are on month-to-month contracts**, against 55% across the "
            "company."
        ),
        "exp_pago_texto": (
            "**Conclusion:** contract explained part of it, but not all. With contract held "
            "constant, electronic check is still associated with some 20 additional points of "
            "churn. Setting up automatic payment, by contrast, is associated with staying, even "
            "among customers with no commitment."
        ),
        "exp_servicios_titulo": "Churn rate gap between not holding and holding each service",
        "exp_servicios_eje": "Percentage points",
        "exp_servicios_texto": (
            "Services that **solve problems** go hand in hand with retention. **Entertainment** "
            "ones barely move it at all."
        ),
        "solucion_titulo": "What the company should do",
        "solucion_intro": (
            "The data points to three fronts, ordered by their weight in churn. None of them "
            "proves a cause, so each action is framed as a test with a control group before "
            "rolling it out to the whole base."
        ),
        "solucion_frentes": [
            {
                "titulo": "Support the first three months",
                "texto": (
                    "56% of customers with three months or less leave, and that 15% of the base "
                    "accounts for almost a third of all churn. Proposal: an onboarding programme "
                    "(follow-up in the first month, installation check) and an offer to move to a "
                    "one-year contract, the variable that separates most: 43% churn on "
                    "month-to-month, 11% on one year and 3% on two years."
                ),
            },
            {
                "titulo": "Do not cut prices: complete fiber with support",
                "texto": (
                    "Fiber holds 69% of churn, but price is not the lever: within fiber, those "
                    "who pay more leave less (Simpson's paradox). What separates is buying it on "
                    "its own: with no extra services 60% leave; with all six, 9%. Proposal: offer "
                    "online security or tech support to fiber customers with no extras, the "
                    "services most associated with staying (about 27 points), rather than "
                    "streaming (3-4 points)."
                ),
            },
            {
                "titulo": "Move electronic check to automatic payment",
                "texto": (
                    "With contract held constant, electronic check shows some 20 more points of "
                    "churn than any automatic payment. Proposal: an incentive to set up automatic "
                    "payment, starting with month-to-month contracts."
                ),
            },
        ],
        "solucion_modelo_titulo": "How to use the model",
        "solucion_modelo_texto": (
            "Every month, the risk list shows who to contact first. The {umbral} threshold sits "
            "in the range where each detected churner costs about one and a half calls; the "
            "final value should be set with three figures the company has: the cost of an offer, "
            "the value of a retained customer and the share of offers that work."
        ),
        "solucion_falta_titulo": "What we still need to know",
        "solucion_falta_texto": (
            "Why fiber fails (price, quality or competition) is not in the data: exit surveys "
            "are needed. And only an experiment with a control group will tell whether services "
            "retain customers or are simply bought by those who already meant to stay."
        ),
        "tldr": [
            "Business plans for the first three months.",
            "Design annual plans that compete strongly against month-to-month plans.",
            "Encourage automatic payment.",
            "Use the app to decide who to call first, based on the risk list.",
        ],
        "exp_limites_titulo": "What this data cannot answer",
        "exp_limites_texto": (
            "**We do not know why fiber is failing.** The data says fiber customers leave far "
            "more often, but not whether it is down to price, service quality, or competitors "
            "targeting that segment specifically. That information is not in the system.\n\n"
            "**We do not know whether services retain customers or merely appear to.** Holding "
            "tech support may make switching provider more of a hassle, or the customer who "
            "already intended to stay may simply be the one who keeps adding extras. Both "
            "explanations fit the data equally well and lead to opposite decisions: in the "
            "first case, giving services away reduces churn; in the second, it only costs money.\n\n"
            "**The same applies to long contracts.** We do not know whether they tie the "
            "customer in or whether they are chosen by those who already meant to stay. It is "
            "probably the former, but we cannot risk issuing a verdict on that.\n\n"
            "All three would be settled the same way: through a controlled campaign, offering "
            "the add-on to a randomly selected group of customers and comparing their behaviour "
            "against an equivalent group that does not receive it."
        ),
        "pestana_modelo": "Model",
        "modelo_intro": (
            "Evaluation on the {n} test customers, which the model did not see during "
            "training. Move the threshold to see how the split between detected churners and "
            "false alarms changes. The production threshold is {umbral}."
        ),
        "modelo_slider": "Test threshold",
        "modelo_matriz_titulo": "Result at this threshold",
        "modelo_detectados": "Churners detected",
        "modelo_falsas": "False alarms",
        "modelo_perdidos": "Churners missed",
        "modelo_descartados": "Correctly left out",
        "modelo_precision": "**Precision {p}:** out of every 100 customers on the list, {p100} actually leave.",
        "modelo_recall": "**Recall {r}:** {r100} out of every 100 churners are detected.",
        "modelo_pr_titulo": "Precision-recall curve",
        "modelo_pr_nota": (
            "Each point on the curve is a different threshold; the marked point is the test "
            "threshold. The dashed line is a random model ({base})."
        ),
        "eje_precision": "Precision",
        "eje_recall": "Recall",
        "modelo_ganancia_titulo": "Cumulative gains curve",
        "modelo_ganancia_nota": (
            "Contacting customers from highest to lowest probability, the share of churners "
            "captured depending on how many customers are contacted. The marked point is the "
            "test threshold."
        ),
        "eje_contactados": "Customers contacted",
        "eje_capturadas": "Churners captured",
        "serie_modelo": "Model",
        "serie_azar": "Random",
        "serie": "Series",
        "modelo_importancia_titulo": "Which variables matter most",
        "modelo_importancia_nota": (
            "Mean absolute contribution of each variable on the test customers, relative to "
            "the average training customer. It measures how much each variable moves the "
            "prediction, not in which direction. The top {n} are shown."
        ),
        "eje_importancia": "Mean absolute contribution (logit)",
        "modelo_challenger_titulo": "Champion versus challengers",
        "modelo_challenger_nota": (
            "PR-AUC difference of each tuned model against logistic regression, on the same "
            "5 cross-validation folds over the training set. The grey band marks ±0.02, the "
            "margin considered noise. Figures from the 11_challenger notebook: not computed "
            "in the app."
        ),
        "modelo_challenger_llamadas": (
            "With the same call list, XGBoost finds 982 of the 1,495 training churners and "
            "logistic regression 964. Logistic regression was kept for the explainability of "
            "its coefficients."
        ),
        "eje_diferencia": "PR-AUC difference against logistic regression",
        "eje_modelo": "Model",
        "fold": "Fold",
        "media": "Mean",
        "tipo": "Type",
        "sobre_proyecto": (
            "End-to-end machine learning project on the IBM Telco Customer Churn "
            "dataset, built on Databricks with MLflow and Unity Catalog."
        ),
        "enlace_repo": "Code on GitHub",
        "ayuda_info": "About the project and the model",
        "ficha_modelo": "Model",
        "ficha_nombre": "Name",
        "ficha_version": "Version",
        "ficha_umbral": "Risk threshold",
        "ficha_fecha": "Exported",
        "grupo_personales": "Personal details",
        "grupo_contrato": "Contract and billing",
        "grupo_servicios": "Services",
        "grupo_telefonia": "Phone",
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
        "explicacion_titulo": "Why this probability",
        "explicacion_nota": (
            "Contribution of each variable relative to the average training customer, "
            "on the logit scale. Orange bars raise the churn probability and blue bars "
            "lower it. The {n} strongest in each direction are shown."
        ),
        "explicacion_sube": "Raises risk",
        "explicacion_baja": "Lowers risk",
        "explicacion_eje": "Contribution to logit",
        "explicacion_efecto": "Effect",
        "explicacion_variable": "Variable",
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
            "is_new_customer": "New customer (0 months)",
            "tenure_max": "Maximum tenure (72 months)",
            "n_support_services": "Support services held",
            "n_entertainment_services": "Entertainment services held",
            "avg_historical_charge": "Average historical charge",
            "charge_ratio": "Current charge / historical average",
            "fiber_no_support": "Fiber without support services",
            "automatic_payment": "Automatic payment",
        },
        "valores": {
            0: "No",
            1: "Yes",
        },
    },
}
