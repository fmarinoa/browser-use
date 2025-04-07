from langchain_google_genai import ChatGoogleGenerativeAI
from browser_use import Agent, Browser, BrowserConfig
from browser_use.browser.context import *
from report.reporte import generate_reporte
from pydantic import SecretStr
import os
import sys
import asyncio
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

# Initialize the model
llm = ChatGoogleGenerativeAI(model='gemini-1.5-flash', api_key=SecretStr(api_key))


# Create agent with the model
browser = Browser(
    config=BrowserConfig(
        headless=False,
        disable_security=False,
#        chrome_instance_path="/usr/bin/google-chrome",
#        chrome_instance_path="/usr/bin/brave-browser",  
    )
)
context = BrowserContext(
    browser=browser, 
    config = BrowserContextConfig(
        browser_window_size={'width': 1360, 'height': 700},
        highlight_elements=True,
        viewport_expansion=500,
        save_recording_path="./report/videos_result",
        no_viewport=False
        
    )
)


agent = Agent(
    task = """
Actúa como un QA automatizado y realiza pruebas de regresión (sanity check) en la página **riobuenoshop.com**. Sigue este flujo:

1. **Flujo de Compra**:  
   - Agrega un producto seleccionando tallas disponibles(si es necesario).  
   - Accede al carrito

2. **Checkout**:  
   - Completa el formulario con **data de prueba** (campos obligatorios):  
     - Asegurate de llenar los campos del formulario
       - ejemplo:  Nombre, Apellidos, Whatsapp, DNI, dirección, teléfono, email válido, Tipo de entrega, Distrito, .  
     - Rellena TODOS los campos
   - Usa el método de pago **"Contra Entrega"**.  
   - finaliza la Compra (Obligatorio)
      - Valida que:  
      - La orden se genere correctamente (pantalla de confirmación + email ).  


3. **Reporte**:  
   - Genera un resumen en español con:  
     - Pasos ejecutados.  
     - Errores encontrados (si aplica).  
     - Evidencia de éxito (ej: "Orden #123 creada correctamente").  
""",
    llm=llm,
    use_vision=True,              # Enable vision capabilities
    browser_context=context,
    
)


async def main():
    try:
        ruta='./report/result/report.json'
        history = await agent.run()
        history.save_to_file(ruta)
        generate_reporte(ruta)
    except Exception as e:
        print(f"Error during execution: {e}")
    finally:
        await browser.close()  # Ensure browser is properly closed

if __name__ == '__main__':
	asyncio.run(main())