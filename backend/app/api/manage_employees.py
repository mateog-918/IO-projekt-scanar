from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
import os
import io
import uuid
import numpy as np
from PIL import Image

from app.services.qr_service import QRService
from app.services.face_recog import add_face_encoding, count_face_encodings
from app.models.employee import db, Employee


employees_bp = Blueprint('manage_employees', __name__)


@employees_bp.route('/', methods=['POST'])
def add_employee():
    """
    Dodaj nowego pracownika (bez automatycznego generowania QR kodu)
    """
    try:
        data = request.get_json()

        if not data or 'name' not in data:
            return jsonify({'success': False, 'message': 'Brak danych pracownika'}), 400
        
        employee = Employee(
            name=data['name'],
            position=data.get('position', ''),
            department=data.get('department', ''),
            qr_code_hash=''
        )

        db.session.add(employee)
        db.session.commit()

        return jsonify({'success': True, 'employee': employee.to_dict()}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Błąd serwera: {str(e)}'
        }), 500


@employees_bp.route('/<int:employee_id>/qr', methods=['POST'])
def generate_employee_qr(employee_id):
    """
    Wygeneruj QR kod dla pracownika
    """
    try:
        employee = Employee.query.get(employee_id)
        if not employee:
            return jsonify({'success': False, 'message': 'Nie znaleziono pracownika'}), 404
        
        # Generowanie QR kodu
        qr_hash = QRService.generate_qr_code(employee.id)
        employee.qr_code_hash = qr_hash
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'QR kod wygenerowany',
            'employee': employee.to_dict(),
            'qr_code_hash': qr_hash
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Błąd serwera: {str(e)}'
        }), 500


@employees_bp.route('/<int:employee_id>/faces', methods=['POST'])
def add_employee_face(employee_id):
    """Upload image (multipart/form-data; file field 'image') and add face encoding to employee.
    Returns JSON {success: bool, message: str, image_path: str, count: int}.
    """
    try:
        file = request.files.get('image')
        if not file:
            return jsonify({'success': False, 'message': 'No image provided'}), 400

        emp = Employee.query.get(employee_id)
        if emp is None:
            return jsonify({'success': False, 'message': 'Employee not found'}), 404

        # Check available slot
        if count_face_encodings(emp) >= 5:
            return jsonify({'success': False, 'message': 'Employee already has 5 face images'}), 400

        # Read image bytes
        image_bytes = file.read()

        # compute embedding using face_recognition
        try:
            import face_recognition
        except Exception as e:
            return jsonify({'success': False, 'message': 'face_recognition is required for this operation'}), 500

        try:
            img = Image.open(io.BytesIO(image_bytes)).convert('RGB')
            img_arr = np.array(img)
            encs = face_recognition.face_encodings(img_arr)
            if not encs:
                return jsonify({'success': False, 'message': 'No face detected in image'}), 400
            query_vec = encs[0]
        except Exception as e:
            return jsonify({'success': False, 'message': f'Error processing image: {str(e)}'}), 400

        # store image to static/face_images
        filename = secure_filename(file.filename) or f"{uuid.uuid4().hex}.jpg"
        ext = os.path.splitext(filename)[1] or '.jpg'
        final_name = f"{employee_id}_{uuid.uuid4().hex}{ext}"
        save_dir = os.path.join(current_app.root_path, 'static', 'face_images')
        os.makedirs(save_dir, exist_ok=True)
        save_path = os.path.join(save_dir, final_name)
        with open(save_path, 'wb') as fh:
            fh.write(image_bytes)

        db_path = os.path.join('static', 'face_images', final_name)

        added = add_face_encoding(emp, query_vec, image_path=db_path)
        if not added:
            return jsonify({'success': False, 'message': 'Could not add encoding (limit reached)'}), 400

        db.session.add(emp)
        db.session.commit()

        return jsonify({'success': True, 'message': 'Image added', 'image_path': db_path, 'count': count_face_encodings(emp)}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Błąd serwera: {str(e)}'}), 500
    

@employees_bp.route('/', methods=['GET'])
def get_employees():
    """
    Pobierz listę wszystkich pracowników
    Parametr opcjonalny: ?active=true/false/all (domyślnie: all)
    """
    try:
        # Get optional filter parameter
        active_filter = request.args.get('active', 'all').lower()
        
        if active_filter == 'true':
            employees = Employee.query.filter_by(is_active=True).all()
        elif active_filter == 'false':
            employees = Employee.query.filter_by(is_active=False).all()
        else:  # 'all' or any other value
            employees = Employee.query.all()
        
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
        if not employee:
            return jsonify({'success': False, 'message': 'Nie znaleziono pracownika'}), 404
        
        return jsonify({'success': True, 'employee': employee.to_dict()}), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Błąd serwera: {str(e)}'
        }), 500


@employees_bp.route('/<int:employee_id>', methods=['PUT'])
def update_employee(employee_id):
    """
    Edytuj dane pracownika (name, position, department)
    """
    try:
        employee = Employee.query.get(employee_id)
        if not employee:
            return jsonify({'success': False, 'message': 'Nie znaleziono pracownika'}), 404
        
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': 'Brak danych do aktualizacji'}), 400
        
        # Update allowed fields
        if 'name' in data:
            employee.name = data['name']
        if 'position' in data:
            employee.position = data['position']
        if 'department' in data:
            employee.department = data['department']
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Dane pracownika zaktualizowane',
            'employee': employee.to_dict()
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Błąd serwera: {str(e)}'
        }), 500


@employees_bp.route('/<int:employee_id>/deactivate', methods=['PUT'])
def deactivate_employee(employee_id):
    """
    Dezaktywuj pracownika (soft delete)
    """
    try:
        employee = Employee.query.get(employee_id)
        if not employee:
            return jsonify({'success': False, 'message': 'Nie znaleziono pracownika'}), 404
        
        if not employee.is_active:
            return jsonify({'success': False, 'message': 'Pracownik jest już dezaktywowany'}), 400
        
        employee.is_active = False
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Pracownik {employee.name} został dezaktywowany',
            'employee': employee.to_dict()
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Błąd serwera: {str(e)}'
        }), 500


@employees_bp.route('/<int:employee_id>/activate', methods=['PUT'])
def activate_employee(employee_id):
    """
    Reaktywuj pracownika
    """
    try:
        employee = Employee.query.get(employee_id)
        if not employee:
            return jsonify({'success': False, 'message': 'Nie znaleziono pracownika'}), 404
        
        if employee.is_active:
            return jsonify({'success': False, 'message': 'Pracownik jest już aktywny'}), 400
        
        employee.is_active = True
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Pracownik {employee.name} został reaktywowany',
            'employee': employee.to_dict()
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Błąd serwera: {str(e)}'
        }), 500


@employees_bp.route('/<int:employee_id>/faces/<int:face_index>', methods=['DELETE'])
def delete_employee_face(employee_id, face_index):
    """
    Usuń konkretną twarz pracownika (index 1-5)
    """
    try:
        employee = Employee.query.get(employee_id)
        if not employee:
            return jsonify({'success': False, 'message': 'Nie znaleziono pracownika'}), 404
        
        if face_index < 1 or face_index > 5:
            return jsonify({'success': False, 'message': 'Nieprawidłowy indeks twarzy (1-5)'}), 400
        
        # Get image path before deleting
        image_path_attr = f'face_image_path_{face_index}'
        image_path = getattr(employee, image_path_attr)
        
        # Delete from database
        setattr(employee, f'face_encoding_{face_index}', None)
        setattr(employee, image_path_attr, None)
        
        # Delete physical file if exists
        if image_path:
            full_path = os.path.join(current_app.root_path, image_path)
            if os.path.exists(full_path):
                try:
                    os.remove(full_path)
                except Exception as e:
                    print(f"Warning: Could not delete file {full_path}: {e}")
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Twarz {face_index} została usunięta',
            'remaining_faces': count_face_encodings(employee)
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Błąd serwera: {str(e)}'
        }), 500


@employees_bp.route('/<int:employee_id>', methods=['DELETE'])
def delete_employee(employee_id):
    """
    Usuń pracownika całkowicie z bazy (hard delete)
    Wymaga parametru confirm=true dla bezpieczeństwa
    """
    try:
        # Security check - require confirmation
        confirm = request.args.get('confirm', '').lower()
        if confirm != 'true':
            return jsonify({
                'success': False,
                'message': 'Wymagane potwierdzenie: dodaj parametr ?confirm=true'
            }), 400
        
        employee = Employee.query.get(employee_id)
        if not employee:
            return jsonify({'success': False, 'message': 'Nie znaleziono pracownika'}), 404
        
        employee_name = employee.name
        
        # Delete all face image files
        for i in range(1, 6):
            image_path = getattr(employee, f'face_image_path_{i}')
            if image_path:
                full_path = os.path.join(current_app.root_path, image_path)
                if os.path.exists(full_path):
                    try:
                        os.remove(full_path)
                    except Exception as e:
                        print(f"Warning: Could not delete file {full_path}: {e}")
        
        # Delete QR code file if exists
        qr_path = os.path.join(current_app.root_path, 'static', 'qr_codes', f'{employee_id}.png')
        if os.path.exists(qr_path):
            try:
                os.remove(qr_path)
            except Exception as e:
                print(f"Warning: Could not delete QR file {qr_path}: {e}")
        
        # Delete from database
        db.session.delete(employee)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Pracownik {employee_name} został całkowicie usunięty'
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Błąd serwera: {str(e)}'
        }), 500


        





