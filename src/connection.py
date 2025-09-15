from flask import Flask, render_template
import os

    # Obtener la ruta absoluta del directorio actual
current_dir = os.path.dirname(os.path.abspath(__file__))
    # Subir un nivel (desde src/descargasPDF a src/) y luego a views
template_dir = os.path.join(current_dir, '..', 'views')

application = Flask(__name__, template_folder=template_dir,static_folder="static")
@application.route('/')
def index():
    return render_template("form.html")

application.run(debug=True)