import os
import firebase_admin
from firebase_admin import credentials, firestore
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FirebaseConnection:
    """Maneja la conexión a Firebase de forma centralizada"""
    _db = None
    
    @classmethod
    def get_db(cls):
        """Retorna la instancia del cliente de Firestore"""
        if cls._db is None:
            cls._initialize()
        return cls._db
    
    @classmethod
    def _initialize(cls):
        """Inicializa la conexión a Firebase"""

        # Ubica el archivo dentro del paquete del agente
        cred_path = os.path.join(
            os.path.dirname(__file__),
            "firebase_key.json"   # ← archivo que vas a crear en la carpeta config
        )

        if not os.path.exists(cred_path):
            raise FileNotFoundError(f"No se encontró archivo de credencial Firebase en: {cred_path}")

        if not firebase_admin._apps:
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred)

        cls._db = firestore.client()
        logger.info(" Conectado a Firebase correctamente")
