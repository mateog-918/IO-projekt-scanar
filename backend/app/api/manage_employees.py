"""
Employee Management API Module
------------------------------
This module provides the Flask Blueprint and routes for CRUD operations 
on employees, QR code generation, and biometric data management.
"""

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
    Creates a new employee record in the database.
    
    This endpoint initializes the employee profile but does not automatically 
    generate a QR code or upload face images.

    **Expected JSON:**

    .. code-block:: json

        {
            "name": "Jan Kowalski",
            "position": "Engineer",
            "department": "IT"
        }

    Returns:
        JSON: A success flag and the serialized employee dictionary.
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
    Generates a unique QR code hash for an employee.

    This hash is used to generate the physical QR code for verification.

    Args:
        employee_id (int): The unique ID of the employee.

    Returns:
        JSON: Success status and the generated QR hash string.
    """
    try:
        employee = Employee.query.get(employee_id)
        if not employee:
            return jsonify({'success': False, 'message': 'Nie znaleziono pracownika'}), 404
        
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
    """
    Uploads a face image and extracts biometric encodings for an employee.
    
    Expects a multipart/form-data request with a file field named 'image'.
    The system extracts the first detected face and stores it in one of the 
    5 available slots.

    Args:
        employee_id (int): Target employee ID.

    Returns:
        JSON: Path to the stored image and the updated face count.
    """
    try:
        file = request.files.get('image')
        if not file:
            return jsonify({'success': False, 'message': 'No image provided'}), 400

        emp = Employee.query.get(employee_id)
        if emp is None:
            return jsonify({'success': False, 'message': 'Employee not found'}), 404

        if count_face_encodings(emp) >= 5:
            return jsonify({'success': False, 'message': 'Employee already has 5 face images'}), 400

        image_bytes = file.read()

        try:
            import face_recognition
        except Exception as e:
            return jsonify({'success': False, 'message': 'face_recognition is required'}), 500

        try:
            img = Image.open(io.BytesIO(image_bytes)).convert('RGB')
            img_arr = np.array(img)
            encs = face_recognition.face_encodings(img_arr)
            if not encs:
                return jsonify({'success': False, 'message': 'No face detected in image'}), 400
            query_vec = encs[0]
        except Exception as e:
            return jsonify({'success': False, 'message': f'Error processing image: {str(e)}'}), 400

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
            return jsonify({'success': False, 'message': 'Could not add encoding'}), 400

        db.session.add(emp)
        db.session.commit()

        return jsonify({
            'success': True, 
            'message': 'Image added', 
            'image_path': db_path, 
            'count': count_face_encodings(emp)
        }), 200

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
        else:
            employees = Employee.query.all()
        
        return jsonify({
            'success': True,
            'employees': [emp.to_dict() for emp in employees]
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'message': f'Błąd serwera: {str(e)}'}), 500

@employees_bp.route('/<int:employee_id>', methods=['GET'])
def get_employee(employee_id):
    """
    Retrieves a single employee's data by their ID.
    """
    try:
        employee = Employee.query.get(employee_id)
        if not employee:
            return jsonify({'success': False, 'message': 'Nie znaleziono pracownika'}), 404
        return jsonify({'success': True, 'employee': employee.to_dict()}), 200
    except Exception as e:
        return jsonify({'success': False, 'message': f'Błąd serwera: {str(e)}'}), 500

@employees_bp.route('/<int:employee_id>', methods=['PUT'])
def update_employee(employee_id):
    """
    Updates basic employee details.

    **Allowed JSON fields:** `name`, `position`, `department`.
    """
    try:
        employee = Employee.query.get(employee_id)
        if not employee:
            return jsonify({'success': False, 'message': 'Nie znaleziono pracownika'}), 404
        
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': 'Brak danych do aktualizacji'}), 400
        
        if 'name' in data:
            employee.name = data['name']
        if 'position' in data:
            employee.position = data['position']
        if 'department' in data:
            employee.department = data['department']
        
        db.session.commit()
        return jsonify({'success': True, 'employee': employee.to_dict()}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Błąd serwera: {str(e)}'}), 500

@employees_bp.route('/<int:employee_id>/deactivate', methods=['PUT'])
def deactivate_employee(employee_id):
    """
    Sets an employee's status to inactive (Soft Delete).
    """
    try:
        employee = Employee.query.get(employee_id)
        if not employee:
            return jsonify({'success': False, 'message': 'Nie znaleziono'}), 404
        
        employee.is_active = False
        db.session.commit()
        return jsonify({'success': True, 'message': 'Dezaktywowano'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@employees_bp.route('/<int:employee_id>/activate', methods=['PUT'])
def activate_employee(employee_id):
    """
    Sets an employee's status back to active.
    """
    try:
        employee = Employee.query.get(employee_id)
        if not employee:
            return jsonify({'success': False, 'message': 'Nie znaleziono'}), 404
        
        employee.is_active = True
        db.session.commit()
        return jsonify({'success': True, 'message': 'Aktywowano'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@employees_bp.route('/<int:employee_id>/faces/<int:face_index>', methods=['DELETE'])
def delete_employee_face(employee_id, face_index):
    """
    Removes a specific face encoding and its image file from the employee.

    Args:
        employee_id (int): Employee ID.
        face_index (int): Index (1 to 5) of the face slot to clear.
    """
    try:
        employee = Employee.query.get(employee_id)
        if not employee:
            return jsonify({'success': False, 'message': 'Nie znaleziono'}), 404
        
        if face_index < 1 or face_index > 5:
            return jsonify({'success': False, 'message': 'Zły indeks (1-5)'}), 400
        
        image_path_attr = f'face_image_path_{face_index}'
        image_path = getattr(employee, image_path_attr)
        
        setattr(employee, f'face_encoding_{face_index}', None)
        setattr(employee, image_path_attr, None)
        
        if image_path:
            full_path = os.path.join(current_app.root_path, image_path)
            if os.path.exists(full_path):
                os.remove(full_path)
        
        db.session.commit()
        return jsonify({'success': True, 'remaining': count_face_encodings(employee)}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@employees_bp.route('/<int:employee_id>', methods=['DELETE'])
def delete_employee(employee_id):
    """
    Permanently deletes an employee and all associated files (Hard Delete).
    
    Args:
        confirm (str): Query parameter. Must be 'true' to confirm deletion.
    """
    try:
        confirm = request.args.get('confirm', '').lower()
        if confirm != 'true':
            return jsonify({'error': 'Wymagane potwierdzenie ?confirm=true'}), 400
        
        employee = Employee.query.get(employee_id)
        if not employee:
            return jsonify({'success': False, 'message': 'Nie znaleziono'}), 404
        
        # Cleanup files
        for i in range(1, 6):
            p = getattr(employee, f'face_image_path_{i}')
            if p:
                f = os.path.join(current_app.root_path, p)
                if os.path.exists(f): os.remove(f)
        
        db.session.delete(employee)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Usunięto całkowicie'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500