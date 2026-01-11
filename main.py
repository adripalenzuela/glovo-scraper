import time
import pandas as pd
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

def main():
    # 1. Configuración Headless
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    url = "https://glovoapp.com/es/es/valladolid/categories/comida_1"
    datos = []

    try:
        driver.get(url)
        time.sleep(5)
        
        # Hacemos scroll profundo para cargar bastantes tiendas
        driver.execute_script("window.scrollTo(0, 2500);")
        time.sleep(3)

        # Buscamos las tarjetas
        tiendas = driver.find_elements(By.CSS_SELECTOR, "div[data-test-id='store-card']")
        # Fallback por si cambia el selector principal
        if not tiendas:
             tiendas = driver.find_elements(By.CSS_SELECTOR, "a[href*='/es/es/valladolid/']")

        print(f"Analizando {len(tiendas)} tiendas...")

        fecha_hoy = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        for tienda in tiendas:
            try:
                texto_completo = tienda.text
                lineas = texto_completo.split('\n')
                
                # --- CORRECCIÓN NOMBRE ---
                # Intentamos buscar el elemento H3 que suele ser el título en Glovo
                try:
                    nombre = tienda.find_element(By.TAG_NAME, "h3").text
                except:
                    # Si falla, usamos heurística: la primera línea que NO sea oferta ni tiempo
                    nombre = "Desconocido"
                    for l in lineas:
                        if len(l) > 3 and "%" not in l and "min" not in l:
                            nombre = l
                            break
                
                # --- CORRECCIÓN OFERTAS ---
                ofertas_encontradas = []
                for linea in lineas:
                    linea_low = linea.lower()
                    
                    # Lógica estricta para separar Ofertas de Valoraciones
                    es_descuento = "-" in linea and "%" in linea # Ej: -20% (Tiene menos y porciento)
                    es_2x1 = "2x1" in linea_low
                    es_gratis = "entrega gratis" in linea_low
                    
                    # Filtramos lo que NO queremos (valoraciones como 97% o (500))
                    es_valoracion = "(" in linea or ( "%" in linea and "-" not in linea and "dto" not in linea_low)

                    if (es_descuento or es_2x1 or es_gratis) and not es_valoracion:
                        ofertas_encontradas.append(linea)

                if ofertas_encontradas:
                    # Guardamos una fila por cada oferta encontrada en ese restaurante
                    for off in list(set(ofertas_encontradas)): # set para quitar duplicados
                        datos.append({
                            "Fecha": fecha_hoy,
                            "Restaurante": nombre,
                            "Oferta": off
                        })

            except Exception as e:
                continue

    except Exception as e:
        print(f"Error global: {e}")
    finally:
        driver.quit()

    # Guardado
    if datos:
        df = pd.DataFrame(datos)
        archivo = "historial_ofertas.csv"
        
        try:
            pd.read_csv(archivo)
            existe = True
        except FileNotFoundError:
            existe = False

        # Guardamos sin índice numérico y en modo append
        df.to_csv(archivo, mode='a', header=not existe, index=False)
        print(f"GUARDADO: {len(datos)} ofertas nuevas.")
    else:
        print("No se encontraron ofertas válidas hoy.")

if __name__ == "__main__":
    main()
