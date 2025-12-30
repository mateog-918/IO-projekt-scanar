from flask import Blueprint, request, jsonify
from app.services.qr_service import QRService
from app.models.employee import db, Employee


employees_bp = Blueprint('manage_employees', __name__)


@employees_bp.route('/', methods=['POST'])
def add_employee():
    """
    Dodaj nowego pracownika i wygeneruj QR kod
    """
    try:
        data = request.get_json()

        if not data or 'name' not in data:
            return jsonify({'success': False, 'message': 'Brak danych pracownika'}), 400
        

        employee = Employee(
            name=data['name'],
            position=data.get('position', ''),
            department=data.get('department', ''),
            qr_code_hash=''  # tymczasowo puste, zostanie zaktualizowane poniżej
        )

        db.session.add(employee)
        db.session.flush()

        #Generowanie QR kodu
        qr_hash = QRService.generate_qr_code(employee.id)
        employee.qr_code_hash = qr_hash

        db.session.commit()


        return jsonify({'success': True, 'message': 'Pracownik dodany', 'employee': employee.to_dict()}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Błąd serwera: {str(e)}'
        }), 500
    

@employees_bp.route('/', methods=['GET'])
def get_employees():
    """
    Pobierz listę wszystkich pracowników
    """

    try:
        employees = Employee.query.filter_by(is_active=True).all()
        return jsonify({
            'success': True,
            'employees': [emp.to_dict() for emp in employees]
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Błąd serwera: {str(e)}'
        }), 500
    

@employees_bp.route('/<int:employee_id>', methods=['GET'])
def get_employee(employee_id):
    """
    Pobierz dane konkretnego pracownika po ID
    """
    try:
        employee = Employee.query.get(employee_id)
        if not employee or not employee.is_active:
            return jsonify({'success': False, 'message': 'Nie znaleziono pracownika'}), 404
        
        return jsonify({'success': True, 'employee': employee.to_dict()}), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Błąd serwera: {str(e)}'
        }), 500



        





