from selenium.webdriver import Chrome
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait as Wait
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    ElementClickInterceptedException,
    WebDriverException
)
import time
import random
import sys
import traceback

#OBJ
privateData = {
    "email": "dirimagenes@vallesaludips.com",
    "password": "SE0uJ9dC",
    "param": "760010732306",
    "fecha": "1092025",
}

# Simula escritura humana con retrasos aleatorios entre caracteres
def human_typing(element, text, delay_range=(0.05, 0.2)):
    for char in text:
        element.send_keys(char)
        time.sleep(random.uniform(*delay_range))


service = Service(ChromeDriverManager().install())
options = webdriver.ChromeOptions()
options.add_argument("--window-size=1080,1080")
driver = Chrome(service=service, options=options)
driver.get("https://www.siras.com.co/siras/Seguridad/Login?Modo=1")

def login(driver, privateData):
    try:   
        username_input = Wait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "Email_I"))
        )
        username_input.send_keys(privateData["email"])

        password_input = Wait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "Password_I"))
        )
        password_input.send_keys(privateData["password"])

        Login_button = Wait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "btnIngresar"))
        )
        Login_button.click()
        print("Login successful")
    except: 
        print(f"An error occurred during login: {traceback.format_exc()}")
    
def select_options(driver,privateData):

        Codigo_Habilitacion_input = Wait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "CodigoHabilitacion_I"))
        )
        Codigo_Habilitacion_input.send_keys(privateData["param"])
        
        button_prestador_encontrado = Wait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'Ingresar con el Prestador Encontrado')]"))
        )
        # driver.execute_script("arguments[0].click();", button_prestador_encontrado)
        button_prestador_encontrado.click()
        button_prestador_encontrado.click()
        
        #Despliega Navbar
        button_navbar_consultas = Wait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "menuNoAuth_DXI2_T"))
        )
        button_navbar_consultas.click()  
                                             
        # Selecciona Opcion_Consultas (lista resumida de atenciones)
        button_opcion_consultas = Wait(driver, 10).until(
             EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'LISTA RESUMIDA DE ATENCIONES')]"))
        )
        button_opcion_consultas.click()

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
        paginasCount = 0
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
    
def obtener_elementos_por_pagina(driver):
       # Busca la tabla:
       Wait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//table[contains(@id, 'gridResumidas')]"))
        )
       # Busca los datos de todos los tr
       filas = driver.find_elements(By.XPATH, "//tr[contains(@id, 'gridResumidas_DXDataRow')]")
       
       


if  __name__ == "__main__":
    login(driver, privateData)
    select_options(driver, privateData)
    total_pages(driver)
    obtener_elementos_por_pagina(driver)
    time.sleep(15)
    driver.quit()
    
    
