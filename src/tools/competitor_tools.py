import os
import requests
from typing import Dict, Any
from google.adk.tools import FunctionTool
from src.context.user_context import get_user_context
from dotenv import load_dotenv
import logging

load_dotenv()
logger = logging.getLogger(__name__)

GOOGLE_PLACES_API_KEY = os.getenv("GOOGLE_PLACES_API_KEY")

def buscar_competidores(industria: str, ciudad: str) -> Dict[str, Any]:
    """
    Busca competidores usando únicamente Places TextSearch.
    No usa geocoding, radio ni coordenadas.
    """
    user_id = get_user_context()
    logger.info(f"Buscando competidores para el usuario: {user_id}")

    if not GOOGLE_PLACES_API_KEY:
        return {"status": "error", "message": "API Key no configurada."}

    try:
        url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
        params = {
            "query": f"{industria} en {ciudad}",
            "key": GOOGLE_PLACES_API_KEY
        }

        response = requests.get(url, params=params)
        data = response.json()

        if data.get("status") not in ["OK", "ZERO_RESULTS"]:
            return {
                "status": "error",
                "message": f"Error en la búsqueda: {data.get('status')}"
            }

        competidores = []
        for place in data.get("results", [])[:10]:
            competidores.append({
                "nombre": place.get("name"),
                "direccion": place.get("formatted_address"),
                "rating": place.get("rating", "N/A"),
                "reseñas": place.get("user_ratings_total", 0),
                "place_id": place.get("place_id")
            })

        return {
            "status": "success",
            "industria": industria,
            "ciudad": ciudad,
            "total": len(competidores),
            "competidores": competidores
        }

    except Exception as e:
        logger.error(f"Error: {e}")
        return {"status": "error", "message": str(e)}


buscar_competidores_tool = FunctionTool(buscar_competidores)
