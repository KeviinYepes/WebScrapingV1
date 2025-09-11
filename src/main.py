from selenium.webdriver import Chrome
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait as Wait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    ElementClickInterceptedException,
    WebDriverException,
    StaleElementReferenceException
)
import time
import random
import sys
import traceback
import os
from datetime import datetime
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('siras_automation.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Datos privados - considera usar variables de entorno en producción
PRIVATE_DATA = {
    "email": "dirimagenes@vallesaludips.com",
    "password": "SE0uJ9dC",
    "param": "760010732306",
    "fecha": "1092025",
}

<<<<<<< HEAD
class SirasAutomation:
    def __init__(self, headless=False):
        self.driver = None
        self.setup_directories()
        self.setup_driver(headless)
        
    def setup_directories(self):
        """Configurar carpeta de descargas"""
        self.descargas_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "descargasPDF")
        if not os.path.exists(self.descargas_dir):
            os.makedirs(self.descargas_dir)
            logger.info(f"Carpeta de descargas creada: {self.descargas_dir}")
=======
# Simula escritura humana con retrasos aleatorios entre caracteres
def human_typing(element, text, delay_range=(0.05, 0.2)):
    for char in text:
        element.send_keys(char)
        time.sleep(random.uniform(*delay_range))

def procesar_reporte():
        button_descarga = Wait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "DocumentViewer_Splitter_Toolbar_Menu_DXI9_T"))
        )
        button_descarga.click()

        regresar= Wait(driver,10).until(
            EC.element_to_be_clickable((By.ID,"btnVolver"))
        )
        regresar.click()


def obtener_elementos_por_pagina(driver):
    try:
        # Espera a que la tabla cargue
        Wait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//table[contains(@id, 'gridResumidas')]"))
        )
        
        # Encontrar todas las filas de datos
        filas = driver.find_elements(By.XPATH, "//tr[contains(@id, 'gridResumidas_DXDataRow')]")
        
        elementos = []
        
        for i, fila in enumerate(filas):
            try:
                # Extraer información de cada fila
                celdas = fila.find_elements(By.TAG_NAME, "td")
                
                if len(celdas) >= 8:  
                    elemento_info = {
                        'tipo_id': celdas[0].text.strip(),
                        'identificacion': celdas[1].text.strip(),
                        'primer_apellido': celdas[2].text.strip(),
                        'segundo_apellido': celdas[3].text.strip(),
                        'primer_nombre': celdas[4].text.strip(),
                        'segundo_nombre': celdas[5].text.strip(),
                        'tipo_ingreso': celdas[6].text.strip(),
                        'clasificacion': celdas[7].text.strip(),
                        'indice_fila': i
                    }
                    elementos.append(elemento_info)
                    
            except Exception as e:
                print(f"Error extrayendo datos de fila {i}: {str(e)}")
                continue
        
        print(f"Encontrados {len(elementos)} elementos en esta página")
        return elementos
        
    except Exception as e:
        print(f"Error obteniendo elementos: {str(e)}")
        return []

def procesar_todas_las_paginas(driver):
    pagina_actual, total_paginas, total_elementos = total_pages(driver)
>>>>>>> 9d4f6b045d525cb2221482cab7a0b55f08cf4cb5
    
    def setup_driver(self, headless=False):
        """Configurar el driver de Chrome con opciones optimizadas"""
        try:
            options = webdriver.ChromeOptions()
            
            # Configurar descargas automáticas
            prefs = {
                "download.default_directory": self.descargas_dir,
                "download.prompt_for_download": False,
                "download.directory_upgrade": True,
                "safebrowsing.enabled": True,
                "plugins.always_open_pdf_externally": True,
                "profile.default_content_settings.popups": 0,
                "profile.default_content_setting_values.automatic_downloads": 1
            }
            options.add_experimental_option("prefs", prefs)
            
            # Opciones adicionales para estabilidad
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-gpu")
            options.add_argument("--window-size=1920,1080")
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            
            if headless:
                options.add_argument("--headless")
            
            service = Service(ChromeDriverManager().install())
            self.driver = Chrome(service=service, options=options)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            logger.info("Driver configurado exitosamente")
            
        except Exception as e:
            logger.error(f"Error configurando driver: {str(e)}")
            raise
    
    def human_typing(self, element, text, delay_range=(0.05, 0.15)):
        """Simular escritura humana"""
        element.clear()
        for char in text:
            element.send_keys(char)
            time.sleep(random.uniform(*delay_range))
    
    def wait_for_element(self, by, selector, timeout=15, clickable=True):
        """Esperar por un elemento con manejo mejorado de errores"""
        try:
            if clickable:
                return Wait(self.driver, timeout).until(
                    EC.element_to_be_clickable((by, selector))
                )
            else:
                return Wait(self.driver, timeout).until(
                    EC.presence_of_element_located((by, selector))
                )
        except TimeoutException:
            logger.error(f"Elemento no encontrado: {selector}")
            raise
    
    def safe_click(self, element, use_js=False):
        """Hacer clic de forma segura con reintentos"""
        max_intentos = 3
        for intento in range(max_intentos):
            try:
                if use_js:
                    self.driver.execute_script("arguments[0].click();", element)
                else:
                    # Scroll al elemento y hacer clic
                    self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
                    time.sleep(0.5)
                    element.click()
                return True
                
            except (ElementClickInterceptedException, StaleElementReferenceException) as e:
                logger.warning(f"Error en intento {intento + 1}: {str(e)}")
                if intento < max_intentos - 1:
                    time.sleep(1)
                else:
                    try:
                        # Último intento con JavaScript
                        self.driver.execute_script("arguments[0].click();", element)
                        return True
                    except:
                        logger.error("No se pudo hacer clic en el elemento")
                        return False
        return False
    
    def verificar_descarga_completada(self, timeout=60):
        """Verificar que la descarga se haya completado con timeout aumentado"""
        inicio = time.time()
        archivos_iniciales = set([f for f in os.listdir(self.descargas_dir) 
                                if f.endswith('.pdf') and not f.endswith('.crdownload')])
        
        while time.time() - inicio < timeout:
            try:
                archivos_actuales = set([f for f in os.listdir(self.descargas_dir) 
                                       if f.endswith('.pdf') and not f.endswith('.crdownload')])
                archivos_temporales = [f for f in os.listdir(self.descargas_dir) 
                                     if f.endswith('.crdownload')]
                
                # Si hay archivos temporales, esperar
                if archivos_temporales:
                    logger.info("Descarga en progreso...")
                    time.sleep(3)
                    continue
                
                nuevos_archivos = archivos_actuales - archivos_iniciales
                
                if nuevos_archivos:
                    nuevo_archivo = list(nuevos_archivos)[0]
                    archivo_path = os.path.join(self.descargas_dir, nuevo_archivo)
                    
                    # Verificar que el archivo existe y tiene contenido
                    if os.path.exists(archivo_path) and os.path.getsize(archivo_path) > 1000:
                        logger.info(f"Descarga completada: {nuevo_archivo}")
                        return archivo_path
                        
                time.sleep(2)
                
            except Exception as e:
                logger.error(f"Error verificando descarga: {str(e)}")
                time.sleep(2)
                
        logger.error("Timeout esperando descarga")
        return None
    
    def login(self, credentials):
        """Realizar login con manejo mejorado de errores"""
        try:
            logger.info("Iniciando login...")
            self.driver.get("https://www.siras.com.co/siras/Seguridad/Login?Modo=1")
            
            # Esperar a que la página cargue completamente
            time.sleep(3)
            
            username_input = self.wait_for_element(By.ID, "Email_I")
            username_input.clear()
            username_input.send_keys(credentials["email"])
            
            password_input = self.wait_for_element(By.ID, "Password_I")
            password_input.clear()
            password_input.send_keys(credentials["password"])
            
            login_button = self.wait_for_element(By.ID, "btnIngresar")
            self.safe_click(login_button)
            
            # Esperar a que el login sea exitoso
            time.sleep(5)
            logger.info("Login exitoso")
            
        except Exception as e:
            logger.error(f"Error durante login: {str(e)}")
            raise
    
    def select_options(self, credentials):
        """Seleccionar opciones y configurar filtros"""
        try:
            logger.info("Configurando opciones...")
            
            # Código de habilitación
            codigo_input = self.wait_for_element(By.ID, "CodigoHabilitacion_I")
            self.human_typing(codigo_input, credentials["param"])
            
            # Botón prestador encontrado
            prestador_button = self.wait_for_element(By.XPATH, "//span[contains(text(), 'Ingresar con el Prestador Encontrado')]")
            self.safe_click(prestador_button)
            self.safe_click(prestador_button)
            time.sleep(3)
            
            # Navbar consultas
            navbar_consultas = self.wait_for_element(By.ID, "menuNoAuth_DXI2_T")
            self.safe_click(navbar_consultas)
            
            # Opción lista resumida
            lista_resumida = self.wait_for_element(By.XPATH, "//span[contains(text(), 'LISTA RESUMIDA DE ATENCIONES')]")
            self.safe_click(lista_resumida)
            time.sleep(3)
            
            # Configurar fechas
            fecha_inicial = self.wait_for_element(By.ID, "FechaInicialFiltro_I")
            fecha_inicial.click()
            time.sleep(1)
            self.human_typing(fecha_inicial, credentials["fecha"])
            
            fecha_final = self.wait_for_element(By.ID, "FechaFinalFiltro_I")
            fecha_final.click()
            time.sleep(1)
            self.human_typing(fecha_final, credentials["fecha"])
            
            # Consultar
            consultar_button = self.wait_for_element(By.XPATH, "//span[contains(text(), 'Consultar')]")
            self.safe_click(consultar_button)
            
            # Esperar a que se carguen los resultados
            time.sleep(10)
            logger.info("Opciones configuradas exitosamente")
            
        except Exception as e:
            logger.error(f"Error configurando opciones: {str(e)}")
            raise
    
    def obtener_info_paginacion(self):
        """Obtener información de paginación"""
        try:
            paginacion = self.wait_for_element(By.CLASS_NAME, "dxp-summary", clickable=False)
            texto = paginacion.text
            logger.info(f"Texto paginación: {texto}")
            
            # Parsear texto de paginación (ej: "1 of 3 (25)")
            partes = texto.split()
            pagina_actual = int(partes[1])
            total_paginas = int(partes[3])
            total_elementos = int(partes[4].replace('(', '').replace(')', ''))
            
            return pagina_actual, total_paginas, total_elementos
            
        except Exception as e:
            logger.error(f"Error obteniendo paginación: {str(e)}")
            return 1, 1, 0
    
    def obtener_elementos_pagina(self):
        """Obtener elementos de la página actual con manejo robusto"""
        try:
            # Esperar a que la tabla esté presente
            self.wait_for_element(By.XPATH, "//table[contains(@id, 'gridResumidas')]", clickable=False)
            time.sleep(3)
            
            filas = self.driver.find_elements(By.XPATH, "//tr[contains(@id, 'gridResumidas_DXDataRow')]")
            elementos = []
            
            for i, fila in enumerate(filas):
                try:
                    celdas = fila.find_elements(By.TAG_NAME, "td")
                    
                    if len(celdas) >= 28:  # Verificar que hay suficientes celdas
                        elemento_info = {
                            'tipo_id': celdas[1].text.strip(),
                            'identificacion': celdas[2].text.strip(),
                            'primer_apellido': celdas[3].text.strip(),
                            'segundo_apellido': celdas[4].text.strip(),
                            'primer_nombre': celdas[5].text.strip(),
                            'segundo_nombre': celdas[6].text.strip(),
                            'tipo_ingreso': celdas[7].text.strip(),
                            'clasificacion': celdas[8].text.strip(),
                            'no_radicado': celdas[27].text.strip() if len(celdas) > 27 else '',
                            'indice_fila': i,
                            'fila_element': fila  # Guardar referencia al elemento
                        }
                        elementos.append(elemento_info)
                        logger.info(f"Extraído: {elemento_info['primer_nombre']} {elemento_info['primer_apellido']} - ID: {elemento_info['identificacion']}")
                        
                except Exception as e:
                    logger.warning(f"Error procesando fila {i}: {str(e)}")
                    continue
            
            logger.info(f"Total elementos encontrados: {len(elementos)}")
            return elementos
            
        except Exception as e:
            logger.error(f"Error obteniendo elementos: {str(e)}")
            return []
    
    def hacer_clic_ver_reporte(self, elemento):
        """Hacer clic en VER REPORTE con múltiples estrategias"""
        estrategias = [
            (By.XPATH, f"//tr[contains(@id, 'DXDataRow{elemento['indice_fila']}')]//span[contains(text(), 'Ver Reporte')]"),
            (By.XPATH, f"//tr[contains(@id, 'DXDataRow{elemento['indice_fila']}')]//*[contains(@id, 'CBtn1')]"),
            (By.XPATH, f"//td[contains(text(), '{elemento['identificacion']}')]/..//span[contains(text(), 'Ver Reporte')]"),
            (By.XPATH, f"//tr[contains(@id, 'DXDataRow{elemento['indice_fila']}')]//a[contains(@class, 'dxbButton')]")
        ]
        
        for by, selector in estrategias:
            try:
                boton_reporte = self.wait_for_element(by, selector, timeout=5)
                if self.safe_click(boton_reporte):
                    logger.info(f"Clic exitoso en VER REPORTE para {elemento['identificacion']}")
                    return True
                    
            except TimeoutException:
                continue
            except Exception as e:
                logger.warning(f"Error en estrategia: {str(e)}")
                continue
        
        logger.error(f"No se pudo hacer clic en VER REPORTE para {elemento['identificacion']}")
        return False
    
    def procesar_reporte(self, elemento):
        """Procesar reporte individual con manejo robusto"""
        try:
            logger.info(f"Procesando reporte para {elemento['identificacion']}")
            
            # Esperar a que aparezca el visor de documentos
            time.sleep(5)
            
            # Buscar botón de descarga
            button_descarga = self.wait_for_element(By.ID, "DocumentViewer_Splitter_Toolbar_Menu_DXI9_T", timeout=20)
            
            if self.safe_click(button_descarga):
                logger.info("Descarga iniciada")
                
                # Verificar descarga
                archivo_descargado = self.verificar_descarga_completada()
                
                if archivo_descargado:
                    logger.info(f"PDF descargado: {os.path.basename(archivo_descargado)}")
                    
                    # Regresar a la lista - múltiples estrategias
                    try:
                        # Estrategias para encontrar el botón volver
                        estrategias_volver = [
                            (By.ID, "btnVolver_I"),
                            (By.XPATH, "//input[@id='btnVolver_I']"),
                            (By.XPATH, "//span[contains(text(), 'Volver a lista')]"),
                            (By.XPATH, "//div[contains(@class, 'dxbButton_Moderno')]//span[contains(text(), 'Volver a lista')]"),
                            (By.XPATH, "//input[@value='Volver a lista']")
                        ]
                        
                        boton_encontrado = False
                        for by, selector in estrategias_volver:
                            try:
                                regresar = self.wait_for_element(by, selector, timeout=5)
                                if self.safe_click(regresar):
                                    logger.info("Botón volver clickeado exitosamente")
                                    boton_encontrado = True
                                    break
                            except TimeoutException:
                                continue
                        
                        if not boton_encontrado:
                            logger.warning("No se encontró botón volver, usando navegador back")
                            self.driver.back()
                        
                        time.sleep(5)
                        return True
                        
                    except Exception as e:
                        logger.error(f"Error regresando: {str(e)}")
                        # Alternativa: usar back del navegador
                        self.driver.back()
                        time.sleep(5)
                        return True
                else:
                    logger.error("Descarga no completada")
                    return False
            else:
                logger.error("No se pudo hacer clic en descarga")
                return False
                
        except Exception as e:
            logger.error(f"Error procesando reporte: {str(e)}")
            try:
                self.driver.back()
                time.sleep(3)
            except:
                pass
            return False
    
    def procesar_todas_paginas(self):
        """Procesar todas las páginas con manejo robusto"""
        try:
            pagina_actual, total_paginas, total_elementos = self.obtener_info_paginacion()
            logger.info(f"Iniciando procesamiento: {total_elementos} elementos en {total_paginas} páginas")
            
            for pagina in range(pagina_actual, total_paginas + 1):
                logger.info(f"=== PROCESANDO PÁGINA {pagina} DE {total_paginas} ===")
                
                elementos = self.obtener_elementos_pagina()
                
                if not elementos:
                    logger.warning("No se encontraron elementos en esta página")
                    continue
                
                for elemento in elementos:
                    try:
                        logger.info(f"Procesando: {elemento['primer_nombre']} {elemento['primer_apellido']} - ID: {elemento['identificacion']}")
                        
                        if self.hacer_clic_ver_reporte(elemento):
                            if self.procesar_reporte(elemento):
                                logger.info(f"✓ Completado: {elemento['identificacion']}")
                                
                                # Esperar a que se recargue la tabla
                                self.wait_for_element(By.XPATH, "//table[contains(@id, 'gridResumidas')]", clickable=False)
                                time.sleep(3)
                            else:
                                logger.error(f"✗ Error procesando: {elemento['identificacion']}")
                        else:
                            logger.error(f"✗ No se pudo acceder al reporte: {elemento['identificacion']}")
                        
                    except Exception as e:
                        logger.error(f"Error con elemento {elemento['identificacion']}: {str(e)}")
                        continue
                
                # Ir a la siguiente página
                if pagina < total_paginas:
                    try:
                        siguiente_boton = self.driver.find_element(By.XPATH, f"//a[contains(text(), '{pagina + 1}')]")
                        self.safe_click(siguiente_boton)
                        time.sleep(5)
                        
                        # Actualizar información de paginación
                        pagina_actual, total_paginas, total_elementos = self.obtener_info_paginacion()
                        
                    except Exception as e:
                        logger.error(f"Error navegando a página {pagina + 1}: {str(e)}")
                        break
            
            logger.info("Procesamiento de todas las páginas completado")
            
        except Exception as e:
            logger.error(f"Error en procesamiento general: {str(e)}")
            raise
    
    def ejecutar_automatizacion(self):
        """Ejecutar el proceso completo"""
        try:
            self.login(PRIVATE_DATA)
            self.select_options(PRIVATE_DATA)
            time.sleep(5)
            
            self.procesar_todas_paginas()
            
            # Mostrar resumen
            archivos_descargados = [f for f in os.listdir(self.descargas_dir) if f.endswith('.pdf')]
            logger.info(f"Proceso completado. Total archivos descargados: {len(archivos_descargados)}")
            logger.info(f"Archivos guardados en: {self.descargas_dir}")
            
            for archivo in archivos_descargados:
                logger.info(f"📄 {archivo}")
                
        except Exception as e:
            logger.error(f"Error en automatización: {str(e)}")
            raise
        finally:
            if self.driver:
                time.sleep(3)
                self.driver.quit()
                logger.info("Driver cerrado")

def main():
    """Función principal"""
    automation = None
    try:
        # Crear instancia con opción headless (cambiar a True para ejecutar sin ventana)
        automation = SirasAutomation(headless=False)
        automation.ejecutar_automatizacion()
        
    except Exception as e:
        logger.error(f"Error fatal: {str(e)}")
        traceback.print_exc()
    finally:
        if automation and automation.driver:
            automation.driver.quit()

<<<<<<< HEAD
if __name__ == "__main__":
    main()
=======
        #fecha inicial
        fecha_inicial_input = Wait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "FechaInicialFiltro_I"))
        )
        fecha_inicial_input.click()
        time.sleep(1)
        human_typing(fecha_inicial_input, privateData["fecha"])

        #fecha final 
        fecha_final_input = Wait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "FechaFinalFiltro_I"))
        )
        fecha_final_input.click()
        time.sleep(1)
        human_typing(fecha_final_input, privateData["fecha"])

        #Botón consultar 
        button_consultar = Wait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'Consultar')]"))
        )
        button_consultar.click()

def total_pages(driver):
    try:   
        paginacion = Wait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "dxp-summary"))
        )
        
        # Extraer información usando split
        partes = paginacion.text.split()

        # "Página 1 de 6 (51 elementos)"
        pagina_actual = int(partes[1])
        total_paginas = int(partes[3])
        total_elementos = int(partes[4].replace('(', '').replace(')', ''))
        
        print(f"Página actual: {pagina_actual}")
        print(f"Total de páginas: {total_paginas}")
        print(f"Total de elementos: {total_elementos}")

        return pagina_actual, total_paginas, total_elementos
          
    except Exception as e: 
         print(f"Error obteniendo información de paginación: {str(e)}")
         return 1, 1, 0
    
def test():
    boton_reporte = Wait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, "gridResumidas_DXCBtn1"))
    )
    driver.execute_script("arguments[0].scrollIntoView();", boton_reporte)
    boton_reporte.click()


if  __name__ == "__main__":
    login(driver, privateData)
    select_options(driver, privateData)
    
    # Esperar a que cargue la consulta
    time.sleep(5)
    
    # Procesar todas las páginas y elementos
    procesar_todas_las_paginas(driver)
    
    
    time.sleep(5)
    driver.quit()
>>>>>>> 9d4f6b045d525cb2221482cab7a0b55f08cf4cb5
