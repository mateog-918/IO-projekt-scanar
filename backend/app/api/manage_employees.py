from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
import os
import io
import uuid
import numpy as np
from PIL import Image

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


        return jsonify({'success': True, 'employee': employee.to_dict()}), 201

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
        if emp.count_face_encodings() >= 5:
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

        added = emp.add_face_encoding(query_vec, image_path=db_path)
        if not added:
            return jsonify({'success': False, 'message': 'Could not add encoding (limit reached)'}), 400

        db.session.add(emp)
        db.session.commit()

        return jsonify({'success': True, 'message': 'Image added', 'image_path': db_path, 'count': emp.count_face_encodings()}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Błąd serwera: {str(e)}'}), 500
    

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



        





