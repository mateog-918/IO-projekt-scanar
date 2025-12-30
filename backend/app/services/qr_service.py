from app.models.employee import Employee, db
import hashlib

class QRService:

    @staticmethod
    def validate_qr_code(qr_data):
        """
        Waliduje QR kod i zwraca dane pracownika
        
        Args:
            qr_data: String z QR kodu (np. "EMP123456789")
            
        Returns:
            dict: {'success': bool, 'employee': dict, 'message': str}
        """
        if not qr_data:
            return {'success': False, 'employee': None, 'message': 'Brak danych QR kodu'}
        
        #qr_hash = hashlib.sha256(qr_data.encode()).hexdigest()

        employee = Employee.query.filter_by(qr_code_hash=qr_data, is_active=True).first()

        if not employee:
            return {'success': False, 'employee': None, 'message': 'Nie znaleziono pracownika dla podanego QR kodu'}
        
        return {'success': True, 'employee': employee.to_dict(), 'message': f'Witaj, {employee.name}'}
    
    @staticmethod
    def generate_qr_code(employee_id):
        """
        Generuje unikalny QR kod dla pracownika
        
        Args:
            employee_id: ID pracownika
            
        Returns:
            str: Unikalny hash QR
        """
        import uuid #uniwersalny indentyfikator
        import time

        unique_string = f"{employee_id}-{time.time()}-{uuid.uuid4()}"
        qr_hash = hashlib.sha256(unique_string.encode()).hexdigest()

        return qr_hash
    


