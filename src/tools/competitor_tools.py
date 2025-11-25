import os
import requests
from typing import Dict, List, Any
from google.adk.tools import FunctionTool
from src.context.user_context import get_user_context
from dotenv import load_dotenv
import logging

load_dotenv()
logger = logging.getLogger(__name__)

GOOGLE_PLACES_API_KEY = os.getenv("GOOGLE_PLACES_API_KEY")


def buscar_competidores(
    industria: str,
    ciudad: str,
    pais: str = "Colombia",
    radio_km: int = 5
) -> Dict[str, Any]:

    user_id = get_user_context()  
    logger.info(f" Buscando competidores para usuario: {user_id}")
    
    if not GOOGLE_PLACES_API_KEY:
        return {
            "status": "error",
            "message": "Google Places API Key no configurada. Contacta al administrador."
        }
    
    try:
        # Geocodificar la ubicación
        geocode_url = "https://maps.googleapis.com/maps/api/geocode/json"
        geocode_params = {
            "address": f"{ciudad}, {pais}",
            "key": GOOGLE_PLACES_API_KEY
        }
        
        geo_response = requests.get(geocode_url, params=geocode_params)
        geo_data = geo_response.json()
        
        if geo_data["status"] != "OK":
            return {
                "status": "error",
                "message": f"No se pudo encontrar la ubicación: {ciudad}, {pais}"
            }
        
        location = geo_data["results"][0]["geometry"]["location"]
        lat, lng = location["lat"], location["lng"]
        
        # Buscar negocios cercanos
        places_url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
        places_params = {
            "location": f"{lat},{lng}",
            "radius": radio_km * 1000,
            "keyword": industria,
            "key": GOOGLE_PLACES_API_KEY
        }
        
        places_response = requests.get(places_url, params=places_params)
        places_data = places_response.json()
        
        if places_data["status"] not in ["OK", "ZERO_RESULTS"]:
            return {
                "status": "error",
                "message": f"Error en la búsqueda: {places_data.get('status')}"
            }
        
        # Procesar resultados
        competidores = []
        for place in places_data.get("results", [])[:10]:
            competidor = {
                "nombre": place.get("name"),
                "direccion": place.get("vicinity"),
                "rating": place.get("rating", "N/A"),
                "total_reseñas": place.get("user_ratings_total", 0),
                "tipos": place.get("types", []),
                "precio_nivel": place.get("price_level", 0) if place.get("price_level") else "N/A",
                "abierto_ahora": place.get("opening_hours", {}).get("open_now", "N/A"),
                "lugar_id": place.get("place_id")
            }
            competidores.append(competidor)
        
        return {
            "status": "success",
            "ubicacion_busqueda": f"{ciudad}, {pais}",
            "industria": industria,
            "total_encontrados": len(competidores),
            "competidores": competidores,
            "resumen": {
                "rating_promedio": round(
                    sum(c["rating"] for c in competidores if isinstance(c["rating"], (int, float))) / len(competidores),
                    2
                ) if competidores else 0,
                "mejor_calificado": max(competidores, key=lambda x: x["rating"] if isinstance(x["rating"], (int, float)) else 0)["nombre"] if competidores else None
            }
        }
        
    except Exception as e:
        logger.error(f" Error buscando competidores: {e}")
        return {"status": "error", "message": str(e)}


def analizar_mercado(
    industria: str,
    ciudad: str,
    mi_precio_promedio: float = 0.0
) -> Dict[str, Any]:
    """
    Analiza el mercado local del usuario y proporciona insights sobre la competencia.
    
    Args:
        industria: Tipo de negocio
        ciudad: Ciudad donde operas
        mi_precio_promedio: Tu precio promedio para comparar (opcional)
        
    Returns:
        Análisis completo del mercado con recomendaciones
    """
    user_id = get_user_context()
    logger.info(f" Analizando mercado para usuario: {user_id}")
    
    try:
        # Buscar competidores
        competidores_data = buscar_competidores(industria, ciudad)
        
        if competidores_data["status"] != "success":
            return competidores_data
        
        competidores = competidores_data["competidores"]
        
        if not competidores:
            return {
                "status": "success",
                "mensaje": f"No se encontraron competidores directos de '{industria}' en {ciudad}",
                "oportunidad": "¡Podrías ser pionero en esta área! Gran oportunidad de mercado."
            }
        
        # Análisis de ratings
        ratings = [c["rating"] for c in competidores if isinstance(c["rating"], (int, float))]
        rating_promedio = sum(ratings) / len(ratings) if ratings else 0
        
        # Análisis de precios
        precios = [c["precio_nivel"].count for c in competidores if c["precio_nivel"] != "N/A"]
        precio_promedio_mercado = sum(precios) / len(precios) if precios else 0
        
        # Análisis de reseñas
        total_reseñas = [c["total_reseñas"] for c in competidores]
        reseñas_promedio = sum(total_reseñas) / len(total_reseñas) if total_reseñas else 0
        
        # Top competidores
        top_competidores = sorted(
            competidores,
            key=lambda x: (x["rating"] if isinstance(x["rating"], (int, float)) else 0, x["total_reseñas"]),
            reverse=True
        )[:3]
        
        # Generar insights
        insights = []
        
        if rating_promedio >= 4.0:
            insights.append("El mercado tiene competidores bien valorados. Necesitas diferenciarte con excelente servicio.")
        else:
            insights.append("Hay oportunidad de destacar con mejor servicio al cliente.")
        
        if reseñas_promedio < 50:
            insights.append("Los competidores tienen pocas reseñas. Pide activamente feedback a tus clientes.")
        
        return {
            "status": "success",
            "analisis": {
                "total_competidores": len(competidores),
                "rating_promedio_mercado": round(rating_promedio, 2),
                "reseñas_promedio": round(reseñas_promedio, 0),
                "nivel_precio_promedio": int(precio_promedio_mercado) if precio_promedio_mercado > 0 else "N/A",
                "competidores_principales": [
                    {
                        "nombre": c["nombre"],
                        "rating": c["rating"],
                        "reseñas": c["total_reseñas"]
                    }
                    for c in top_competidores
                ],
                "insights": insights,
                "recomendaciones": [
                    f"Apunta a un rating superior a {round(rating_promedio + 0.3, 1)} para destacar",
                    f"Consigue al menos {int(reseñas_promedio * 1.2)} reseñas para ser competitivo",
                    "Monitorea los precios de tus top 3 competidores mensualmente"
                ]
            }
        }
        
    except Exception as e:
        logger.error(f" Error analizando mercado: {e}")
        return {"status": "error", "message": str(e)}

buscar_competidores_tool = FunctionTool(buscar_competidores)
analizar_mercado_tool = FunctionTool(analizar_mercado)