import time
import pandas as pd
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

def main():
    # 1. Configuración Headless (Obligatoria para la nube)
    chrome_options = Options()
    chrome_options.add_argument("--headless") # Sin interfaz gráfica
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36")

    # Inicializar driver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    url = "https://glovoapp.com/es/es/valladolid/categories/comida_1"
    datos = []

    try:
        driver.get(url)
        time.sleep(5) # Espera carga inicial
        
        # Scroll para cargar más elementos
        driver.execute_script("window.scrollTo(0, 2000);")
        time.sleep(3)

        tiendas = driver.find_elements(By.CSS_SELECTOR, "div[data-test-id='store-card']")
        if not tiendas:
             tiendas = driver.find_elements(By.CSS_SELECTOR, "a[href*='/es/es/valladolid/']")

        print(f"Analizando {len(tiendas)} tiendas...")

        fecha_hoy = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        palabras_clave = ["%", "2x1", "gratis", "descuento"]

        for tienda in tiendas:
            try:
                texto = tienda.text
                lineas = texto.split('\n')
                nombre = lineas[0] if lineas else "Desconocido"
                
                # Buscar ofertas
                ofertas_detectadas = [linea for linea in lineas if any(p in linea.lower() for p in palabras_clave)]
                
                if ofertas_detectadas:
                    # Agregamos cada oferta como una fila
                    for oferta in ofertas_detectadas:
                        datos.append({
                            "Fecha": fecha_hoy,
                            "Restaurante": nombre,
                            "Oferta": oferta
                        })
            except:
                continue

    except Exception as e:
        print(f"Error: {e}")
    finally:
        driver.quit()

    # 2. Guardar en CSV (Excel)
    if datos:
        df = pd.DataFrame(datos)
        # mode='a' significa append (agregar al final sin borrar lo anterior)
        # header=False si el archivo ya existe para no repetir titulos
        archivo = "historial_ofertas.csv"
        
        try:
            pd.read_csv(archivo)
            existe = True
        except FileNotFoundError:
            existe = False

        df.to_csv(archivo, mode='a', header=not existe, index=False)
        print(f"Se guardaron {len(datos)} ofertas en {archivo}")
    else:
        print("No se encontraron ofertas hoy.")

if __name__ == "__main__":
    main()
