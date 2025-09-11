# from selenium.webdriver import Chrome
# from selenium import webdriver
# from webdriver_manager.chrome import ChromeDriverManager
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.webdriver.support.ui import WebDriverWait as Wait
# from selenium.common.exceptions import (
#     TimeoutException,
#     NoSuchElementException,
#     ElementClickInterceptedException,
#     WebDriverException
# )
# import time
# import random
# import sys
# import traceback

# #OBJ
# privateData = {
#     "email": "dirimagenes@vallesaludips.com",
#     "password": "SE0uJ9dC",
#     "param": "760010732306",
#     "fecha": "1092025",
# }

# # Simula escritura humana con retrasos aleatorios entre caracteres
# def human_typing(element, text, delay_range=(0.05, 0.2)):
#     for char in text:
#         element.send_keys(char)
#         time.sleep(random.uniform(*delay_range))


# service = Service(ChromeDriverManager().install())
# options = webdriver.ChromeOptions()
# options.add_argument("--window-size=1080,1080")
# driver = Chrome(service=service, options=options)
# driver.get("https://www.siras.com.co/siras/Seguridad/Login?Modo=1")

# def login(driver, privateData):
#     try:   
#         username_input = Wait(driver, 10).until(
#             EC.element_to_be_clickable((By.ID, "Email_I"))
#         )
#         username_input.send_keys(privateData["email"])

#         password_input = Wait(driver, 10).until(
#             EC.element_to_be_clickable((By.ID, "Password_I"))
#         )
#         password_input.send_keys(privateData["password"])

#         Login_button = Wait(driver, 10).until(
#             EC.element_to_be_clickable((By.ID, "btnIngresar"))
#         )
#         Login_button.click()
#         print("Login successful")
#     except: 
#         print(f"An error occurred during login: {traceback.format_exc()}")
    
# def select_options(driver,privateData):

#         Codigo_Habilitacion_input = Wait(driver, 10).until(
#             EC.element_to_be_clickable((By.ID, "CodigoHabilitacion_I"))
#         )
#         Codigo_Habilitacion_input.send_keys(privateData["param"])
        
#         button_prestador_encontrado = Wait(driver, 10).until(
#             EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'Ingresar con el Prestador Encontrado')]"))
#         )
#         # driver.execute_script("arguments[0].click();", button_prestador_encontrado)
#         button_prestador_encontrado.click()
#         button_prestador_encontrado.click()
        
#         #Despliega Navbar
#         button_navbar_consultas = Wait(driver, 10).until(
#             EC.element_to_be_clickable((By.ID, "menuNoAuth_DXI2_T"))
#         )
#         button_navbar_consultas.click()  
                                             
#         # Selecciona Opcion_Consultas (lista resumida de atenciones)
#         button_opcion_consultas = Wait(driver, 10).until(
#              EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'LISTA RESUMIDA DE ATENCIONES')]"))
#         )
#         button_opcion_consultas.click()

#         #fecha inicial
#         fecha_inicial_input = Wait(driver, 10).until(
#             EC.element_to_be_clickable((By.ID, "FechaInicialFiltro_I"))
#         )
#         fecha_inicial_input.click()
#         time.sleep(1)
#         human_typing(fecha_inicial_input, privateData["fecha"])

#         #fecha final 
#         fecha_final_input = Wait(driver, 10).until(
#             EC.element_to_be_clickable((By.ID, "FechaFinalFiltro_I"))
#         )
#         fecha_final_input.click()
#         time.sleep(1)
#         human_typing(fecha_final_input, privateData["fecha"])

#         #Botón consultar 
#         button_consultar = Wait(driver, 10).until(
#             EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'Consultar')]"))
#         )
#         button_consultar.click()

# def total_pages(driver):
#     try:   
#         paginasCount = 0
#         paginacion = Wait(driver, 10).until(
#             EC.presence_of_element_located((By.CLASS_NAME, "dxp-summary"))
#         )
        
#         # Extraer información usando split
#         partes = paginacion.text.split()

#         # "Página 1 de 6 (51 elementos)"
#         pagina_actual = int(partes[1])
#         total_paginas = int(partes[3])
#         total_elementos = int(partes[4].replace('(', '').replace(')', ''))
        
#         print(f"Página actual: {pagina_actual}")
#         print(f"Total de páginas: {total_paginas}")
#         print(f"Total de elementos: {total_elementos}")

#         return pagina_actual, total_paginas, total_elementos
          
#     except Exception as e: 
#          print(f"Error obteniendo información de paginación: {str(e)}")
#          return 1, 1, 0
    

       
       


# if  __name__ == "__main__":
#     login(driver, privateData)
#     select_options(driver, privateData)
#     total_pages(driver)
#     # obtener_elementos_por_pagina(driver)
#     time.sleep(15)
#     driver.quit()
    
    
# ////
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
        # Esperar a que la tabla cargue
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
                
                if len(celdas) >= 8:  # Asegurar que tiene todas las columnas
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
    
    for pagina in range(pagina_actual, total_paginas + 1):
        print(f"\n=== Procesando página {pagina} de {total_paginas} ===")
        
        # Obtener elementos de la página actual
        elementos = obtener_elementos_por_pagina(driver)
        
        # Procesar cada elemento
        for elemento in elementos:
            try:
                
                boton_reporte = Wait(driver, 10).until(
                    EC.element_to_be_clickable((By.ID, "gridResumidas_DXCBtn1"))
                )
                # Encontrar y hacer clic en "VER REPORTE" para este elemento
                # boton_reporte = Wait(driver, 10).until(
                #     EC.element_to_be_clickable((By.XPATH, f"//td[contains(text(), '{elemento['identificacion']}')]/..//a[contains(text(), 'VER REPORTE')]"))
                # )
                driver.execute_script("arguments[0].scrollIntoView();", boton_reporte)
                time.sleep(1)
                boton_reporte.click()
                # Procesar el reporte
                procesar_reporte()
                
                # Volver a la página principal
                driver.back()
                time.sleep(2)
                
                # Esperar a que la tabla se recargue
                Wait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, "//table[contains(@id, 'gridResumidas')]"))
                )
                
            except Exception as e:
                print(f"Error procesando elemento: {str(e)}")
                continue
        
        # Ir a la siguiente página si no es la última
        if pagina < total_paginas:
            try:
                siguiente_boton = driver.find_element(By.XPATH, f"//a[contains(text(), '{pagina + 1}')]")
                siguiente_boton.click()
                time.sleep(3)
                
                # Actualizar información de paginación después de cambiar de página
                pagina_actual, total_paginas, total_elementos = total_pages(driver)
                
            except Exception as e:
                print(f"Error yendo a página {pagina + 1}: {str(e)}")
                break

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
    # procesar_todas_las_paginas(driver)
    
    time.sleep(5)
    driver.quit()