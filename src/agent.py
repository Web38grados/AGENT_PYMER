from google.adk.agents import Agent
from src.tools import ALL_TOOLS
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Cargar system prompt
prompt_path = os.path.join(
    os.path.dirname(__file__), 
    "prompts", 
    "system_prompt.txt"
)

try:
    with open(prompt_path, "r", encoding="utf-8") as f:
        instruccion = f.read()
except FileNotFoundError:
    logger.warning(f" No se encontró {prompt_path}, usando prompt por defecto")

root_agent = Agent(
    name="asesor_pymer",
    model="gemini-2.0-flash-exp",
    instruction=instruccion,
    tools=ALL_TOOLS,
)

logger.info(" Agente PYMER inicializado correctamente")



if __name__ == "__main__":
    print(" Agente PYMER listo para usar")
    print("Para probarlo, ejecuta: adk web")