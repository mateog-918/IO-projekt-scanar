""""
Blueprints for verification-related API endpoints.
"""

from flask import Blueprint, request, jsonify
from app.services.qr_service import QRService


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