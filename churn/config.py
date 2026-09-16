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
TARGET = "Churn"


# Grupos de columnas
ID = "customerID"

DEMOGRAFICAS = ["gender", "SeniorCitizen", "Partner", "Dependents"]
CONTRATO     = ["Contract", "PaperlessBilling", "PaymentMethod"]
TELEFONIA    = ["PhoneService", "MultipleLines"]
INTERNET     = ["InternetService", "OnlineSecurity", "OnlineBackup", "DeviceProtection", "TechSupport", "StreamingTV", "StreamingMovies"]

CATEGORICAS = DEMOGRAFICAS + CONTRATO + TELEFONIA + INTERNET
NUMERICAS   = ["tenure", "MonthlyCharges", "TotalCharges"]

# Subgrupos de servicios, según los hallazgos de la Fase 2 en notebooks/02_exploration
SERVICIOS_SOPORTE = ["OnlineSecurity", "OnlineBackup", "DeviceProtection", "TechSupport"]
SERVICIOS_OCIO    = ["StreamingTV", "StreamingMovies"]