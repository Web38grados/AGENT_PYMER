from contextvars import ContextVar
from typing import Optional
import logging

logger = logging.getLogger(__name__)

# Variable de contexto para almacenar el user_id de la sesión actual
current_user_id: ContextVar[Optional[str]] = ContextVar('current_user_id', default=None)


def set_user_context(user_id: str):
    """Establece el user_id en el contexto actual"""
    current_user_id.set(user_id)
    logger.info(f" Contexto de usuario establecido: {user_id}")


def get_user_context() -> str:
    """Obtiene el user_id del contexto actual"""
    user_id = current_user_id.get()

def clear_user_context():
    """Limpia el contexto de usuario"""
    current_user_id.set(None)