#from selenium.webdriver import Chrome
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
import shutil
import glob
import urllib3
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
import requests

# Deshabilitar warnings de SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Configurar logging mejorado
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('siras_automation.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class SirasAutomation:
    
    def __init__(self, headless=True):
        self.driver = None
        self.setup_directories()
        self.setup_driver(headless)
        self.archivos_procesados = {} 
        
    def setup_directories(self):
        """Carpeta de descarga"""
        self.descargas_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "descargasPDF")
        if not os.path.exists(self.descargas_dir):
            os.makedirs(self.descargas_dir)
            print(f"Carpeta de descargas creada: {self.descargas_dir}")
    
    def setup_driver(self, headless=False):
        """Configuración mejorada del driver de chrome con timeouts optimizados"""
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
            
            # Opciones mejoradas para estabilidad del navegador
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-gpu")
            options.add_argument("--window-size=1920,1080")
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_argument("--disable-web-security")
            options.add_argument("--disable-features=VizDisplayCompositor")
            options.add_argument("--disable-extensions")
            options.add_argument("--disable-plugins")
            options.add_argument("--disable-images")  # Acelerar carga
            
            # Configuraciones de red y timeouts
            options.add_argument("--max_old_space_size=4096")
            options.add_argument("--disable-background-timer-throttling")
            options.add_argument("--disable-renderer-backgrounding")
            options.add_argument("--disable-backgrounding-occluded-windows")
            options.add_argument("--disable-extensions")
            options.add_argument("--disable-plugins-discovery")
            options.add_argument("--no-first-run")
            options.add_argument("--no-default-browser-check")
            options.add_argument("--disable-component-extensions-with-background-pages")
            options.add_argument("--disable-backgrounding-occluded-windows")
            options.add_argument("--disable-renderer-backgrounding")
            
            # User agent para evitar detección
            options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
            
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            
            if headless:
                options.add_argument("--headless")
            
            # Configurar timeouts más largos para el WebDriver
            service = Service(ChromeDriverManager().install())
            
            # Configurar timeouts del driver
            self.driver = Chrome(service=service, options=options)
            
            # Configurar timeouts de página y scripts
            self.driver.set_page_load_timeout(120)  # 2 minutos para cargar página
            self.driver.set_script_timeout(60)      # 1 minuto para scripts
            self.driver.implicitly_wait(15)         # 15 segundos para elementos
            
            # Remover propiedades de detección de automatización
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            self.driver.execute_cdp_cmd('Network.setUserAgentOverride', {
                "userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            })
            
            logger.info("Driver configurado exitosamente con timeouts mejorados")
            
        except Exception as e:
            logger.error(f"Error configurando driver: {str(e)}")
            raise
    
    def procesar_datos(self, correo, password, codigo, fecha_inicial, fecha_final, headless=True):
        """
        Función principal que procesa los datos y ejecuta toda la automatización.
        
        Args:
            correo (str): Email para login
            password (str): Contraseña para login
            codigo (str): Código de habilitación
            fecha_inicial (str): Fecha inicial para consulta
            fecha_final (str): Fecha final para consulta
            headless (bool): Ejecutar en modo headless
        
        Returns:
            dict: Resultado del procesamiento
        """
        start_time = datetime.now()
        
        try:
            # Validar y procesar datos de entrada
            datos = {
                "email": correo.strip() if correo else "",
                "password": password.strip() if password else "",
                "param": codigo.strip() if codigo else "",
                "fecha": fecha_inicial.strip() if fecha_inicial else "",
                "fechaF": fecha_final.strip() if fecha_final else "",
            }
            
            # Validar datos requeridos
            if not datos["email"]:
                raise ValueError("El correo es requerido")
            if not datos["password"]:
                raise ValueError("La contraseña es requerida")
            if not datos["fecha"]:
                raise ValueError("La fecha inicial es requerida")
            if not datos["fechaF"]:
                raise ValueError("La fecha final es requerida")
            
            logger.info("Datos procesados correctamente")
            logger.info(f"Email: {datos['email']}")
            logger.info(f"Fecha inicial: {datos['fecha']}")
            logger.info(f"Fecha final: {datos['fechaF']}")
            
            # Reinicializar el driver si es necesario
            if not self.driver or headless != getattr(self, '_headless_mode', True):
                if self.driver:
                    self.cleanup_driver()
                self.__init__(headless=headless)
                self._headless_mode = headless
            
            # Ejecutar automatización completa
            resultado = self.ejecutar_automatizacion(datos)
            
            # Calcular tiempo total
            end_time = datetime.now()
            duracion = end_time - start_time
            
            resultado.update({
                "tiempo_total": str(duracion),
                "fecha_procesamiento": end_time.strftime('%Y-%m-%d %H:%M:%S'),
                "datos_entrada": datos
            })
            
            return resultado
            
        except Exception as e:
            logger.error(f"Error en procesar_datos: {str(e)}")
            error_result = {
                "exito": False,
                "error": str(e),
                "archivos_procesados": 0,
                "archivos_descargados": 0,
                "tiempo_total": str(datetime.now() - start_time),
                "fecha_procesamiento": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            return error_result
        
        finally:
            # Limpiar recursos si es necesario
            pass  # Mantenemos el driver activo para reutilización
    
    def reiniciar_driver_si_necesario(self):
        """Reinicia el driver si hay problemas de conexión"""
        try:
            if self.driver:
                try:
                    # Probar si el driver sigue funcionando
                    self.driver.current_url
                except:
                    logger.warning("Driver no responde, reiniciando...")
                    self.driver.quit()
                    time.sleep(5)
                    self.setup_driver(headless=getattr(self, '_headless_mode', True))
                    return True
            return False
        except Exception as e:
            logger.error(f"Error reiniciando driver: {str(e)}")
            return False
    
    def human_typing(self, element, text, delay_range=(0.05, 0.15)):
        """Simula escritura humana letra por letra"""
        try:
            element.clear()
            for char in text:
                element.send_keys(char)
                time.sleep(random.uniform(*delay_range))
        except Exception as e:
            logger.warning(f"Error en human_typing: {str(e)}")
            # Fallback: escribir todo de una vez
            element.clear()
            element.send_keys(text)
    
    def wait_for_element(self, by, selector, timeout=30, clickable=True, retries=3):
        """Esperar elemento con reintentos y manejo de errores mejorado"""
        for intento in range(retries):
            try:
                if clickable:
                    element = Wait(self.driver, timeout).until(
                        EC.element_to_be_clickable((by, selector))
                    )
                else:
                    element = Wait(self.driver, timeout).until(
                        EC.presence_of_element_located((by, selector))
                    )
                return element
                
            except TimeoutException as e:
                logger.warning(f"Intento {intento + 1}/{retries} - Elemento no encontrado: {selector}")
                if intento < retries - 1:
                    time.sleep(5)
                    # Intentar refrescar la página si es el último intento antes del fallo
                    if intento == retries - 2:
                        try:
                            self.driver.refresh()
                            time.sleep(10)
                        except:
                            pass
                else:
                    logger.error(f"Elemento no encontrado después de {retries} intentos: {selector}")
                    raise
            except Exception as e:
                logger.error(f"Error inesperado esperando elemento: {str(e)}")
                if intento < retries - 1:
                    time.sleep(5)
                else:
                    raise
    
    def safe_click(self, element, use_js=False, retries=5):
        """Clic seguro con múltiples estrategias y reintentos"""
        for intento in range(retries):
            try:
                if use_js:
                    self.driver.execute_script("arguments[0].click();", element)
                    return True
                else:
                    # Scroll al elemento y hacer clic
                    self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
                    time.sleep(1)
                    
                    # Intentar clic normal
                    element.click()
                    return True
                    
            except (ElementClickInterceptedException, StaleElementReferenceException) as e:
                logger.warning(f"Error en clic, intento {intento + 1}: {str(e)}")
                if intento < retries - 1:
                    time.sleep(2)
                    try:
                        # Intentar con JavaScript como fallback
                        self.driver.execute_script("arguments[0].click();", element)
                        return True
                    except:
                        continue
                else:
                    logger.error("No se pudo hacer clic después de varios intentos")
                    return False
            except Exception as e:
                logger.warning(f"Error inesperado en clic: {str(e)}")
                if intento < retries - 1:
                    time.sleep(2)
                else:
                    return False
        return False
    
    def safe_navigate(self, url, retries=3):
        """Navegación segura con reintentos"""
        for intento in range(retries):
            try:
                logger.info(f"Navegando a: {url} (intento {intento + 1})")
                self.driver.get(url)
                time.sleep(5)
                return True
            except Exception as e:
                logger.warning(f"Error navegando (intento {intento + 1}): {str(e)}")
                if intento < retries - 1:
                    time.sleep(10)
                    if self.reiniciar_driver_si_necesario():
                        continue
                else:
                    logger.error("Falló la navegación después de varios intentos")
                    raise
        return False
    
    def verificar_descarga_completada(self, timeout=120):
        """Verificar descarga con timeout más largo"""
        inicio = time.time()
        archivos_iniciales = set([f for f in os.listdir(self.descargas_dir) 
                                if f.endswith('.pdf') and not f.endswith('.crdownload')])
        logger.info("Esperando descarga...")
        while time.time() - inicio < timeout:
            try:
                archivos_actuales = set([f for f in os.listdir(self.descargas_dir) 
                                       if f.endswith('.pdf') and not f.endswith('.crdownload')])
                archivos_temporales = [f for f in os.listdir(self.descargas_dir) 
                                     if f.endswith('.crdownload')]
                
                # Si hay archivos temporales, esperar
                if archivos_temporales:
                    logger.info("Descarga en progreso...")
                    time.sleep(5)
                    continue
                
                nuevos_archivos = archivos_actuales - archivos_iniciales
                
                if nuevos_archivos:
                    nuevo_archivo = list(nuevos_archivos)[0]
                    archivo_path = os.path.join(self.descargas_dir, nuevo_archivo)
                    
                    # Verificar que el archivo existe y tiene contenido
                    if os.path.exists(archivo_path) and os.path.getsize(archivo_path) > 1000:
                        logger.info(f"Descarga completada: {nuevo_archivo}")
                        return archivo_path
                        
                time.sleep(3)
                
            except Exception as e:
                logger.error(f"Error verificando descarga: {str(e)}")
                time.sleep(3)
                
        logger.error("Timeout esperando descarga")
        return None
    
    def generar_nombre_archivo(self, elemento):
        """Genera nombre de archivo limpio y único"""
        try:
            def limpiar_texto(texto):
                if not texto:
                    return ""
                # Reemplazar caracteres problemáticos
                caracteres_prohibidos = ['<', '>', ':', '"', '|', '?', '*', '/', '\\', '\n', '\r', '\t']
                for char in caracteres_prohibidos:
                    texto = texto.replace(char, '')
                return texto.strip()
            
            no_radicado = limpiar_texto(elemento.get('no_radicado', ''))
            
            # Formato principal
            if no_radicado:
                nombre = f"{no_radicado}.pdf"
            else:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                nombre = f"SinRadicado_{timestamp}.pdf"
            
            # Limpiar espacios y caracteres especiales
            nombre = '_'.join(nombre.split())
            nombre = nombre.replace('__', '_')
            
            return nombre
            
        except Exception as e:
            logger.error(f"Error generando nombre de archivo: {str(e)}")
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            return f"archivo_{timestamp}.pdf"
    
    def renombrar_archivo_descargado(self, archivo_original, elemento):
        """Renombrar archivo descargado"""
        try:
            if not os.path.exists(archivo_original):
                logger.error(f"Archivo original no existe: {archivo_original}")
                return None
            
            nuevo_nombre = self.generar_nombre_archivo(elemento)
            nuevo_path = os.path.join(self.descargas_dir, nuevo_nombre)
            
            # Si el archivo ya existe, agregar timestamp
            if os.path.exists(nuevo_path):
                timestamp = datetime.now().strftime("%H%M%S")
                nombre_base = nuevo_nombre.replace('.pdf', '')
                nuevo_nombre = f"{nombre_base}_{timestamp}.pdf"
                nuevo_path = os.path.join(self.descargas_dir, nuevo_nombre)
            
            # Renombrar archivo
            shutil.move(archivo_original, nuevo_path)
            logger.info(f"Archivo renombrado: {os.path.basename(archivo_original)} → {nuevo_nombre}")
            
            # Registrar el archivo procesado
            self.archivos_procesados[nuevo_nombre] = elemento
            
            return nuevo_path
            
        except Exception as e:
            logger.error(f"Error renombrando archivo: {str(e)}")
            return archivo_original
    
    def login(self, credentials, retries=3):
        """Login con manejo de errores mejorado"""
        for intento in range(retries):
            try:
                logger.info(f"Iniciando login (intento {intento + 1})...")
                
                if not self.safe_navigate("https://www.siras.com.co/siras/Seguridad/Login?Modo=1"):
                    continue
                
                username_input = self.wait_for_element(By.ID, "Email_I", timeout=30)
                username_input.clear()
                self.human_typing(username_input, credentials["email"])
                time.sleep(1)
                
                password_input = self.wait_for_element(By.ID, "Password_I", timeout=30)
                password_input.clear()
                self.human_typing(password_input, credentials["password"])
                
                time.sleep(1)
                login_button = self.wait_for_element(By.ID, "btnIngresar", timeout=30)
                if self.safe_click(login_button):
                    logger.info("Login exitoso")
                    return True
                
            except Exception as e:
                logger.error(f"Error durante login (intento {intento + 1}): {str(e)}")
                if intento < retries - 1:
                    time.sleep(15)
                    self.reiniciar_driver_si_necesario()
                else:
                    raise
        return False
    
    def select_options(self, credentials, retries=3):
        """Configurar opciones con manejo de errores mejorado"""
        for intento in range(retries):
            try:
                logger.info(f"Configurando opciones (intento {intento + 1})...")
                
                if credentials["param"]:
                    # Código de habilitación
                    codigo_input = self.wait_for_element(By.ID, "CodigoHabilitacion_I", timeout=30)
                    self.human_typing(codigo_input, credentials["param"])
                    
                    # Botón prestador
                    prestador_button = self.wait_for_element(
                        By.XPATH, "//span[contains(text(), 'Ingresar con el Prestador Encontrado')]", timeout=30
                    )
                    self.safe_click(prestador_button)
                    self.safe_click(prestador_button)
                
                # Navbar consultas
                navbar_consultas = self.wait_for_element(By.ID, "menuNoAuth_DXI2_T", timeout=30)
                self.safe_click(navbar_consultas)
                
                # Opción lista resumida
                lista_resumida = self.wait_for_element(
                    By.XPATH, "//span[contains(text(), 'LISTA RESUMIDA DE ATENCIONES')]", timeout=30
                )
                self.safe_click(lista_resumida)
                
                # Configurar fechas
                fecha_inicial = self.wait_for_element(By.ID, "FechaInicialFiltro_I", timeout=30)
                self.safe_click(fecha_inicial)
                fecha_inicial.send_keys(credentials["fecha"])
                
                fecha_final = self.wait_for_element(By.ID, "FechaFinalFiltro_I", timeout=30)
                self.safe_click(fecha_final)
                fecha_final.send_keys(credentials["fechaF"])
                
                # Consultar
                consultar_button = self.wait_for_element(
                    By.XPATH, "//span[contains(text(), 'Consultar')]", timeout=30
                )
                self.safe_click(consultar_button)
                
                # Esperar resultados
                logger.info("Opciones configuradas exitosamente")
                return True
                
            except Exception as e:
                logger.error(f"Error configurando opciones (intento {intento + 1}): {str(e)}")
                if intento < retries - 1:
                    time.sleep(2)
                else:
                    raise
        return False
    
    def obtener_info_paginacion(self):
        """Obtener información de paginación con manejo de errores"""
        try:
            paginacion = self.wait_for_element(By.CLASS_NAME, "dxp-summary", timeout=20, clickable=False)
            texto = paginacion.text
            logger.info(f"Texto paginación: {texto}")
            
            # Parsear texto de paginación
            partes = texto.split()
            pagina_actual = int(partes[1])
            total_paginas = int(partes[3])
            total_elementos = int(partes[4].replace('(', '').replace(')', ''))
            
            return pagina_actual, total_paginas, total_elementos
            
        except Exception as e:
            logger.error(f"Error obteniendo paginación: {str(e)}")
            return 1, 1, 0
    
    def obtener_elementos_pagina(self):
        """Obtener elementos de la página actual"""
        try:
            # Esperar tabla con timeout más largo
            self.wait_for_element(By.XPATH, "//table[contains(@id, 'gridResumidas')]", timeout=30, clickable=False)
            
            filas = self.driver.find_elements(By.XPATH, "//tr[contains(@id, 'gridResumidas_DXDataRow')]")
            elementos = []
            
            for i, fila in enumerate(filas):
                try:
                    celdas = fila.find_elements(By.TAG_NAME, "td")
                    
                    if len(celdas) >= 28:
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
                            'fila_element': fila
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
        """Hacer clic en Ver Reporte con múltiples estrategias"""
        estrategias = [
            (By.XPATH, f"//td[contains(text(), '{elemento['identificacion']}')]/..//span[contains(text(), 'Ver Reporte')]"),
        ]
        
        for by, selector in estrategias:
            try:
                boton_reporte = self.wait_for_element(by, selector, timeout=10)
                if self.safe_click(boton_reporte):
                    logger.info(f"Clic exitoso en VER REPORTE para {elemento['identificacion']}")
                    return True
                    
            except TimeoutException:
                continue
            except Exception as e:
                logger.warning(f"Error en estrategia de clic: {str(e)}")
                continue
        
        logger.error(f"No se pudo hacer clic en VER REPORTE para {elemento['identificacion']}")
        return False
    
    def procesar_reporte(self, elemento):
        """Procesar reporte individual con manejo mejorado de errores"""
        try:
            logger.info(f"Procesando reporte para {elemento['identificacion']} - Radicado: {elemento['no_radicado']}")
            
            # Esperar visor de documentos con timeout más largo
            time.sleep(2)
            
            # Buscar botón de descarga
            button_descarga = self.wait_for_element(By.ID, "DocumentViewer_Splitter_Toolbar_Menu_DXI9_T", timeout=45)
            
            if self.safe_click(button_descarga):
                logger.info("Descarga iniciada")
                
                # Verificar descarga con timeout más largo
                archivo_descargado = self.verificar_descarga_completada(timeout=180)
                
                if archivo_descargado:
                    logger.info(f"PDF descargado: {os.path.basename(archivo_descargado)}")
                    
                    # Renombrar archivo
                    archivo_renombrado = self.renombrar_archivo_descargado(archivo_descargado, elemento)
                    
                    # Regresar a la lista
                    estrategias_volver = [
                        (By.XPATH, "//span[contains(text(), 'Volver a lista')]"),
                    ]
                    
                    boton_encontrado = False
                    for by, selector in estrategias_volver:
                        try:
                            regresar = self.wait_for_element(by, selector, timeout=10)
                            if self.safe_click(regresar):
                                logger.info("Regresando a lista...")
                                boton_encontrado = True
                                break
                        except TimeoutException:
                            continue
                    
                    if not boton_encontrado:
                        logger.info("Usando navegador back...")
                        self.driver.back()
                    
                    time.sleep(2)
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
                time.sleep(2)
            except:
                pass
            return False
    
    def procesar_todas_paginas(self):
        """Procesar todas las páginas con manejo robusto de errores"""
        try:
            pagina_actual, total_paginas, total_elementos = self.obtener_info_paginacion()
            logger.info(f"Iniciando procesamiento: {total_elementos} elementos en {total_paginas} páginas")
            
            for pagina in range(pagina_actual, total_paginas + 1):
                logger.info(f"=== PROCESANDO PÁGINA {pagina} DE {total_paginas} ===")
                
                # Obtener elementos con reintentos
                elementos = []
                for intento_elementos in range(3):
                    elementos = self.obtener_elementos_pagina()
                    if elementos:
                        break
                    logger.warning(f"No se encontraron elementos, reintentando... ({intento_elementos + 1}/3)")
                    time.sleep(2)
                
                if not elementos:
                    logger.warning("No se encontraron elementos en esta página, continuando...")
                    continue
                
                # Procesar cada elemento
                for idx, elemento in enumerate(elementos):
                    try:
                        logger.info(f"Procesando {idx + 1}/{len(elementos)}: {elemento['primer_nombre']} {elemento['primer_apellido']} - ID: {elemento['identificacion']}")
                        
                        if self.hacer_clic_ver_reporte(elemento):
                            if self.procesar_reporte(elemento):
                                logger.info(f"✓ Completado: {elemento['identificacion']}")
                                
                                # Esperar recarga de tabla
                                self.wait_for_element(By.XPATH, "//table[contains(@id, 'gridResumidas')]", timeout=30, clickable=False)
                                time.sleep(5)
                            else:
                                logger.error(f"✗ Error procesando reporte: {elemento['identificacion']}")
                        else:
                            logger.error(f"✗ No se pudo acceder al reporte: {elemento['identificacion']}")
                        
                    except Exception as e:
                        logger.error(f"Error con elemento {elemento['identificacion']}: {str(e)}")
                        continue
                
                # Navegar a siguiente página
                if pagina < total_paginas:
                    try:
                        siguiente_boton = self.driver.find_element(By.XPATH, f"//a[contains(text(), '{pagina + 1}')]")
                        if self.safe_click(siguiente_boton):
                            time.sleep(10)
                            
                            # Actualizar información de paginación
                            pagina_actual, total_paginas, total_elementos = self.obtener_info_paginacion()
                        else:
                            logger.error(f"No se pudo navegar a página {pagina + 1}")
                            break
                            
                    except Exception as e:
                        logger.error(f"Error navegando a página {pagina + 1}: {str(e)}")
                        break
            
            logger.info("Procesamiento de todas las páginas completado")
            
        except Exception as e:
            logger.error(f"Error en procesamiento general: {str(e)}")
            raise
    
    def generar_reporte_archivos(self):
        """Generar reporte de archivos procesados"""
        try:
            reporte_path = os.path.join(self.descargas_dir, "reporte_archivos.txt")
            
            with open(reporte_path, 'w', encoding='utf-8') as f:
                f.write("REPORTE DE ARCHIVOS PROCESADOS\n")
                f.write("=" * 50 + "\n")
                f.write(f"Fecha de procesamiento: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Total de archivos procesados: {len(self.archivos_procesados)}\n\n")
                
                f.write("DETALLE DE ARCHIVOS:\n")
                f.write("-" * 30 + "\n")
                
                for nombre_archivo, elemento in self.archivos_procesados.items():
                    f.write(f"Archivo: {nombre_archivo}\n")
                    f.write(f"  - Identificación: {elemento['identificacion']}\n")
                    f.write(f"  - Nombre: {elemento['primer_nombre']} {elemento['segundo_nombre']}\n")
                    f.write(f"  - Apellidos: {elemento['primer_apellido']} {elemento['segundo_apellido']}\n")
                    f.write(f"  - No. Radicado: {elemento['no_radicado']}\n")
                    f.write(f"  - Tipo ID: {elemento['tipo_id']}\n")
                    f.write(f"  - Clasificación: {elemento['clasificacion']}\n")
                    f.write("-" * 30 + "\n")
            
            logger.info(f"Reporte generado: {reporte_path}")
            
        except Exception as e:
            logger.error(f"Error generando reporte: {str(e)}")
    
    def cleanup_driver(self):
        """Limpiar recursos del driver de forma segura"""
        try:
            if self.driver:
                self.driver.quit()
                logger.info("Driver cerrado correctamente")
        except Exception as e:
            logger.warning(f"Error cerrando driver: {str(e)}")
    
    def ejecutar_automatizacion(self, datos):
        """
        Ejecutar el proceso completo con manejo robusto de errores
        
        Args:
            datos (dict): Diccionario con credenciales y parámetros
            
        Returns:
            dict: Resultado del procesamiento
        """
        try:
            logger.info("=== INICIANDO AUTOMATIZACIÓN SIRAS ===")
            
            # Login con reintentos
            if not self.login(datos):
                raise Exception("No se pudo completar el login")
            
            # Configurar opciones
            if not self.select_options(datos):
                raise Exception("No se pudieron configurar las opciones")
            
            time.sleep(10)
            
            # Procesar todas las páginas
            self.procesar_todas_paginas()
            
            # Generar reporte
            self.generar_reporte_archivos()
            
            # Mostrar resumen
            archivos_descargados = [f for f in os.listdir(self.descargas_dir) if f.endswith('.pdf')]
            
            logger.info("=" * 50)
            logger.info("RESUMEN DE PROCESAMIENTO")
            logger.info("=" * 50)
            logger.info(f"Archivos descargados: {len(archivos_descargados)}")
            logger.info(f"Archivos procesados exitosamente: {len(self.archivos_procesados)}")
            logger.info(f"Directorio de descargas: {self.descargas_dir}")
            logger.info("=" * 50)
            
            if self.archivos_procesados:
                logger.info("ARCHIVOS PROCESADOS:")
                for nombre_archivo, elemento in self.archivos_procesados.items():
                    logger.info(f"   ✓ {nombre_archivo} (ID: {elemento['identificacion']}, Radicado: {elemento['no_radicado']})")
            else:
                logger.warning("No se procesaron archivos exitosamente")
            
            return {
                "exito": True,
                "archivos_procesados": len(self.archivos_procesados),
                "archivos_descargados": len(archivos_descargados),
                "directorio_descargas": self.descargas_dir,
                "archivos_detalle": list(self.archivos_procesados.keys()),
                "mensaje": "Automatización completada exitosamente"
            }
                
        except Exception as e:
            logger.error(f"Error en automatización: {str(e)}")
            logger.error("Stack trace:", exc_info=True)
            
            return {
                "exito": False,
                "error": str(e),
                "archivos_procesados": len(self.archivos_procesados),
                "archivos_descargados": 0,
                "directorio_descargas": self.descargas_dir,
                "mensaje": f"Error en automatización: {str(e)}"
            }


# Funciones de utilidad para usar el bot
def ejecutar_siras_bot(correo, password, codigo, fecha_inicial, fecha_final, headless=True):
    """
    Función principal para ejecutar el bot de SIRAS
    
    Args:
        correo (str): Email para login
        password (str): Contraseña para login
        codigo (str): Código de habilitación
        fecha_inicial (str): Fecha inicial (formato: ddmmyyyy)
        fecha_final (str): Fecha final (formato: ddmmyyyy)
        headless (bool): Ejecutar en modo headless
    
    Returns:
        dict: Resultado del procesamiento
    
    Example:
        resultado = ejecutar_siras_bot(
            correo="usuario@ejemplo.com",
            password="mi_password",
            codigo="123456789",
            fecha_inicial="01012025",
            fecha_final="31012025",
            headless=True
        )
        print(resultado)
    """
    automation = None
    
    try:
        logger.info("Iniciando bot de SIRAS...")
        automation = SirasAutomation(headless=headless)
        
        resultado = automation.procesar_datos(
            correo=correo,
            password=password,
            codigo=codigo,
            fecha_inicial=fecha_inicial,
            fecha_final=fecha_final,
            headless=headless
        )
        
        return resultado
        
    except Exception as e:
        logger.error(f"Error ejecutando bot: {str(e)}")
        return {
            "exito": False,
            "error": str(e),
            "mensaje": f"Error ejecutando bot: {str(e)}"
        }
        
    finally:
        if automation:
            automation.cleanup_driver()


def main():
    """Función principal con datos de ejemplo"""
    
    # Datos de ejemplo - reemplazar con datos reales
    datos_ejemplo = {
        "correo": "dirimagenes@vallesaludips.com",
        "password": "SE0uJ9dC", 
        "codigo": "760010732306",
        "fecha_inicial": "1792025",
        "fecha_final": "1792025"
    }
    
    try:
        # Verificar argumentos de línea de comandos para modo headless
        headless_mode = '--headless' in sys.argv or '-h' in sys.argv
        
        logger.info(f"Ejecutando con datos de ejemplo en modo {'headless' if headless_mode else 'con interfaz'}")
        
        # Ejecutar bot
        resultado = ejecutar_siras_bot(
            correo=datos_ejemplo["correo"],
            password=datos_ejemplo["password"],
            codigo=datos_ejemplo["codigo"],
            fecha_inicial=datos_ejemplo["fecha_inicial"],
            fecha_final=datos_ejemplo["fecha_final"],
            headless=headless_mode
        )
        
        # Mostrar resultado
        print("\n" + "="*50)
        print("RESULTADO FINAL")
        print("="*50)
        for key, value in resultado.items():
            print(f"{key}: {value}")
        print("="*50)
        
        if resultado.get("exito"):
            logger.info("AUTOMATIZACIÓN COMPLETADA EXITOSAMENTE")
        else:
            logger.error("AUTOMATIZACIÓN FALLÓ")
            sys.exit(1)
        
    except KeyboardInterrupt:
        logger.warning("Proceso interrumpido por el usuario")
    except Exception as e:
        logger.error(f"Error fatal en la automatización: {str(e)}")
        logger.error("Stack trace completo:", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()