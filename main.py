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
    # Usamos un tamaño de ventana grande para que quepan más elementos al cargar
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    url = "https://glovoapp.com/es/es/valladolid/categories/comida_1"
    datos = []

    try:
        print(f"Abriendo: {url}")
        driver.get(url)
        time.sleep(3) # Espera inicial
        
        # --- SECCIÓN DE SCROLL INFINITO MEJORADA ---
        print("Iniciando scroll para cargar todos los restaurantes...")
        
        last_height = driver.execute_script("return document.body.scrollHeight")
        scroll_attempts = 0
        max_scrolls = 60 # Límite de seguridad para que no se quede colgado eternamente
        
        while scroll_attempts < max_scrolls:
            # Bajar hasta el fondo de la página
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            
            # Esperar a que carguen los nuevos elementos (importante no bajar esto de 2 seg)
            time.sleep(2)
            
            # Calcular nueva altura
            new_height = driver.execute_script("return document.body.scrollHeight")
            
            # Si la altura no ha cambiado, hemos llegado al final
            if new_height == last_height:
                # Intento extra de espera por si acaso internet va lento
                time.sleep(2)
                new_height = driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    print("Fin del scroll: parece que hemos llegado al final.")
                    break
            
            last_height = new_height
            scroll_attempts += 1
            # Feedback para saber que sigue vivo
            if scroll_attempts % 5 == 0:
                print(f"Scroll nro {scroll_attempts}...")

        # ---------------------------------------------

        # Buscamos las tarjetas después de haber cargado todo
        tiendas = driver.find_elements(By.CSS_SELECTOR, "div[data-test-id='store-card']")
        # Fallback
        if not tiendas:
             tiendas = driver.find_elements(By.CSS_SELECTOR, "a[href*='/es/es/valladolid/']")

        print(f"Analizando {len(tiendas)} tiendas encontradas...")

        fecha_hoy = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        for tienda in tiendas:
            try:
                texto_completo = tienda.text
                lineas = texto_completo.split('\n')
                
                # Extracción nombre (busca H3 o usa heurística)
                try:
                    nombre = tienda.find_element(By.TAG_NAME, "h3").text
                except:
                    nombre = "Desconocido"
                    for l in lineas:
                        if len(l) > 3 and "%" not in l and "min" not in l:
                            nombre = l
                            break
                
                # Extracción ofertas
                ofertas_encontradas = []
                for linea in lineas:
                    linea_low = linea.lower()
                    
                    es_descuento = "-" in linea and "%" in linea # Ej: -20%
                    es_2x1 = "2x1" in linea_low
                    es_gratis = "entrega gratis" in linea_low
                    
                    # Filtro estricto para evitar valoraciones (ej: 97%)
                    es_valoracion = "(" in linea or ( "%" in linea and "-" not in linea and "dto" not in linea_low)

                    if (es_descuento or es_2x1 or es_gratis) and not es_valoracion:
                        ofertas_encontradas.append(linea)

                if ofertas_encontradas:
                    for off in list(set(ofertas_encontradas)):
                        datos.append({
                            "Fecha": fecha_hoy,
                            "Restaurante": nombre,
                            "Oferta": off
                        })

            except Exception:
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

        df.to_csv(archivo, mode='a', header=not existe, index=False)
        print(f"GUARDADO: {len(datos)} ofertas nuevas en el archivo.")
    else:
        print("No se encontraron ofertas válidas hoy.")

if __name__ == "__main__":
    main()
