import os
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, firestore
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

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
        if not firebase_admin._apps:
            cred_path = os.getenv("FIREBASE_CREDENTIALS_PATH")
            
            if not cred_path:
                raise ValueError("FIREBASE_CREDENTIALS_PATH no configurado")
            
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred)
            cls._db = firestore.client()
            logger.info(f" Conectado a Firebase: {cls._db._database_string}")