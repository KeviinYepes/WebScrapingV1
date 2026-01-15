from selenium.webdriver import Chrome 
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait as Wait
import time
#Credenciales 
USER = "standard_user"
PASSWORD = "secret_sauce"
def main():
    service = Service(ChromeDriverManager().install()) #instala el driver
    option = webdriver.ChromeOptions() #configuraciones del navegador
    # option.add_argument("--headless") #no abre la ventana del navegador
    option.add_argument("--window-size=1920,1080") #tamaño ventana
    driver = Chrome(service=service, options=option)
    driver.get("https://www.saucedemo.com/") #abre la url
    #Seleccionamos  los elementos de la pagina
    user_input = driver.find_element(By.ID,"user-name")
    password_input = driver.find_element(By.ID,"password")
    button = driver.find_element(By.ID,"login-button")
    #Añadimos los valores a los campos
    password_input.send_keys(PASSWORD)
    user_input.send_keys(USER)
    #Presionamos el botón
    button.click()
    time.sleep(15)
    driver.quit() #cierra el navegador
if __name__ == "__main__":
    main()
