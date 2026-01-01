""""
Blueprints for verification-related API endpoints.
"""

from flask import Blueprint, request, jsonify
from app.services.qr_service import QRService
from app.models.employee import Employee


verification_bp = Blueprint('verification', __name__)

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
            match = emp.matches_face_image(image_bytes, tolerance=tolerance)
        except RuntimeError as e:
            return jsonify({'error': str(e)}), 500

        return jsonify({'match': bool(match)})

    except Exception as e:
        return jsonify({'error': str(e)}), 500