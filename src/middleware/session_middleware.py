from src.context.user_context import set_user_context, clear_user_context


class SessionMiddleware:
    """
    Middleware que extrae el user_id de las peticiones HTTP
    y lo establece en el contexto
    """
    
    @staticmethod
    def extract_user_from_request(request_data: dict) -> str:
        """
        Extrae el user_id de la petición
        Puede venir de JWT, headers, session, etc.
        """
        # Opción 1: De parámetros de la petición
        user_id = request_data.get('user_id')
        
        # Opción 2: De JWT (implementar según tu auth)
        # token = request_data.get('headers', {}).get('Authorization')
        # user_id = decode_jwt(token)
        
        # Opción 3: De sesión
        # session_id = request_data.get('session_id')
        # user_id = get_user_from_session(session_id)
        
        # Fallback: Usuario demo para desarrollo
    
    @staticmethod
    def process_request(request_data: dict):
        """Procesa la petición y establece el contexto"""
        user_id = SessionMiddleware.extract_user_from_request(request_data)
        set_user_context(user_id)
        return user_id
    
    @staticmethod
    def cleanup():
        """Limpia el contexto después de la petición"""
        clear_user_context()