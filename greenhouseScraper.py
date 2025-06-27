from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# --- Configuración del WebDriver ---
# Asegurate de que el path al chromedriver sea correcto
# Si lo tenes en la misma carpeta que el script, puedes usar solo el nombre
# Si no, especifica la ruta completa: r"C:\ruta\a\tu\chromedriver.exe"
CHROMEDRIVER_PATH = "./chromedriver.exe" # O "./chromedriver" para macOS/Linux

# Configurar opciones de Chrome (opcional pero recomendado)
chrome_options = Options()
chrome_options.add_argument("--headless")  # Ejecutar en modo sin cabeza (sin abrir la ventana del navegador)
chrome_options.add_argument("--disable-gpu") # Necesario para --headless en algunos sistemas
chrome_options.add_argument("--no-sandbox") # Necesario para --headless en algunos entornos Linux
chrome_options.add_argument("--window-size=1920,1080") # Definir tamaño de la ventana (útil para headless)
chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36") # Cambiar el User-Agent

service = Service(CHROMEDRIVER_PATH)

# Inicializar el navegador
try:
    driver = webdriver.Chrome(service=service, options=chrome_options)
    print("Navegador Chrome inicializado correctamente.")
except Exception as e:
    print(f"Error al inicializar el navegador: {e}")
    exit() # Salir si el navegador no se puede iniciar

# --- URL del sitio Greenhouse (ejemplo) ---
# Puedes buscar "Greenhouse careers" de alguna empresa que te interese para encontrar su URL
# Ejemplo: https://boards.greenhouse.io/spacex
# Reemplaza con la URL real que quieres scrapear
TARGET_URL = "https://boards.greenhouse.io/datadog"

print(f"Navegando a: {TARGET_URL}")
driver.get(TARGET_URL)

# --- Esperar a que la página cargue (espera implícita o explícita) ---
# La espera explícita es más robusta porque espera por un elemento específico.
# Aquí esperamos a que aparezca un elemento que contenga los listados de trabajo.
# Puedes inspeccionar la página para encontrar un selector CSS o XPath adecuado.
# Common elements on Greenhouse: div.opening, a.job-link, h4.job-title
try:
    # Esperar hasta que al menos un enlace de trabajo sea visible
    # WebDriverWait(driver, 10) significa que esperará hasta 10 segundos
    # EC.presence_of_element_located((By.CSS_SELECTOR, "a.job-link")) espera que el elemento esté presente en el DOM
    # EC.visibility_of_element_located((By.CSS_SELECTOR, "a.job-link")) espera que el elemento sea visible en la página
    WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "div.opening"))
    )
    print("Elementos de trabajo cargados.")
except TimeoutException:
    print("Tiempo de espera agotado. Los elementos de trabajo no aparecieron.")
    driver.quit()
    exit()
except NoSuchElementException:
    print("No se encontró el selector CSS especificado para los elementos de trabajo.")
    driver.quit()
    exit()

# --- Extraer información ---
job_listings = driver.find_elements(By.CSS_SELECTOR, "div.opening") # O "div.job-row" o similar

if not job_listings:
    print("No se encontraron listados de trabajo con el selector 'div.opening'.")
    print("Intenta inspeccionar el HTML de la página para encontrar el selector correcto.")
else:
    print(f"Se encontraron {len(job_listings)} puestos de trabajo.")
    for job in job_listings:
        try:
            # En Greenhouse, los títulos suelen estar en un <a> o <h4> dentro de div.opening
            title_element = job.find_element(By.CSS_SELECTOR, "a.job-link, h4.job-title")
            title = title_element.text.strip()
            link = title_element.get_attribute("href")

            # La ubicación a veces está en un <span> o <div class="location">
            try:
                location_element = job.find_element(By.CSS_SELECTOR, "span.location, div.location")
                location = location_element.text.strip()
            except NoSuchElementException:
                location = "Ubicación no encontrada"

            print(f"Título: {title}")
            print(f"Link: {link}")
            print(f"Ubicación: {location}")
            print("-" * 30)

        except NoSuchElementException:
            print("No se pudieron encontrar el título o el enlace para un puesto.")
        except Exception as e:
            print(f"Error al procesar un puesto: {e}")

# --- Cerrar el navegador ---
driver.quit()
print("Navegador cerrado.")
