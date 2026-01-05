""""
Blueprints for verification-related API endpoints.
"""
import base64
import os

from flask import Blueprint, request, jsonify
from flask import Flask
from flask_cors import CORS
from app.services.qr_service import QRService
from app.services.face_recog import matches_face_image
from app.models.employee import Employee


verification_bp = Blueprint('verification', __name__)

# Ścieżka do folderu zapisu
QR_FOLDER = './QRcode'

# Tworzymy folder, jeśli nie istnieje
if not os.path.exists(QR_FOLDER):
    os.makedirs(QR_FOLDER)

@verification_bp.route('/qr', methods=['POST'])
def verify_qr():
    """
    Endpoint do weryfikacji QR kodu
    
    Expected JSON:
    {
        "qr_data": "hash_qr_kodu"
    }
    
    Returns:
    {
        "success": true/false,
        "message": "Witaj! Jan Kowalski",
        "employee": {
            "id": 1,
            "name": "Jan Kowalski",
            "position": "Engineer",
            "department": "IT"
        }
    }
    """
    try:
        data = request.get_json()

        if not data or 'qr_data' not in data:
            return jsonify({'success': False, 'message': 'Brak danych QR kodu', 'employee': None}), 400
        
        qr_data = data['qr_data']

        result = QRService.validate_qr_code(qr_data)

        status_code = 200 if result['success'] else 404
        return jsonify(result), status_code

    except Exception as e:
        return jsonify({'success': False, 'message': str(e), 'employee': None}), 500


@verification_bp.route('/employees/<int:employee_id>/match', methods=['POST'])
def match_employee_face(employee_id):
    """POST multipart/form-data with file field 'image'. Returns JSON {'match': true/false}.
    Uses a fixed matching tolerance of 0.6 (not configurable via the API).
    """
    try:
        file = request.files.get('image')
        if not file:
            return jsonify({'error': 'No image provided'}), 400

        image_bytes = file.read()
        tolerance = 0.6  # fixed, enforced value

        emp = Employee.query.get(employee_id)
        if emp is None:
            return jsonify({'error': 'Employee not found'}), 404

        try:
            match = matches_face_image(emp, image_bytes, tolerance=tolerance)
        except RuntimeError as e:
            return jsonify({'error': str(e)}), 500

        return jsonify({'match': bool(match)})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@verification_bp.route('/save_qr', methods=['POST'])
def save_qr():
    data = request.get_json()
    image_data = data.get('image') # Base64 string
    employee_name = data.get('name')

    if not image_data or not employee_name:
        return jsonify({"error": "Missing data"}), 400

    try:
        # Usuwamy nagłówek "data:image/png;base64," z ciągu Base64
        header, encoded = image_data.split(",", 1)
        binary_data = base64.b64decode(encoded)

        # Tworzymy ścieżkę pliku (np. ./QRcode/Jan Kowalski.png)
        # Używamy .replace, aby usunąć znaki, których system operacyjny nie lubi w nazwach plików
        clean_name = "".join([c for c in employee_name if c.isalnum() or c in (' ', '-', '_')]).strip()
        file_path = os.path.join(QR_FOLDER, f"{clean_name}.png")

        # Zapisujemy plik (wb = write binary). To automatycznie nadpisze istniejący plik.
        with open(file_path, 'wb') as f:
            f.write(binary_data)

        return jsonify({"message": f"Saved to {file_path}"}), 200
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500