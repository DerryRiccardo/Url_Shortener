import os
import redis
from app.utils.logger import app_logger
from dotenv import load_dotenv

load_dotenv()

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# Simpan koneksi dalam variabel global
_redis_client = None

def get_redis_client() -> redis.Redis | None:
    global _redis_client
    if _redis_client is None:
        try:
            # decode_responses=True = hasil dari Redis berupa String
            _redis_client = redis.from_url(REDIS_URL, decode_responses=True)
            # Ping untuk memastikan koneksi berhasil
            _redis_client.ping()
            app_logger.info(f"Connected to Redis successfully at {REDIS_URL}")
        except Exception as e:
            app_logger.error(f"Failed to connect to Redis: {e}")
            _redis_client = None
            
    return _redis_client

def close_redis():
    global _redis_client
    if _redis_client:
        _redis_client.close()
        _redis_client = None
        app_logger.info("Redis connection closed.")
