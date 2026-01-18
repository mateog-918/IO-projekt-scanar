"""
Verification API Endpoints
--------------------------
Blueprints for verification-related API endpoints, handling QR code 
validation and face matching logic.
"""
import base64
import os

from flask import Blueprint, request, jsonify
from app.services.qr_service import QRService
from app.services.face_recog import matches_face_image
from app.services.logging_service import LoggingService
from app.models.employee import Employee
from app.models.event_log import EventType

verification_bp = Blueprint('verification', __name__)

#: Path to the folder where generated QR codes are stored
QR_FOLDER = './static/qr_codes'

if not os.path.exists(QR_FOLDER):
    os.makedirs(QR_FOLDER)

@verification_bp.route('/qr', methods=['POST'])
def verify_qr():
    """
    Verifies a scanned QR code and logs the scan event.

    Expects a JSON payload containing the QR hash and an optional image.

    **Request Body:**

    .. code-block:: json

        {
            "qr_data": "hash_qr_kodu",
            "image": "base64_encoded_image_optional"
        }

    Returns:
        tuple: A JSON response and an HTTP status code.
        
        .. code-block:: json

            {
                "success": true,
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
        image_data = data.get('image') 
        
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
    Matches a captured face image against the stored encodings for an employee.

    Args:
        employee_id (int): The ID of the employee to verify.

    **Request:**
        Multipart/form-data with a file field named ``image``.

    Returns:
        Response: JSON indicating match status and the log ID.
        
        .. code-block:: json

            {
                "match": true,
                "log_id": 123
            }
    """
    try:
        file = request.files.get('image')
        if not file:
            return jsonify({'error': 'No image provided'}), 400

        image_bytes = file.read()
        tolerance = 0.6 

        emp = Employee.query.get(employee_id)
        if emp is None:
            return jsonify({'error': 'Employee not found'}), 404

        try:
            match = matches_face_image(emp, image_bytes, tolerance=tolerance)
        except RuntimeError as e:
            return jsonify({'error': str(e)}), 500

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
    """
    Saves a generated QR code image to the local filesystem.

    Expects a JSON payload with a base64 image, employee name, and ID.

    **Request Body:**

    .. code-block:: json

        {
            "image": "data:image/png;base64,...",
            "name": "Jan Kowalski",
            "id": 1
        }
    """
    data = request.get_json()
    image_data = data.get('image')
    employee_name = data.get('name')
    employee_id = data.get('id')

    if not image_data or not employee_name:
        return jsonify({"error": "Missing data"}), 400

    try:
        header, encoded = image_data.split(",", 1)
        binary_data = base64.b64decode(encoded)

        clean_name = "".join([c for c in employee_name if c.isalnum() or c in (' ', '-', '_')]).strip() + f" {employee_id}"
        file_path = os.path.join(QR_FOLDER, f"{clean_name}.png")

        with open(file_path, 'wb') as f:
            f.write(binary_data)

        return jsonify({"message": f"Saved to {file_path}"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500