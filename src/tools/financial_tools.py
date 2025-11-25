from config.firebase_config import FirebaseConnection
from google.adk.tools import FunctionTool
from src.context.user_context import get_user_context
from typing import Dict, List, Any
import logging

logger = logging.getLogger(__name__)
db = FirebaseConnection.get_db()


def obtener_datos_financieros() -> Dict[str, List[Dict[str, Any]]]:
    """
    Obtiene los datos financieros y de costos indirectos del usuario actual.
    Ya no necesitas pasar el user_id, se obtiene automáticamente de la sesión.
    
    Returns:
        Diccionario con tres colecciones:
        - financial_settings: Configuración de márgenes, impuestos, etc.
        - indirect_fixed_costs: Costos fijos (alquiler, salarios, etc.)
        - indirect_variable_costs: Costos variables (servicios, materiales, etc.)
    """
    user_id = get_user_context()
    
    colecciones = [
        "financial_settings",
        "indirect_fixed_costs",
        "indirect_variable_costs"
    ]
    
    resultados = {}
    
    try:
        for col in colecciones:
            docs = db.collection(col).where("userId", "==", user_id).get()
            data = [doc.to_dict() for doc in docs]
            resultados[col] = data
            logger.info(f" Datos obtenidos de '{col}' para {user_id}: {len(data)} registros")
        
        return resultados
        
    except Exception as e:
        logger.error(f" Error obteniendo datos para {user_id}: {e}")
        return {col: [] for col in colecciones}


def calcular_punto_equilibrio(precio_venta: float, costo_variable_unitario: float) -> Dict[str, Any]:
    """
    Calcula el punto de equilibrio del negocio del usuario actual.
    
    Args:
        precio_venta: Precio de venta por unidad
        costo_variable_unitario: Costo variable por unidad producida
        
    Returns:
        Diccionario con el análisis del punto de equilibrio
    """
    user_id = get_user_context()
    
    try:
        datos = obtener_datos_financieros()
        
        costos_fijos_totales = sum(
            item.get('valor', 0) 
            for item in datos.get('indirect_fixed_costs', [])
        )
        
        margen_contribucion = precio_venta - costo_variable_unitario
        
        if margen_contribucion <= 0:
            return {
                "status": "error",
                "message": "El precio de venta debe ser mayor al costo variable unitario"
            }
        
        pe_unidades = costos_fijos_totales / margen_contribucion
        pe_dinero = pe_unidades * precio_venta
        
        return {
            "status": "success",
            "punto_equilibrio": {
                "unidades": round(pe_unidades, 2),
                "dinero": round(pe_dinero, 2),
                "costos_fijos_totales": costos_fijos_totales,
                "margen_contribucion": margen_contribucion,
                "mensaje": f"Necesitas vender {round(pe_unidades)} unidades para cubrir tus costos fijos"
            }
        }
        
    except Exception as e:
        logger.error(f" Error calculando punto de equilibrio: {e}")
        return {"status": "error", "message": str(e)}


def analizar_rentabilidad(ventas_mensuales: float, costo_ventas: float) -> Dict[str, Any]:
    """
    Analiza la rentabilidad del negocio del usuario actual.
    
    Args:
        ventas_mensuales: Total de ventas en el mes
        costo_ventas: Costo total de las ventas (costos directos)
        
    Returns:
        Análisis detallado de rentabilidad con recomendaciones
    """
    user_id = get_user_context()
    
    try:
        datos = obtener_datos_financieros()
        
        costos_fijos = sum(item.get('valor', 0) for item in datos.get('indirect_fixed_costs', []))
        costos_variables = sum(item.get('valor', 0) for item in datos.get('indirect_variable_costs', []))
        
        utilidad_bruta = ventas_mensuales - costo_ventas
        margen_bruto = (utilidad_bruta / ventas_mensuales * 100) if ventas_mensuales > 0 else 0
        
        utilidad_operativa = utilidad_bruta - costos_fijos - costos_variables
        margen_operativo = (utilidad_operativa / ventas_mensuales * 100) if ventas_mensuales > 0 else 0
        
        estado = "rentable" if utilidad_operativa > 0 else ("punto_equilibrio" if utilidad_operativa == 0 else "perdida")
        
        return {
            "status": "success",
            "analisis": {
                "ventas": ventas_mensuales,
                "costo_ventas": costo_ventas,
                "utilidad_bruta": round(utilidad_bruta, 2),
                "margen_bruto_porcentaje": round(margen_bruto, 2),
                "costos_fijos": costos_fijos,
                "costos_variables": costos_variables,
                "utilidad_operativa": round(utilidad_operativa, 2),
                "margen_operativo_porcentaje": round(margen_operativo, 2),
                "estado": estado
            }
        }
        
    except Exception as e:
        logger.error(f" Error analizando rentabilidad: {e}")
        return {"status": "error", "message": str(e)}


def proyectar_ventas(ventas_actuales: float, crecimiento_porcentaje: float, meses: int) -> Dict[str, Any]:
    """
    Proyecta ventas futuras basándose en un crecimiento estimado.
    
    Args:
        ventas_actuales: Ventas del mes actual
        crecimiento_porcentaje: Porcentaje de crecimiento esperado mensual
        meses: Número de meses a proyectar
        
    Returns:
        Proyección de ventas mes a mes
    """
    try:
        proyeccion = []
        venta_proyectada = ventas_actuales
        
        for mes in range(1, meses + 1):
            venta_proyectada = venta_proyectada * (1 + crecimiento_porcentaje / 100)
            proyeccion.append({
                "mes": mes,
                "venta_proyectada": round(venta_proyectada, 2)
            })
        
        return {
            "status": "success",
            "proyeccion": proyeccion,
            "total_proyectado": round(sum(p["venta_proyectada"] for p in proyeccion), 2)
        }
        
    except Exception as e:
        logger.error(f" Error proyectando ventas: {e}")
        return {"status": "error", "message": str(e)}


obtener_datos_financieros_tool = FunctionTool(obtener_datos_financieros)
calcular_punto_equilibrio_tool = FunctionTool(calcular_punto_equilibrio)
analizar_rentabilidad_tool = FunctionTool(analizar_rentabilidad)
proyectar_ventas_tool = FunctionTool(proyectar_ventas)