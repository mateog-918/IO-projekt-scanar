from flask import Flask
from flask import request, make_response, send_from_directory
from flasgger import Swagger
import re
import os
from flask_sqlalchemy import SQLAlchemy
from app.models.employee import db

def create_app():
    app = Flask(__name__)
    Swagger(app)

    #Konfiguracja bazy danych - używamy ścieżki bezwzględnej do folderu instance
    instance_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'instance')
    os.makedirs(instance_path, exist_ok=True)  # Tworzymy folder instance jeśli nie istnieje
    db_path = os.path.join(instance_path, 'scanar.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    #Tworzenie tabel w bazie danych
    with app.app_context():
        db.create_all()

    @app.route('/')
    def home():
        return "Flask is running!"
    
    @app.route("/swagger.yaml")
    def swagger_spec():
        return send_from_directory(os.path.dirname(__file__), 'swagger.yaml')
    
    @app.after_request
    def add_cors_headers(response):
        http_origin = request.environ.get('HTTP_ORIGIN', None)
        http_access_ctrl_req_headers = request.environ.get('HTTP_ACCESS_CONTROL_REQUEST_HEADERS', None)
        if http_origin and re.search(r'^[a-zA-Z0-9\-_\.:/]+$', http_origin):
            response.headers['Access-Control-Allow-Origin'] = http_origin
            response.headers['Access-Control-Allow-Credentials'] = "true"
            response.headers['Access-Control-Allow-Methods'] = "GET, POST, PUT, DELETE, OPTIONS"
            response.headers['Access-Control-Allow-Headers'] = http_access_ctrl_req_headers or "*"
        return response
    
    # Obsługa OPTIONS dla CORS
    @app.route('/<path:path>', methods=['OPTIONS'])
    def options(path):
        response = make_response()
        response.headers['Access-Control-Allow-Origin'] = "*"
        response.headers['Access-Control-Allow-Methods'] = "GET, POST, PUT, DELETE, OPTIONS"
        response.headers['Access-Control-Allow-Headers'] = "*"

        return response
    
    #Register blueprints
    from app.api.verification import verification_bp
    app.register_blueprint(verification_bp, url_prefix='/api/verification')

    from app.api.manage_employees import employees_bp
    app.register_blueprint(employees_bp, url_prefix='/api/manage_employees')
    
    return app


if __name__ == "__main__":
    app = create_app()

    app.run(host='0.0.0.0', port=5000, debug=True)