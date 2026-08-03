import sys
import uuid
from contextvars import ContextVar
from loguru import logger
import json

# Context Variable untuk menyimpan Request ID unik setiap siklus request agar tidak saling menimpa
# Misalnya ada user A dan B barengan request, maka request user A dan request user B akan punya ID yang berbeda tapi logged nya sama
# Jika ID merupakan random string itu berarti itu dipicu oleh user, tapi kalau bertuliskan SYSTEM itu berarti dipicu oleh backend (CRON / background task)
request_id_context_var: ContextVar[str] = ContextVar("request_id", default="SYSTEM")

SENSITIVE_KEYS = ["password", "token", "secret", "access_token", "authorization", "secret_key"]

# Fungsi patch untuk menyuntikkan request_id ke dalam log record dan menyensor data sensitif
def patch_record(record):
    # 1. Menempelkan Request ID dari ContextVar ke dalam extra dict
    record["extra"]["request_id"] = request_id_context_var.get()
    
    # 2. Sensor data sensitif
    for key in list(record["extra"].keys()):
        if any(sens in str(key).lower() for sens in SENSITIVE_KEYS):
            record["extra"][key] = "***REDACTED***"
            
    return True

# Bersihkan konfigurasi default loguru
logger.remove()

# 1. Sink Terminal (Konsol) - Format khusus dengan request_id
logger.add(
    sys.stderr, 
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{extra[request_id]}</cyan> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level="DEBUG",
    filter=patch_record
)

# Fungsi custom format untuk file log JSON
def json_formatter(record):
    log_obj = {
        "time": record["time"].isoformat(),
        "level": record["level"].name,
        "request_id": record["extra"].get("request_id", "SYSTEM"),
        "module": f"{record['name']}:{record['line']}",
        "message": record["message"]
    }
    
    # Jika ada error (Exception), tambahkan ke log
    if record["exception"]:
        log_obj["exception"] = record["exception"].text
        
    # Escape curly braces agar tidak dianggap sebagai format tag oleh Loguru
    return json.dumps(log_obj).replace("{", "{{").replace("}", "}}") + "\n"


# 2. Sink File JSON - Format terstruktur dengan rotasi dan retensi
logger.add(
    "logs/app.json", 
    format=json_formatter,
    rotation="10 MB",
    retention="7 days",
    level="INFO",
    filter=patch_record
)

# Export app_logger untuk dipakai di seluruh proyek
app_logger = logger
