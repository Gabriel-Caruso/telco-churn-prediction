# Unity Catalog
CATALOG = "telco_churn"
BRONZE = f"{CATALOG}.bronze"
SILVER = f"{CATALOG}.silver"
GOLD = f"{CATALOG}.gold"
MODELS = f"{CATALOG}.models"

# Ficheros / files
VOLUME = f"/Volumes/{CATALOG}/bronze/raw"
RAW_CSV = f"{VOLUME}/telco_churn.csv"

# Tablas / tables
BRONZE_TABLE = f"{BRONZE}.customers_raw"
SILVER_TABLE = f"{SILVER}.customers_clean"
GOLD_TABLE = f"{GOLD}.customer_features"

# Modelo / model
MODEL_NAME = f"{MODELS}.churn_classifier"

RANDOM_SEED = 42

# Grupos de columnas
ID     = "customer_id"
TARGET = "churn"

DEMOGRAFICAS = ["gender", "senior_citizen", "partner", "dependents"]
CONTRATO     = ["contract", "paperless_billing", "payment_method"]
TELEFONIA    = ["phone_service", "multiple_lines"]
INTERNET     = ["internet_service", "online_security", "online_backup",
                "device_protection", "tech_support", "streaming_tv", "streaming_movies"]

CATEGORICAS = DEMOGRAFICAS + CONTRATO + TELEFONIA + INTERNET
NUMERICAS   = ["tenure", "monthly_charges", "total_charges"]

# Subgrupos de servicios, según los hallazgos de la Fase 2 en notebooks/02_exploration
SERVICIOS_SOPORTE = ["online_security", "online_backup", "device_protection", "tech_support"]
SERVICIOS_OCIO    = ["streaming_tv", "streaming_movies"]
METODOS_AUTOMATICOS = ["Bank transfer (automatic)", "Credit card (automatic)"]

