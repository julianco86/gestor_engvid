# --- 1. IMPORTACIÓN DE LIBRERÍAS ---
# 'csv': Librería nativa de Python para leer y escribir archivos separados por comas (Excel básico).
import csv 
# 'selenium': La herramienta principal que nos permite controlar un navegador web.
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
# 'WebDriverWait' y 'EC': Herramientas para hacer "esperas inteligentes" (explicado abajo).
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
# 'ChromeDriverManager': Una maravilla que descarga y actualiza el driver de Chrome automáticamente 
# para que no tengas que hacerlo manualmente.
from webdriver_manager.chrome import ChromeDriverManager

# --- 2. CONFIGURACIÓN INICIAL ---
NOMBRE_ARCHIVO = 'engvid_completo.csv'

print(f"🚀 Iniciando extracción TOTAL...")

# Configuración del navegador (Chrome Options)
options = webdriver.ChromeOptions()
# options.add_argument('--headless') 
# ^ Si descomentas la línea de arriba, el navegador funciona "sin cabeza" (invisible), 
# lo cual es más rápido, pero no ves lo que pasa. Para aprender, mejor dejarlo visible.

# Aquí nace el 'driver'. Es tu "control remoto" para manejar Chrome desde Python.
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

datos_para_csv = []

# --- 3. BLOQUE TRY / FINALLY (Manejo de Errores) ---
# El 'try' le dice a Python: "Intenta ejecutar este bloque riesgoso".
# Si algo falla, saltará al bloque 'except' (si lo hubiera) o directo al 'finally'.
try:
    url = "https://www.engvid.com/english-lessons/"
    
    # Ordenamos al driver ir a la página. Es como escribir la URL y dar Enter.
    driver.get(url)

    print("⏳ Esperando que el JavaScript cargue todos los videos...")
    
    # --- 4. LA ESPERA INTELIGENTE (Clave del Éxito) ---
    # No usamos time.sleep(20) porque es tonto esperar si la página carga en 2 segundos.
    # WebDriverWait espera HASTA 20 segundos, pero si el elemento aparece antes, continúa de inmediato.
    # Estamos vigilando que aparezca al menos un elemento con la clase 'lessonlinks_all_row'.
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.CLASS_NAME, "lessonlinks_all_row"))
    )

    # --- 5. RECOLECCIÓN DE ELEMENTOS ---
    # Buscamos TODOS los elementos que coincidan con la clase. 
    # Esto devuelve una lista de objetos Selenium (las "tarjetas" de los videos).
    todas_las_tarjetas = driver.find_elements(By.CLASS_NAME, "lessonlinks_all_row")
    
    total = len(todas_las_tarjetas)
    print(f"✅ ¡Se encontraron {total} lecciones en total! Procesando...")

    # --- 6. EL BUCLE DE EXTRACCIÓN ---
    # 'enumerate' es genial: nos da la tarjeta y automáticamente lleva un contador ('i') empezando en 1.
    for i, tarjeta in enumerate(todas_las_tarjetas, 1):
        try:
            # .text: Extrae el texto visible que ve el usuario en pantalla.
            titulo = tarjeta.find_element(By.CLASS_NAME, "lessonlinks_all_lessontitle").text
            
            # .get_attribute("href"): Extrae atributos ocultos del HTML. 
            # Aquí sacamos la URL a la que apunta el enlace.
            link_elem = tarjeta.find_element(By.CLASS_NAME, "lessonlinks_all_lesson_link")
            link = link_elem.get_attribute("href")
            
            # Limpieza de datos:
            # 1. Sacamos el texto crudo.
            # 2. .replace("\n", " | "): Convertimos los 'Enter' en barras para que no rompan el CSV.
            # 3. .strip(): Elimina espacios vacíos al principio y al final.
            info = tarjeta.find_element(By.CLASS_NAME, "lessonlinks_all_category_list").text
            info_limpia = info.replace("\n", " | ").replace("•", "").strip()

            # Guardamos los datos limpios en un diccionario temporal
            datos_para_csv.append({
                "ID": i,
                "Titulo": titulo,
                "Detalles": info_limpia,
                "URL": link
            })
            
            # Un "log" para que sepas que el programa no se congeló
            if i % 200 == 0:
                print(f"   ... procesando registro {i} de {total}")

        except Exception as e:
            # Si una tarjeta específica falla, imprimimos el error pero 'continue' hace que 
            # el bucle salte a la siguiente tarjeta sin detener todo el programa.
            print(f"⚠️ Error leve en tarjeta #{i}")
            continue

    # --- 7. GUARDADO EN DISCO ---
    if datos_para_csv:
        print(f"\n💾 Guardando {len(datos_para_csv)} registros en '{NOMBRE_ARCHIVO}'...")
        
        # 'w': Modo escritura (write). Si el archivo existe, lo sobrescribe.
        # encoding='utf-8-sig': CRUCIAL para Excel en español. Permite que se vean tildes y ñ correctamente.
        with open(NOMBRE_ARCHIVO, 'w', newline='', encoding='utf-8-sig') as archivo_csv:
            campos = ["ID", "Titulo", "Detalles", "URL"]
            
            # DictWriter conecta las llaves de tu diccionario con las columnas del Excel.
            writer = csv.DictWriter(archivo_csv, fieldnames=campos)
            
            writer.writeheader()       # Escribe la fila 1 (ID, Titulo...)
            writer.writerows(datos_para_csv) # Escribe las 2500 filas de datos
            
        print(f"🎉 ¡Extracción completa finalizada! Revisa tu archivo.")

# --- 8. LIMPIEZA FINAL ---
# El bloque 'finally' se ejecuta SIEMPRE, haya error o no.
finally:
    # driver.quit(): Cierra todas las ventanas y mata el proceso de Chrome. 
    # Si no haces esto, tu memoria RAM se llenará de procesos "zombie" de Chrome.
    driver.quit()