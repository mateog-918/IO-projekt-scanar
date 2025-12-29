from flask import Flask
from flask import request, make_response
from flasgger import Swagger
import re

def create_app():
    app = Flask(__name__)
    Swagger(app)

    @app.route('/')
    def home():
        return "Flask is running!"
    
    @app.route("/swagger.yaml")
    def swagger_spec():
        return app.send_static_file("swagger.yaml")
    
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
    
    return app


if __name__ == "__main__":
    app = create_app()

    app.run(host='0.0.0.0', port=5000, debug=True)