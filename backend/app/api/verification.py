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
from app.services.logging_service import LoggingService
from app.models.employee import Employee
from app.models.event_log import EventType


verification_bp = Blueprint('verification', __name__)

# Ścieżka do folderu zapisu
QR_FOLDER = './static/qr_codes'

# Tworzymy folder, jeśli nie istnieje
if not os.path.exists(QR_FOLDER):
    os.makedirs(QR_FOLDER)

@verification_bp.route('/qr', methods=['POST'])
def verify_qr():
    """
    Endpoint do weryfikacji QR kodu
    
    Expected JSON:
    {
        "qr_data": "hash_qr_kodu",
        "image": "base64_encoded_image_optional"
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
        image_data = data.get('image')  # Optional base64 image
        
        # Extract binary image if provided
        image_bytes = None
        if image_data:
            try:
                if ',' in image_data:
                    header, encoded = image_data.split(",", 1)
                    image_bytes = base64.b64decode(encoded)
                else:
                    image_bytes = base64.b64decode(image_data)
            except Exception as e:
                print(f"Error decoding image: {e}")

        result = QRService.validate_qr_code(qr_data)

        # Log the event
        if result['success']:
            employee_id = result['employee']['id']
            LoggingService.log_event(
                event_type=EventType.QR_SCANNED,
                employee_id=employee_id,
                qr_code_hash=qr_data,
                image_bytes=image_bytes,
                message=f"QR code successfully scanned for {result['employee']['name']}"
            )
        else:
            LoggingService.log_event(
                event_type=EventType.INVALID_QR,
                qr_code_hash=qr_data,
                image_bytes=image_bytes,
                message=f"Invalid QR code scanned"
            )

        status_code = 200 if result['success'] else 404
        return jsonify(result), status_code

    except Exception as e:
        return jsonify({'success': False, 'message': str(e), 'employee': None}), 500


@verification_bp.route('/employees/<int:employee_id>/match', methods=['POST'])
def match_employee_face(employee_id):
    """
    POST multipart/form-data with file field 'image'. 
    Returns JSON {'match': true/false, 'message': '...', 'log_id': 123}.
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

        # Log the event
        if match:
            event_log = LoggingService.log_event(
                event_type=EventType.VERIFICATION_SUCCESS,
                employee_id=employee_id,
                image_bytes=image_bytes,
                message=f"Successful verification for employee {emp.name}"
            )
        else:
            event_log = LoggingService.log_event(
                event_type=EventType.FACE_MISMATCH,
                employee_id=employee_id,
                image_bytes=image_bytes,
                message=f"Face mismatch for employee {emp.name}"
            )

        response = {'match': bool(match)}
        if event_log:
            response['log_id'] = event_log.id
        
        return jsonify(response)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@verification_bp.route('/save_qr', methods=['POST'])
def save_qr():
    data = request.get_json()
    image_data = data.get('image') # Base64 string
    employee_name = data.get('name')
    employee_id = data.get('id')


    if not image_data or not employee_name:
        return jsonify({"error": "Missing data"}), 400

    try:
        # Usuwamy nagłówek "data:image/png;base64," z ciągu Base64
        header, encoded = image_data.split(",", 1)
        binary_data = base64.b64decode(encoded)


        # Używamy .replace, aby usunąć znaki, których system operacyjny nie lubi w nazwach plików
        clean_name = "".join([c for c in employee_name if c.isalnum() or c in (' ', '-', '_')]).strip() + f" {employee_id}"
        file_path = os.path.join(QR_FOLDER, f"{clean_name}.png")

        # Zapisujemy plik (wb = write binary). To automatycznie nadpisze istniejący plik.
        with open(file_path, 'wb') as f:
            f.write(binary_data)

        return jsonify({"message": f"Saved to {file_path}"}), 200
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500