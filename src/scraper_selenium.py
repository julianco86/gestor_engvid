# ==========================================
# 1. IMPORTACIÓN DE LIBRERÍAS
# ==========================================

import csv  # Para crear y escribir archivos Excel/CSV.
import os   # <--- ¡NUEVO! Librería del Sistema Operativo. Nos permite navegar por carpetas.
import time # Para hacer pausas si es necesario.

# Importaciones de Selenium (La herramienta de automatización web)
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# ==========================================
# 2. CONFIGURACIÓN DEL SISTEMA DE RUTAS (NUEVO)
# ==========================================
# Objetivo: Que el código sepa guardar el archivo en la carpeta 'data', 
# sin importar desde dónde ejecutes este script.

# A. ¿Dónde está este archivo .py ahora mismo?
# __file__: Es una variable mágica que guarda el nombre de este script.
# abspath: Obtiene la ruta completa (ej: C:\Users\TuUsuario\Proyecto\src\script.py)
# dirname: Se queda solo con la carpeta (ej: C:\Users\TuUsuario\Proyecto\src)
ruta_carpeta_src = os.path.dirname(os.path.abspath(__file__))

# B. ¿Dónde está la carpeta principal del proyecto?
# Como estamos en 'src', necesitamos subir un nivel para ver las otras carpetas.
ruta_proyecto = os.path.dirname(ruta_carpeta_src) 

# C. Construimos la ruta final hacia la carpeta 'data'
# os.path.join: Une las partes usando la barra correcta (\ en Windows, / en Mac).
# Esto crea: C:\Users\TuUsuario\Proyecto\data\engvid_completo.csv
NOMBRE_ARCHIVO = 'engvid_completo.csv'
RUTA_FINAL_CSV = os.path.join(ruta_proyecto, 'data', NOMBRE_ARCHIVO)

print(f"📍 El script está en: {ruta_carpeta_src}")
print(f"📂 El archivo se guardará en: {RUTA_FINAL_CSV}")

# ==========================================
# 3. INICIO DEL NAVEGADOR
# ==========================================

print(f"🚀 Iniciando el navegador robotizado...")

# Opciones de Chrome
options = webdriver.ChromeOptions()
# options.add_argument('--headless') # Descomenta si NO quieres ver la ventana abierta.

# Iniciamos el driver (el control remoto de Chrome)
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# Lista vacía donde iremos guardando cada lección encontrada
datos_para_csv = []

# ==========================================
# 4. LÓGICA DE EXTRACCIÓN (SCRAPING)
# ==========================================

try: # Bloque TRY: Si algo falla aquí dentro, saltamos al bloque EXCEPT o FINALLY.
    
    # A. Cargar la página web
    url = "https://www.engvid.com/english-lessons/"
    driver.get(url)

    print("⏳ Esperando a que el JavaScript de la página cargue los videos...")
    
    # B. Espera Inteligente
    # Le decimos al robot: "Espera máximo 20 segundos hasta que veas aparecer
    # al menos un elemento con la clase 'lessonlinks_all_row'".
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.CLASS_NAME, "lessonlinks_all_row"))
    )

    # C. Capturar los elementos
    # Buscamos TODOS los bloques que tengan la clase de una tarjeta de video.
    todas_las_tarjetas = driver.find_elements(By.CLASS_NAME, "lessonlinks_all_row")
    
    total = len(todas_las_tarjetas)
    print(f"✅ ¡Éxito! Se encontraron {total} lecciones en total. Procesando...")

    # D. Bucle para procesar tarjeta por tarjeta
    # enumerate(..., 1) nos da la tarjeta y un contador 'i' que empieza en 1.
    for i, tarjeta in enumerate(todas_las_tarjetas, 1):
        try:
            # --- Extracción de Título ---
            # Buscamos la clase específica del título DENTRO de la tarjeta actual.
            titulo = tarjeta.find_element(By.CLASS_NAME, "lessonlinks_all_lessontitle").text
            
            # --- Extracción de Link ---
            # Buscamos el link y sacamos su atributo 'href' (la dirección web).
            link_elem = tarjeta.find_element(By.CLASS_NAME, "lessonlinks_all_lesson_link")
            link = link_elem.get_attribute("href")
            
            # --- Extracción de Detalles ---
            # Extraemos el texto de categorías y nivel.
            info = tarjeta.find_element(By.CLASS_NAME, "lessonlinks_all_category_list").text
            # Limpieza: Reemplazamos 'Enters' por barras y quitamos espacios extra.
            info_limpia = info.replace("\n", " | ").replace("•", "").strip()

            # --- Almacenamiento Temporal ---
            # Guardamos los datos limpios en nuestra lista principal
            datos_para_csv.append({
                "ID": i,
                "Titulo": titulo,
                "Detalles": info_limpia,
                "URL": link
            })
            
            # --- Monitor de Progreso ---
            # Cada 200 videos, imprimimos un aviso para saber que sigue trabajando.
            if i % 200 == 0:
                print(f"   ... procesando registro {i} de {total}")

        except Exception as e:
            # Si una tarjeta específica falla, mostramos error pero NO detenemos el programa.
            print(f"⚠️ Error leve leyendo la tarjeta #{i}")
            continue # Salta a la siguiente iteración del bucle

    # ==========================================
    # 5. GUARDADO DEL ARCHIVO (USANDO LA RUTA NUEVA)
    # ==========================================
    
    if datos_para_csv:
        print(f"\n💾 Guardando {len(datos_para_csv)} registros...")
        
        # Abrimos el archivo en la ruta RUTA_FINAL_CSV (la carpeta 'data').
        # 'w' = Write (Escribir/Sobrescribir).
        # encoding='utf-8-sig' = Formato correcto para tildes en Excel.
        with open(RUTA_FINAL_CSV, 'w', newline='', encoding='utf-8-sig') as archivo_csv:
            
            # Definimos los nombres de las columnas
            campos = ["ID", "Titulo", "Detalles", "URL"]
            
            # Creamos el escritor CSV
            writer = csv.DictWriter(archivo_csv, fieldnames=campos)
            
            # Escribimos los encabezados y luego todos los datos
            writer.writeheader()
            writer.writerows(datos_para_csv)
            
        print(f"🎉 ¡Misión Cumplida! Archivo guardado exitosamente en:")
        print(f"👉 {RUTA_FINAL_CSV}")
    else:
        print("⚠️ Alerta: No se encontraron datos para guardar.")

# ==========================================
# 6. CIERRE DE RECURSOS
# ==========================================
finally:
    # Este bloque se ejecuta SIEMPRE al final.
    print("\n🏁 Cerrando navegador y liberando memoria...")
    driver.quit()