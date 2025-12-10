import os
from dotenv import load_dotenv

# Cargar .env solo si existe (para desarrollo local)
# En producción (Render), las variables vienen directamente del ambiente
try:
    load_dotenv()
except:
    pass

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Debug: verificar que se carga correctamente
if not GEMINI_API_KEY:
    import warnings
    warnings.warn("GEMINI_API_KEY no está configurada")