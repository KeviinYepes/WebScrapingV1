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

privateData = {
    "email": "dirimagenes@vallesaludips.com",
    "password": "SE0uJ9dC",
    "param": "760010732306"
}

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
    try:
        Codigo_Habilitacion_input = Wait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "CodigoHabilitacion_I"))
        )
        Codigo_Habilitacion_input.send_keys(privateData["param"])
        #TODO : acomodar este fucking fiel
        prestador_prestador_encontrado = Wait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, "botonIngresarEncontrado_CD"))
        )
        time.sleep(2)
        prestador_prestador_encontrado.click()
        # if not privateData.get("param"):
        #     prestador_predeterminado_input = Wait(driver, 10).until(
        #         EC.element_to_be_clickable((By.ID, "botonIngresar"))
        #     )
        #     time.sleep(2)
        #     prestador_predeterminado_input.click()
        # else: 
        #     prestador_prestador_encontrado = Wait(driver, 10).until(
        #         EC.element_to_be_clickable((By.ID, "botonIngresarEncontrado"))
        #     )
        #     time.sleep(2)
        #     prestador_prestador_encontrado.click()
    except:
        print(f"An error occurred during option selection: {traceback.format_exc()}")


if  __name__ == "__main__":
    login(driver, privateData)
    select_options(driver, privateData)
    time.sleep(15)
    driver.quit()
