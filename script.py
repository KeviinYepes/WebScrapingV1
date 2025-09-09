import requests 
from bs4 import BeautifulSoup

# Url of the site
url = "https://dockerlabs.es/"
# Request to the site
respuesta = requests.get(url)

if respuesta.status_code == 200:
    soup = BeautifulSoup(respuesta.text, 'html.parser')

    maquinas = soup.find_all('div', onclick=True)

    for maquina in maquinas:
        EventMaquina = maquina['onclick'] 
        nombre_maquina = EventMaquina.split("'")[1]
        dificultad = maquina.find('span', class_='badge')
        autor = EventMaquina.split("'")[7]
        
        if nombre_maquina is not None and dificultad is not None and autor is not None:
            print(f"Máquina: {nombre_maquina}, Dificultad: {dificultad.text.strip()}, autor: {autor}")
        

else:
    print(f"Error al acceder a la página {respuesta.status_code}")
