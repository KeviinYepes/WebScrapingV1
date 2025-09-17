from flask import Flask, render_template, request
import os
from webscraping import SirasAutomation
import time

current_dir = os.path.dirname(os.path.abspath(__file__))
template_dir = os.path.join(current_dir, '..', 'views')

application = Flask(__name__, template_folder=template_dir,  static_url_path='/static')

@application.route('/')
def index():
    # Siempre mostrar el formulario vacío
    return render_template("form.html")

@application.route('/data', methods=["POST"])
def form_data():
    # Capturar datos del formulario
    correo = request.form.get("email")
    password = request.form.get("password")
    codigo = request.form.get("codigo")
    fecha_inicial = request.form.get("fecha_inicial")
    fecha_final = request.form.get("fecha_final")
    
    # Validar campos
    if not all([correo, password, codigo, fecha_inicial, fecha_final]):
        return render_template("form.html", error="Todos los campos son obligatorios")
    else:
        try:
            automation = SirasAutomation(headless=True)
            datos = automation.procesar_datos(correo, password, codigo, fecha_inicial, fecha_final)
            time.sleep(4)
            
            # MOSTRAR UNA PÁGINA DIFERENTE con los resultados
        except Exception as e:
            error_msg = f"Error procesando los datos: {str(e)}"
            return render_template("form.html", error=error_msg)

if __name__ == '__main__':
    application.run(debug=True)