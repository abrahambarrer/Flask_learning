from flask import Flask, jsonify
from flask_swagger_ui import get_swaggerui_blueprint

app = Flask(__name__)

# --- Configuración de Swagger ---
SWAGGER_URL = '/docs'  # URL para acceder a Swagger UI
API_URL = '/static/swagger.json'  # ruta al archivo con la especificación OpenAPI

swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,  # URL base
    API_URL,      # JSON con la documentación
    config={'app_name': "Ejemplo API Flask + Swagger"}
)

app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)


# --- Endpoints de la API ---
@app.route('/saludo', methods=['GET'])
def saludo():
    """Endpoint de prueba"""
    return jsonify({"mensaje": "Hola desde la API Flask"})


if __name__ == '__main__':
    app.run(debug=True)
