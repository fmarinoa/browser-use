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
llm = ChatGoogleGenerativeAI(model='gemini-2.0-flash', api_key=SecretStr(api_key))


# Create agent with the model
browser = Browser(
    config=BrowserConfig(
        headless=True,
        disable_security=True,
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
Genera una tabla comparativa en formato JSON con los 5 mejores precios del iPhone 16 en Lima, Perú, 
considerando las siguientes especificaciones:
- Precios en soles peruanos (PEN)
- Tienda
- Especificar capacidad (128GB, 256GB, etc.) y color cuando esté disponible
- Incluir precios con y sin descuentos (si aplica)
""",
    llm=llm,
    use_vision=True,              # Enable vision capabilities
    browser_context=context,
    
)


async def main():
    try:
        ruta = './report/result/report.json'
        history = await agent.run()
        history.save_to_file(ruta)
        generate_reporte(ruta)

        if history.has_errors():
            print("Execution completed with errors")
            return 1  # Indica error
        
        print("Execution completed successfully")
        return 0  # Indica éxito

    except Exception as e:
        print(f"Error during execution: {e}")
        return 1  # Indica error

    finally:
        await browser.close()  # Ensure browser is properly closed

if __name__ == '__main__':
    try:
        exit_code = asyncio.run(main())
    except Exception as e:
        print(f"Unexpected error: {e}")
        exit_code = 1
    sys.exit(exit_code)