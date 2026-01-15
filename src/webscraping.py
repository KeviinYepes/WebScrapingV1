from selenium.webdriver import Chrome
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait as Wait
from selenium.webdriver.common.keys import Keys
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
from datetime import datetime, timedelta
import logging
import shutil
import urllib3
import requests
import subprocess
import re
import zipfile
import io
from pathlib import Path

# Deshabilitar warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ============================================================================
# CONFIGURACIÓN DE LOGGING MEJORADA
# ============================================================================
class ColoredFormatter(logging.Formatter):
    COLORS = {
        'DEBUG': '\033[36m',    # Cyan
        'INFO': '\033[32m',     # Green
        'WARNING': '\033[33m',  # Yellow
        'ERROR': '\033[31m',    # Red
        'CRITICAL': '\033[41m', # Red background
    }
    RESET = '\033[0m'
    
    def format(self, record):
        log_time = datetime.now().strftime('%H:%M:%S')
        levelname = record.levelname
        message = record.getMessage()
        color = self.COLORS.get(levelname, '')
        
        if levelname == 'INFO':
            return f'[{log_time}] {color}{message}{self.RESET}'
        else:
            return f'[{log_time}] {levelname:8s} {color}{message}{self.RESET}'

# Configurar logging
log_filename = f'siras_automation_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'

file_handler = logging.FileHandler(log_filename, encoding='utf-8')
file_handler.setLevel(logging.DEBUG)
file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(file_formatter)

console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)
console_formatter = ColoredFormatter()
console_handler.setFormatter(console_formatter)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(file_handler)
logger.addHandler(console_handler)

# ============================================================================
# CLASE MEJORADA PARA MANEJO DE CHROMEDRIVER CON MÚLTIPLES ESTRATEGIAS
# ============================================================================
class ChromeDriverManager:
    def __init__(self):
        self.logger = logger
        self.chrome_version = None
        self.strategies = [
            self.strategy_1_webdriver_manager,
            self.strategy_2_local_driver,
            self.strategy_3_chrome_for_testing,
            self.strategy_4_system_chromedriver
        ]
    
    def get_chrome_version(self):
        """Obtener versión de Chrome instalado"""
        try:
            # Método para Windows
            if sys.platform == "win32":
                import winreg
                try:
                    key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Google\Chrome\BLBeacon")
                    version, _ = winreg.QueryValueEx(key, "version")
                    self.chrome_version = version.split('.')[0]  # Solo major version
                    self.logger.info(f"✅ Chrome versión detectada: {version}")
                    return version
                except:
                    pass
            
            # Método para macOS/Linux o fallback Windows
            try:
                # Intentar ejecutar chrome --version
                if sys.platform == "win32":
                    command = r'reg query "HKEY_CURRENT_USER\Software\Google\Chrome\BLBeacon" /v version'
                    result = subprocess.run(command, capture_output=True, text=True, shell=True)
                    if result.returncode == 0:
                        for line in result.stdout.split('\n'):
                            if 'version' in line:
                                version = line.split()[-1]
                                self.chrome_version = version.split('.')[0]
                                self.logger.info(f"✅ Chrome versión detectada: {version}")
                                return version
                else:
                    result = subprocess.run(['google-chrome', '--version'], 
                                          capture_output=True, text=True)
                    if result.returncode == 0:
                        version = result.stdout.strip().split()[-1]
                        self.chrome_version = version.split('.')[0]
                        self.logger.info(f"✅ Chrome versión detectada: {version}")
                        return version
            except:
                pass
            
            self.logger.warning("⚠️ No se pudo detectar versión de Chrome, usando versión por defecto")
            self.chrome_version = "120"  # Versión por defecto
            return self.chrome_version
            
        except Exception as e:
            self.logger.error(f"❌ Error obteniendo versión de Chrome: {str(e)}")
            self.chrome_version = "120"
            return self.chrome_version
    
    def strategy_1_webdriver_manager(self):
        """Estrategia 1: Usar webdriver-manager (método original)"""
        try:
            from webdriver_manager.chrome import ChromeDriverManager as WDM_ChromeDriverManager
            
            self.logger.info("🧪 Probando estrategia 1: webdriver-manager...")
            
            # Obtener versión de Chrome si no está disponible
            if not self.chrome_version:
                self.get_chrome_version()
            
            # Intentar con versión específica
            driver_path = WDM_ChromeDriverManager().install()
            self.logger.info(f"✅ ChromeDriver instalado: {driver_path}")
            return driver_path
            
        except Exception as e:
            self.logger.debug(f"   ⚠️  Estrategia 1 falló: {str(e)}")
            return None
    
    def strategy_2_local_driver(self):
        """Estrategia 2: Buscar ChromeDriver en ubicaciones comunes"""
        self.logger.info("🧪 Probando estrategia 2: Buscando ChromeDriver local...")
        
        common_paths = [
            # Windows
            r"C:\Program Files\Google\Chrome\Application\chromedriver.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chromedriver.exe",
            r"C:\Windows\System32\chromedriver.exe",
            r"C:\Windows\chromedriver.exe",
            os.path.join(os.environ.get('USERPROFILE', ''), 'Downloads', 'chromedriver.exe'),
            os.path.join(os.environ.get('USERPROFILE', ''), 'Desktop', 'chromedriver.exe'),
            # Linux/Mac
            "/usr/local/bin/chromedriver",
            "/usr/bin/chromedriver",
            "/opt/google/chrome/chromedriver",
            "/Applications/Google Chrome.app/Contents/MacOS/chromedriver",
            # Directorio actual
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "chromedriver.exe"),
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "chromedriver"),
        ]
        
        for path in common_paths:
            if os.path.exists(path):
                self.logger.info(f"✅ ChromeDriver encontrado en: {path}")
                return path
        
        self.logger.debug("   ⚠️  No se encontró ChromeDriver en ubicaciones comunes")
        return None
    
    def strategy_3_chrome_for_testing(self):
        """Estrategia 3: Descargar de Chrome for Testing"""
        try:
            self.logger.info("🧪 Probando estrategia 3: Descargando Chrome for Testing...")
            
            if not self.chrome_version:
                self.get_chrome_version()
            
            # URL base de Chrome for Testing
            base_url = "https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing"
            
            # Determinar sistema operativo y arquitectura
            if sys.platform == "win32":
                platform = "win64"
                extension = ".exe"
            elif sys.platform == "darwin":
                platform = "mac-arm64" if os.uname().machine == "arm64" else "mac-x64"
                extension = ""
            else:
                platform = "linux64"
                extension = ""
            
            # Intentar con versión específica o la última estable
            versions_to_try = [
                self.chrome_version,
                "120", "119", "118", "117"  # Versiones comunes
            ]
            
            for version in versions_to_try:
                try:
                    # URL para la versión específica
                    url = f"{base_url}/{version}/{platform}/chromedriver-{platform}.zip"
                    
                    self.logger.info(f"   📥 Intentando descargar versión {version}...")
                    
                    response = requests.get(url, stream=True, timeout=30)
                    response.raise_for_status()
                    
                    # Crear directorio temporal
                    temp_dir = os.path.join(os.path.dirname(__file__), "temp_chromedriver")
                    os.makedirs(temp_dir, exist_ok=True)
                    
                    # Extraer zip
                    with zipfile.ZipFile(io.BytesIO(response.content)) as zip_file:
                        zip_file.extractall(temp_dir)
                    
                    # Buscar chromedriver en el zip extraído
                    for root, dirs, files in os.walk(temp_dir):
                        for file in files:
                            if "chromedriver" in file.lower():
                                chromedriver_path = os.path.join(root, file)
                                self.logger.info(f"✅ ChromeDriver descargado: {chromedriver_path}")
                                return chromedriver_path
                    
                except Exception as e:
                    self.logger.debug(f"   ⚠️  Error con versión {version}: {str(e)}")
                    continue
            
            self.logger.debug("   ⚠️  No se pudo descargar ChromeDriver de Chrome for Testing")
            return None
            
        except Exception as e:
            self.logger.debug(f"   ⚠️  Estrategia 3 falló: {str(e)}")
            return None
    
    def strategy_4_system_chromedriver(self):
        """Estrategia 4: Usar ChromeDriver del sistema PATH"""
        self.logger.info("🧪 Probando estrategia 4: Buscando ChromeDriver en PATH...")
        
        # Comprobar si chromedriver está en PATH
        try:
            if sys.platform == "win32":
                result = subprocess.run(['where', 'chromedriver'], 
                                      capture_output=True, text=True)
            else:
                result = subprocess.run(['which', 'chromedriver'], 
                                      capture_output=True, text=True)
            
            if result.returncode == 0:
                driver_path = result.stdout.strip().split('\n')[0]
                self.logger.info(f"✅ ChromeDriver encontrado en PATH: {driver_path}")
                return driver_path
                
        except Exception as e:
            self.logger.debug(f"   ⚠️  Error buscando en PATH: {str(e)}")
        
        return None
    
    def get_driver_path(self):
        """Obtener ruta de ChromeDriver usando múltiples estrategias"""
        self.logger.info("🔧 Buscando ChromeDriver con múltiples estrategias...")
        
        for i, strategy in enumerate(self.strategies):
            self.logger.info(f"   🔄 Intentando estrategia {i+1}...")
            driver_path = strategy()
            if driver_path and os.path.exists(driver_path):
                return driver_path
        
        # Si todas fallan, dar instrucciones claras
        self.logger.error("❌ No se pudo encontrar ChromeDriver con ninguna estrategia")
        self.give_manual_instructions()
        return None
    
    def give_manual_instructions(self):
        """Dar instrucciones manuales al usuario"""
        self.logger.info("\n" + "="*60)
        self.logger.info("💡 INSTRUCCIONES MANUALES PARA INSTALAR CHROMEDRIVER")
        self.logger.info("="*60)
        self.logger.info("1. Descargar ChromeDriver manualmente de:")
        self.logger.info("   https://googlechromelabs.github.io/chrome-for-testing/")
        self.logger.info("")
        self.logger.info("2. Pasos para Windows:")
        self.logger.info("   a. Ve a la página web")
        self.logger.info("   b. Busca 'Latest stable release'")
        self.logger.info("   c. Descarga 'chromedriver-win64.zip'")
        self.logger.info("   d. Extrae 'chromedriver.exe'")
        self.logger.info("   e. Mueve a: C:\\Windows\\System32\\")
        self.logger.info("")
        self.logger.info("3. Pasos alternativos:")
        self.logger.info("   a. Coloca chromedriver.exe en la misma carpeta que este script")
        self.logger.info("   b. O en: C:\\Program Files\\Google\\Chrome\\Application\\")
        self.logger.info("")
        self.logger.info("4. Verifica tu versión de Chrome:")
        self.logger.info("   - Abre Chrome")
        self.logger.info("   - Ve a Configuración → Acerca de Chrome")
        self.logger.info("")
        self.logger.info("5. Ejecuta de nuevo después de instalar")
        self.logger.info("="*60)

# ============================================================================
# CLASE MEJORADA PARA MANEJO DE FECHAS
# ============================================================================
class ManejadorFechasAvanzado:
    def __init__(self, driver, logger):
        self.driver = driver
        self.logger = logger
        self.strategies = [
            self.strategy_1_calendar_button,
            self.strategy_2_javascript_injection,
            self.strategy_3_keyboard_combination,
            self.strategy_4_direct_value_set,
            self.strategy_5_focus_and_type
        ]
    
    def establecer_fecha(self, campo_id, fecha_str, tipo_fecha):
        """Método principal que prueba múltiples estrategias"""
        self.logger.info(f"📅 Intentando establecer fecha {tipo_fecha}: {fecha_str}")
        
        # Convertir fecha DDMMYYYY a DD/MM/YYYY
        fecha_formateada = f"{fecha_str[0:2]}/{fecha_str[2:4]}/{fecha_str[4:]}"
        self.logger.info(f"   📋 Fecha formateada: {fecha_formateada}")
        
        for i, strategy in enumerate(self.strategies):
            self.logger.info(f"   🧪 Probando estrategia {i+1}...")
            if strategy(campo_id, fecha_formateada, tipo_fecha):
                # Verificar si la fecha se estableció correctamente
                if self.verificar_fecha_establecida(campo_id, fecha_formateada):
                    self.logger.info(f"   ✅ Estrategia {i+1} exitosa!")
                    return True
                else:
                    self.logger.info(f"   ⚠️  Estrategia {i+1} no estableció la fecha correctamente")
        
        self.logger.error(f"   ❌ Todas las estrategias fallaron para fecha {tipo_fecha}")
        return False
    
    def strategy_1_calendar_button(self, campo_id, fecha_formateada, tipo_fecha):
        """Estrategia 1: Usar botón del calendario"""
        try:
            campo = self.driver.find_element(By.ID, campo_id)
            
            # Buscar botón del calendario
            calendar_button_selectors = [
                f"//table[@id='{campo_id.replace('_I', '')}']//td[contains(@class, 'dxeButtonEditButton')]",
                f"//input[@id='{campo_id}']/following::td[contains(@class, 'ButtonEditButton')]",
                f"//img[contains(@src, 'DropDown')]/ancestor::td[contains(@class, 'dxeButton')]"
            ]
            
            calendar_button = None
            for selector in calendar_button_selectors:
                try:
                    calendar_button = self.driver.find_element(By.XPATH, selector)
                    break
                except:
                    continue
            
            if calendar_button:
                self.logger.info("   📅 Encontrado botón de calendario, haciendo clic...")
                calendar_button.click()
                time.sleep(2)
                campo.click()
                time.sleep(0.5)
            
            # Limpiar campo
            campo.send_keys(Keys.CONTROL + "a")
            campo.send_keys(Keys.DELETE)
            time.sleep(0.5)
            
            # Escribir fecha
            for char in fecha_formateada:
                campo.send_keys(char)
                time.sleep(0.1)
            
            # Presionar TAB
            campo.send_keys(Keys.TAB)
            time.sleep(1)
            
            return True
            
        except Exception as e:
            self.logger.debug(f"   ⚠️  Estrategia 1 falló: {str(e)}")
            return False
    
    def strategy_2_javascript_injection(self, campo_id, fecha_formateada, tipo_fecha):
        """Estrategia 2: Inyección de JavaScript"""
        try:
            script = f"""
            var campo = document.getElementById('{campo_id}');
            if (!campo) return false;
            
            campo.value = '{fecha_formateada}';
            
            var eventos = ['input', 'change', 'blur', 'keyup', 'keydown', 'keypress'];
            eventos.forEach(function(eventName) {{
                var event = new Event(eventName, {{ bubbles: true }});
                campo.dispatchEvent(event);
            }});
            
            if (typeof ASPx !== 'undefined') {{
                ASPx.ETextChanged('{campo_id.replace('_I', '')}');
                ASPx.ELostFocus('{campo_id.replace('_I', '')}');
            }}
            
            return true;
            """
            
            result = self.driver.execute_script(script)
            time.sleep(1)
            
            if result:
                campo = self.driver.find_element(By.ID, campo_id)
                campo.click()
                time.sleep(0.3)
                campo.send_keys(Keys.TAB)
                time.sleep(0.5)
                return True
            return False
            
        except Exception as e:
            self.logger.debug(f"   ⚠️  Estrategia 2 falló: {str(e)}")
            return False
    
    def strategy_3_keyboard_combination(self, campo_id, fecha_formateada, tipo_fecha):
        """Estrategia 3: Combinaciones de teclado"""
        try:
            campo = self.driver.find_element(By.ID, campo_id)
            campo.click()
            time.sleep(0.5)
            
            campo.send_keys(Keys.CONTROL + "a")
            time.sleep(0.2)
            campo.send_keys(Keys.DELETE)
            time.sleep(0.2)
            
            for _ in range(20):
                campo.send_keys(Keys.BACK_SPACE)
                time.sleep(0.05)
            
            time.sleep(1)
            
            partes = fecha_formateada.split('/')
            
            for char in partes[0]:
                campo.send_keys(char)
                time.sleep(0.15)
            
            campo.send_keys('/')
            time.sleep(0.2)
            
            for char in partes[1]:
                campo.send_keys(char)
                time.sleep(0.15)
            
            campo.send_keys('/')
            time.sleep(0.2)
            
            for char in partes[2]:
                campo.send_keys(char)
                time.sleep(0.15)
            
            campo.send_keys(Keys.ENTER)
            time.sleep(0.5)
            campo.send_keys(Keys.TAB)
            time.sleep(1)
            
            return True
            
        except Exception as e:
            self.logger.debug(f"   ⚠️  Estrategia 3 falló: {str(e)}")
            return False
    
    def strategy_4_direct_value_set(self, campo_id, fecha_formateada, tipo_fecha):
        """Estrategia 4: Establecer valor directamente"""
        try:
            campo = self.driver.find_element(By.ID, campo_id)
            
            self.driver.execute_script(f"""
                var elem = arguments[0];
                elem.setAttribute('value', '{fecha_formateada}');
            """, campo)
            
            time.sleep(0.5)
            
            self.driver.execute_script(f"""
                var elem = arguments[0];
                elem.value = '{fecha_formateada}';
            """, campo)
            
            time.sleep(0.5)
            
            self.driver.execute_script("""
                if (typeof jQuery !== 'undefined') {
                    var elem = arguments[0];
                    $(elem).trigger('input').trigger('change').trigger('blur');
                }
            """, campo)
            
            body = self.driver.find_element(By.TAG_NAME, 'body')
            body.click()
            time.sleep(1)
            
            return True
            
        except Exception as e:
            self.logger.debug(f"   ⚠️  Estrategia 4 falló: {str(e)}")
            return False
    
    def strategy_5_focus_and_type(self, campo_id, fecha_formateada, tipo_fecha):
        """Estrategia 5: Escribir lentamente"""
        try:
            campo = self.driver.find_element(By.ID, campo_id)
            campo.click()
            time.sleep(0.5)
            
            self.driver.execute_script("arguments[0].value = '';", campo)
            time.sleep(0.5)
            
            delay = 0.2
            for char in fecha_formateada:
                campo.send_keys(char)
                time.sleep(delay + random.uniform(-0.05, 0.05))
            
            campo.send_keys(Keys.TAB)
            time.sleep(1)
            
            campo.click()
            time.sleep(0.3)
            campo.send_keys(Keys.TAB)
            time.sleep(0.5)
            
            return True
            
        except Exception as e:
            self.logger.debug(f"   ⚠️  Estrategia 5 falló: {str(e)}")
            return False
    
    def verificar_fecha_establecida(self, campo_id, fecha_esperada):
        """Verificar si la fecha se estableció correctamente"""
        try:
            campo = self.driver.find_element(By.ID, campo_id)
            valor_actual = campo.get_attribute('value')
            
            self.logger.info(f"   🔍 Verificando fecha: Valor actual = '{valor_actual}'")
            
            if not valor_actual or '0100' in valor_actual or 'Digite' in valor_actual:
                self.logger.error(f"   ❌ Fecha no establecida (valor: '{valor_actual}')")
                return False
            
            if valor_actual.strip() == fecha_esperada:
                self.logger.info(f"   ✅ Fecha establecida correctamente: {valor_actual}")
                return True
            else:
                self.logger.warning(f"   ⚠️  Fecha diferente: Esperada '{fecha_esperada}', Actual '{valor_actual}'")
                
                if re.match(r'\d{2}/\d{2}/\d{4}', valor_actual):
                    self.logger.info(f"   ✅ Formato válido detectado: {valor_actual}")
                    return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"   ❌ Error verificando fecha: {str(e)}")
            return False

# ============================================================================
# CLASE PRINCIPAL SIRASAUTOMATION
# ============================================================================
class SirasAutomation:
    
    def __init__(self, headless=True):
        self.driver = None
        self.setup_directories()
        self.driver_path = None
        self.setup_driver(headless)
        self.archivos_procesados = {}
        self.manejador_fechas = None
        
    def setup_directories(self):
        self.descargas_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "descargasPDF")
        if not os.path.exists(self.descargas_dir):
            os.makedirs(self.descargas_dir)
            logger.info(f"Carpeta de descargas creada: {self.descargas_dir}")
    
    def setup_driver(self, headless=False):
        try:
            # Usar nuestro ChromeDriverManager personalizado
            driver_manager = ChromeDriverManager()
            self.driver_path = driver_manager.get_driver_path()
            
            if not self.driver_path:
                raise Exception("No se pudo obtener ChromeDriver")
            
            logger.info(f"✅ Usando ChromeDriver en: {self.driver_path}")
            
            options = webdriver.ChromeOptions()
            
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
            
            # Configuraciones optimizadas
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-gpu")
            options.add_argument("--window-size=1920,1080")
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            
            # User agent actualizado
            options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
            
            if headless:
                options.add_argument("--headless=new")  # Nueva sintaxis para headless
            
            # Crear servicio con el driver_path encontrado
            service = Service(executable_path=self.driver_path)
            
            try:
                self.driver = Chrome(service=service, options=options)
            except Exception as e:
                logger.error(f"❌ Error al crear driver: {str(e)}")
                # Intentar sin service si falla
                self.driver = Chrome(options=options)
            
            # Configurar timeouts
            self.driver.set_page_load_timeout(120)
            self.driver.set_script_timeout(60)
            self.driver.implicitly_wait(15)
            
            # Remover detección de automatización
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            # Inicializar manejador de fechas
            self.manejador_fechas = ManejadorFechasAvanzado(self.driver, logger)
            
            logger.info("✅ Driver configurado exitosamente")
            
        except Exception as e:
            logger.error(f"❌ Error configurando navegador: {str(e)}")
            raise
    
    def calcular_fecha_2_dias_antes(self, fecha_base_str=None):
        """Calcular fecha de 2 días antes de la fecha base o de hoy"""
        try:
            if fecha_base_str:
                fecha_base = datetime.strptime(fecha_base_str, "%d%m%Y")
            else:
                fecha_base = datetime.now()
            
            # Restar 2 días
            fecha_resultado = fecha_base - timedelta(days=2)
            
            # Formatear para el sistema (DDMMYYYY)
            fecha_formateada = fecha_resultado.strftime("%d%m%Y")
            
            logger.info(f"📅 Fecha calculada (2 días antes): {fecha_resultado.strftime('%d/%m/%Y')}")
            logger.info(f"📅 Formato para sistema: {fecha_formateada}")
            
            return fecha_formateada
            
        except Exception as e:
            logger.error(f"❌ Error calculando fecha: {str(e)}")
            # Fallback: usar fecha fija 12/01/2026
            return "12012026"
    
    def procesar_datos(self, correo, password, codigo, fecha_inicial=None, fecha_final=None, headless=True):
        start_time = datetime.now()
        
        try:
            # Validar datos de entrada
            datos = {
                "email": correo.strip() if correo else "",
                "password": password.strip() if password else "",
                "param": codigo.strip() if codigo else "",
            }
            
            # Calcular fechas si no se proporcionan
            if not fecha_inicial:
                fecha_inicial = self.calcular_fecha_2_dias_antes()
            if not fecha_final:
                fecha_final = self.calcular_fecha_2_dias_antes(fecha_inicial)
            
            datos["fecha"] = fecha_inicial
            datos["fechaF"] = fecha_final
            
            # Validar datos requeridos
            if not datos["email"]:
                raise ValueError("El correo es requerido")
            if not datos["password"]:
                raise ValueError("La contraseña es requerida")
            
            logger.info("📋 Datos procesados correctamente")
            logger.info(f"   📧 Email: {datos['email']}")
            logger.info(f"   📅 Fecha inicial: {datos['fecha']} (formato: {datos['fecha'][0:2]}/{datos['fecha'][2:4]}/{datos['fecha'][4:]})")
            logger.info(f"   📅 Fecha final: {datos['fechaF']} (formato: {datos['fechaF'][0:2]}/{datos['fechaF'][2:4]}/{datos['fechaF'][4:]})")
            
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
            logger.error(f"❌ Error en procesar_datos: {str(e)}")
            error_result = {
                "exito": False,
                "error": str(e),
                "archivos_procesados": 0,
                "archivos_descargados": 0,
                "tiempo_total": str(datetime.now() - start_time),
                "fecha_procesamiento": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            return error_result
    
    # ... (resto de los métodos se mantienen igual)
    def reiniciar_driver_si_necesario(self):
        try:
            if self.driver:
                try:
                    self.driver.current_url
                except:
                    logger.warning("⚠️ Driver no responde, reiniciando...")
                    self.driver.quit()
                    time.sleep(5)
                    self.setup_driver(headless=getattr(self, '_headless_mode', True))
                    return True
            return False
        except Exception as e:
            logger.error(f"❌ Error reiniciando driver: {str(e)}")
            return False
    
    def human_typing(self, element, text, delay_range=(0.05, 0.15)):
        try:
            element.clear()
            for char in text:
                element.send_keys(char)
                time.sleep(random.uniform(*delay_range))
        except Exception as e:
            logger.warning(f"⚠️ Error en human_typing: {str(e)}")
            element.clear()
            element.send_keys(text)
    
    def wait_for_element(self, by, selector, timeout=30, clickable=True, retries=3):
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
                logger.warning(f"🔄 Intento {intento + 1}/{retries} - Elemento no encontrado: {selector}")
                if intento < retries - 1:
                    time.sleep(5)
                    if intento == retries - 2:
                        try:
                            self.driver.refresh()
                            time.sleep(10)
                        except:
                            pass
                else:
                    logger.error(f"❌ Elemento no encontrado después de {retries} intentos: {selector}")
                    raise
            except Exception as e:
                logger.error(f"❌ Error inesperado esperando elemento: {str(e)}")
                if intento < retries - 1:
                    time.sleep(5)
                else:
                    raise
    
    def safe_click(self, element, use_js=False, retries=5):
        for intento in range(retries):
            try:
                if use_js:
                    self.driver.execute_script("arguments[0].click();", element)
                    return True
                else:
                    self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
                    time.sleep(1)
                    element.click()
                    return True
                    
            except (ElementClickInterceptedException, StaleElementReferenceException) as e:
                logger.warning(f"⚠️ Error en clic, intento {intento + 1}: {str(e)}")
                if intento < retries - 1:
                    time.sleep(2)
                    try:
                        self.driver.execute_script("arguments[0].click();", element)
                        return True
                    except:
                        continue
                else:
                    logger.error("❌ No se pudo hacer clic después de varios intentos")
                    return False
            except Exception as e:
                logger.warning(f"⚠️ Error inesperado en clic: {str(e)}")
                if intento < retries - 1:
                    time.sleep(2)
                else:
                    return False
        return False
    
    def safe_navigate(self, url, retries=3):
        for intento in range(retries):
            try:
                logger.info(f"🌐 Navegando a: {url} (intento {intento + 1})")
                self.driver.get(url)
                time.sleep(5)
                return True
            except Exception as e:
                logger.warning(f"⚠️ Error navegando (intento {intento + 1}): {str(e)}")
                if intento < retries - 1:
                    time.sleep(10)
                    if self.reiniciar_driver_si_necesario():
                        continue
                else:
                    logger.error("❌ Falló la navegación después de varios intentos")
                    raise
        return False
    
    def establecer_fechas_avanzado(self, fecha_inicial_str, fecha_final_str):
        """Establecer fechas usando el manejador avanzado"""
        try:
            logger.info("📅 INICIANDO CONFIGURACIÓN AVANZADA DE FECHAS")
            
            # IDs de los campos según el HTML
            campo_inicial_id = "FechaInicialFiltro_I"
            campo_final_id = "FechaFinalFiltro_I"
            
            # Establecer fecha inicial
            logger.info("🔧 Configurando fecha INICIAL...")
            if not self.manejador_fechas.establecer_fecha(campo_inicial_id, fecha_inicial_str, "inicial"):
                logger.error("❌ No se pudo establecer fecha inicial con ninguna estrategia")
                return False
            
            time.sleep(2)
            
            # Establecer fecha final
            logger.info("🔧 Configurando fecha FINAL...")
            if not self.manejador_fechas.establecer_fecha(campo_final_id, fecha_final_str, "final"):
                logger.error("❌ No se pudo establecer fecha final con ninguna estrategia")
                return False
            
            # Verificación final
            logger.info("🔍 Verificación final de fechas...")
            self.verificar_fechas_finales()
            
            time.sleep(2)
            logger.info("✅ Fechas configuradas exitosamente")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error estableciendo fechas: {str(e)}")
            return False
    
    def verificar_fechas_finales(self):
        """Verificación final de fechas"""
        try:
            logger.info("🔍 Verificando fechas establecidas...")
            
            # Verificar fecha inicial
            campo_inicial = self.driver.find_element(By.ID, 'FechaInicialFiltro_I')
            valor_inicial = campo_inicial.get_attribute('value')
            logger.info(f"📋 Fecha inicial final: '{valor_inicial}'")
            
            if not valor_inicial or '0100' in valor_inicial or 'Digite' in valor_inicial:
                logger.error(f"❌ Fecha inicial incorrecta: {valor_inicial}")
                return False
            
            # Verificar fecha final
            campo_final = self.driver.find_element(By.ID, 'FechaFinalFiltro_I')
            valor_final = campo_final.get_attribute('value')
            logger.info(f"📋 Fecha final final: '{valor_final}'")
            
            if not valor_final or '0100' in valor_final or 'Digite' in valor_final:
                logger.error(f"❌ Fecha final incorrecta: {valor_final}")
                return False
            
            logger.info("✅ Fechas verificadas correctamente")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error verificando fechas: {str(e)}")
            return False
    
    def select_options(self, credentials, retries=3):
        for intento in range(retries):
            try:
                logger.info(f"⚙️ Configurando opciones (intento {intento + 1})...")
                
                if credentials["param"]:
                    codigo_input = self.wait_for_element(By.ID, "CodigoHabilitacion_I", timeout=30)
                    self.human_typing(codigo_input, credentials["param"])
                    
                    prestador_button = self.wait_for_element(
                        By.XPATH, "//span[contains(text(), 'Ingresar con el Prestador Encontrado')]", timeout=30
                    )
                    self.safe_click(prestador_button)
                    time.sleep(2)
                
                # Navbar consultas
                navbar_consultas = self.wait_for_element(By.ID, "menuNoAuth_DXI2_T", timeout=30)
                self.safe_click(navbar_consultas)
                
                # Opción lista resumida
                lista_resumida = self.wait_for_element(
                    By.XPATH, "//span[contains(text(), 'LISTA RESUMIDA DE ATENCIONES')]", timeout=30
                )
                self.safe_click(lista_resumida)
                
                time.sleep(8)
                
                # USAR MÉTODO AVANZADO PARA FECHAS
                if not self.establecer_fechas_avanzado(credentials["fecha"], credentials["fechaF"]):
                    logger.error("❌ No se pudieron establecer las fechas, reintentando...")
                    if intento < retries - 1:
                        time.sleep(5)
                        continue
                    else:
                        raise Exception("No se pudieron establecer las fechas después de varios intentos")
                
                # Verificar
                time.sleep(2)
                if not self.verificar_fechas_finales():
                    raise Exception("Las fechas no se establecieron correctamente")
                
                # Hacer clic en Consultar
                consultar_button = self.wait_for_element(
                    By.XPATH, "//span[contains(text(), 'Consultar')]", timeout=30
                )
                self.safe_click(consultar_button)
                
                logger.info("✅ Opciones configuradas exitosamente")
                return True
                
            except Exception as e:
                logger.error(f"❌ Error configurando opciones (intento {intento + 1}): {str(e)}")
                if intento < retries - 1:
                    time.sleep(5)
                    try:
                        self.driver.refresh()
                        time.sleep(5)
                    except:
                        pass
                else:
                    raise
        return False
    
    def verificar_descarga_completada(self, timeout=120):
        inicio = time.time()
        archivos_iniciales = set([f for f in os.listdir(self.descargas_dir) 
                                if f.endswith('.pdf') and not f.endswith('.crdownload')])
        logger.info("⏳ Esperando descarga...")
        
        while time.time() - inicio < timeout:
            try:
                archivos_actuales = set([f for f in os.listdir(self.descargas_dir) 
                                       if f.endswith('.pdf') and not f.endswith('.crdownload')])
                archivos_temporales = [f for f in os.listdir(self.descargas_dir) 
                                     if f.endswith('.crdownload')]
                
                if archivos_temporales:
                    logger.info("📥 Descarga en progreso...")
                    time.sleep(5)
                    continue
                
                nuevos_archivos = archivos_actuales - archivos_iniciales
                
                if nuevos_archivos:
                    nuevo_archivo = list(nuevos_archivos)[0]
                    archivo_path = os.path.join(self.descargas_dir, nuevo_archivo)
                    
                    if os.path.exists(archivo_path) and os.path.getsize(archivo_path) > 1000:
                        logger.info(f"✅ Descarga completada: {nuevo_archivo}")
                        return archivo_path
                        
                time.sleep(3)
                
            except Exception as e:
                logger.error(f"❌ Error verificando descarga: {str(e)}")
                time.sleep(3)
                
        logger.error("⏰ Timeout esperando descarga")
        return None
    
    def generar_nombre_archivo(self, elemento):
        try:
            def limpiar_texto(texto):
                if not texto:
                    return ""
                caracteres_prohibidos = ['<', '>', ':', '"', '|', '?', '*', '/', '\\', '\n', '\r', '\t']
                for char in caracteres_prohibidos:
                    texto = texto.replace(char, '')
                return texto.strip()
            
            no_radicado = limpiar_texto(elemento.get('no_radicado', ''))
            
            if no_radicado:
                nombre = f"{no_radicado}.pdf"
            else:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                nombre = f"SinRadicado_{timestamp}.pdf"
            
            nombre = '_'.join(nombre.split())
            nombre = nombre.replace('__', '_')
            
            return nombre
            
        except Exception as e:
            logger.error(f"❌ Error generando nombre de archivo: {str(e)}")
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            return f"archivo_{timestamp}.pdf"
    
    def renombrar_archivo_descargado(self, archivo_original, elemento):
        try:
            if not os.path.exists(archivo_original):
                logger.error(f"❌ Archivo original no existe: {archivo_original}")
                return None
            
            nuevo_nombre = self.generar_nombre_archivo(elemento)
            nuevo_path = os.path.join(self.descargas_dir, nuevo_nombre)
            
            if os.path.exists(nuevo_path):
                timestamp = datetime.now().strftime("%H%M%S")
                nombre_base = nuevo_nombre.replace('.pdf', '')
                nuevo_nombre = f"{nombre_base}_{timestamp}.pdf"
                nuevo_path = os.path.join(self.descargas_dir, nuevo_nombre)
            
            shutil.move(archivo_original, nuevo_path)
            logger.info(f"📄 Archivo renombrado: {os.path.basename(archivo_original)} → {nuevo_nombre}")
            
            self.archivos_procesados[nuevo_nombre] = elemento
            
            return nuevo_path
            
        except Exception as e:
            logger.error(f"❌ Error renombrando archivo: {str(e)}")
            return archivo_original
    
    def login(self, credentials, retries=3):
        for intento in range(retries): 
            try:
                logger.info(f"🔐 Iniciando login (intento {intento + 1})...")
                
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
                    logger.info("✅ Login exitoso")
                    return True
                
            except Exception as e:
                logger.error(f"❌ Error durante login (intento {intento + 1}): {str(e)}")
                if intento < retries - 1:
                    time.sleep(15)
                    self.reiniciar_driver_si_necesario()
                else:
                    raise
        return False
    
    def obtener_info_paginacion(self):
        try:
            paginacion = self.wait_for_element(By.CLASS_NAME, "dxp-summary", timeout=20, clickable=False)
            texto = paginacion.text
            logger.info(f"📊 Texto paginación: {texto}")
            
            partes = texto.split()
            pagina_actual = int(partes[1])
            total_paginas = int(partes[3])
            total_elementos = int(partes[4].replace('(', '').replace(')', ''))
            
            return pagina_actual, total_paginas, total_elementos
            
        except Exception as e:
            logger.error(f"❌ Error obteniendo paginación: {str(e)}")
            return 1, 1, 0
    
    def obtener_elementos_pagina(self):
        try:
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
                        logger.info(f"📋 Extraído: {elemento_info['primer_nombre']} {elemento_info['primer_apellido']} - ID: {elemento_info['identificacion']}")
                        
                except Exception as e:
                    logger.warning(f"⚠️ Error procesando fila {i}: {str(e)}")
                    continue
            
            logger.info(f"📊 Total elementos encontrados: {len(elementos)}")
            return elementos
            
        except Exception as e:
            logger.error(f"❌ Error obteniendo elementos: {str(e)}")
            return []
    
    def hacer_clic_ver_reporte(self, elemento):
        estrategias = [
            (By.XPATH, f"//td[contains(text(), '{elemento['identificacion']}')]/..//span[contains(text(), 'Ver Reporte')]"),
        ]
        
        for by, selector in estrategias:
            try:
                boton_reporte = self.wait_for_element(by, selector, timeout=10)
                if self.safe_click(boton_reporte):
                    logger.info(f"✅ Clic exitoso en VER REPORTE para {elemento['identificacion']}")
                    return True
                    
            except TimeoutException:
                continue
            except Exception as e:
                logger.warning(f"⚠️ Error en estrategia de clic: {str(e)}")
                continue
        
        logger.error(f"❌ No se pudo hacer clic en VER REPORTE para {elemento['identificacion']}")
        return False
    
    def procesar_reporte(self, elemento):
        try:
            logger.info(f"📄 Procesando reporte para {elemento['identificacion']} - Radicado: {elemento['no_radicado']}")
            
            time.sleep(2)
            
            button_descarga = self.wait_for_element(By.ID, "DocumentViewer_Splitter_Toolbar_Menu_DXI9_T", timeout=45)
            
            if self.safe_click(button_descarga):
                logger.info("📥 Descarga iniciada")
                
                archivo_descargado = self.verificar_descarga_completada(timeout=180)
                
                if archivo_descargado:
                    logger.info(f"✅ PDF descargado: {os.path.basename(archivo_descargado)}")
                    
                    archivo_renombrado = self.renombrar_archivo_descargado(archivo_descargado, elemento)
                    
                    estrategias_volver = [
                        (By.XPATH, "//span[contains(text(), 'Volver a lista')]"),
                    ]
                    
                    boton_encontrado = False
                    for by, selector in estrategias_volver:
                        try:
                            regresar = self.wait_for_element(by, selector, timeout=10)
                            if self.safe_click(regresar):
                                logger.info("↩️ Regresando a lista...")
                                boton_encontrado = True
                                break
                        except TimeoutException:
                            continue
                    
                    if not boton_encontrado:
                        logger.info("↩️ Usando navegador back...")
                        self.driver.back()
                    
                    time.sleep(2)
                    return True
                else:
                    logger.error("❌ Descarga no completada")
                    return False
            else:
                logger.error("❌ No se pudo hacer clic en descarga")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error procesando reporte: {str(e)}")
            try:
                self.driver.back()
                time.sleep(2)
            except:
                pass
            return False
    
    def procesar_todas_paginas(self):
        try:
            pagina_actual, total_paginas, total_elementos = self.obtener_info_paginacion()
            logger.info(f"📚 Iniciando procesamiento: {total_elementos} elementos en {total_paginas} páginas")
            
            for pagina in range(pagina_actual, total_paginas + 1):
                logger.info(f"📖 === PROCESANDO PÁGINA {pagina} DE {total_paginas} ===")
                
                elementos = []
                for intento_elementos in range(3):
                    elementos = self.obtener_elementos_pagina()
                    if elementos:
                        break
                    logger.warning(f"⚠️ No se encontraron elementos, reintentando... ({intento_elementos + 1}/3)")
                    time.sleep(2)
                
                if not elementos:
                    logger.warning("⚠️ No se encontraron elementos en esta página, continuando...")
                    continue
                
                for idx, elemento in enumerate(elementos):
                    try:
                        logger.info(f"🔍 Procesando {idx + 1}/{len(elementos)}: {elemento['primer_nombre']} {elemento['primer_apellido']} - ID: {elemento['identificacion']}")
                        
                        if self.hacer_clic_ver_reporte(elemento):
                            if self.procesar_reporte(elemento):
                                logger.info(f"✅ Completado: {elemento['identificacion']}")
                                
                                self.wait_for_element(By.XPATH, "//table[contains(@id, 'gridResumidas')]", timeout=30, clickable=False)
                                time.sleep(5)
                            else:
                                logger.error(f"❌ Error procesando reporte: {elemento['identificacion']}")
                        else:
                            logger.error(f"❌ No se pudo acceder al reporte: {elemento['identificacion']}")
                        
                    except Exception as e:
                        logger.error(f"❌ Error con elemento {elemento['identificacion']}: {str(e)}")
                        continue
                
                if pagina < total_paginas:
                    try:
                        siguiente_boton = self.driver.find_element(By.XPATH, f"//a[contains(text(), '{pagina + 1}')]")
                        if self.safe_click(siguiente_boton):
                            time.sleep(10)
                            
                            pagina_actual, total_paginas, total_elementos = self.obtener_info_paginacion()
                        else:
                            logger.error(f"❌ No se pudo navegar a página {pagina + 1}")
                            break
                            
                    except Exception as e:
                        logger.error(f"❌ Error navegando a página {pagina + 1}: {str(e)}")
                        break
            
            logger.info("🎉 Procesamiento de todas las páginas completado")
            
        except Exception as e:
            logger.error(f"❌ Error en procesamiento general: {str(e)}")
            raise
    
    def generar_reporte_archivos(self):
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
            
            logger.info(f"📋 Reporte generado: {reporte_path}")
            
        except Exception as e:
            logger.error(f"❌ Error generando reporte: {str(e)}")
    
    def cleanup_driver(self):
        try:
            if self.driver:
                self.driver.quit()
                logger.info("✅ Driver cerrado correctamente")
        except Exception as e:
            logger.warning(f"⚠️ Error cerrando driver: {str(e)}")
    
    def ejecutar_automatizacion(self, datos):
        try:
            logger.info("🚀 === INICIANDO AUTOMATIZACIÓN SIRAS ===")
            
            if not self.login(datos):
                raise Exception("❌ No se pudo completar el login")
            
            if not self.select_options(datos):
                raise Exception("❌ No se pudieron configurar las opciones")
            
            time.sleep(10)
            
            self.procesar_todas_paginas()
            
            self.generar_reporte_archivos()
            
            archivos_descargados = [f for f in os.listdir(self.descargas_dir) if f.endswith('.pdf')]
            
            logger.info("=" * 50)
            logger.info("📊 RESUMEN DE PROCESAMIENTO")
            logger.info("=" * 50)
            logger.info(f"Archivos descargados: {len(archivos_descargados)}")
            logger.info(f"Archivos procesados exitosamente: {len(self.archivos_procesados)}")
            logger.info(f"Directorio de descargas: {self.descargas_dir}")
            logger.info("=" * 50)
            
            if self.archivos_procesados:
                logger.info("📂 ARCHIVOS PROCESADOS:")
                for nombre_archivo, elemento in self.archivos_procesados.items():
                    logger.info(f"   ✅ {nombre_archivo} (ID: {elemento['identificacion']}, Radicado: {elemento['no_radicado']})")
            else:
                logger.warning("⚠️ No se procesaron archivos exitosamente")
            
            return {
                "exito": True,
                "archivos_procesados": len(self.archivos_procesados),
                "archivos_descargados": len(archivos_descargados),
                "directorio_descargas": self.descargas_dir,
                "archivos_detalle": list(self.archivos_procesados.keys()),
                "mensaje": "✅ Automatización completada exitosamente"
            }
                
        except Exception as e:
            logger.error(f"❌ Error en automatización: {str(e)}")
            logger.error("Stack trace:", exc_info=True)
            
            return {
                "exito": False,
                "error": str(e),
                "archivos_procesados": len(self.archivos_procesados),
                "archivos_descargados": 0,
                "directorio_descargas": self.descargas_dir,
                "mensaje": f"❌ Error en automatización: {str(e)}"
            }

# ============================================================================
# FUNCIONES DE UTILIDAD
# ============================================================================
def ejecutar_siras_bot(correo, password, codigo, fecha_inicial=None, fecha_final=None, headless=True):
    automation = None
    
    try:
        logger.info("🤖 Iniciando bot de SIRAS...")
        
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
        logger.error(f"❌ Error ejecutando bot: {str(e)}")
        return {
            "exito": False,
            "error": str(e),
            "mensaje": f"❌ Error ejecutando bot: {str(e)}"
        }
        
    finally:
        if automation:
            automation.cleanup_driver()

def main():
    # Datos de ejemplo
    datos_ejemplo = {
        "correo": "dirimagenes@vallesaludips.com",
        "password": "SE0uJ9dC", 
        "codigo": "760010732306",
    }
    
    logger.info("🚀 Ejecutando con datos de ejemplo (fechas calculadas automáticamente)")
    
    try:
        headless_mode = '--headless' in sys.argv or '-h' in sys.argv
        
        resultado = ejecutar_siras_bot(
            correo=datos_ejemplo["correo"],
            password=datos_ejemplo["password"],
            codigo=datos_ejemplo["codigo"],
            fecha_inicial=None,  # Se calculará automáticamente
            fecha_final=None,    # Se calculará automáticamente
            headless=headless_mode
        )
        
        print("\n" + "="*50)
        print("📊 RESULTADO FINAL")
        print("="*50)
        for key, value in resultado.items():
            if key not in ['datos_entrada', 'archivos_detalle']:
                print(f"{key}: {value}")
        print("="*50)
        
        if resultado.get("exito"):
            logger.info("🎉 AUTOMATIZACIÓN COMPLETADA EXITOSAMENTE")
        else:
            logger.error("❌ AUTOMATIZACIÓN FALLÓ")
            sys.exit(1)
        
    except KeyboardInterrupt:
        logger.warning("⚠️ Proceso interrumpido por el usuario")
    except Exception as e:
        logger.error(f"💥 Error fatal en la automatización: {str(e)}")
        logger.error("Stack trace completo:", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()