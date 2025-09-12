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
    "fecha": "1192025",
}

class SirasAutomation:
    def __init__(self, headless=False):
        self.driver = None
        self.setup_directories()
        self.setup_driver(headless)
        self.archivos_procesados = {} 
        
    def setup_directories(self):
        #Carpeta de descarga 
        self.descargas_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "descargasPDF")
        if not os.path.exists(self.descargas_dir):
            os.makedirs(self.descargas_dir)
            print(f"Carpeta de descargas creada: {self.descargas_dir}")
    
    def setup_driver(self, headless=False):
        #Configuración del driver de chrome
        try:
            options = webdriver.ChromeOptions()
            
            # Configurar descargas aut
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
            
            # Opciones para estabilidad del navegador
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
        #Simula escritura letra por letra
        element.clear()
        for char in text:
            element.send_keys(char)
            time.sleep(random.uniform(*delay_range))
    
    def wait_for_element(self, by, selector, timeout=15, clickable=True):
        #Esperar 
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
        #Intentar de diferentes momentos los clicks
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
        #Esperar el timeout de la descarga
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
    
    def generar_nombre_archivo(self, elemento):
        #Generamos el nombre del archivo
        try:
            # Limpiar caracteres especiales
            def limpiar_texto(texto):
                if not texto:
                    return ""
                # Reemplazar caracteres problemáticos
                caracteres_prohibidos = ['<', '>', ':', '"', '|', '?', '*', '/', '\\']
                for char in caracteres_prohibidos:
                    texto = texto.replace(char, '')
                return texto.strip()
            
            no_radicado = limpiar_texto(elemento.get('no_radicado', ''))
            identificacion = limpiar_texto(elemento.get('identificacion', ''))
            primer_nombre = limpiar_texto(elemento.get('primer_nombre', ''))
            primer_apellido = limpiar_texto(elemento.get('primer_apellido', ''))
            
            # Formato principal: NoRadicado_ID_Nombre_Apellido.pdf 
            #Si hay numero de radicado
            if no_radicado:
                nombre = f"{no_radicado}_{identificacion}_{primer_nombre}_{primer_apellido}.pdf"
            else:
                # Fallback si no hay número de radicado
                nombre = f"SinRadicado_{identificacion}_{primer_nombre}_{primer_apellido}.pdf"
            
            # Remover espacios múltiples y caracteres especiales adicionales
            nombre = '_'.join(nombre.split())
            nombre = nombre.replace('__', '_')
            
            return nombre
            
        except Exception as e:
            logger.error(f"Error generando nombre de archivo: {str(e)}")
            # Nombre fallback
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            return f"archivo_{timestamp}.pdf"
    
    def renombrar_archivo_descargado(self, archivo_original, elemento):
        #Renombrarlos
        try:
            if not os.path.exists(archivo_original):
                logger.error(f"Archivo original no existe: {archivo_original}")
                return None
            
            nuevo_nombre = self.generar_nombre_archivo(elemento)
            nuevo_path = os.path.join(self.descargas_dir, nuevo_nombre)
            
            # Si el archivo con el nuevo nombre ya existe, agregar timestamp
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
    
    def login(self, credentials):
        #Realiza el proceso del login con la data del usuario
        #TODO Pendiente parametrizar para que esta información sea dinamica 
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
            print("Login Exitoso")
            
        except Exception as e:
            print(f"Error durante login: {str(e)}")
            raise
    
    def select_options(self, credentials):
        #Proceso de seleccionar las opciones despues de ingresar al Login
        #TODO pendiente configurar la parte de la fecha para que se autocomplemente como el script anterior
        try:
            print("Configurando opciones...")
            
            if credentials["param"] is not None:
                # Código de habilitación
                codigo_input = self.wait_for_element(By.ID, "CodigoHabilitacion_I")
                self.human_typing(codigo_input, credentials["param"])
                
                # Botón prestador encontrado
                prestador_button = self.wait_for_element(By.XPATH, "//span[contains(text(), 'Ingresar con el Prestador Encontrado')]")
                self.safe_click(prestador_button)
                self.safe_click(prestador_button)
                time.sleep(3)
                time.sleep(3)
            else: 
                print("Process without CodigoHabilitación")
            
            # Navbar consultas
            navbar_consultas = self.wait_for_element(By.ID, "menuNoAuth_DXI2_T")
            self.safe_click(navbar_consultas)
            
            # Opción lista resumida
            lista_resumida = self.wait_for_element(By.XPATH, "//span[contains(text(), 'LISTA RESUMIDA DE ATENCIONES')]")
            self.safe_click(lista_resumida)
            time.sleep(3)
            
            # Configurar fechas
            fecha_inicial = self.wait_for_element(By.ID, "FechaInicialFiltro_I")
            self.safe_click(fecha_inicial)
            time.sleep(1)
            fecha_inicial.send_keys(credentials["fecha"])
            # self.human_typing(fecha_inicial, credentials["fecha"])
            
            fecha_final = self.wait_for_element(By.ID, "FechaFinalFiltro_I")
            self.safe_click(fecha_final)
            time.sleep(1)
            fecha_final.send_keys(credentials["fecha"])
            # self.human_typing(fecha_final, credentials["fecha"])
            
            # Consultar
            consultar_button = self.wait_for_element(By.XPATH, "//span[contains(text(), 'Consultar')]")
            self.safe_click(consultar_button)
            
            # Esperar a que se carguen los resultados
            time.sleep(10)
            print("Opciones configuradas exitosamente")
            
        except Exception as e:
            print(f"Error configurando opciones: {str(e)}")
            raise
    
    def obtener_info_paginacion(self):
        #Obtener la información de la páginacion
        try:
            paginacion = self.wait_for_element(By.CLASS_NAME, "dxp-summary", clickable=False)
            texto = paginacion.text
            print(f"Texto paginación: {texto}")
            
            # Parsear texto de paginación (ejemplo: "1 of 3 (25)")
            partes = texto.split()
            pagina_actual = int(partes[1])
            total_paginas = int(partes[3])
            total_elementos = int(partes[4].replace('(', '').replace(')', ''))
            
            return pagina_actual, total_paginas, total_elementos
            
        except Exception as e:
            print(f"Error obteniendo paginación: {str(e)}")
            return 1, 1, 0
    
    def obtener_elementos_pagina(self):
        #Obtener los datos de la tabla 
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
                            'fila_element': fila  
                        }
                        elementos.append(elemento_info)
                        logger.info(f"Extraído: {elemento_info['primer_nombre']} {elemento_info['primer_apellido']} - ID: {elemento_info['identificacion']} - Radicado: {elemento_info['no_radicado']}")
                        
                except Exception as e:
                    print(f"Error procesando fila {i}: {str(e)}")
                    continue
            
            print(f"Total elementos encontrados: {len(elementos)}")
            return elementos
            
        except Exception as e:
            print(f"Error obteniendo elementos: {str(e)}")
            return []
    
    def hacer_clic_ver_reporte(self, elemento):
        #Botón de ver reporte , proceso
        estrategias = [
            # (By.XPATH, f"//tr[contains(@id, 'DXDataRow{elemento['indice_fila']}')]//span[contains(text(), 'Ver Reporte')]"),
            # (By.XPATH, f"//tr[contains(@id, 'DXDataRow{elemento['indice_fila']}')]//*[contains(@id, 'CBtn1')]"),
            (By.XPATH, f"//td[contains(text(), '{elemento['identificacion']}')]/..//span[contains(text(), 'Ver Reporte')]"),
            (By.XPATH, f"//tr[contains(@id, 'DXDataRow{elemento['indice_fila']}')]//a[contains(@class, 'dxbButton')]")
        ]
        
        for by, selector in estrategias:
            try:
                boton_reporte = self.wait_for_element(by, selector, timeout=5)
                if self.safe_click(boton_reporte):
                    print(f"Clic exitoso en VER REPORTE para {elemento['identificacion']}")
                    return True
                    
            except TimeoutException:
                continue
            except Exception as e:
                print(f"Error en estrategia: {str(e)}")
                continue
        
        print(f"No se pudo hacer clic en VER REPORTE para {elemento['identificacion']}")
        return False
    
    def procesar_reporte(self, elemento):
        #Manejar el reporte individual , descargar y regresar
        try:
            logger.info(f"Procesando reporte para {elemento['identificacion']} - Radicado: {elemento['no_radicado']}")
            
            # Esperar a que aparezca el visor de documentos
            time.sleep(5)
            
            # Buscar botón de descarga
            button_descarga = self.wait_for_element(By.ID, "DocumentViewer_Splitter_Toolbar_Menu_DXI9_T", timeout=20)
            
            if self.safe_click(button_descarga):
                print("Descarga iniciada")
                
                # Verificar descarga
                archivo_descargado = self.verificar_descarga_completada()
                
                if archivo_descargado:
                    print(f"PDF descargado: {os.path.basename(archivo_descargado)}")
                    
                    # Renombrar archivo con información del elemento
                    archivo_renombrado = self.renombrar_archivo_descargado(archivo_descargado, elemento)
                    
                    # Regresar a la lista - múltiples estrategias
                    try:
                        # Estrategias para encontrar el botón volver
                        estrategias_volver = [
                            # (By.ID, "btnVolver_I"),
                            # (By.XPATH, "//input[@id='btnVolver_I']"),
                            (By.XPATH, "//span[contains(text(), 'Volver a lista')]"),
                            (By.XPATH, "//div[contains(@class, 'dxbButton_Moderno')]//span[contains(text(), 'Volver a lista')]"),
                            (By.XPATH, "//input[@value='Volver a lista']")
                        ]
                        
                        boton_encontrado = False
                        for by, selector in estrategias_volver:
                            try:
                                regresar = self.wait_for_element(by, selector, timeout=5)
                                if self.safe_click(regresar):
                                    print("Botón regresar clickeado exitosamente")
                                    boton_encontrado = True
                                    break
                            except TimeoutException:
                                continue
                        
                        if not boton_encontrado:
                            print("No se encontró botón de regresar, usando navegador back")
                            self.driver.back()
                        
                        time.sleep(5)
                        return True
                        
                    except Exception as e:
                        print(f"Error regresando: {str(e)}")
                        # Alternativa: usar back del navegador
                        self.driver.back()
                        time.sleep(5)
                        return True
                else:
                    print("Descarga no completada")
                    return False
            else:
                print("No se pudo hacer clic en descarga")
                return False
                
        except Exception as e:
            print(f"Error procesando reporte: {str(e)}")
            try:
                self.driver.back()
                time.sleep(3)
            except:
                pass
            return False
    
    def procesar_todas_paginas(self):
        #Procesar todos los datos de la página
        try:
            pagina_actual, total_paginas, total_elementos = self.obtener_info_paginacion()
            print(f"Iniciando procesamiento: {total_elementos} elementos en {total_paginas} páginas")
            
            for pagina in range(pagina_actual, total_paginas + 1):
                print(f"=== PROCESANDO PÁGINA {pagina} DE {total_paginas} ===")
                
                elementos = self.obtener_elementos_pagina()
                
                if not elementos:
                    print("No se encontraron elementos en esta página")
                    continue
                
                for elemento in elementos:
                    try:
                        print(f"Procesando: {elemento['primer_nombre']} {elemento['primer_apellido']} - ID: {elemento['identificacion']} - Radicado: {elemento['no_radicado']}")
                        
                        if self.hacer_clic_ver_reporte(elemento):
                            if self.procesar_reporte(elemento):
                                print(f"✓ Completado: {elemento['identificacion']}")
                                
                                # Esperar a que se recargue la tabla
                                self.wait_for_element(By.XPATH, "//table[contains(@id, 'gridResumidas')]", clickable=False)
                                time.sleep(3)
                            else:
                                print(f"✗ Error procesando: {elemento['identificacion']}")
                        else:
                            print(f"✗ No se pudo acceder al reporte: {elemento['identificacion']}")
                        
                    except Exception as e:
                        print(f"Error con elemento {elemento['identificacion']}: {str(e)}")
                        continue
                
                #siguiente página
                if pagina < total_paginas:
                    try:
                        siguiente_boton = self.driver.find_element(By.XPATH, f"//a[contains(text(), '{pagina + 1}')]")
                        self.safe_click(siguiente_boton)
                        time.sleep(5)
                        
                        # Actualizar información de paginación
                        pagina_actual, total_paginas, total_elementos = self.obtener_info_paginacion()
                        
                    except Exception as e:
                        print(f"Error navegando a página {pagina + 1}: {str(e)}")
                        break
            
            print("Procesamiento de todas las páginas completado")
            
        except Exception as e:
            print(f"Error en procesamiento general: {str(e)}")
            raise
    
    def generar_reporte_archivos(self):
        #Funcion de prueba para ver los datos del archivo descargado
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
    
    def ejecutar_automatizacion(self):
        #Ejecuta el proceso
        try:
            self.login(PRIVATE_DATA)
            self.select_options(PRIVATE_DATA)
            time.sleep(5)
            
            self.procesar_todas_paginas()
            
            # Generar reporte de archivos
            self.generar_reporte_archivos()
            
            # Mostrar resumen
            archivos_descargados = [f for f in os.listdir(self.descargas_dir) if f.endswith('.pdf')]
            print(f"Proceso completado. Total archivos descargados: {len(archivos_descargados)}")
            print(f"Archivos guardados en: {self.descargas_dir}")
            
            print("\n📄 ARCHIVOS PROCESADOS:")
            for nombre_archivo, elemento in self.archivos_procesados.items():
                print(f"   {nombre_archivo} (ID: {elemento['identificacion']}, Radicado: {elemento['no_radicado']})")
                
        except Exception as e:
            print(f"Error en automatización: {str(e)}")
            raise
        finally:
            if self.driver:
                time.sleep(3)
                self.driver.quit()
                print("Driver cerrado")

def main():
    #Funciona Main
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

if __name__ == "__main__":
    main()